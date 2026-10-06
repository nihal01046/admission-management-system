from django.db import models
from django.conf import settings
from courses.models import Course
import random
import string

class AdmissionApplication(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Document Verification', 'Document Verification'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Enrolled', 'Enrolled'),
    )

    application_id = models.CharField(max_length=30, unique=True, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='applications')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Draft')
    current_step = models.PositiveIntegerField(default=1)

    # Personal Snapshot
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Parent / Guardian Snapshot
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)

    # Academic Snapshot
    previous_institution = models.CharField(max_length=255, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    board_university = models.CharField(max_length=150, blank=True)
    passing_year = models.PositiveIntegerField(null=True, blank=True)
    percentage_cgpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Admin Review Notes
    rejection_reason = models.TextField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.application_id:
            # Generate e.g. CAE202500123
            random_digits = ''.join(random.choices(string.digits, k=5))
            self.application_id = f"CAE2025{random_digits}"
            while AdmissionApplication.objects.filter(application_id=self.application_id).exists():
                random_digits = ''.join(random.choices(string.digits, k=5))
                self.application_id = f"CAE2025{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_id} - {self.full_name} ({self.course.course_code})"

    @property
    def can_enroll(self):
        return self.status == 'Approved' and not hasattr(self, 'enrollment') and self.course.has_available_seats

    @property
    def is_enrolled(self):
        return hasattr(self, 'enrollment') or self.status == 'Enrolled'

    @property
    def status_badge_class(self):
        mapping = {
            'Draft': 'badge-secondary',
            'Submitted': 'badge-info',
            'Under Review': 'badge-primary',
            'Document Verification': 'badge-warning',
            'Approved': 'badge-success',
            'Rejected': 'badge-danger',
            'Enrolled': 'badge-purple',
        }
        return mapping.get(self.status, 'badge-secondary')


class ApplicationTimeline(models.Model):
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=40)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.application.application_id} - {self.title}"
