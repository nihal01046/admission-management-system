from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_overview, name='overview'),
    path('export/applications/', views.export_applications_csv, name='export_applications'),
    path('export/enrollments/', views.export_enrollments_csv, name='export_enrollments'),
]
