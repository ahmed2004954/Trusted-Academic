from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.student_booking_list, name='student_list'),
    path('create/<int:teacher_pk>/', views.booking_create, name='create'),
    path('parent/create/<int:teacher_pk>/<int:student_pk>/', views.parent_booking_create, name='parent_create'),
    path('<int:pk>/', views.student_booking_detail, name='student_detail'),
    path('<int:pk>/cancel/', views.student_cancel_booking, name='student_cancel'),
    path('<int:pk>/reschedule/', views.student_reschedule_booking, name='student_reschedule'),
    path('<int:pk>/attendance/confirm/', views.student_confirm_attendance, name='student_confirm_attendance'),
    path('teacher/', views.teacher_booking_list, name='teacher_list'),
    path('teacher/<int:pk>/', views.teacher_booking_detail, name='teacher_detail'),
    path('teacher/<int:pk>/cancel/', views.teacher_cancel_booking, name='teacher_cancel'),
    path('teacher/<int:pk>/reschedule/', views.teacher_reschedule_booking, name='teacher_reschedule'),
    path('teacher/<int:pk>/attendance-code/', views.teacher_attendance_code, name='teacher_attendance_code'),
    path('teacher/<int:pk>/<str:action>/', views.teacher_booking_action, name='teacher_action'),
]
