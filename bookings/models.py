from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from teachers.models import BookingMode, LessonType, TeacherSubject


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING_TEACHER_ACCEPTANCE = 'pending_teacher_acceptance', _('Pending teacher acceptance')
        TEACHER_REJECTED = 'teacher_rejected', _('Teacher rejected')
        AWAITING_STUDENT_PAYMENT = 'awaiting_student_payment', _('Awaiting student payment')
        PENDING_PAYMENT = 'pending_payment', _('Pending payment')
        AWAITING_RECEIPT_VERIFICATION = 'awaiting_receipt_verification', _('Awaiting receipt verification')
        CONFIRMED = 'confirmed', _('Confirmed')
        IN_PROGRESS = 'in_progress', _('In progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED_BY_STUDENT = 'cancelled_by_student', _('Cancelled by student')
        CANCELLED_BY_TEACHER = 'cancelled_by_teacher', _('Cancelled by teacher')
        RESCHEDULED = 'rescheduled', _('Rescheduled')
        NO_SHOW_STUDENT = 'no_show_student', _('No-show student')
        NO_SHOW_TEACHER = 'no_show_teacher', _('No-show teacher')
        DISPUTED = 'disputed', _('Disputed')

    class DurationMinutes(models.IntegerChoices):
        THIRTY = 30, _('30 minutes')
        SIXTY = 60, _('60 minutes')
        NINETY = 90, _('90 minutes')
        ONE_TWENTY = 120, _('120 minutes')

    BLOCKING_STATUSES = {
        BookingStatus.PENDING_TEACHER_ACCEPTANCE,
        BookingStatus.AWAITING_STUDENT_PAYMENT,
        BookingStatus.PENDING_PAYMENT,
        BookingStatus.AWAITING_RECEIPT_VERIFICATION,
        BookingStatus.CONFIRMED,
        BookingStatus.IN_PROGRESS,
    }

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='student_bookings',
        limit_choices_to={'role': 'student'},
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='parent_bookings',
        limit_choices_to={'role': 'parent'},
        blank=True,
        null=True,
    )
    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.PROTECT, related_name='bookings')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.PROTECT, related_name='bookings')
    grade_level = models.ForeignKey('subjects.GradeLevel', on_delete=models.PROTECT, related_name='bookings')
    teacher_subject = models.ForeignKey(
        'teachers.TeacherSubject',
        on_delete=models.PROTECT,
        related_name='bookings',
        blank=True,
        null=True,
    )
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(choices=DurationMinutes.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    teacher_payout = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(
        max_length=40,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING_PAYMENT,
    )
    booking_mode = models.CharField(max_length=20, choices=BookingMode.choices, default=BookingMode.AUTOMATIC)
    meeting_url = models.URLField(blank=True)
    attendance_code = models.CharField(max_length=20, blank=True)
    attendance_confirmed_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)
    payment_deadline = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['teacher', 'scheduled_start', 'scheduled_end']),
            models.Index(fields=['student', 'scheduled_start']),
            models.Index(fields=['booking_status']),
        ]

    def __str__(self) -> str:
        return f'{self.student} with {self.teacher} at {self.scheduled_start:%Y-%m-%d %H:%M}'

    def clean(self) -> None:
        super().clean()
        errors = {}

        if self.student_id and self.student.role != 'student':
            errors['student'] = _('Only student users can create bookings.')
        if self.parent_id and self.parent.role != 'parent':
            errors['parent'] = _('Parent must use a parent account.')
        if self.teacher_id and not self.teacher.can_receive_bookings:
            errors['teacher'] = _('This teacher cannot receive bookings yet.')
        if self.scheduled_start and self.scheduled_end and self.scheduled_start >= self.scheduled_end:
            errors['scheduled_end'] = _('Scheduled end must be after scheduled start.')
        if self.scheduled_start and self.duration_minutes:
            expected_end = self.scheduled_start + timedelta(minutes=self.duration_minutes)
            if self.scheduled_end and self.scheduled_end != expected_end:
                errors['scheduled_end'] = _('Scheduled end must match the selected duration.')

        if self.teacher_id and self.subject_id and self.grade_level_id and self.lesson_type:
            teacher_subject = self.teacher_subject or TeacherSubject.objects.filter(
                teacher_profile=self.teacher,
                subject=self.subject,
                grade_level=self.grade_level,
                lesson_type=self.lesson_type,
                is_active=True,
            ).first()
            if not teacher_subject:
                errors['teacher_subject'] = _('The selected offering is not active for this teacher.')
            elif not self._teacher_subject_matches(teacher_subject):
                errors['teacher_subject'] = _('The selected offering does not match the booking details.')

        if self.teacher_id and self.scheduled_start and self.scheduled_end and self.booking_status in self.BLOCKING_STATUSES:
            overlaps = Booking.objects.filter(
                teacher=self.teacher,
                booking_status__in=self.BLOCKING_STATUSES,
                scheduled_start__lt=self.scheduled_end,
                scheduled_end__gt=self.scheduled_start,
            )
            if self.pk:
                overlaps = overlaps.exclude(pk=self.pk)
            if overlaps.exists():
                errors['scheduled_start'] = _('This teacher already has a blocking booking at that time.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def _teacher_subject_matches(self, teacher_subject: TeacherSubject) -> bool:
        return (
            teacher_subject.teacher_profile_id == self.teacher_id
            and teacher_subject.subject_id == self.subject_id
            and teacher_subject.grade_level_id == self.grade_level_id
            and teacher_subject.lesson_type == self.lesson_type
            and teacher_subject.is_active
        )

    def generate_attendance_code(self) -> str:
        if not self.attendance_code:
            self.attendance_code = get_random_string(8).upper()
        return self.attendance_code

    def accept_by_teacher(self) -> None:
        if self.booking_status != self.BookingStatus.PENDING_TEACHER_ACCEPTANCE:
            raise ValidationError(_('Only manual booking requests can be accepted by the teacher.'))
        self.booking_status = self.BookingStatus.AWAITING_STUDENT_PAYMENT
        self.payment_deadline = timezone.now() + timedelta(hours=24)
        self.save(update_fields=['booking_status', 'payment_deadline', 'updated_at'])

    def reject_by_teacher(self, reason: str = '') -> None:
        if self.booking_status != self.BookingStatus.PENDING_TEACHER_ACCEPTANCE:
            raise ValidationError(_('Only manual booking requests can be rejected by the teacher.'))
        self.booking_status = self.BookingStatus.TEACHER_REJECTED
        self.cancellation_reason = reason
        self.save(update_fields=['booking_status', 'cancellation_reason', 'updated_at'])
