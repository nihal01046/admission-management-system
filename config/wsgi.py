"""
WSGI config for College Admission and Student Enrollment Management System.
Exposes WSGI callable as ``application`` and ``app`` for Vercel deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
app = application
