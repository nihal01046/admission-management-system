from django.db import models
from django.conf import settings
from admissions.models import AdmissionApplication
from courses.models import Course
import random
import string

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    enrollment_id = models.CharField(max_length=30, unique=True, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    application = models.OneToOneField(AdmissionApplication, on_delete=models.CASCADE, related_name='enrollment')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='enrollments')
    academic_year = models.CharField(max_length=30, default='2025-2026')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    roll_number = models.CharField(max_length=40, blank=True)
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.enrollment_id:
            # Generate clean ID e.g., ENR202500123
            digits = ''.join(random.choices(string.digits, k=5))
            self.enrollment_id = f"ENR2025{digits}"
            while Enrollment.objects.filter(enrollment_id=self.enrollment_id).exists():
                digits = ''.join(random.choices(string.digits, k=5))
                self.enrollment_id = f"ENR2025{digits}"
        if not self.roll_number:
            code = self.course.course_code.replace(" ", "")
            seq = Enrollment.objects.filter(course=self.course).count() + 1
            self.roll_number = f"{code}-2025-{seq:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment_id} - {self.student.full_name} ({self.course.course_code})"
