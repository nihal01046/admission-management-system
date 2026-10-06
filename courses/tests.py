from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_tester',
            email='admin_course@college.edu',
            password='adminpassword',
            role='ADMIN'
        )
        self.student = User.objects.create_user(
            username='student_tester',
            email='student_course@college.edu',
            password='password123',
            role='STUDENT'
        )
        self.course = Course.objects.create(
            course_name='Bachelor of Computer Applications',
            course_code='BCA-TEST',
            department='Computer Applications',
            duration='3 Years',
            total_seats=60,
            available_seats=60,
            fees=45000.00,
            status='Active'
        )

    def test_course_creation_admin(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('courses:create'), {
            'course_name': 'Data Science Honors',
            'course_code': 'BS-DS',
            'department': 'Computer Science',
            'duration': '4 Years',
            'total_seats': 40,
            'available_seats': 40,
            'fees': 60000.00,
            'eligibility': '10+2 with Math 60%',
            'description': 'Advanced Data Science degree',
            'status': 'Active'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(course_code='BS-DS').exists())

    def test_course_creation_student_forbidden(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse('courses:create'), {
            'course_name': 'Unauthorized Course',
            'course_code': 'UNAUTH',
            'department': 'Arts',
            'total_seats': 30,
            'available_seats': 30,
            'fees': 20000,
            'status': 'Active'
        })
        self.assertEqual(response.status_code, 302) # Access denied redirect
        self.assertFalse(Course.objects.filter(course_code='UNAUTH').exists())

    def test_course_update(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('courses:edit', args=[self.course.id]), {
            'course_name': 'BCA Advanced',
            'course_code': 'BCA-TEST',
            'department': 'Computer Applications',
            'duration': '3 Years',
            'total_seats': 65,
            'available_seats': 65,
            'fees': 48000.00,
            'eligibility': '10+2 with Math',
            'status': 'Active'
        })
        self.assertEqual(response.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.course_name, 'BCA Advanced')
        self.assertEqual(self.course.total_seats, 65)

    def test_course_toggle_status(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('courses:delete', args=[self.course.id]), {
            'action': 'toggle'
        })
        self.assertEqual(response.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.status, 'Inactive')
