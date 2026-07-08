from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_offering, create_teacher, create_user
from teachers.models import TeacherProfile


class TeacherDiscoveryTests(TestCase):
    def test_only_approved_teachers_are_publicly_discoverable(self):
        approved_teacher = create_teacher(email='approved@example.com', approved=True, full_name='Approved Teacher')
        pending_teacher = create_teacher(email='pending@example.com', approved=False, full_name='Pending Teacher')
        create_offering(teacher=approved_teacher)
        create_offering(teacher=pending_teacher)

        response = self.client.get(reverse('teachers:public_list'))

        self.assertContains(response, approved_teacher.user.get_full_name())
        self.assertNotContains(response, pending_teacher.user.get_full_name())

    def test_pending_teacher_detail_is_not_public(self):
        pending_teacher = create_teacher(email='pending-detail@example.com', approved=False)

        response = self.client.get(reverse('teachers:public_detail', args=[pending_teacher.pk]))

        self.assertEqual(response.status_code, 404)


class TeacherOnboardingTests(TestCase):
    def test_new_teacher_starts_pending_and_is_hidden_until_admin_approval(self):
        teacher = create_teacher(email='onboarding@example.com', approved=False, full_name='Onboarding Teacher')
        create_offering(teacher=teacher)

        self.assertEqual(teacher.approval_status, TeacherProfile.ApprovalStatus.PENDING)
        self.assertFalse(teacher.can_receive_bookings)

        list_response = self.client.get(reverse('teachers:public_list'))
        self.assertNotContains(list_response, teacher.user.get_full_name())

        admin = create_user('onboarding-admin@example.com', role='admin', full_name='Admin', is_staff=True)
        self.client.force_login(admin)
        self.client.post(
            reverse('adminpanel:review_teacher', args=[teacher.pk]),
            {'action': 'approve', 'verification_notes': 'Documents verified'},
        )

        teacher.refresh_from_db()
        self.assertEqual(teacher.approval_status, TeacherProfile.ApprovalStatus.APPROVED)
        self.assertTrue(teacher.can_receive_bookings)

        approved_response = self.client.get(reverse('teachers:public_list'))
        self.assertContains(approved_response, teacher.user.get_full_name())

    def test_non_staff_user_cannot_approve_teacher(self):
        teacher = create_teacher(email='protect@example.com', approved=False)
        create_offering(teacher=teacher)

        student = create_user('student-protect@example.com', role='student')
        self.client.force_login(student)
        response = self.client.post(
            reverse('adminpanel:review_teacher', args=[teacher.pk]),
            {'action': 'approve'},
        )

        self.assertEqual(response.status_code, 302)
        teacher.refresh_from_db()
        self.assertEqual(teacher.approval_status, TeacherProfile.ApprovalStatus.PENDING)
