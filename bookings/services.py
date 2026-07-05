from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from teachers.models import BookingMode, TeacherSubject
from payments.models import Payment, Wallet

from .models import Booking, TeacherBookingViolation


STUDENT_CANCELLABLE_STATUSES = {
    Booking.BookingStatus.CONFIRMED,
    Booking.BookingStatus.PENDING_PAYMENT,
    Booking.BookingStatus.AWAITING_STUDENT_PAYMENT,
    Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION,
}
TEACHER_CANCELLABLE_STATUSES = {Booking.BookingStatus.CONFIRMED}
RESCHEDULABLE_STATUSES = {
    Booking.BookingStatus.CONFIRMED,
    Booking.BookingStatus.PENDING_PAYMENT,
    Booking.BookingStatus.AWAITING_STUDENT_PAYMENT,
    Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION,
}


def calculate_booking_amounts(teacher_subject: TeacherSubject) -> tuple[Decimal, Decimal, Decimal]:
    price = teacher_subject.default_price
    commission_percentage = Decimal(str(settings.PLATFORM_COMMISSION_PERCENTAGE))
    platform_fee = (price * commission_percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    teacher_payout = (price - platform_fee).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return price, platform_fee, teacher_payout


@transaction.atomic
def create_booking(*, student, teacher_subject: TeacherSubject, scheduled_start, duration_minutes: int, parent=None) -> Booking:
    teacher = teacher_subject.teacher_profile
    if not teacher.can_receive_bookings:
        raise ValidationError({'teacher': 'This teacher cannot receive bookings yet.'})
    if not teacher_subject.is_active:
        raise ValidationError({'teacher_subject': 'The selected offering is not active.'})

    price, platform_fee, teacher_payout = calculate_booking_amounts(teacher_subject)
    booking_mode = teacher.booking_mode
    booking_status = (
        Booking.BookingStatus.PENDING_TEACHER_ACCEPTANCE
        if booking_mode == BookingMode.MANUAL
        else Booking.BookingStatus.PENDING_PAYMENT
    )
    booking = Booking(
        student=student,
        teacher=teacher,
        subject=teacher_subject.subject,
        grade_level=teacher_subject.grade_level,
        teacher_subject=teacher_subject,
        lesson_type=teacher_subject.lesson_type,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_start + timedelta(minutes=duration_minutes),
        duration_minutes=duration_minutes,
        price=price,
        platform_fee=platform_fee,
        teacher_payout=teacher_payout,
        booking_status=booking_status,
        booking_mode=booking_mode,
        parent=parent,
    )
    booking.save()
    return booking


def estimate_student_refund(booking: Booking, at_time=None) -> Decimal:
    at_time = at_time or timezone.now()
    if booking.scheduled_start - at_time > timedelta(hours=6):
        return booking.price
    return (booking.price * Decimal('0.80')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def cancel_booking_by_student(booking_id: int, reason: str = '') -> Booking:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related('teacher__user', 'student').get(pk=booking_id)
        if booking.booking_status not in STUDENT_CANCELLABLE_STATUSES:
            raise ValidationError(_('This booking cannot be cancelled by the student.'))
        if booking.scheduled_start <= timezone.now():
            raise ValidationError(_('Bookings can only be cancelled before the lesson starts.'))

        refund_amount = estimate_student_refund(booking)
        _apply_refund_and_wallet_reversal(booking, refund_amount, reason)
        booking.booking_status = Booking.BookingStatus.CANCELLED_BY_STUDENT
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason.strip()
        booking.save(update_fields=['booking_status', 'cancelled_at', 'cancellation_reason', 'updated_at'])

    _send_booking_change_email(
        booking,
        _('Booking cancelled by student'),
        _('Booking #%(booking_id)s was cancelled by the student. Refund amount: %(refund)s EGP. Reason: %(reason)s')
        % {'booking_id': booking.pk, 'refund': refund_amount, 'reason': reason.strip() or '-'},
    )
    return booking


def cancel_booking_by_teacher(booking_id: int, reason: str = '') -> Booking:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related('teacher__user', 'student').get(pk=booking_id)
        if booking.booking_status not in TEACHER_CANCELLABLE_STATUSES:
            raise ValidationError(_('Only confirmed upcoming bookings can be cancelled by the teacher.'))
        if booking.scheduled_start <= timezone.now():
            raise ValidationError(_('Bookings can only be cancelled before the lesson starts.'))

        _apply_refund_and_wallet_reversal(booking, booking.price, reason)
        booking.booking_status = Booking.BookingStatus.CANCELLED_BY_TEACHER
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason.strip()
        booking.save(update_fields=['booking_status', 'cancelled_at', 'cancellation_reason', 'updated_at'])
        TeacherBookingViolation.objects.create(
            teacher=booking.teacher,
            booking=booking,
            violation_type=TeacherBookingViolation.ViolationType.CANCELLATION,
            reason=reason.strip(),
        )

    _send_booking_change_email(
        booking,
        _('Booking cancelled by teacher'),
        _('Booking #%(booking_id)s was cancelled by the teacher. Full refund amount: %(refund)s EGP. Reason: %(reason)s')
        % {'booking_id': booking.pk, 'refund': booking.price, 'reason': reason.strip() or '-'},
    )
    return booking


def reschedule_booking_by_student(booking_id: int, scheduled_start, reason: str = '') -> Booking:
    return _reschedule_booking(booking_id, scheduled_start, reason, actor='student')


def reschedule_booking_by_teacher(booking_id: int, scheduled_start, reason: str = '') -> Booking:
    return _reschedule_booking(booking_id, scheduled_start, reason, actor='teacher')


def _reschedule_booking(booking_id: int, scheduled_start, reason: str, actor: str) -> Booking:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related('teacher__user', 'student').get(pk=booking_id)
        if booking.booking_status not in RESCHEDULABLE_STATUSES:
            raise ValidationError(_('This booking cannot be rescheduled.'))
        if booking.scheduled_start <= timezone.now():
            raise ValidationError(_('Bookings can only be rescheduled before the lesson starts.'))
        if scheduled_start <= timezone.now():
            raise ValidationError(_('New lesson start time must be in the future.'))
        if actor == 'student' and booking.reschedule_count >= 1:
            raise ValidationError(_('Students can reschedule each booking only once.'))

        scheduled_end = scheduled_start + timedelta(minutes=booking.duration_minutes)
        _validate_teacher_overlap(booking, scheduled_start, scheduled_end)

        original_start = booking.scheduled_start
        booking.scheduled_start = scheduled_start
        booking.scheduled_end = scheduled_end
        if actor == 'student':
            booking.reschedule_count += 1
        booking.reschedule_reason = reason.strip()
        booking.save(update_fields=['scheduled_start', 'scheduled_end', 'reschedule_count', 'reschedule_reason', 'updated_at'])

        if actor == 'teacher':
            TeacherBookingViolation.objects.create(
                teacher=booking.teacher,
                booking=booking,
                violation_type=TeacherBookingViolation.ViolationType.RESCHEDULE,
                reason=reason.strip(),
            )

    _send_booking_change_email(
        booking,
        _('Booking rescheduled'),
        _('Booking #%(booking_id)s was rescheduled from %(old_start)s to %(new_start)s. Reason: %(reason)s')
        % {
            'booking_id': booking.pk,
            'old_start': original_start.strftime('%Y-%m-%d %H:%M'),
            'new_start': booking.scheduled_start.strftime('%Y-%m-%d %H:%M'),
            'reason': reason.strip() or '-',
        },
    )
    return booking


def _apply_refund_and_wallet_reversal(booking: Booking, refund_amount: Decimal, reason: str) -> None:
    try:
        payment = Payment.objects.select_for_update().get(booking=booking)
    except Payment.DoesNotExist:
        return

    if payment.payment_status == Payment.PaymentStatus.PAID:
        payment.payment_status = (
            Payment.PaymentStatus.REFUNDED if refund_amount >= payment.amount else Payment.PaymentStatus.PARTIALLY_REFUNDED
        )
    elif payment.payment_status == Payment.PaymentStatus.AWAITING_VERIFICATION:
        payment.payment_status = Payment.PaymentStatus.REFUNDED if refund_amount >= payment.amount else Payment.PaymentStatus.PARTIALLY_REFUNDED

    payment.refund_amount = refund_amount
    payment.refunded_at = timezone.now()
    payment.refund_notes = reason.strip()

    update_fields = ['payment_status', 'refund_amount', 'refunded_at', 'refund_notes', 'updated_at']
    if payment.wallet_pending_credited_at and not payment.wallet_pending_reversed_at and not booking.wallet_settled_at:
        wallet = Wallet.objects.select_for_update().get_or_create(teacher=booking.teacher)[0]
        if wallet.pending_balance < booking.teacher_payout:
            raise ValidationError(_('Wallet pending balance is lower than the booking payout.'))
        wallet.pending_balance -= booking.teacher_payout
        wallet.total_earned -= booking.teacher_payout
        wallet.save(update_fields=['pending_balance', 'total_earned', 'updated_at'])
        payment.wallet_pending_reversed_at = timezone.now()
        update_fields.append('wallet_pending_reversed_at')

    payment.save(update_fields=update_fields)


def _validate_teacher_overlap(booking: Booking, scheduled_start, scheduled_end) -> None:
    if Booking.objects.filter(
        teacher=booking.teacher,
        booking_status__in=Booking.BLOCKING_STATUSES,
        scheduled_start__lt=scheduled_end,
        scheduled_end__gt=scheduled_start,
    ).exclude(pk=booking.pk).exists():
        raise ValidationError(_('This teacher already has a blocking booking at that time.'))


def _send_booking_change_email(booking: Booking, subject: str, body: str) -> None:
    recipients = [email for email in [booking.student.email, booking.teacher.user.email] if email]
    if recipients:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
