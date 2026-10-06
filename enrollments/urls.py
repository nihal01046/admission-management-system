from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/<str:application_id>/', views.enroll_student, name='enroll_student'),
    path('confirmation/<str:application_id>/', views.enrollment_confirmation, name='confirmation'),
    path('letter/<str:application_id>/', views.download_enrollment_letter, name='enrollment_letter'),
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('manage/', views.admin_manage_enrollments, name='manage'),
]
