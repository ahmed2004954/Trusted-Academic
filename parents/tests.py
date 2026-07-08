from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_parent, create_student, create_test_booking


class ParentPrivacyTests(TestCase):
    def test_linked_parent_can_view_student_booking_history(self):
        student = create_student()
        parent = create_parent(student=student)
        booking = create_test_booking(student=student)

        self.client.force_login(parent)
        response = self.client.get(reverse('parents:student_booking_history', args=[student.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, booking.teacher.user.get_full_name())

    def test_unrelated_parent_cannot_view_student_booking_history(self):
        student = create_student()
        create_parent(email='linked-parent@example.com', student=student)
        unrelated_parent = create_parent(email='unrelated-parent@example.com')
        create_test_booking(student=student)

        self.client.force_login(unrelated_parent)
        response = self.client.get(reverse('parents:student_booking_history', args=[student.pk]))

        self.assertEqual(response.status_code, 404)
