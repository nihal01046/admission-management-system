from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<int:pk>/', views.course_detail, name='detail'),
    path('api/<int:pk>/info/', views.api_course_info, name='api_info'),
    path('manage/', views.admin_course_manage, name='manage'),
    path('manage/create/', views.admin_course_create, name='create'),
    path('manage/<int:pk>/edit/', views.admin_course_edit, name='edit'),
    path('manage/<int:pk>/delete/', views.admin_course_delete, name='delete'),
]
