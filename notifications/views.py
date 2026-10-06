from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    """View all notifications for the current user"""
    filter_type = request.GET.get('filter', 'all')
    notifications = Notification.objects.filter(recipient=request.user)

    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'filter_type': filter_type,
    })


@login_required
def mark_as_read(request, pk):
    """Mark a single notification as read and redirect to its target link"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications for the user as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')
