from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.test_helpers import (
    create_parent,
    create_student,
    create_teacher,
    create_test_booking,
    create_user,
)
from parents.models import ParentProfile, ParentStudentLink
from students.models import StudentProfile

User = get_user_model()


class ParentCreateStudentTests(TestCase):
    def test_parent_creates_managed_child_account_and_link(self):
        parent = create_parent(email='pcreate@example.com')
        self.client.force_login(parent)

        response = self.client.post(reverse('parents:create_student'), {
            'full_name': 'Child One',
            'email': 'child-one@example.com',
        })

        self.assertEqual(response.status_code, 302)
        child = User.objects.get(email='child-one@example.com')
        self.assertEqual(child.role, User.Role.STUDENT)
        self.assertTrue(
            ParentStudentLink.objects.filter(parent__user=parent, student=child).exists()
        )

    def test_non_parent_cannot_create_student(self):
        teacher = create_teacher(email='tcreate@example.com').user
        self.client.force_login(teacher)

        response = self.client.post(reverse('parents:create_student'), {'full_name': 'Nope'})

        self.assertEqual(response.status_code, 403)


class ParentLinkStudentTests(TestCase):
    def test_parent_links_existing_student_via_code(self):
        student = create_student(email='linkme@example.com')
        profile, _ = StudentProfile.objects.get_or_create(user=student)
        code = profile.generate_linking_code()
        parent = create_parent(email='plink@example.com')
        self.client.force_login(parent)

        response = self.client.post(reverse('parents:link_student'), {'linking_code': code})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ParentStudentLink.objects.filter(parent__user=parent, student=student).exists()
        )

    def test_invalid_linking_code_creates_no_link(self):
        parent = create_parent(email='plink-bad@example.com')
        self.client.force_login(parent)

        response = self.client.post(reverse('parents:link_student'), {'linking_code': 'BADCODE1'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            ParentStudentLink.objects.filter(parent__user=parent).exists()
        )

    def test_parent_dashboard_requires_parent_role(self):
        student = create_student(email='dash-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('parents:dashboard'))

        self.assertEqual(response.status_code, 403)


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
