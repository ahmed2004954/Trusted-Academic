from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.student_booking_list, name='student_list'),
    path('create/<int:teacher_pk>/', views.booking_create, name='create'),
    path('<int:pk>/', views.student_booking_detail, name='student_detail'),
    path('teacher/', views.teacher_booking_list, name='teacher_list'),
    path('teacher/<int:pk>/', views.teacher_booking_detail, name='teacher_detail'),
    path('teacher/<int:pk>/<str:action>/', views.teacher_booking_action, name='teacher_action'),
]
