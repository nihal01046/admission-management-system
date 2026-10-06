from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]
