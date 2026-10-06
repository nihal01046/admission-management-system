from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='list'),
    path('delete/<int:pk>/', views.document_delete, name='delete'),
    path('manage/', views.admin_manage_documents, name='manage'),
    path('verify/<int:pk>/', views.admin_verify_document, name='verify'),
]
