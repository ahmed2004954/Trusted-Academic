from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('booking/<int:booking_pk>/', views.booking_thread, name='booking_thread'),
    path('thread/<int:pk>/', views.thread_detail, name='thread_detail'),
]
