from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        VODAFONE_CASH = 'vodafone_cash', _('Vodafone Cash')
        INSTAPAY = 'instapay', _('Instapay')
        EWALLET = 'ewallet', _('E-wallet')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        AWAITING_VERIFICATION = 'awaiting_verification', _('Awaiting verification')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially refunded')

    booking = models.OneToOneField('bookings.Booking', on_delete=models.PROTECT, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EGP')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    receipt_image = models.ImageField(upload_to='payments/receipts/', blank=True)
    transaction_reference = models.CharField(max_length=255, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='verified_payments',
        blank=True,
        null=True,
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.booking_id} - {self.amount} {self.currency} - {self.payment_status}'
