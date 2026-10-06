from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import student_required, admin_required
from accounts.forms import StudentProfileForm, ProfileUpdateForm
from .models import StudentProfile
from admissions.models import AdmissionApplication
from enrollments.models import Enrollment
from courses.models import Course
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

@student_required
def student_dashboard(request):
    """Student Dashboard matching Image 1 #5"""
    student = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student)
    applications = AdmissionApplication.objects.filter(student=student).select_related('course')

    total_apps = applications.count()
    approved_apps = applications.filter(status__in=['Approved', 'Enrolled']).count()
    pending_apps = applications.filter(status__in=['Submitted', 'Under Review', 'Document Verification', 'Draft']).count()
    rejected_apps = applications.filter(status='Rejected').count()

    latest_app = applications.first()

    # Determine timeline state based on latest application
    app_submitted = bool(latest_app and latest_app.status != 'Draft')
    doc_verified = bool(latest_app and latest_app.status in ['Document Verification', 'Approved', 'Enrolled'])
    adm_approved = bool(latest_app and latest_app.status in ['Approved', 'Enrolled'])
    enrolled = bool(latest_app and latest_app.status == 'Enrolled')

    recommended_courses = Course.objects.filter(status='Active')[:3]

    today_formatted = datetime.date.today().strftime("%B %d, %Y")

    return render(request, 'students/dashboard.html', {
        'profile': profile,
        'total_apps': total_apps,
        'approved_apps': approved_apps,
        'pending_apps': pending_apps,
        'rejected_apps': rejected_apps,
        'latest_app': latest_app,
        'app_submitted': app_submitted,
        'doc_verified': doc_verified,
        'adm_approved': adm_approved,
        'enrolled': enrolled,
        'recommended_courses': recommended_courses,
        'today_formatted': today_formatted,
    })


@student_required
def student_profile(request):
    """Student Profile View and Edit"""
    student = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student)

    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, request.FILES, instance=student)
        profile_form = StudentProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('students:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        user_form = ProfileUpdateForm(instance=student)
        profile_form = StudentProfileForm(instance=profile)

    return render(request, 'students/profile.html', {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    })


# --- Admin Student Management ---

@admin_required
def admin_student_list(request):
    """Admin: Manage and Search All Students"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    students = User.objects.filter(role='STUDENT').select_related('student_profile').order_by('-date_joined')

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(student_profile__student_id__icontains=query) |
            Q(phone_number__icontains=query)
        )

    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/admin_student_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_count': students.count(),
    })


@admin_required
def admin_student_detail(request, user_id):
    """Admin: Detailed Student Profile, Applications and Enrollments"""
    student_user = get_object_or_404(User, id=user_id, role='STUDENT')
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)
    applications = AdmissionApplication.objects.filter(student=student_user).select_related('course')
    enrollments = Enrollment.objects.filter(student=student_user).select_related('course')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            student_user.is_active = not student_user.is_active
            student_user.save()
            status_text = "activated" if student_user.is_active else "deactivated"
            messages.success(request, f"Student account has been {status_text}.")
            return redirect('students:admin_student_detail', user_id=student_user.id)

    return render(request, 'students/admin_student_detail.html', {
        'student_user': student_user,
        'profile': profile,
        'applications': applications,
        'enrollments': enrollments,
    })
