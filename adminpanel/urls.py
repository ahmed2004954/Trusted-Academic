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
    path('subjects/', views.manage_subjects, name='manage_subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/<int:subject_id>/edit/', views.edit_subject, name='edit_subject'),
    path('subjects/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    path('grade-levels/add/', views.add_grade_level, name='add_grade_level'),
    path('grade-levels/<int:gl_id>/edit/', views.edit_grade_level, name='edit_grade_level'),
    path('pricing/add/', views.add_pricing_range, name='add_pricing_range'),
    path('pricing/<int:pr_id>/edit/', views.edit_pricing_range, name='edit_pricing_range'),
]
