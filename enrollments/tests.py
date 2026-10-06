from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course
from students.models import StudentProfile
from admissions.models import AdmissionApplication
from enrollments.models import Enrollment

User = get_user_model()

class EnrollmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='enr_student',
            email='enrstudent@college.edu',
            password='password123',
            first_name='Clara',
            last_name='Oswald',
            role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student)

        self.course = Course.objects.create(
            course_name='Bachelor of Commerce',
            course_code='BCOM-ENR',
            department='Commerce',
            total_seats=2,
            available_seats=2,
            status='Active'
        )

        self.approved_app = AdmissionApplication.objects.create(
            student=self.student,
            course=self.course,
            status='Approved',
            full_name='Clara Oswald',
            email='enrstudent@college.edu',
            phone_number='9876543211',
        )

        self.pending_app = AdmissionApplication.objects.create(
            student=self.student,
            course=self.course,
            status='Submitted',
            full_name='Clara Oswald',
            email='enrstudent@college.edu',
            phone_number='9876543211',
        )

    def test_enrollment_success_and_seat_reduction(self):
        self.client.force_login(self.student)
        
        initial_seats = self.course.available_seats
        response = self.client.post(reverse('enrollments:enroll_student', args=[self.approved_app.application_id]))
        self.assertEqual(response.status_code, 302)

        # Check Enrollment record created
        self.assertTrue(Enrollment.objects.filter(application=self.approved_app).exists())
        enrollment = Enrollment.objects.get(application=self.approved_app)
        self.assertEqual(enrollment.status, 'Confirmed')
        self.assertTrue(enrollment.roll_number.startswith('BCOM-ENR'))

        # Check seats reduced
        self.course.refresh_from_db()
        self.assertEqual(self.course.available_seats, initial_seats - 1)

        # Check application status updated to Enrolled
        self.approved_app.refresh_from_db()
        self.assertEqual(self.approved_app.status, 'Enrolled')

    def test_enrollment_rejected_if_not_approved(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse('enrollments:enroll_student', args=[self.pending_app.application_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Enrollment.objects.filter(application=self.pending_app).exists())

    def test_duplicate_enrollment_prevention(self):
        self.client.force_login(self.student)
        
        # First enrollment
        self.client.post(reverse('enrollments:enroll_student', args=[self.approved_app.application_id]))
        self.assertEqual(Enrollment.objects.filter(student=self.student).count(), 1)

        # Attempt to enroll again for another approved application in same course
        second_app = AdmissionApplication.objects.create(
            student=self.student,
            course=self.course,
            status='Approved',
            full_name='Clara Oswald',
            email='enrstudent@college.edu',
            phone_number='9876543211',
        )
        resp2 = self.client.post(reverse('enrollments:enroll_student', args=[second_app.application_id]))
        self.assertEqual(resp2.status_code, 302)
        # Count should remain 1
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)
