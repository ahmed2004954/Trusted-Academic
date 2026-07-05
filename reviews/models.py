from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _


class Review(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.PROTECT, related_name='review')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reviews_given',
        limit_choices_to={'role': 'student'},
    )
    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.PROTECT, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher', 'is_visible']),
            models.Index(fields=['student', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.teacher} - {self.rating}/5'

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.student_id and self.student.role != 'student':
            errors['student'] = _('Only student users can leave reviews.')
        if self.booking_id:
            if self.booking.booking_status != self.booking.BookingStatus.COMPLETED:
                errors['booking'] = _('Reviews are allowed only after completed bookings.')
            if self.student_id and self.booking.student_id != self.student_id:
                errors['student'] = _('Only the booking student can review this lesson.')
            if self.teacher_id and self.booking.teacher_id != self.teacher_id:
                errors['teacher'] = _('Review teacher must match the booking teacher.')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        old_teacher_id = None
        if self.pk:
            old_teacher_id = Review.objects.filter(pk=self.pk).values_list('teacher_id', flat=True).first()
        self.full_clean()
        super().save(*args, **kwargs)
        self.recalculate_teacher_rating(self.teacher)
        if old_teacher_id and old_teacher_id != self.teacher_id:
            from teachers.models import TeacherProfile

            old_teacher = TeacherProfile.objects.filter(pk=old_teacher_id).first()
            if old_teacher:
                self.recalculate_teacher_rating(old_teacher)

    def delete(self, *args, **kwargs):
        teacher = self.teacher
        result = super().delete(*args, **kwargs)
        self.recalculate_teacher_rating(teacher)
        return result

    @staticmethod
    def recalculate_teacher_rating(teacher) -> None:
        visible_reviews = teacher.reviews.filter(is_visible=True)
        summary = visible_reviews.aggregate(average=Avg('rating'))
        teacher.average_rating = round(summary['average'] or 0, 2)
        teacher.total_reviews = visible_reviews.count()
        teacher.save(update_fields=['average_rating', 'total_reviews', 'updated_at'])
