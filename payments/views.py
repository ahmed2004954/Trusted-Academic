from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from teachers.models import BookingMode

from .forms import PaymentReceiptForm, PaymentRejectionForm
from .models import Payment


PAYABLE_STATUSES = {
    Booking.BookingStatus.PENDING_PAYMENT,
    Booking.BookingStatus.AWAITING_STUDENT_PAYMENT,
}


def _manual_payment_details() -> dict:
    return {
        'vodafone_cash_number': settings.MANUAL_PAYMENT_VODAFONE_CASH_NUMBER,
        'instapay_handle': settings.MANUAL_PAYMENT_INSTAPAY_HANDLE,
        'ewallet_instructions': settings.MANUAL_PAYMENT_EWALLET_INSTRUCTIONS,
    }


def _get_or_create_payment(booking: Booking) -> Payment:
    payment, _created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.price,
            'currency': 'EGP',
            'payment_method': Payment.PaymentMethod.VODAFONE_CASH,
        },
    )
    if payment.amount != booking.price:
        payment.amount = booking.price
        payment.save(update_fields=['amount', 'updated_at'])
    return payment


def _send_payment_email(payment: Payment, subject: str, body: str) -> None:
    recipient = payment.booking.student.email
    if recipient:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)


def _booking_summary(booking: Booking) -> str:
    return (
        f'Booking #{booking.pk}\n'
        f'Teacher: {booking.teacher.user.get_full_name()}\n'
        f'Subject: {booking.subject.name} - {booking.grade_level.name}\n'
        f'Scheduled: {booking.scheduled_start:%Y-%m-%d %H:%M}\n'
        f'Amount: {booking.price} EGP'
    )


@login_required
def payment_instructions(request, booking_pk):
    if request.user.role != 'student':
        raise PermissionDenied
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=booking_pk,
        student=request.user,
    )
    if booking.booking_status not in PAYABLE_STATUSES:
        messages.error(request, _('This booking is not ready for payment.'))
        return redirect('bookings:student_detail', pk=booking.pk)

    payment = _get_or_create_payment(booking)
    if request.method == 'POST':
        form = PaymentReceiptForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            with transaction.atomic():
                payment = form.save(commit=False)
                payment.amount = booking.price
                payment.currency = 'EGP'
                payment.payment_status = Payment.PaymentStatus.AWAITING_VERIFICATION
                payment.rejection_reason = ''
                payment.save()
                booking.booking_status = Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION
                booking.save(update_fields=['booking_status', 'updated_at'])
            messages.success(request, _('Receipt uploaded. We will verify it shortly.'))
            return redirect('payments:history')
    else:
        form = PaymentReceiptForm(instance=payment)

    return render(
        request,
        'payments/instructions.html',
        {
            'booking': booking,
            'payment': payment,
            'form': form,
            'manual_payment_details': _manual_payment_details(),
        },
    )


@login_required
def payment_history(request):
    if request.user.role != 'student':
        raise PermissionDenied
    payments = Payment.objects.filter(booking__student=request.user).select_related(
        'booking__teacher__user', 'booking__subject', 'booking__grade_level'
    )
    return render(request, 'payments/history.html', {'payments': payments})


@staff_member_required
def pending_verifications(request):
    payments = Payment.objects.filter(payment_status=Payment.PaymentStatus.AWAITING_VERIFICATION).select_related(
        'booking__student', 'booking__teacher__user', 'booking__subject', 'booking__grade_level'
    )
    return render(request, 'payments/admin_pending.html', {'payments': payments})


@staff_member_required
def verification_detail(request, payment_pk):
    payment = get_object_or_404(
        Payment.objects.select_related('booking__student', 'booking__teacher__user', 'booking__subject', 'booking__grade_level'),
        pk=payment_pk,
    )
    form = PaymentRejectionForm()
    return render(request, 'payments/admin_detail.html', {'payment': payment, 'form': form})


@staff_member_required
def approve_payment(request, payment_pk):
    if request.method != 'POST':
        raise PermissionDenied
    payment = get_object_or_404(Payment.objects.select_related('booking__student', 'booking__teacher__user'), pk=payment_pk)
    with transaction.atomic():
        now = timezone.now()
        booking = payment.booking
        payment.payment_status = Payment.PaymentStatus.PAID
        payment.verified_by = request.user
        payment.verified_at = now
        payment.paid_at = now
        payment.rejection_reason = ''
        payment.save(update_fields=['payment_status', 'verified_by', 'verified_at', 'paid_at', 'rejection_reason', 'updated_at'])

        if not booking.attendance_code:
            booking.generate_attendance_code()
        booking.booking_status = Booking.BookingStatus.CONFIRMED
        booking.save(update_fields=['booking_status', 'attendance_code', 'updated_at'])

    _send_payment_email(
        payment,
        _('Payment approved'),
        _('Your payment has been approved.\n\n') + _booking_summary(payment.booking),
    )
    messages.success(request, _('Payment approved and booking confirmed.'))
    return redirect('payments:admin_pending')


@staff_member_required
def reject_payment(request, payment_pk):
    if request.method != 'POST':
        raise PermissionDenied
    payment = get_object_or_404(Payment.objects.select_related('booking__student', 'booking__teacher__user'), pk=payment_pk)
    form = PaymentRejectionForm(request.POST)
    if not form.is_valid():
        return render(request, 'payments/admin_detail.html', {'payment': payment, 'form': form})

    with transaction.atomic():
        booking = payment.booking
        payment.payment_status = Payment.PaymentStatus.FAILED
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.rejection_reason = form.cleaned_data['rejection_reason'].strip()
        payment.save(update_fields=['payment_status', 'verified_by', 'verified_at', 'rejection_reason', 'updated_at'])

        booking.booking_status = (
            Booking.BookingStatus.AWAITING_STUDENT_PAYMENT
            if booking.booking_mode == BookingMode.MANUAL
            else Booking.BookingStatus.PENDING_PAYMENT
        )
        booking.save(update_fields=['booking_status', 'updated_at'])

    _send_payment_email(
        payment,
        _('Payment receipt rejected'),
        _('Your payment receipt was rejected. Reason: %(reason)s\n\n') % {'reason': payment.rejection_reason}
        + _booking_summary(payment.booking),
    )
    messages.success(request, _('Payment rejected and booking returned to payable status.'))
    return redirect('payments:admin_pending')
