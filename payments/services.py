from django.db import transaction
from django.db.models import F
from django.utils import timezone

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
