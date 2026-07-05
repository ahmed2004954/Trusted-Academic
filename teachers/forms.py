from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import TeacherCertificate, TeacherProfile


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ('headline', 'bio', 'experience_years', 'photo', 'cv_file', 'intro_video_url')
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'intro_video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_experience_years(self) -> int:
        experience_years = self.cleaned_data['experience_years']
        if experience_years > 80:
            raise ValidationError(_('Experience years cannot be greater than 80.'))
        return experience_years


class TeacherCertificateForm(forms.ModelForm):
    class Meta:
        model = TeacherCertificate
        fields = ('title', 'issuing_organization', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TeacherReviewForm(forms.ModelForm):
    action = forms.ChoiceField(
        choices=(
            ('approve', _('Approve')),
            ('reject', _('Reject')),
            ('suspend', _('Suspend')),
        ),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = TeacherProfile
        fields = ('verification_notes',)
        widgets = {
            'verification_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self) -> dict:
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        notes = cleaned_data.get('verification_notes', '').strip()
        if action in {'reject', 'suspend'} and not notes:
            raise ValidationError(_('Verification notes are required when rejecting or suspending a teacher.'))
        return cleaned_data
