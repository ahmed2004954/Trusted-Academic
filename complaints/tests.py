from django.test import TestCase
from django.urls import reverse

from bookings.models import Booking
from complaints.models import Complaint
from complaints.services import user_can_create_complaint, user_can_view_complaint
from core.test_helpers import create_parent, create_student, create_test_booking


class ComplaintAccessTests(TestCase):
    def test_complaint_create_is_limited_to_booking_participants(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        unrelated_student = create_student(email='unrelated-student@example.com')

        self.assertTrue(user_can_create_complaint(booking.student, booking))
        self.assertTrue(user_can_create_complaint(booking.teacher.user, booking))
        self.assertFalse(user_can_create_complaint(unrelated_student, booking))

    def test_complaint_detail_hides_from_unrelated_users(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        complaint = Complaint.objects.create(
            booking=booking,
            created_by=booking.student,
            against_user=booking.teacher.user,
            category=Complaint.Category.QUALITY,
            description='Issue with lesson quality.',
        )
        unrelated_student = create_student(email='complaint-outsider@example.com')

        self.assertTrue(user_can_view_complaint(booking.student, complaint))
        self.assertTrue(user_can_view_complaint(booking.teacher.user, complaint))
        self.assertFalse(user_can_view_complaint(unrelated_student, complaint))

        self.client.force_login(unrelated_student)
        response = self.client.get(reverse('complaints:detail', args=[complaint.pk]))
        self.assertEqual(response.status_code, 404)

    def test_linked_parent_can_create_but_cannot_view_complaint_between_student_and_teacher(self):
        student = create_student(email='complaint-student@example.com')
        parent = create_parent(email='complaint-parent@example.com', student=student)
        booking = create_test_booking(student=student, status=Booking.BookingStatus.CONFIRMED)
        complaint = Complaint.objects.create(
            booking=booking,
            created_by=booking.student,
            against_user=booking.teacher.user,
            category=Complaint.Category.QUALITY,
            description='Issue with lesson quality.',
        )

        self.assertTrue(user_can_create_complaint(parent, booking))
        self.assertFalse(user_can_view_complaint(parent, complaint))
