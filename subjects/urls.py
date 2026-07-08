from django.urls import path

from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.subject_list, name='list'),
    path('browse/', views.subject_browse, name='browse'),
]
