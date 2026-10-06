from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('manage/', views.admin_student_list, name='manage'),
    path('manage/<int:user_id>/', views.admin_student_detail, name='admin_student_detail'),
]
