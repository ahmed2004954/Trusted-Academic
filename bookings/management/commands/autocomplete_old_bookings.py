from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking
from payments.services import complete_booking_without_attendance


class Command(BaseCommand):
    help = 'Complete confirmed bookings older than 24 hours after scheduled end without attendance confirmation.'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=24)
        booking_ids = Booking.objects.filter(
            booking_status=Booking.BookingStatus.CONFIRMED,
            scheduled_end__lt=cutoff,
            attendance_confirmed_at__isnull=True,
        ).values_list('pk', flat=True)
        updated = 0
        for booking_id in booking_ids:
            if complete_booking_without_attendance(booking_id):
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Auto-completed {updated} booking(s).'))
