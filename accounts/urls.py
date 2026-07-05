from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/<str:role>/', views.register_view, name='register_with_role'),
    path('profile/', views.profile_view, name='profile'),
]
