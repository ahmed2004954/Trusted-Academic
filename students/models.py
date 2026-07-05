from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'},
    )
    grade_level = models.ForeignKey(
        'subjects.GradeLevel',
        on_delete=models.SET_NULL,
        related_name='student_profiles',
        blank=True,
        null=True,
    )
    school_name = models.CharField(max_length=255, blank=True)
    created_by_parent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    linking_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__full_name']

    def __str__(self) -> str:
        return f'{self.user.get_full_name()} student profile'

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != 'student':
            raise ValidationError({'user': _('Only student users can have a student profile.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_linking_code(self, save: bool = True) -> str:
        if self.linking_code:
            return self.linking_code

        code = get_random_string(8).upper()
        while StudentProfile.objects.filter(linking_code=code).exclude(pk=self.pk).exists():
            code = get_random_string(8).upper()
        self.linking_code = code
        if save:
            self.save(update_fields=['linking_code', 'updated_at'])
        return code
