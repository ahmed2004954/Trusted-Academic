from django.test import TestCase
from django.urls import reverse

from bookings.models import Booking
from complaints.models import Complaint
from complaints.services import user_can_create_complaint, user_can_view_complaint
from core.test_helpers import create_parent, create_student, create_test_booking, create_user


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


class ComplaintCreateViewTests(TestCase):
    def test_student_submits_complaint_against_teacher(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('complaints:create', args=[booking.pk]),
            {
                'against_user': booking.teacher.user_id,
                'category': Complaint.Category.QUALITY,
                'description': 'The lesson quality was poor and off-topic.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Complaint.objects.filter(booking=booking, created_by=booking.student).exists()
        )

    def test_unrelated_user_cannot_open_create_page(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        intruder = create_student(email='complaint-create-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('complaints:create', args=[booking.pk]))

        self.assertEqual(response.status_code, 403)


class ComplaintStaffQueueTests(TestCase):
    def test_staff_can_view_queue(self):
        staff = create_user('complaint-staff@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.get(reverse('complaints:staff_queue'))

        self.assertEqual(response.status_code, 200)

    def test_non_staff_redirected_from_queue(self):
        student = create_student(email='queue-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('complaints:staff_queue'))

        self.assertEqual(response.status_code, 302)

    def test_staff_resolves_complaint(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        complaint = Complaint.objects.create(
            booking=booking,
            created_by=booking.student,
            against_user=booking.teacher.user,
            category=Complaint.Category.QUALITY,
            description='Issue with lesson quality.',
        )
        staff = create_user('resolve-staff@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.post(
            reverse('complaints:staff_detail', args=[complaint.pk]),
            {'status': Complaint.Status.RESOLVED, 'resolution_notes': 'Refunded the student.'},
        )

        self.assertEqual(response.status_code, 302)
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, Complaint.Status.RESOLVED)
        self.assertEqual(complaint.resolved_by, staff)
