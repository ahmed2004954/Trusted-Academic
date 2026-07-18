from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_offering, create_teacher, create_user
from teachers.models import TeacherCertificate, TeacherProfile


class TeacherProfileSetupTests(TestCase):
    def test_teacher_can_setup_profile(self):
        teacher_user = create_user('setup@example.com', role='teacher')
        self.client.force_login(teacher_user)

        response = self.client.post(reverse('teachers:setup_profile'), {
            'headline': 'Physics tutor',
            'bio': 'Ten years of experience teaching physics.',
            'experience_years': 10,
            'intro_video_url': '',
            'booking_mode': 'automatic',
        })

        self.assertEqual(response.status_code, 302)
        profile = TeacherProfile.objects.get(user=teacher_user)
        self.assertEqual(profile.headline, 'Physics tutor')
        self.assertEqual(profile.experience_years, 10)

    def test_setup_profile_rejects_excessive_experience(self):
        teacher_user = create_user('setup-bad@example.com', role='teacher')
        self.client.force_login(teacher_user)

        response = self.client.post(reverse('teachers:setup_profile'), {
            'headline': 'Overqualified',
            'bio': 'Impossible experience.',
            'experience_years': 120,
            'booking_mode': 'automatic',
        })

        self.assertEqual(response.status_code, 200)
        profile = TeacherProfile.objects.get(user=teacher_user)
        self.assertNotEqual(profile.experience_years, 120)

    def test_setup_profile_requires_teacher_role(self):
        student = create_user('setup-student@example.com', role='student')
        self.client.force_login(student)

        response = self.client.get(reverse('teachers:setup_profile'))

        self.assertEqual(response.status_code, 403)


class TeacherCertificateTests(TestCase):
    def test_teacher_can_upload_certificate(self):
        teacher_user = create_user('cert@example.com', role='teacher')
        self.client.force_login(teacher_user)
        upload = SimpleUploadedFile('cert.pdf', b'%PDF-1.4 fake', content_type='application/pdf')

        response = self.client.post(reverse('teachers:upload_certificate'), {
            'title': 'BSc Mathematics',
            'issuing_organization': 'Cairo University',
            'file': upload,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TeacherCertificate.objects.filter(
                teacher_profile__user=teacher_user, title='BSc Mathematics'
            ).exists()
        )

    def test_certificate_upload_requires_teacher_role(self):
        student = create_user('cert-student@example.com', role='student')
        self.client.force_login(student)

        response = self.client.get(reverse('teachers:upload_certificate'))

        self.assertEqual(response.status_code, 403)


class TeacherStatusTests(TestCase):
    def test_pending_teacher_sees_status_page(self):
        teacher = create_teacher(email='status@example.com', approved=False)
        self.client.force_login(teacher.user)

        response = self.client.get(reverse('teachers:my_status'))

        self.assertEqual(response.status_code, 200)

    def test_teacher_dashboard_accessible(self):
        teacher = create_teacher(email='dash@example.com')
        self.client.force_login(teacher.user)

        response = self.client.get(reverse('teachers:dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_status_requires_login(self):
        response = self.client.get(reverse('teachers:my_status'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


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
