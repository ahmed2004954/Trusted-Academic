from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.test_helpers import create_offering, create_student, create_teacher, create_test_booking
from teachers.models import BookingMode
from .models import Booking
from .services import create_booking


class BookingRulesTests(TestCase):
    def test_booking_snapshots_price_when_created(self):
        offering = create_offering(default_price=Decimal('200.00'))
        booking = create_test_booking(offering=offering)

        offering.default_price = Decimal('250.00')
        offering.save()
        booking.refresh_from_db()

        self.assertEqual(booking.price, Decimal('200.00'))
        self.assertEqual(booking.platform_fee, Decimal('30.00'))
        self.assertEqual(booking.teacher_payout, Decimal('170.00'))

    def test_overlapping_blocking_booking_is_prevented(self):
        student = create_student()
        offering = create_offering()
        start = timezone.now() + timezone.timedelta(days=1)
        create_booking(student=student, teacher_subject=offering, scheduled_start=start, duration_minutes=60)

        with self.assertRaises(ValidationError):
            create_booking(
                student=create_student(email='other-student@example.com'),
                teacher_subject=offering,
                scheduled_start=start + timezone.timedelta(minutes=30),
                duration_minutes=60,
            )

    def test_non_blocking_completed_booking_does_not_prevent_new_booking(self):
        offering = create_offering()
        start = timezone.now() + timezone.timedelta(days=1)
        create_test_booking(offering=offering, scheduled_start=start, status=Booking.BookingStatus.COMPLETED)

        booking = create_booking(
            student=create_student(email='new-student@example.com'),
            teacher_subject=offering,
            scheduled_start=start + timezone.timedelta(minutes=30),
            duration_minutes=60,
        )

        self.assertEqual(booking.booking_status, Booking.BookingStatus.PENDING_PAYMENT)


class ManualBookingFlowTests(TestCase):
    def test_manual_booking_awaits_teacher_acceptance_before_payment(self):
        teacher = create_teacher(
            email='manual-teacher@example.com',
            booking_mode=BookingMode.MANUAL,
            full_name='Manual Teacher',
        )
        offering = create_offering(teacher=teacher)
        booking = create_test_booking(offering=offering)

        self.assertEqual(booking.booking_status, Booking.BookingStatus.PENDING_TEACHER_ACCEPTANCE)

        self.client.force_login(teacher.user)
        self.client.post(reverse('bookings:teacher_action', args=[booking.pk, 'accept']))

        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, Booking.BookingStatus.AWAITING_STUDENT_PAYMENT)
        self.assertIsNotNone(booking.payment_deadline)
