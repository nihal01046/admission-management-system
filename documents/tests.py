from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document
from students.models import StudentProfile

User = get_user_model()

class DocumentManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='doc_student',
            email='docstudent@college.edu',
            password='password123',
            role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student)

        self.admin = User.objects.create_superuser(
            username='doc_admin',
            email='docadmin@college.edu',
            password='adminpassword',
            role='ADMIN'
        )

        test_file = SimpleUploadedFile("marksheet.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        self.document = Document.objects.create(
            student=self.student,
            document_type='ACADEMIC_12',
            file=test_file,
            file_name='marksheet.pdf',
            status='Pending'
        )

    def test_admin_verify_document(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('documents:verify', args=[self.document.id]), {
            'action': 'verify'
        })
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'Verified')
        self.assertEqual(self.document.verified_by, self.admin)

    def test_admin_reject_document_with_reason(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('documents:verify', args=[self.document.id]), {
            'action': 'reject',
            'rejection_reason': 'File is blurry and unreadable.'
        })
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'Rejected')
        self.assertEqual(self.document.rejection_reason, 'File is blurry and unreadable.')

    def test_student_cannot_delete_verified_document(self):
        self.document.status = 'Verified'
        self.document.save()

        self.client.force_login(self.student)
        response = self.client.get(reverse('documents:delete', args=[self.document.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(id=self.document.id).exists())
