from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum
from accounts.decorators import admin_required
from courses.models import Course
from admissions.models import AdmissionApplication
from enrollments.models import Enrollment
from django.contrib.auth import get_user_model
import csv
import datetime

User = get_user_model()

@admin_required
def reports_overview(request):
    """Admin Reports Overview and Analytics Dashboard"""
    # 1. Total statistics
    total_students = User.objects.filter(role='STUDENT').count()
    total_applications = AdmissionApplication.objects.count()
    total_enrollments = Enrollment.objects.filter(status='Confirmed').count()
    total_courses = Course.objects.count()

    # 2. Applications by course
    apps_by_course = Course.objects.annotate(
        app_count=Count('applications'),
        enr_count=Count('enrollments')
    ).order_by('-app_count')

    # 3. Applications by status
    status_counts = AdmissionApplication.objects.values('status').annotate(count=Count('id')).order_by('-count')

    # 4. Seat Availability Breakdown
    courses_seats = Course.objects.all().order_by('course_name')

    return render(request, 'reports/overview.html', {
        'total_students': total_students,
        'total_applications': total_applications,
        'total_enrollments': total_enrollments,
        'total_courses': total_courses,
        'apps_by_course': apps_by_course,
        'status_counts': status_counts,
        'courses_seats': courses_seats,
    })


@admin_required
def export_applications_csv(request):
    """Export applications dataset to CSV"""
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="admissions_report_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Application ID', 'Student Name', 'Email', 'Phone',
        'Course Code', 'Course Name', 'Status', 'Date Submitted',
        'Percentage / CGPA', 'Reviewed By'
    ])

    apps = AdmissionApplication.objects.select_related('student', 'course', 'reviewed_by').all().order_by('-created_at')
    for app in apps:
        writer.writerow([
            app.application_id,
            app.full_name,
            app.email,
            app.phone_number,
            app.course.course_code,
            app.course.course_name,
            app.status,
            app.submitted_at.strftime('%Y-%m-%d %H:%M') if app.submitted_at else 'Draft',
            app.percentage_cgpa or 'N/A',
            app.reviewed_by.full_name if app.reviewed_by else 'N/A'
        ])

    return response


@admin_required
def export_enrollments_csv(request):
    """Export enrollments dataset to CSV"""
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="enrollments_report_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Enrollment ID', 'Roll Number', 'Student Name', 'Email',
        'Course', 'Department', 'Academic Year', 'Enrollment Date', 'Status'
    ])

    enrs = Enrollment.objects.select_related('student', 'course').all().order_by('-created_at')
    for enr in enrs:
        writer.writerow([
            enr.enrollment_id,
            enr.roll_number,
            enr.student.full_name,
            enr.student.email,
            enr.course.course_name,
            enr.course.department,
            enr.academic_year,
            enr.enrollment_date.strftime('%Y-%m-%d'),
            enr.status
        ])

    return response
