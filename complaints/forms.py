from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Complaint


class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['against_user', 'category', 'description']
        widgets = {
            'against_user': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'against_user': _('Complaint against'),
            'category': _('Category'),
            'description': _('Description'),
        }

    def __init__(self, *args, booking, user, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        if booking.student_id != user.id:
            choices.append(booking.student)
        if booking.teacher.user_id != user.id:
            choices.append(booking.teacher.user)
        if booking.parent_id and booking.parent_id != user.id:
            choices.append(booking.parent)
        self.fields['against_user'].queryset = get_user_model().objects.filter(pk__in=[choice.pk for choice in choices])


class ComplaintStaffUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'status': _('Status'),
            'resolution_notes': _('Resolution notes'),
        }
