from django.db import models
from django.core.validators import MinValueValidator

class Course(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    course_name = models.CharField(max_length=150)
    course_code = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, default='3 Years')
    total_seats = models.PositiveIntegerField(default=60, validators=[MinValueValidator(1)])
    available_seats = models.PositiveIntegerField(default=60)
    eligibility = models.TextField(default='10+2 Higher Secondary Examination passed with minimum 50% aggregate marks.')
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=45000.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course_name']

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

    @property
    def has_available_seats(self):
        return self.available_seats > 0 and self.status == 'Active'

    @property
    def filled_seats(self):
        return max(0, self.total_seats - self.available_seats)

    @property
    def occupancy_rate(self):
        if self.total_seats == 0:
            return 0
        return round((self.filled_seats / self.total_seats) * 100, 1)

    def reduce_seat(self):
        if self.available_seats > 0:
            self.available_seats -= 1
            self.save(update_fields=['available_seats', 'updated_at'])
            return True
        return False

    def restore_seat(self):
        if self.available_seats < self.total_seats:
            self.available_seats += 1
            self.save(update_fields=['available_seats', 'updated_at'])
            return True
        return False
