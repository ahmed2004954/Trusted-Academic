from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Complaint(models.Model):
    class Category(models.TextChoices):
        TEACHER_ABSENCE = 'teacher_absence', _('Teacher absence')
        STUDENT_ABSENCE = 'student_absence', _('Student absence')
        BEHAVIOR = 'behavior', _('Behavior')
        QUALITY = 'quality', _('Quality')
        CONTENT_VIOLATION = 'content_violation', _('Content violation')
        PAYMENT = 'payment', _('Payment')
        OTHER = 'other', _('Other')

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        UNDER_REVIEW = 'under_review', _('Under review')
        RESOLVED = 'resolved', _('Resolved')
        REJECTED = 'rejected', _('Rejected')

    booking = models.ForeignKey('bookings.Booking', on_delete=models.PROTECT, related_name='complaints')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_complaints',
    )
    against_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='complaints_against',
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    description = models.TextField()
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='resolved_complaints',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['against_user', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'Complaint #{self.pk or "new"} for booking #{self.booking_id or "new"}'

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.booking_id and self.against_user_id:
            participant_ids = {self.booking.student_id, self.booking.teacher.user_id}
            if self.booking.parent_id:
                participant_ids.add(self.booking.parent_id)
            if self.against_user_id not in participant_ids:
                errors['against_user'] = _('Complaint must be against a booking participant.')
        if self.created_by_id and self.against_user_id and self.created_by_id == self.against_user_id:
            errors['against_user'] = _('Complaint cannot be against yourself.')
        if self.status in {self.Status.RESOLVED, self.Status.REJECTED}:
            if not self.resolution_notes:
                errors['resolution_notes'] = _('Resolution notes are required when closing a complaint.')
            if not self.resolved_by_id:
                errors['resolved_by'] = _('Resolved by is required when closing a complaint.')
        elif self.resolved_at or self.resolved_by_id:
            errors['status'] = _('Only resolved or rejected complaints can have resolution metadata.')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        if self.status in {self.Status.RESOLVED, self.Status.REJECTED} and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status not in {self.Status.RESOLVED, self.Status.REJECTED}:
            self.resolved_at = None
            self.resolved_by = None
        self.full_clean()
        super().save(*args, **kwargs)
