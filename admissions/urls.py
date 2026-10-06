from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    path('apply/', views.apply_wizard, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('<str:application_id>/', views.application_detail, name='application_detail'),
    path('admin/manage/', views.admin_manage_applications, name='admin_manage'),
    path('admin/<str:application_id>/', views.admin_application_detail, name='admin_detail'),
]
