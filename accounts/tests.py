from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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
