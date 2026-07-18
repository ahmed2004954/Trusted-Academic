from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.test_helpers import create_user

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.password = 'StrongPass123!'

    def test_student_registration_and_login(self):
        # 1. Register a student
        response = self.client.post(self.register_url, {
            'full_name': 'Student Name',
            'email': 'student@example.com',
            'phone': '01012345678',
            'role': User.Role.STUDENT,
            'password1': self.password,
            'password2': self.password,
        })
        # Check redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Logout
        self.client.logout()

        # 2. Login as student
        response = self.client.post(self.login_url, {
            'username': 'student@example.com',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        # Verify the user is authenticated in the session
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_teacher_registration_and_login(self):
        # 1. Register a teacher
        response = self.client.post(self.register_url, {
            'full_name': 'Teacher Name',
            'email': 'teacher@example.com',
            'phone': '01012345679',
            'role': User.Role.TEACHER,
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 302)
        
        # Logout
        self.client.logout()

        # 2. Login as teacher
        response = self.client.post(self.login_url, {
            'username': 'teacher@example.com',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_parent_registration_and_login(self):
        # 1. Register a parent
        response = self.client.post(self.register_url, {
            'full_name': 'Parent Name',
            'email': 'parent@example.com',
            'phone': '01012345680',
            'role': User.Role.PARENT,
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 302)
        
        # Logout
        self.client.logout()

        # 2. Login as parent
        response = self.client.post(self.login_url, {
            'username': 'parent@example.com',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_email_case_insensitive_login(self):
        # Register a user
        User.objects.create_user(
            email='CaseSensitive@example.com',
            full_name='Test User',
            password=self.password,
            role=User.Role.STUDENT,
        )

        # Login with lowercase email
        response = self.client.post(self.login_url, {
            'username': 'casesensitive@example.com',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_wrong_password_login_fails(self):
        User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password=self.password,
            role=User.Role.STUDENT,
        )

        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword',
        })
        # If login fails, it returns 200 and re-renders the login page
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(self.register_url, {
            'full_name': 'Mismatch User',
            'email': 'mismatch@example.com',
            'phone': '01012349999',
            'role': User.Role.STUDENT,
            'password1': self.password,
            'password2': 'DifferentPass123!',
        })
        # Form re-renders with errors, no user created, no session started.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='mismatch@example.com').exists())
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            email='dupe@example.com',
            full_name='Existing User',
            password=self.password,
            role=User.Role.STUDENT,
        )
        response = self.client.post(self.register_url, {
            'full_name': 'Second User',
            'email': 'dupe@example.com',
            'phone': '01012340000',
            'role': User.Role.STUDENT,
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='dupe@example.com').count(), 1)

    def test_registration_via_url_cannot_create_admin_role(self):
        response = self.client.post(
            reverse('accounts:register_with_role', args=['admin']),
            {
                'full_name': 'Sneaky Admin',
                'email': 'sneaky@example.com',
                'phone': '01012341111',
                'role': User.Role.ADMIN,
                'password1': self.password,
                'password2': self.password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='sneaky@example.com').exists())


class LogoutTests(TestCase):
    def test_logout_clears_session_and_redirects_home(self):
        user = create_user('logout@example.com', role='student')
        self.client.force_login(user)
        self.assertIn('_auth_user_id', self.client.session)

        # Django 5's LogoutView only accepts POST (GET returns 405).
        response = self.client.post(reverse('accounts:logout'))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.profile_url = reverse('accounts:profile')

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_authenticated_student_can_view_profile(self):
        user = create_user('profile-student@example.com', role='student')
        self.client.force_login(user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)

    def test_profile_post_updates_user_fields(self):
        user = create_user('profile-edit@example.com', role='teacher', full_name='Old Name')
        self.client.force_login(user)

        response = self.client.post(self.profile_url, {
            'full_name': 'New Name',
            'phone': '01055556666',
        })

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.full_name, 'New Name')
        self.assertEqual(user.phone, '01055556666')
