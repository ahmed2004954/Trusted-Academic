from django.urls import path

from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('booking/<int:booking_pk>/create/', views.complaint_create, name='create'),
    path('<int:pk>/', views.complaint_detail, name='detail'),
    path('staff/', views.staff_complaint_queue, name='staff_queue'),
    path('staff/<int:pk>/', views.staff_complaint_detail, name='staff_detail'),
]
