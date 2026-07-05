from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'teacher',
        'subject',
        'grade_level',
        'lesson_type',
        'scheduled_start',
        'booking_status',
        'booking_mode',
        'price',
    )
    list_filter = ('booking_status', 'booking_mode', 'lesson_type', 'subject', 'grade_level', 'scheduled_start')
    search_fields = (
        'student__email',
        'student__full_name',
        'teacher__user__email',
        'teacher__user__full_name',
        'subject__name',
    )
    readonly_fields = ('created_at', 'updated_at')
