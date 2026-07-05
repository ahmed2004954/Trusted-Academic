from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Report


class ReportCreateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['summary', 'strengths', 'weaknesses', 'homework', 'next_steps']
        widgets = {
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'homework': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'summary': _('Lesson summary'),
            'strengths': _('Strengths'),
            'weaknesses': _('Weaknesses'),
            'homework': _('Homework'),
            'next_steps': _('Next steps'),
        }
