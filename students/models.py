from django.db import models
from django.conf import settings
import uuid

class StudentProfile(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=30, unique=True, blank=True)
    
    # Personal Info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    
    # Parent / Guardian Info
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)
    
    # Academic Info
    previous_institution = models.CharField(max_length=255, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    board_university = models.CharField(max_length=150, blank=True)
    passing_year = models.PositiveIntegerField(null=True, blank=True)
    percentage_cgpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate clean student ID e.g., STU20250001
            count = StudentProfile.objects.count() + 1
            self.student_id = f"STU2025{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name} ({self.student_id})"
