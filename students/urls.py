from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('linking-code/', views.linking_code, name='linking_code'),
]
