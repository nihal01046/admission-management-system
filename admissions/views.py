from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from accounts.decorators import student_required, admin_required
from .models import AdmissionApplication, ApplicationTimeline
from .forms import ApplicationStep1Form, ApplicationStep2Form, ApplicationStep3Form, AdminReviewForm
from courses.models import Course
from students.models import StudentProfile
from documents.models import Document
from notifications.services import send_notification
from django.contrib.auth import get_user_model

User = get_user_model()

@student_required
def apply_wizard(request):
    """
    5-step Admission Application Wizard matching Image 1 #7:
    Step 1: Personal Details
    Step 2: Academic Details
    Step 3: Course Preference
    Step 4: Documents Upload
    Step 5: Review & Submit
    """
    student = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student)

    # Check if continuing an existing draft application
    draft_app_id = request.session.get('draft_app_id')
    draft_app = None
    if draft_app_id:
        draft_app = AdmissionApplication.objects.filter(id=draft_app_id, student=student, status='Draft').first()

    step = int(request.GET.get('step', draft_app.current_step if draft_app else 1))
    if step < 1 or step > 5:
        step = 1

    # Form initialization based on step
    courses = Course.objects.filter(status='Active')

    if request.method == 'POST':
        current_action = request.POST.get('action', 'next')
        
        # Ensure draft application instance exists
        if not draft_app:
            default_course = courses.first()
            if not default_course:
                default_course = Course.objects.create(
                    course_name='BCA',
                    course_code='BCA-DEFAULT',
                    department='Computer Applications',
                    total_seats=60,
                    available_seats=60,
                    status='Active'
                )
            draft_app = AdmissionApplication.objects.create(
                student=student,
                course=default_course,
                status='Draft',
                full_name=student.full_name,
                email=student.email,
                phone_number=student.phone_number or '',
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                address=profile.address,
                father_name=profile.father_name,
                mother_name=profile.mother_name,
                guardian_contact=profile.guardian_contact,
                previous_institution=profile.previous_institution,
                qualification=profile.qualification,
                board_university=profile.board_university,
                passing_year=profile.passing_year,
                percentage_cgpa=profile.percentage_cgpa,
            )
            request.session['draft_app_id'] = draft_app.id

        if step == 1:
            form = ApplicationStep1Form(request.POST, instance=draft_app)
            if form.is_valid():
                form.save()
                draft_app.current_step = 2
                draft_app.save(update_fields=['current_step'])
                return redirect(f"{request.path}?step=2")
            else:
                messages.error(request, "Please verify your personal details.")

        elif step == 2:
            form = ApplicationStep2Form(request.POST, instance=draft_app)
            if form.is_valid():
                form.save()
                draft_app.current_step = 3
                draft_app.save(update_fields=['current_step'])
                return redirect(f"{request.path}?step=3")
            else:
                messages.error(request, "Please verify your academic details.")

        elif step == 3:
            course_id = request.POST.get('course')
            if course_id:
                selected_course = get_object_or_404(Course, id=course_id)
                # Check duplicate application for the same active course
                existing = AdmissionApplication.objects.filter(
                    student=student,
                    course=selected_course
                ).exclude(status__in=['Draft', 'Rejected']).exists()

                if existing:
                    messages.warning(request, f"You already have an active application submitted for {selected_course.course_name}.")
                else:
                    draft_app.course = selected_course
                    draft_app.current_step = 4
                    draft_app.save(update_fields=['course', 'current_step'])
                    return redirect(f"{request.path}?step=4")
            else:
                messages.error(request, "Please select a preferred course.")

        elif step == 4:
            # Handle uploaded files
            id_file = request.FILES.get('id_proof')
            photo_file = request.FILES.get('passport_photo')
            marksheet_file = request.FILES.get('marksheet')

            if id_file:
                Document.objects.create(
                    student=student,
                    application=draft_app,
                    document_type='ID_PROOF',
                    file=id_file,
                    title='Identity Proof'
                )
            if photo_file:
                Document.objects.create(
                    student=student,
                    application=draft_app,
                    document_type='PHOTO',
                    file=photo_file,
                    title='Passport Photo'
                )
            if marksheet_file:
                Document.objects.create(
                    student=student,
                    application=draft_app,
                    document_type='ACADEMIC_12',
                    file=marksheet_file,
                    title='Qualifying Marksheet'
                )

            draft_app.current_step = 5
            draft_app.save(update_fields=['current_step'])
            return redirect(f"{request.path}?step=5")

        elif step == 5:
            # Final Submission
            if current_action == 'save_draft':
                messages.info(request, "Application saved as draft. You can resume anytime.")
                return redirect('admissions:my_applications')

            # Validate before final submission
            if not draft_app.course.has_available_seats:
                messages.error(request, f"Sorry, seats for {draft_app.course.course_name} are currently full.")
                return redirect(f"{request.path}?step=3")

            draft_app.status = 'Submitted'
            draft_app.submitted_at = timezone.now()
            draft_app.save()

            # Create Timeline Record
            ApplicationTimeline.objects.create(
                application=draft_app,
                status='Submitted',
                title='Application Submitted',
                description='Student submitted the complete application online.',
                performed_by=student
            )

            # Notifications
            send_notification(
                recipient=student,
                title='Application Submitted',
                message=f'Your application {draft_app.application_id} for {draft_app.course.course_name} has been submitted successfully.',
                link=f'/admissions/{draft_app.application_id}/',
                notification_type='SUCCESS'
            )

            admin_users = User.objects.filter(role='ADMIN')
            for adm in admin_users:
                send_notification(
                    recipient=adm,
                    title='New Application Received',
                    message=f'New application {draft_app.application_id} from {draft_app.full_name} for {draft_app.course.course_code}.',
                    link=f'/admissions/admin/{draft_app.application_id}/',
                    notification_type='INFO'
                )

            # Clear session draft
            if 'draft_app_id' in request.session:
                del request.session['draft_app_id']

            messages.success(request, f"Congratulations! Your application ({draft_app.application_id}) has been submitted successfully.")
            return redirect('admissions:application_detail', application_id=draft_app.application_id)

    # Initial GET data setup
    if not draft_app:
        initial_data = {
            'full_name': student.full_name,
            'email': student.email,
            'phone_number': student.phone_number or '',
            'date_of_birth': profile.date_of_birth,
            'gender': profile.gender,
            'address': profile.address,
            'father_name': profile.father_name,
            'mother_name': profile.mother_name,
            'guardian_contact': profile.guardian_contact,
        }
    else:
        initial_data = None

    step1_form = ApplicationStep1Form(instance=draft_app, initial=initial_data)
    step2_form = ApplicationStep2Form(instance=draft_app)
    step3_form = ApplicationStep3Form(instance=draft_app)

    uploaded_docs = Document.objects.filter(application=draft_app) if draft_app else []

    return render(request, 'admissions/application_form.html', {
        'step': step,
        'draft_app': draft_app,
        'step1_form': step1_form,
        'step2_form': step2_form,
        'step3_form': step3_form,
        'courses': courses,
        'uploaded_docs': uploaded_docs,
    })


@student_required
def my_applications(request):
    """Student: View list of own submitted and draft applications"""
    applications = AdmissionApplication.objects.filter(student=request.user).select_related('course').order_by('-created_at')
    return render(request, 'admissions/my_applications.html', {'applications': applications})


@student_required
def application_detail(request, application_id):
    """Student: View complete application status, timeline, and enrollment trigger"""
    application = get_object_or_404(
        AdmissionApplication.objects.select_related('course', 'student'),
        application_id=application_id,
        student=request.user
    )
    documents = Document.objects.filter(application=application)
    timeline = application.timeline.all().order_by('created_at')

    return render(request, 'admissions/application_detail.html', {
        'application': application,
        'documents': documents,
        'timeline': timeline,
    })


# --- Admin Application Management ---

@admin_required
def admin_manage_applications(request):
    """Admin: Manage all admission applications with search, status & course filter"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    course_filter = request.GET.get('course', '').strip()

    applications = AdmissionApplication.objects.select_related('student', 'course').order_by('-created_at')

    if query:
        applications = applications.filter(
            Q(application_id__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(course__course_name__icontains=query) |
            Q(course__course_code__icontains=query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    if course_filter:
        applications = applications.filter(course_id=course_filter)

    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    courses = Course.objects.all()

    return render(request, 'admissions/admin_applications_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'courses': courses,
        'total_count': applications.count(),
    })


@admin_required
def admin_application_detail(request, application_id):
    """Admin: Detailed Application Review, Approval, Rejection, and Document Inspection"""
    application = get_object_or_404(
        AdmissionApplication.objects.select_related('student', 'course', 'reviewed_by'),
        application_id=application_id
    )
    documents = Document.objects.filter(application=application)
    timeline = application.timeline.all().order_by('created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_remarks = request.POST.get('admin_remarks', '').strip()
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        if action == 'approve':
            application.status = 'Approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_remarks = admin_remarks
            application.save()

            ApplicationTimeline.objects.create(
                application=application,
                status='Approved',
                title='Admission Approved',
                description=f'Admission approved by {request.user.full_name}. Student may proceed with enrollment.',
                performed_by=request.user
            )

            send_notification(
                recipient=application.student,
                title='Admission Application Approved!',
                message=f'Congratulations! Your application {application.application_id} for {application.course.course_name} has been approved.',
                link=f'/admissions/{application.application_id}/',
                notification_type='SUCCESS'
            )
            messages.success(request, f"Application {application.application_id} has been Approved.")

        elif action == 'reject':
            if not rejection_reason:
                messages.error(request, "A rejection reason is required to reject an application.")
                return redirect('admissions:admin_detail', application_id=application.application_id)

            application.status = 'Rejected'
            application.rejection_reason = rejection_reason
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_remarks = admin_remarks
            application.save()

            ApplicationTimeline.objects.create(
                application=application,
                status='Rejected',
                title='Application Rejected',
                description=f'Rejected by admissions committee. Reason: {rejection_reason}',
                performed_by=request.user
            )

            send_notification(
                recipient=application.student,
                title='Application Status Update',
                message=f'Your application {application.application_id} was not approved. Reason: {rejection_reason}',
                link=f'/admissions/{application.application_id}/',
                notification_type='DANGER'
            )
            messages.warning(request, f"Application {application.application_id} has been marked Rejected.")

        elif action == 'under_review':
            application.status = 'Under Review'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_remarks = admin_remarks
            application.save()

            ApplicationTimeline.objects.create(
                application=application,
                status='Under Review',
                title='Under Review',
                description='Application is under active evaluation by the review panel.',
                performed_by=request.user
            )
            messages.info(request, f"Application {application.application_id} moved to Under Review.")

        elif action == 'doc_verify':
            application.status = 'Document Verification'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_remarks = admin_remarks
            application.save()

            ApplicationTimeline.objects.create(
                application=application,
                status='Document Verification',
                title='Document Verification Stage',
                description='Documents are being verified against institution records.',
                performed_by=request.user
            )
            messages.info(request, f"Application {application.application_id} moved to Document Verification.")

        return redirect('admissions:admin_detail', application_id=application.application_id)

    return render(request, 'admissions/admin_application_detail.html', {
        'application': application,
        'documents': documents,
        'timeline': timeline,
    })
