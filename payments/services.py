from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from teachers.models import TeacherProfile

from .models import Payment, Wallet


def get_or_create_wallet(teacher: TeacherProfile) -> Wallet:
    wallet, _created = Wallet.objects.get_or_create(teacher=teacher)
    return wallet


def add_pending_earning(booking: Booking) -> bool:
    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(booking=booking)
        if payment.wallet_pending_credited_at:
            return False

        wallet = Wallet.objects.select_for_update().get_or_create(teacher=booking.teacher)[0]
        wallet.pending_balance = F('pending_balance') + booking.teacher_payout
        wallet.total_earned = F('total_earned') + booking.teacher_payout
        wallet.save(update_fields=['pending_balance', 'total_earned', 'updated_at'])

        payment.wallet_pending_credited_at = timezone.now()
        payment.save(update_fields=['wallet_pending_credited_at', 'updated_at'])
        return True


def settle_booking_wallet(booking: Booking) -> bool:
    if booking.wallet_settled_at:
        return False

    wallet = Wallet.objects.select_for_update().get_or_create(teacher=booking.teacher)[0]
    if wallet.pending_balance < booking.teacher_payout:
        raise ValidationError(_('Wallet pending balance is lower than the booking payout.'))
    wallet.pending_balance = F('pending_balance') - booking.teacher_payout
    wallet.available_balance = F('available_balance') + booking.teacher_payout
    wallet.save(update_fields=['pending_balance', 'available_balance', 'updated_at'])
    booking.wallet_settled_at = timezone.now()
    return True


def complete_booking_with_attendance(booking_id: int, attendance_code: str) -> bool:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related('teacher').get(pk=booking_id)
        if booking.booking_status == Booking.BookingStatus.COMPLETED and booking.attendance_confirmed_at:
            settle_booking_wallet(booking)
            booking.save(update_fields=['wallet_settled_at', 'updated_at'])
            return False
        if not booking.can_use_attendance_code():
            raise ValidationError(_('Attendance can only be confirmed during the lesson attendance window.'))
        if not booking.attendance_code or attendance_code.strip().upper() != booking.attendance_code.upper():
            raise ValidationError(_('The attendance code is incorrect.'))

        booking.attendance_confirmed_at = timezone.now()
        booking.booking_status = Booking.BookingStatus.COMPLETED
        settle_booking_wallet(booking)
        booking.save(update_fields=['attendance_confirmed_at', 'booking_status', 'wallet_settled_at', 'updated_at'])
        return True


def complete_booking_without_attendance(booking_id: int) -> bool:
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related('teacher').get(pk=booking_id)
        if booking.booking_status == Booking.BookingStatus.COMPLETED:
            settle_booking_wallet(booking)
            booking.save(update_fields=['wallet_settled_at', 'updated_at'])
            return False
        if booking.booking_status != Booking.BookingStatus.CONFIRMED:
            raise ValidationError(_('Only confirmed bookings can be auto-completed.'))

        booking.booking_status = Booking.BookingStatus.COMPLETED
        settle_booking_wallet(booking)
        booking.save(update_fields=['booking_status', 'wallet_settled_at', 'updated_at'])
        return True
