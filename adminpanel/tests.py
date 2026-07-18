from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_student, create_teacher, create_user
from teachers.models import TeacherProfile


class AdminPanelAccessTests(TestCase):
    def test_dashboard_requires_staff(self):
        student = create_student(email='panel-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('adminpanel:dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_staff_can_view_dashboard(self):
        staff = create_user('panel-staff@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.get(reverse('adminpanel:dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_staff_can_view_user_list(self):
        staff = create_user('panel-users@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.get(reverse('adminpanel:user_list'))

        self.assertEqual(response.status_code, 200)

    def test_staff_can_view_booking_monitor(self):
        staff = create_user('panel-book@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.get(reverse('adminpanel:booking_monitor'))

        self.assertEqual(response.status_code, 200)


class TeacherReviewTests(TestCase):
    def test_pending_teachers_list_shows_pending_only(self):
        create_teacher(email='pending-1@example.com', approved=False)
        staff = create_user('review-staff@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.get(reverse('adminpanel:pending_teachers'))

        self.assertEqual(response.status_code, 200)

    def test_staff_approves_teacher(self):
        teacher = create_teacher(email='to-approve@example.com', approved=False)
        staff = create_user('approve-staff@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.post(
            reverse('adminpanel:review_teacher', args=[teacher.pk]),
            {'action': 'approve', 'verification_notes': 'Credentials verified.'},
        )

        self.assertEqual(response.status_code, 302)
        teacher.refresh_from_db()
        self.assertEqual(teacher.approval_status, TeacherProfile.ApprovalStatus.APPROVED)

    def test_staff_rejects_teacher(self):
        teacher = create_teacher(email='to-reject@example.com', approved=False)
        staff = create_user('reject-staff2@example.com', role='admin', is_staff=True, full_name='Staff')
        self.client.force_login(staff)

        response = self.client.post(
            reverse('adminpanel:review_teacher', args=[teacher.pk]),
            {'action': 'reject', 'verification_notes': 'Insufficient documentation.'},
        )

        self.assertEqual(response.status_code, 302)
        teacher.refresh_from_db()
        self.assertEqual(teacher.approval_status, TeacherProfile.ApprovalStatus.REJECTED)

    def test_non_staff_cannot_review_teacher(self):
        teacher = create_teacher(email='review-blocked@example.com', approved=False)
        student = create_student(email='review-blocked-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('adminpanel:review_teacher', args=[teacher.pk]))

        self.assertEqual(response.status_code, 302)
