from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class AuthenticationForm(BaseAuthenticationForm):
    """Login form that uses email instead of username."""
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )


class UserRegistrationForm(BaseUserCreationForm):
    """Signup form for public user roles (student/teacher/parent)."""
    PUBLIC_ROLES = [
        (User.Role.STUDENT, _('Student')),
        (User.Role.TEACHER, _('Teacher')),
        (User.Role.PARENT, _('Parent')),
    ]

    role = forms.ChoiceField(
        label=_('I am a'),
        choices=PUBLIC_ROLES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('full_name', 'email', 'phone', 'role')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return email.lower()

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == User.Role.ADMIN:
            raise ValidationError(_('Invalid role selected.'))
        return role
