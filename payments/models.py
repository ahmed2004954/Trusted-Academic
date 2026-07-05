from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
    wallet_pending_credited_at = models.DateTimeField(blank=True, null=True)
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


class Wallet(models.Model):
    teacher = models.OneToOneField('teachers.TeacherProfile', on_delete=models.PROTECT, related_name='wallet')
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['teacher__user__full_name']

    def __str__(self) -> str:
        return f'{self.teacher.user.get_full_name()} wallet'


class WithdrawalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        COMPLETED = 'completed', _('Completed')

    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.PROTECT, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    payment_details = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='processed_withdrawal_requests',
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True)
    balance_deducted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['requested_at']),
        ]

    def __str__(self) -> str:
        return f'{self.teacher.user.get_full_name()} - {self.amount} - {self.status}'

    def approve_and_reserve_balance(self, user, notes: str = '') -> None:
        self._require_status(self.Status.PENDING)
        self._deduct_available_balance_once()
        self._mark_processed(self.Status.APPROVED, user, notes)

    def complete_with_reserved_balance(self, user, notes: str = '') -> None:
        if self.status not in {self.Status.PENDING, self.Status.APPROVED}:
            raise ValidationError(_('Only pending or approved withdrawal requests can be completed.'))
        self._deduct_available_balance_once()
        self._mark_processed(self.Status.COMPLETED, user, notes)

    def reject_without_balance_change(self, user, notes: str = '') -> None:
        self._require_status(self.Status.PENDING)
        self._mark_processed(self.Status.REJECTED, user, notes)

    def _require_status(self, status: str) -> None:
        if self.status != status:
            raise ValidationError(_('Withdrawal request cannot move from its current status to the requested status.'))

    def _deduct_available_balance_once(self) -> None:
        if self.balance_deducted_at:
            return
        wallet, _created = Wallet.objects.select_for_update().get_or_create(teacher=self.teacher)
        if wallet.available_balance < self.amount:
            raise ValidationError(_('Withdrawal amount exceeds available wallet balance.'))
        wallet.available_balance -= self.amount
        wallet.save(update_fields=['available_balance', 'updated_at'])
        self.balance_deducted_at = timezone.now()

    def _mark_processed(self, status: str, user, notes: str = '') -> None:
        self.status = status
        self.processed_by = user
        self.processed_at = timezone.now()
        self.notes = notes.strip()
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'notes', 'balance_deducted_at'])
