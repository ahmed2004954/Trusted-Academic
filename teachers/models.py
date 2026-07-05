from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


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
