from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from accounts.decorators import student_required, admin_required
from .models import Enrollment
from admissions.models import AdmissionApplication, ApplicationTimeline
from courses.models import Course
from notifications.services import send_notification
from django.template.loader import render_to_string
import datetime

@student_required
def enroll_student(request, application_id):
    """
    Handles the official enrollment action for an approved application.
    Enforces seat capacity, prevents duplicate enrollment, and automatically
    reduces course available seats.
    """
    application = get_object_or_404(
        AdmissionApplication.objects.select_related('course', 'student'),
        application_id=application_id,
        student=request.user
    )

    # Validation Checks
    if application.status != 'Approved':
        messages.error(request, "Enrollment is only allowed for Approved applications.")
        return redirect('admissions:application_detail', application_id=application.application_id)

    if hasattr(application, 'enrollment'):
        return redirect('enrollments:confirmation', application_id=application.application_id)

    course = application.course
    if not course.has_available_seats:
        messages.error(request, f"Sorry, no seats are currently available in {course.course_name}.")
        return redirect('admissions:application_detail', application_id=application.application_id)

    # Check if student is already enrolled in this course through another application
    if Enrollment.objects.filter(student=request.user, course=course, status='Confirmed').exists():
        messages.warning(request, f"You are already actively enrolled in {course.course_name}.")
        return redirect('enrollments:my_enrollments')

    if request.method == 'POST':
        # Create Enrollment record
        enrollment = Enrollment.objects.create(
            student=request.user,
            application=application,
            course=course,
            academic_year='2025-2026',
            status='Confirmed',
            remarks='Online enrollment self-confirmed by student.'
        )

        # Decrement available seats
        course.reduce_seat()

        # Update application status
        application.status = 'Enrolled'
        application.save(update_fields=['status', 'updated_at'])

        # Update Timeline
        ApplicationTimeline.objects.create(
            application=application,
            status='Enrolled',
            title='Enrollment Confirmed',
            description=f'Student confirmed admission enrollment. Roll number allocated: {enrollment.roll_number}',
            performed_by=request.user
        )

        # Notify Student
        send_notification(
            recipient=request.user,
            title='Enrollment Successful!',
            message=f'Your enrollment in {course.course_name} is confirmed. Roll No: {enrollment.roll_number}',
            link=f'/enrollments/confirmation/{application.application_id}/',
            notification_type='SUCCESS'
        )

        messages.success(request, f"Enrollment confirmed! Welcome to {course.course_name}.")
        return redirect('enrollments:confirmation', application_id=application.application_id)

    return render(request, 'enrollments/enroll_confirm_prompt.html', {
        'application': application,
        'course': course,
    })


@student_required
def enrollment_confirmation(request, application_id):
    """
    Enrollment Confirmation Page matching Image 1 #8 EXACTLY
    """
    application = get_object_or_404(
        AdmissionApplication.objects.select_related('course', 'student', 'enrollment'),
        application_id=application_id,
        student=request.user
    )

    if not hasattr(application, 'enrollment'):
        messages.warning(request, "Enrollment has not been completed for this application yet.")
        return redirect('admissions:application_detail', application_id=application.application_id)

    enrollment = application.enrollment

    return render(request, 'enrollments/confirmation.html', {
        'application': application,
        'enrollment': enrollment,
        'course': application.course,
    })


@student_required
def my_enrollments(request):
    """Student: View list of current enrollments"""
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'application')
    return render(request, 'enrollments/my_enrollments.html', {'enrollments': enrollments})


@login_required
def download_enrollment_letter(request, application_id):
    """
    Generates a formal, printable / downloadable Admission & Enrollment Letter
    with College Letterhead, seal, details, and signatures.
    """
    if request.user.is_admin_user:
        application = get_object_or_404(AdmissionApplication.objects.select_related('course', 'student', 'enrollment'), application_id=application_id)
    else:
        application = get_object_or_404(AdmissionApplication.objects.select_related('course', 'student', 'enrollment'), application_id=application_id, student=request.user)

    if not hasattr(application, 'enrollment'):
        messages.error(request, "Enrollment letter is not available before enrollment confirmation.")
        return redirect('admissions:application_detail', application_id=application_id)

    enrollment = application.enrollment

    return render(request, 'enrollments/enrollment_letter.html', {
        'application': application,
        'enrollment': enrollment,
        'course': application.course,
        'student': application.student,
        'today': datetime.date.today(),
    })


# --- Admin Enrollment Management ---

@admin_required
def admin_manage_enrollments(request):
    """Admin: Manage, search and view all student enrollments"""
    query = request.GET.get('q', '').strip()
    course_filter = request.GET.get('course', '').strip()

    enrollments = Enrollment.objects.select_related('student', 'course', 'application').order_by('-created_at')

    if query:
        enrollments = enrollments.filter(
            Q(enrollment_id__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__email__icontains=query) |
            Q(course__course_name__icontains=query)
        )

    if course_filter:
        enrollments = enrollments.filter(course_id=course_filter)

    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    courses = Course.objects.all()

    return render(request, 'enrollments/admin_enrollments_list.html', {
        'page_obj': page_obj,
        'query': query,
        'course_filter': course_filter,
        'courses': courses,
        'total_count': enrollments.count(),
    })
