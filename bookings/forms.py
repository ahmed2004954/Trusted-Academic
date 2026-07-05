from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from teachers.models import TeacherSubject

from .models import Booking
from .services import create_booking


class BookingCreateForm(forms.Form):
    teacher_subject = forms.ModelChoiceField(
        queryset=TeacherSubject.objects.none(),
        label=_('Offering'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    scheduled_start = forms.DateTimeField(
        label=_('Start time'),
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    )
    duration_minutes = forms.ChoiceField(
        choices=Booking.DurationMinutes.choices,
        label=_('Duration'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, teacher=None, student=None, parent=None, initial_offering=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        self.student = student
        self.parent = parent
        offerings = TeacherSubject.objects.filter(is_active=True).select_related('subject', 'grade_level', 'teacher_profile')
        if teacher:
            offerings = offerings.filter(teacher_profile=teacher)
        self.fields['teacher_subject'].queryset = offerings
        if initial_offering:
            self.fields['teacher_subject'].initial = initial_offering

    def clean_duration_minutes(self) -> int:
        return int(self.cleaned_data['duration_minutes'])

    def clean_scheduled_start(self):
        scheduled_start = self.cleaned_data['scheduled_start']
        if scheduled_start <= timezone.now():
            raise ValidationError(_('Booking start time must be in the future.'))
        return scheduled_start

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if self.student and self.student.role != 'student':
            raise ValidationError(_('Only student accounts can create bookings for now.'))
        return cleaned_data

    def save(self) -> Booking:
        return create_booking(
            student=self.student,
            teacher_subject=self.cleaned_data['teacher_subject'],
            scheduled_start=self.cleaned_data['scheduled_start'],
            duration_minutes=self.cleaned_data['duration_minutes'],
            parent=self.parent,
        )


class BookingCancellationForm(forms.Form):
    reason = forms.CharField(
        label=_('Reason'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class BookingRescheduleForm(forms.Form):
    scheduled_start = forms.DateTimeField(
        label=_('New start time'),
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    )
    reason = forms.CharField(
        label=_('Reason'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )

    def clean_scheduled_start(self):
        scheduled_start = self.cleaned_data['scheduled_start']
        if scheduled_start <= timezone.now():
            raise ValidationError(_('New lesson start time must be in the future.'))
        return scheduled_start
