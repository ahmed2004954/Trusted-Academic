from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('booking/<int:booking_pk>/', views.payment_instructions, name='instructions'),
    path('history/', views.payment_history, name='history'),
    path('wallet/', views.wallet_dashboard, name='wallet'),
    path('admin/pending/', views.pending_verifications, name='admin_pending'),
    path('admin/<int:payment_pk>/', views.verification_detail, name='admin_detail'),
    path('admin/<int:payment_pk>/approve/', views.approve_payment, name='admin_approve'),
    path('admin/<int:payment_pk>/reject/', views.reject_payment, name='admin_reject'),
    path('admin/withdrawals/', views.withdrawal_queue, name='admin_withdrawal_queue'),
    path('admin/withdrawals/<int:withdrawal_pk>/', views.withdrawal_detail, name='admin_withdrawal_detail'),
    path(
        'admin/withdrawals/<int:withdrawal_pk>/<str:action>/',
        views.process_withdrawal,
        name='admin_withdrawal_action',
    ),
]
