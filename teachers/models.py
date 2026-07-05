from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonType(models.TextChoices):
    ONE_TO_ONE = 'one_to_one', _('One-to-one')
    GROUP = 'group', _('Group')


class BookingMode(models.TextChoices):
    AUTOMATIC = 'automatic', _('Automatic')
    MANUAL = 'manual', _('Manual')


class TeacherProfile(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        SUSPENDED = 'suspended', _('Suspended')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': 'teacher'},
    )
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    headline = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='teachers/photos/', blank=True)
    cv_file = models.FileField(upload_to='teachers/cvs/', blank=True)
    intro_video_url = models.URLField(blank=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    booking_mode = models.CharField(
        max_length=20,
        choices=BookingMode.choices,
        default=BookingMode.AUTOMATIC,
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.user.get_full_name()} teacher profile'

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != 'teacher':
            raise ValidationError({'user': _('Only teacher users can have a teacher profile.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_publicly_visible(self) -> bool:
        return self.approval_status == self.ApprovalStatus.APPROVED

    @property
    def can_receive_bookings(self) -> bool:
        return self.is_publicly_visible

    @property
    def is_complete(self) -> bool:
        return all([self.bio, self.headline, self.cv_file])

    def approve(self, notes: str = '') -> None:
        self.approval_status = self.ApprovalStatus.APPROVED
        if notes:
            self.verification_notes = notes
        self.save()

    def reject(self, notes: str) -> None:
        self.approval_status = self.ApprovalStatus.REJECTED
        self.verification_notes = notes
        self.save()

    def suspend(self, notes: str = '') -> None:
        self.approval_status = self.ApprovalStatus.SUSPENDED
        if notes:
            self.verification_notes = notes
        self.save()


class TeacherCertificate(models.Model):
    teacher_profile = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    file = models.FileField(upload_to='teachers/certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f'{self.title} - {self.teacher_profile.user.get_full_name()}'


class TeacherSubject(models.Model):
    teacher_profile = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='teacher_subjects',
    )
    grade_level = models.ForeignKey(
        'subjects.GradeLevel',
        on_delete=models.CASCADE,
        related_name='teacher_subjects',
    )
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices)
    price_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_max = models.DecimalField(max_digits=10, decimal_places=2)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    group_capacity = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject__name', 'grade_level__order', 'lesson_type']
        constraints = [
            models.UniqueConstraint(
                fields=['teacher_profile', 'subject', 'grade_level', 'lesson_type'],
                name='unique_teacher_subject_grade_lesson_type',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.teacher_profile.user.get_full_name()} - {self.subject} - {self.grade_level}'

    def clean(self) -> None:
        super().clean()
        if self.lesson_type == LessonType.ONE_TO_ONE and self.group_capacity is not None:
            raise ValidationError({'group_capacity': _('Group capacity is only available for group lessons.')})
        if self.lesson_type == LessonType.GROUP and not self.group_capacity:
            raise ValidationError({'group_capacity': _('Group capacity is required for group lessons.')})
        if self.group_capacity and self.group_capacity > settings.PLATFORM_MAX_GROUP_SIZE:
            raise ValidationError(
                {'group_capacity': _('Group capacity cannot exceed %(max_size)s students.') % {
                    'max_size': settings.PLATFORM_MAX_GROUP_SIZE,
                }}
            )

        if (
            self.price_min is not None
            and self.price_max is not None
            and self.default_price is not None
            and not self.price_min <= self.default_price <= self.price_max
        ):
            raise ValidationError(
                {'default_price': _('Default price must be between the teacher minimum and maximum price.')}
            )

        if self.price_min is not None and self.price_max is not None and self.price_min > self.price_max:
            raise ValidationError({'price_max': _('Maximum price must be greater than or equal to minimum price.')})

        if (
            self.subject_id
            and self.grade_level_id
            and self.lesson_type
            and self.price_min is not None
            and self.price_max is not None
        ):
            pricing_range = PlatformPricingRange.objects.filter(
                subject=self.subject,
                grade_level=self.grade_level,
                lesson_type=self.lesson_type,
                is_active=True,
            ).first()
            if not pricing_range:
                raise ValidationError(_('No active platform pricing range is configured for this subject and grade.'))
            if self.price_min < pricing_range.min_price or self.price_min > pricing_range.max_price:
                raise ValidationError(
                    {'price_min': _('Minimum price must be between %(min_price)s and %(max_price)s.') % {
                        'min_price': pricing_range.min_price,
                        'max_price': pricing_range.max_price,
                    }}
                )
            if self.price_max < pricing_range.min_price or self.price_max > pricing_range.max_price:
                raise ValidationError(
                    {'price_max': _('Maximum price must be between %(min_price)s and %(max_price)s.') % {
                        'min_price': pricing_range.min_price,
                        'max_price': pricing_range.max_price,
                    }}
                )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class PlatformPricingRange(models.Model):
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='pricing_ranges',
    )
    grade_level = models.ForeignKey(
        'subjects.GradeLevel',
        on_delete=models.CASCADE,
        related_name='pricing_ranges',
    )
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject__name', 'grade_level__order', 'lesson_type']
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'grade_level', 'lesson_type'],
                name='unique_platform_pricing_range',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.subject} - {self.grade_level} - {self.get_lesson_type_display()}'

    def clean(self) -> None:
        super().clean()
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValidationError({'max_price': _('Maximum price must be greater than or equal to minimum price.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class AvailabilitySlot(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

    teacher_profile = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='availability_slots',
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self) -> str:
        return f'{self.teacher_profile.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'

    def clean(self) -> None:
        super().clean()
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': _('End time must be later than start time.')})

        if not self.teacher_profile_id or self.day_of_week is None or not self.start_time or not self.end_time:
            return

        overlapping_slots = AvailabilitySlot.objects.filter(
            teacher_profile=self.teacher_profile,
            day_of_week=self.day_of_week,
            is_active=True,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            overlapping_slots = overlapping_slots.exclude(pk=self.pk)
        if overlapping_slots.exists():
            raise ValidationError(_('Availability slots for the same teacher cannot overlap.'))

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
