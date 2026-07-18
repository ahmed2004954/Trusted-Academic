from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.test_helpers import (
    create_offering,
    create_payment,
    create_student,
    create_teacher,
    create_test_booking,
    create_user,
)
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

    def test_teacher_can_reject_manual_booking(self):
        teacher = create_teacher(
            email='reject-teacher@example.com',
            booking_mode=BookingMode.MANUAL,
            full_name='Reject Teacher',
        )
        offering = create_offering(teacher=teacher)
        booking = create_test_booking(offering=offering)

        self.client.force_login(teacher.user)
        self.client.post(
            reverse('bookings:teacher_action', args=[booking.pk, 'reject']),
            {'reason': 'Schedule conflict'},
        )

        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, Booking.BookingStatus.TEACHER_REJECTED)


class BookingCreateViewTests(TestCase):
    def test_student_creates_booking_via_view(self):
        offering = create_offering()
        student = create_student(email='booking-student@example.com')
        self.client.force_login(student)
        start = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(
            reverse('bookings:create', args=[offering.teacher_profile.pk]),
            {
                'teacher_subject': offering.pk,
                'scheduled_start': start.strftime('%Y-%m-%dT%H:%M'),
                'duration_minutes': 60,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Booking.objects.filter(student=student, teacher=offering.teacher_profile).exists()
        )

    def test_booking_create_rejects_teacher_role(self):
        offering = create_offering()
        other_teacher = create_teacher(email='other-teacher@example.com')
        self.client.force_login(other_teacher.user)

        response = self.client.get(reverse('bookings:create', args=[offering.teacher_profile.pk]))

        self.assertEqual(response.status_code, 403)

    def test_cannot_book_unapproved_teacher(self):
        teacher = create_teacher(email='pending-book@example.com', approved=False)
        offering = create_offering(teacher=teacher)
        student = create_student(email='book-pending-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('bookings:create', args=[teacher.pk]))

        self.assertEqual(response.status_code, 403)


class BookingListDetailViewTests(TestCase):
    def test_student_sees_own_booking_detail(self):
        booking = create_test_booking()
        self.client.force_login(booking.student)

        response = self.client.get(reverse('bookings:student_detail', args=[booking.pk]))

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_see_other_students_booking(self):
        booking = create_test_booking()
        intruder = create_student(email='intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('bookings:student_detail', args=[booking.pk]))

        self.assertEqual(response.status_code, 404)

    def test_teacher_sees_own_booking_detail(self):
        booking = create_test_booking()
        self.client.force_login(booking.teacher.user)

        response = self.client.get(reverse('bookings:teacher_detail', args=[booking.pk]))

        self.assertEqual(response.status_code, 200)

    def test_student_booking_list_requires_login(self):
        response = self.client.get(reverse('bookings:student_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class BookingCancelRescheduleViewTests(TestCase):
    def test_student_cancels_confirmed_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('bookings:student_cancel', args=[booking.pk]),
            {'reason': 'Cannot attend anymore'},
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, Booking.BookingStatus.CANCELLED_BY_STUDENT)

    def test_student_reschedules_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        self.client.force_login(booking.student)
        new_start = timezone.now() + timezone.timedelta(days=5)

        response = self.client.post(
            reverse('bookings:student_reschedule', args=[booking.pk]),
            {
                'scheduled_start': new_start.strftime('%Y-%m-%dT%H:%M'),
                'reason': 'Need a later slot',
            },
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.scheduled_start.date(), new_start.date())


class AttendanceConfirmationViewTests(TestCase):
    """Attendance completion requires a paid booking so the teacher wallet
    already holds the pending payout (credited at payment approval)."""

    def _confirmed_paid_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        payment = create_payment(booking)
        admin = create_user('attendance-admin@example.com', role='admin', full_name='Admin', is_staff=True)
        self.client.force_login(admin)
        self.client.post(reverse('payments:admin_approve', args=[payment.pk]))
        self.client.logout()

        booking.refresh_from_db()
        now = timezone.now()
        booking.scheduled_start = now - timezone.timedelta(minutes=5)
        booking.scheduled_end = now + timezone.timedelta(minutes=55)
        booking.save(update_fields=['scheduled_start', 'scheduled_end', 'updated_at'])
        return booking

    def test_student_confirms_attendance_with_valid_code(self):
        booking = self._confirmed_paid_booking()
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('bookings:student_confirm_attendance', args=[booking.pk]),
            {'attendance_code': booking.attendance_code},
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, Booking.BookingStatus.COMPLETED)

    def test_wrong_attendance_code_does_not_complete_booking(self):
        booking = self._confirmed_paid_booking()
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('bookings:student_confirm_attendance', args=[booking.pk]),
            {'attendance_code': 'WRONGXXX'},
        )

        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertNotEqual(booking.booking_status, Booking.BookingStatus.COMPLETED)
