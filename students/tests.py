from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_student, create_teacher
from students.models import StudentProfile


class StudentDashboardTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('students:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_student_can_view_dashboard(self):
        student = create_student()
        self.client.force_login(student)

        response = self.client.get(reverse('students:dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_non_student_cannot_view_dashboard(self):
        teacher = create_teacher(email='dash-teacher@example.com').user
        self.client.force_login(teacher)

        response = self.client.get(reverse('students:dashboard'))

        self.assertEqual(response.status_code, 403)


class StudentLinkingCodeTests(TestCase):
    def test_linking_code_page_generates_code(self):
        student = create_student(email='code-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('students:linking_code'))

        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(user=student)
        self.assertTrue(profile.linking_code)

    def test_post_regenerates_linking_code(self):
        student = create_student(email='regen-student@example.com')
        profile, _ = StudentProfile.objects.get_or_create(user=student)
        original = profile.generate_linking_code()
        self.client.force_login(student)

        response = self.client.post(reverse('students:linking_code'))

        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertTrue(profile.linking_code)
        self.assertNotEqual(profile.linking_code, original)

    def test_linking_code_requires_student_role(self):
        teacher = create_teacher(email='code-teacher@example.com').user
        self.client.force_login(teacher)

        response = self.client.get(reverse('students:linking_code'))

        self.assertEqual(response.status_code, 403)
