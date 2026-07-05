from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.PROTECT, related_name='report')
    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.PROTECT, related_name='reports')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='lesson_reports',
        limit_choices_to={'role': 'student'},
    )
    summary = models.TextField()
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    homework = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    sent_to_parent_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['teacher', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'Report for booking {self.booking_id}'

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.student_id and self.student.role != 'student':
            errors['student'] = _('Only student users can receive reports.')
        if self.booking_id:
            if self.booking.booking_status != self.booking.BookingStatus.COMPLETED:
                errors['booking'] = _('Reports are allowed only for completed bookings.')
            if self.student_id and self.booking.student_id != self.student_id:
                errors['student'] = _('Report student must match the booking student.')
            if self.teacher_id and self.booking.teacher_id != self.teacher_id:
                errors['teacher'] = _('Report teacher must match the booking teacher.')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
