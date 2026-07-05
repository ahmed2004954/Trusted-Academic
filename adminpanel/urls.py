from django.urls import path

from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/', views.booking_monitor, name='booking_monitor'),
    path('users/', views.user_list, name='user_list'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('review/teachers/', views.pending_teachers, name='pending_teachers'),
    path('review/teachers/<int:profile_id>/', views.review_teacher, name='review_teacher'),
]
