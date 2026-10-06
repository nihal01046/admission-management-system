from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_student and not request.user.is_superuser:
            messages.error(request, "Access restricted to student accounts.")
            return redirect('accounts:admin_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in as an administrator to access this page.")
            return redirect('accounts:admin_login')
        if not request.user.is_admin_user:
            messages.error(request, "Access denied. Administrative privileges required.")
            return redirect('students:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
