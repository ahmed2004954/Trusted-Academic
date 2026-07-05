from django.urls import path

from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('review/teachers/', views.pending_teachers, name='pending_teachers'),
    path('review/teachers/<int:profile_id>/', views.review_teacher, name='review_teacher'),
]
