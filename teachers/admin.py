from django.contrib import admin

from .models import AvailabilitySlot, PlatformPricingRange, TeacherCertificate, TeacherProfile, TeacherSubject


class TeacherCertificateInline(admin.TabularInline):
    model = TeacherCertificate
    extra = 0


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'approval_status', 'booking_mode', 'experience_years', 'average_rating', 'created_at')
    list_filter = ('approval_status', 'booking_mode', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'headline')
    inlines = [TeacherCertificateInline]


@admin.register(TeacherCertificate)
class TeacherCertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher_profile', 'issuing_organization', 'uploaded_at')
    search_fields = ('title', 'issuing_organization', 'teacher_profile__user__email')


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        'teacher_profile',
        'subject',
        'grade_level',
        'lesson_type',
        'price_min',
        'default_price',
        'price_max',
        'is_active',
    )
    list_filter = ('lesson_type', 'is_active', 'subject', 'grade_level')
    search_fields = ('teacher_profile__user__email', 'teacher_profile__user__full_name', 'subject__name')


@admin.register(PlatformPricingRange)
class PlatformPricingRangeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'grade_level', 'lesson_type', 'min_price', 'max_price', 'is_active')
    list_filter = ('lesson_type', 'is_active', 'subject', 'grade_level')
    search_fields = ('subject__name', 'grade_level__name')


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('teacher_profile', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('teacher_profile__user__email', 'teacher_profile__user__full_name')
