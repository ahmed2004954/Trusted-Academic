from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from subjects.models import GradeLevel, Subject

from .models import AvailabilitySlot, BookingMode, LessonType, PlatformPricingRange, TeacherCertificate, TeacherProfile, TeacherSubject


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ('headline', 'bio', 'experience_years', 'photo', 'cv_file', 'intro_video_url', 'booking_mode')
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'intro_video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'booking_mode': forms.Select(attrs={'class': 'form-control'}, choices=BookingMode.choices),
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


class TeacherSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherSubject
        fields = (
            'subject',
            'grade_level',
            'lesson_type',
            'price_min',
            'price_max',
            'default_price',
            'group_capacity',
            'is_active',
        )
        labels = {
            'subject': 'المادة الدراسية',
            'grade_level': 'الصف الدراسي',
            'lesson_type': 'نوع الدرس',
            'price_min': 'الحد الأدنى للسعر',
            'price_max': 'الحد الأقصى للسعر',
            'default_price': 'السعر الافتراضي',
            'group_capacity': 'السعة الاستيعابية للمجموعة',
            'is_active': 'نشط',
        }
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'grade_level': forms.Select(attrs={'class': 'form-control'}),
            'lesson_type': forms.Select(attrs={'class': 'form-control'}),
            'price_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'default_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'group_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active subjects and grade levels in the dropdowns
        self.fields['subject'].queryset = Subject.objects.filter(is_active=True).order_by('name')
        self.fields['grade_level'].queryset = GradeLevel.objects.filter(is_active=True).order_by('category', 'order', 'name')

    def clean(self) -> dict:
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        grade_level = cleaned_data.get('grade_level')
        lesson_type = cleaned_data.get('lesson_type')
        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')
        default_price = cleaned_data.get('default_price')
        group_capacity = cleaned_data.get('group_capacity')

        if lesson_type == LessonType.ONE_TO_ONE and group_capacity is not None:
            self.add_error('group_capacity', _('Group capacity is only available for group lessons.'))

        if lesson_type == LessonType.GROUP and not group_capacity:
            self.add_error('group_capacity', _('Group capacity is required for group lessons.'))

        if group_capacity and group_capacity > settings.PLATFORM_MAX_GROUP_SIZE:
            self.add_error(
                'group_capacity',
                _('Group capacity cannot exceed %(max_size)s students.') % {'max_size': settings.PLATFORM_MAX_GROUP_SIZE},
            )

        if price_min is not None and price_max is not None and price_min > price_max:
            self.add_error('price_max', _('Maximum price must be greater than or equal to minimum price.'))

        if (
            price_min is not None
            and price_max is not None
            and default_price is not None
            and not price_min <= default_price <= price_max
        ):
            self.add_error('default_price', _('Default price must be between the teacher minimum and maximum price.'))

        if subject and grade_level and lesson_type and price_min is not None and price_max is not None:
            pricing_range = PlatformPricingRange.objects.filter(
                subject=subject,
                grade_level=grade_level,
                lesson_type=lesson_type,
                is_active=True,
            ).first()
            if not pricing_range:
                raise ValidationError(_('No active platform pricing range is configured for this subject and grade.'))
            if price_min < pricing_range.min_price or price_min > pricing_range.max_price:
                self.add_error(
                    'price_min',
                    _('Minimum price must be between %(min_price)s and %(max_price)s.') % {
                        'min_price': pricing_range.min_price,
                        'max_price': pricing_range.max_price,
                    },
                )
            if price_max < pricing_range.min_price or price_max > pricing_range.max_price:
                self.add_error(
                    'price_max',
                    _('Maximum price must be between %(min_price)s and %(max_price)s.') % {
                        'min_price': pricing_range.min_price,
                        'max_price': pricing_range.max_price,
                    },
                )
        return cleaned_data


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ('day_of_week', 'start_time', 'end_time', 'is_active')
        labels = {
            'day_of_week': 'اليوم',
            'start_time': 'وقت البدء',
            'end_time': 'وقت الانتهاء',
            'is_active': 'نشط',
        }
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
