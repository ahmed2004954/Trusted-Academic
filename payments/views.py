from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from teachers.models import BookingMode, TeacherProfile
from adminpanel.models import record_audit_log

from .forms import PaymentReceiptForm, PaymentRejectionForm, WithdrawalActionForm, WithdrawalRequestForm
from .models import Payment, WithdrawalRequest
from .services import add_pending_earning, get_or_create_wallet


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


def _send_withdrawal_email(withdrawal: WithdrawalRequest) -> None:
    recipient = withdrawal.teacher.user.email
    if recipient:
        send_mail(
            _('Withdrawal request updated'),
            _(
                'Your withdrawal request #%(request_id)s is now %(status)s.\n\nAmount: %(amount)s EGP\nNotes: %(notes)s'
            ) % {
                'request_id': withdrawal.pk,
                'status': withdrawal.get_status_display(),
                'amount': withdrawal.amount,
                'notes': withdrawal.notes or '-',
            },
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=True,
        )


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
        add_pending_earning(booking)
        record_audit_log(request.user, 'payment.approve', payment, {'booking_id': booking.pk})

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
        record_audit_log(
            request.user,
            'payment.reject',
            payment,
            {'booking_id': booking.pk, 'reason': payment.rejection_reason},
        )

    _send_payment_email(
        payment,
        _('Payment receipt rejected'),
        _('Your payment receipt was rejected. Reason: %(reason)s\n\n') % {'reason': payment.rejection_reason}
        + _booking_summary(payment.booking),
    )
    messages.success(request, _('Payment rejected and booking returned to payable status.'))
    return redirect('payments:admin_pending')


@login_required
def wallet_dashboard(request):
    if request.user.role != 'teacher':
        raise PermissionDenied

    teacher = get_object_or_404(TeacherProfile.objects.select_related('user'), user=request.user)
    wallet = get_or_create_wallet(teacher)
    minimum_threshold = Decimal(str(settings.TEACHER_WITHDRAWAL_MINIMUM_THRESHOLD))

    if request.method == 'POST':
        form = WithdrawalRequestForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.teacher = teacher
            amount = withdrawal.amount
            if amount < minimum_threshold:
                form.add_error('amount', _('Minimum withdrawal amount is %(amount)s EGP.') % {'amount': minimum_threshold})
            elif amount > wallet.available_balance:
                form.add_error('amount', _('Withdrawal amount exceeds available wallet balance.'))
            else:
                withdrawal.save()
                messages.success(request, _('Withdrawal request submitted.'))
                return redirect('payments:wallet')
    else:
        form = WithdrawalRequestForm()

    withdrawals = teacher.withdrawal_requests.select_related('processed_by')
    return render(
        request,
        'payments/wallet.html',
        {
            'wallet': wallet,
            'withdrawals': withdrawals,
            'form': form,
            'minimum_threshold': minimum_threshold,
        },
    )


@staff_member_required
def withdrawal_queue(request):
    withdrawals = WithdrawalRequest.objects.select_related('teacher__user', 'processed_by')
    return render(request, 'payments/admin_withdrawal_queue.html', {'withdrawals': withdrawals})


@staff_member_required
def withdrawal_detail(request, withdrawal_pk):
    withdrawal = get_object_or_404(
        WithdrawalRequest.objects.select_related('teacher__user', 'processed_by'),
        pk=withdrawal_pk,
    )
    wallet = get_or_create_wallet(withdrawal.teacher)
    form = WithdrawalActionForm()
    return render(request, 'payments/admin_withdrawal_detail.html', {'withdrawal': withdrawal, 'wallet': wallet, 'form': form})


@staff_member_required
def process_withdrawal(request, withdrawal_pk, action):
    if request.method != 'POST':
        raise PermissionDenied
    withdrawal = get_object_or_404(WithdrawalRequest.objects.select_related('teacher__user'), pk=withdrawal_pk)
    form = WithdrawalActionForm(request.POST)
    if not form.is_valid():
        wallet = get_or_create_wallet(withdrawal.teacher)
        return render(request, 'payments/admin_withdrawal_detail.html', {'withdrawal': withdrawal, 'wallet': wallet, 'form': form})

    notes = form.cleaned_data['notes']
    try:
        with transaction.atomic():
            withdrawal = WithdrawalRequest.objects.select_for_update().select_related('teacher__user').get(pk=withdrawal.pk)
            if action == 'approve':
                withdrawal.approve_and_reserve_balance(request.user, notes)
            elif action == 'reject':
                withdrawal.reject_without_balance_change(request.user, notes)
            elif action == 'complete':
                withdrawal.complete_with_reserved_balance(request.user, notes)
            else:
                raise PermissionDenied
            record_audit_log(
                request.user,
                f'withdrawal.{action}',
                withdrawal,
                {'notes': notes, 'amount': str(withdrawal.amount)},
            )
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
        return redirect('payments:admin_withdrawal_detail', withdrawal_pk=withdrawal.pk)

    _send_withdrawal_email(withdrawal)
    messages.success(request, _('Withdrawal request updated.'))
    return redirect('payments:admin_withdrawal_detail', withdrawal_pk=withdrawal.pk)
