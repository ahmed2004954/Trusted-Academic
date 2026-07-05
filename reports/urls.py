from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('<int:pk>/', views.report_detail, name='detail'),
    path('bookings/<int:booking_pk>/create/', views.create_report, name='create'),
]
