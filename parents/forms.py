from django import forms
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from students.models import StudentProfile


class ManagedStudentCreateForm(forms.Form):
    full_name = forms.CharField(label=_('Student name'), max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=_('Email'), required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    school_name = forms.CharField(label=_('School name'), required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    grade_level = forms.ModelChoiceField(
        label=_('Grade level'),
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    notes = forms.CharField(label=_('Notes'), required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from subjects.models import GradeLevel

        self.fields['grade_level'].queryset = GradeLevel.objects.filter(is_active=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def save(self):
        User = get_user_model()
        email = self.cleaned_data.get('email') or self._generate_email(User)
        student = User.objects.create_user(
            email=email,
            full_name=self.cleaned_data['full_name'],
            password=get_random_string(16),
            role=User.Role.STUDENT,
            is_verified=True,
        )
        StudentProfile.objects.create(
            user=student,
            grade_level=self.cleaned_data.get('grade_level'),
            school_name=self.cleaned_data.get('school_name', ''),
            created_by_parent=True,
            notes=self.cleaned_data.get('notes', ''),
        )
        return student

    def _generate_email(self, User):
        while True:
            email = f'managed-{get_random_string(10).lower()}@student.local'
            if not User.objects.filter(email=email).exists():
                return email


class LinkStudentForm(forms.Form):
    linking_code = forms.CharField(label=_('Linking code'), max_length=12, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_linking_code(self):
        return self.cleaned_data['linking_code'].strip().upper()
