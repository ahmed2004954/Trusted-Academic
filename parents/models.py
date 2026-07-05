from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ParentProfile(models.Model):
    class ContactMethod(models.TextChoices):
        EMAIL = 'email', _('Email')
        PHONE = 'phone', _('Phone')
        WHATSAPP = 'whatsapp', _('WhatsApp')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        limit_choices_to={'role': 'parent'},
    )
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=ContactMethod.choices,
        default=ContactMethod.EMAIL,
    )
    receive_email_reports = models.BooleanField(default=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ParentStudentLink',
        related_name='linked_parent_profiles',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__full_name']

    def __str__(self) -> str:
        return f'{self.user.get_full_name()} parent profile'

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != 'parent':
            raise ValidationError({'user': _('Only parent users can have a parent profile.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ParentStudentLink(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name='student_links')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_links',
        limit_choices_to={'role': 'student'},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['parent', 'student'], name='unique_parent_student_link'),
        ]

    def __str__(self) -> str:
        return f'{self.parent.user.get_full_name()} -> {self.student.get_full_name()}'

    def clean(self) -> None:
        super().clean()
        if self.student_id and self.student.role != 'student':
            raise ValidationError({'student': _('Only student users can be linked to a parent.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
