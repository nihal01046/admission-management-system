from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Course
from .forms import CourseForm

def course_list(request):
    """Student and public view of all courses with search and department filter"""
    query = request.GET.get('q', '').strip()
    dept = request.GET.get('dept', '').strip()

    courses = Course.objects.all()

    # Students / public only see Active courses unless admin
    if not (request.user.is_authenticated and request.user.is_admin_user):
        courses = courses.filter(status='Active')

    if query:
        courses = courses.filter(
            Q(course_name__icontains=query) |
            Q(course_code__icontains=query) |
            Q(department__icontains=query) |
            Q(description__icontains=query)
        )

    if dept:
        courses = courses.filter(department__iexact=dept)

    departments = Course.objects.values_list('department', flat=True).distinct()

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'departments': departments,
        'query': query,
        'selected_dept': dept,
    })


def course_detail(request, pk):
    """Detailed Course syllabus and eligibility view"""
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})


@admin_required
def admin_course_manage(request):
    """Admin Course Management matching Image 1 #6 & Image 2 #4 EXACTLY"""
    query = request.GET.get('q', '').strip()
    courses = Course.objects.all().order_by('id')

    if query:
        courses = courses.filter(
            Q(course_name__icontains=query) |
            Q(course_code__icontains=query) |
            Q(department__icontains=query)
        )

    return render(request, 'courses/admin_course_manage.html', {
        'courses': courses,
        'query': query,
    })


@admin_required
def admin_course_create(request):
    """Admin: Add New Course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.course_name}' has been created successfully.")
            return redirect('courses:manage')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = CourseForm()

    return render(request, 'courses/admin_course_form.html', {
        'form': form,
        'action_title': 'Add New Course',
        'is_edit': False
    })


@admin_required
def admin_course_edit(request, pk):
    """Admin: Edit Existing Course"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.course_name}' has been updated.")
            return redirect('courses:manage')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/admin_course_form.html', {
        'form': form,
        'course': course,
        'action_title': f'Edit Course: {course.course_name}',
        'is_edit': True
    })


@admin_required
def admin_course_delete(request, pk):
    """Admin: Deactivate or Delete Course"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'deactivate')
        if action == 'delete':
            # Check if applications or enrollments exist
            if course.applications.exists() or course.enrollments.exists():
                course.status = 'Inactive'
                course.save()
                messages.warning(request, f"Cannot permanently delete '{course.course_name}' as student records are linked. It has been marked Inactive instead.")
            else:
                course.delete()
                messages.success(request, f"Course '{course.course_name}' has been deleted.")
        else:
            # Toggle active status
            course.status = 'Inactive' if course.status == 'Active' else 'Active'
            course.save()
            messages.success(request, f"Course status updated to {course.status}.")
        return redirect('courses:manage')

    return render(request, 'courses/admin_course_confirm_delete.html', {'course': course})


def api_course_info(request, pk):
    """JSON API to fetch dynamic course eligibility and seats for Application Step 3"""
    course = get_object_or_404(Course, pk=pk)
    return JsonResponse({
        'id': course.id,
        'course_name': course.course_name,
        'course_code': course.course_code,
        'department': course.department,
        'duration': course.duration,
        'fees': float(course.fees),
        'total_seats': course.total_seats,
        'available_seats': course.available_seats,
        'eligibility': course.eligibility,
        'has_seats': course.has_available_seats,
    })
