from django.urls import path

from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list, name='public_list'),
    path('<int:pk>/', views.teacher_detail, name='public_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/setup/', views.setup_profile, name='setup_profile'),
    path('certificates/upload/', views.upload_certificate, name='upload_certificate'),
    path('status/', views.my_status, name='my_status'),
    path('subjects/', views.manage_subjects, name='manage_subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/<int:pk>/edit/', views.edit_subject, name='edit_subject'),
    path('subjects/<int:pk>/delete/', views.delete_subject, name='delete_subject'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('availability/add/', views.add_availability, name='add_availability'),
    path('availability/<int:pk>/edit/', views.edit_availability, name='edit_availability'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete_availability'),
]
