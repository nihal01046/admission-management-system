from django.db import models
from django.conf import settings
from admissions.models import AdmissionApplication
import os

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('ID_PROOF', 'Identity Proof (Aadhaar / Passport)'),
        ('PHOTO', 'Passport Size Photo'),
        ('ACADEMIC_10', '10th Standard Marksheet'),
        ('ACADEMIC_12', '12th / Qualifying Marksheet'),
        ('TRANSFER_CERT', 'Transfer / Migration Certificate'),
        ('OTHER', 'Other Supporting Document'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    application = models.ForeignKey(
        AdmissionApplication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=150, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            try:
                size_bytes = self.file.size
                if size_bytes < 1024:
                    self.file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    self.file_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    self.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            except Exception:
                self.file_size = "Unknown"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.student.full_name} ({self.status})"

    @property
    def is_image(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']

    @property
    def is_pdf(self):
        return self.file.name.lower().endswith('.pdf')
