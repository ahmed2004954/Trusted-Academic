from django.urls import path

from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/setup/', views.setup_profile, name='setup_profile'),
    path('certificates/upload/', views.upload_certificate, name='upload_certificate'),
    path('status/', views.my_status, name='my_status'),
]
