from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from students.models import StudentProfile

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='test_student',
            email='teststudent@gmail.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student)

        self.admin = User.objects.create_superuser(
            username='test_admin',
            email='admin@college.edu',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )

    def test_student_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'New Student',
            'email': 'newstudent@example.com',
            'phone_number': '9876543210',
            'password': 'secretpassword',
            'confirm_password': 'secretpassword',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newstudent@example.com').exists())
        new_user = User.objects.get(email='newstudent@example.com')
        self.assertEqual(new_user.role, 'STUDENT')
        self.assertTrue(hasattr(new_user, 'student_profile'))

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Mismatch Student',
            'email': 'mismatch@example.com',
            'phone_number': '9876543210',
            'password': 'password1',
            'confirm_password': 'password2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='mismatch@example.com').exists())

    def test_user_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'teststudent@gmail.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:dashboard_redirect'), target_status_code=302)

    def test_user_login_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'teststudent@gmail.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_role_permissions_student_cannot_access_admin_dashboard(self):
        self.client.login(username='test_student', password='password123')
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirected to student dashboard or blocked

    def test_role_permissions_admin_can_access_admin_dashboard(self):
        self.client.login(username='test_admin', password='adminpassword')
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
