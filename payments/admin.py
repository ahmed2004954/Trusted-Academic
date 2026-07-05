from django.contrib import admin

from .models import Payment, Wallet, WithdrawalRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'currency', 'payment_method', 'payment_status', 'refund_amount', 'verified_by', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'currency', 'created_at')
    search_fields = ('booking__student__email', 'booking__teacher__user__email', 'transaction_reference')
    readonly_fields = (
        'created_at',
        'updated_at',
        'verified_at',
        'paid_at',
        'refunded_at',
        'wallet_pending_credited_at',
        'wallet_pending_reversed_at',
    )


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'available_balance', 'pending_balance', 'total_earned', 'updated_at')
    search_fields = ('teacher__user__email', 'teacher__user__full_name')
    readonly_fields = ('updated_at',)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'amount', 'payment_method', 'status', 'requested_at', 'processed_at', 'processed_by')
    list_filter = ('status', 'payment_method', 'requested_at', 'processed_at')
    search_fields = ('teacher__user__email', 'teacher__user__full_name', 'payment_details')
    readonly_fields = ('requested_at', 'processed_at', 'processed_by', 'balance_deducted_at')
