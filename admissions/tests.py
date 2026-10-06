from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course
from students.models import StudentProfile
from admissions.models import AdmissionApplication, ApplicationTimeline
import datetime

User = get_user_model()

class AdmissionApplicationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='app_student',
            email='appstudent@college.edu',
            password='password123',
            first_name='Alex',
            last_name='Morgan',
            role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student)

        self.admin = User.objects.create_superuser(
            username='app_admin',
            email='appadmin@college.edu',
            password='adminpassword',
            role='ADMIN'
        )

        self.course = Course.objects.create(
            course_name='B.Sc Computer Science',
            course_code='BSC-CS-APP',
            department='Computer Science',
            total_seats=50,
            available_seats=50,
            status='Active'
        )

    def test_application_creation_and_submission(self):
        self.client.force_login(self.student)
        
        # Step 1: Personal Details
        resp1 = self.client.post(reverse('admissions:apply') + '?step=1', {
            'full_name': 'Alex Morgan',
            'email': 'appstudent@college.edu',
            'phone_number': '9871112233',
            'date_of_birth': '2005-08-12',
            'gender': 'Male',
            'address': '22 Baker St',
            'father_name': 'Robert Morgan',
            'mother_name': 'Clara Morgan',
            'guardian_contact': '9871112244',
        })
        self.assertEqual(resp1.status_code, 302)

        # Check draft exists
        app = AdmissionApplication.objects.filter(student=self.student).first()
        self.assertIsNotNone(app)
        self.assertEqual(app.status, 'Draft')

        # Step 3: Select Course
        resp3 = self.client.post(reverse('admissions:apply') + '?step=3', {
            'course': self.course.id
        })
        self.assertEqual(resp3.status_code, 302)

        # Step 5: Final Submission
        resp5 = self.client.post(reverse('admissions:apply') + '?step=5', {
            'action': 'submit'
        })
        self.assertEqual(resp5.status_code, 302)

        app.refresh_from_db()
        self.assertEqual(app.status, 'Submitted')
        self.assertTrue(app.application_id.startswith('CAE2025'))
        self.assertTrue(ApplicationTimeline.objects.filter(application=app, status='Submitted').exists())

    def test_admin_application_approval(self):
        app = AdmissionApplication.objects.create(
            student=self.student,
            course=self.course,
            status='Submitted',
            full_name='Alex Morgan',
            email='appstudent@college.edu',
            phone_number='9871112233',
        )
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('admissions:admin_detail', args=[app.application_id]), {
            'action': 'approve',
            'admin_remarks': 'Candidate eligible for seat offer.'
        })
        self.assertEqual(resp.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Approved')
        self.assertEqual(app.reviewed_by, self.admin)

    def test_admin_application_rejection_requires_reason(self):
        app = AdmissionApplication.objects.create(
            student=self.student,
            course=self.course,
            status='Submitted',
            full_name='Alex Morgan',
            email='appstudent@college.edu',
            phone_number='9871112233',
        )
        self.client.force_login(self.admin)
        # Without reason
        resp = self.client.post(reverse('admissions:admin_detail', args=[app.application_id]), {
            'action': 'reject',
            'rejection_reason': ''
        })
        app.refresh_from_db()
        self.assertNotEqual(app.status, 'Rejected') # Blocked because reason is missing

        # With reason
        resp2 = self.client.post(reverse('admissions:admin_detail', args=[app.application_id]), {
            'action': 'reject',
            'rejection_reason': 'Marks below program cutoff threshold.'
        })
        app.refresh_from_db()
        self.assertEqual(app.status, 'Rejected')
        self.assertEqual(app.rejection_reason, 'Marks below program cutoff threshold.')
