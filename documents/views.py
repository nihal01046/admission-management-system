from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from accounts.decorators import student_required, admin_required
from .models import Document
from .forms import DocumentUploadForm
from notifications.services import send_notification

@student_required
def document_list(request):
    """Student: View and upload academic and identity documents"""
    documents = Document.objects.filter(student=request.user).order_by('-uploaded_at')

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.student = request.user
            doc.save()
            messages.success(request, f"Document '{doc.get_document_type_display()}' uploaded successfully.")
            return redirect('documents:list')
        else:
            messages.error(request, "Failed to upload document. Please check the file format and size.")
    else:
        form = DocumentUploadForm()

    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'form': form,
    })


@student_required
def document_delete(request, pk):
    """Student: Delete pending document"""
    doc = get_object_or_404(Document, pk=pk, student=request.user)
    if doc.status == 'Verified':
        messages.error(request, "Cannot delete a document that has already been verified by administration.")
    else:
        doc.delete()
        messages.success(request, "Document removed successfully.")
    return redirect('documents:list')


# --- Admin Document Management ---

@admin_required
def admin_manage_documents(request):
    """Admin: Inspect, search, verify and reject uploaded documents"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('type', '').strip()

    documents = Document.objects.select_related('student', 'application', 'verified_by').order_by('-uploaded_at')

    if query:
        documents = documents.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__email__icontains=query) |
            Q(file_name__icontains=query)
        )

    if status_filter:
        documents = documents.filter(status=status_filter)

    if type_filter:
        documents = documents.filter(document_type=type_filter)

    paginator = Paginator(documents, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/admin_documents_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'doc_types': Document.DOCUMENT_TYPES,
        'total_count': documents.count(),
    })


@admin_required
def admin_verify_document(request, pk):
    """Admin: Verify or Reject a document"""
    doc = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('rejection_reason', '').strip()

        if action == 'verify':
            doc.status = 'Verified'
            doc.verified_by = request.user
            doc.verified_at = timezone.now()
            doc.rejection_reason = None
            doc.save()

            send_notification(
                recipient=doc.student,
                title='Document Verified',
                message=f'Your uploaded document "{doc.get_document_type_display()}" has been verified.',
                link='/documents/',
                notification_type='SUCCESS'
            )
            messages.success(request, f"Document for {doc.student.full_name} has been verified.")

        elif action == 'reject':
            if not reason:
                messages.error(request, "Please enter a reason for rejecting the document.")
                return redirect('documents:manage')

            doc.status = 'Rejected'
            doc.verified_by = request.user
            doc.verified_at = timezone.now()
            doc.rejection_reason = reason
            doc.save()

            send_notification(
                recipient=doc.student,
                title='Document Rejected',
                message=f'Your document "{doc.get_document_type_display()}" was rejected. Reason: {reason}',
                link='/documents/',
                notification_type='DANGER'
            )
            messages.warning(request, f"Document for {doc.student.full_name} was marked Rejected.")

    return redirect('documents:manage')
