from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'currency', 'payment_method', 'payment_status', 'verified_by', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'currency', 'created_at')
    search_fields = ('booking__student__email', 'booking__teacher__user__email', 'transaction_reference')
    readonly_fields = ('created_at', 'updated_at', 'verified_at', 'paid_at', 'refunded_at')
