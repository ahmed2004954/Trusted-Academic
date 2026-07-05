from django.urls import path

from . import views

app_name = 'parents'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/link/', views.link_student, name='link_student'),
    path('students/<int:student_pk>/bookings/', views.student_booking_history, name='student_booking_history'),
]
