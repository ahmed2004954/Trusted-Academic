from django.contrib import admin

from .models import Booking, TeacherBookingViolation


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
        'attendance_confirmed_at',
        'wallet_settled_at',
        'cancelled_at',
        'reschedule_count',
    )
    list_filter = ('booking_status', 'booking_mode', 'lesson_type', 'subject', 'grade_level', 'scheduled_start')
    search_fields = (
        'student__email',
        'student__full_name',
        'teacher__user__email',
        'teacher__user__full_name',
        'subject__name',
    )
    readonly_fields = ('created_at', 'updated_at', 'attendance_code', 'attendance_confirmed_at', 'wallet_settled_at')


@admin.register(TeacherBookingViolation)
class TeacherBookingViolationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'booking', 'violation_type', 'created_at')
    list_filter = ('violation_type', 'created_at')
    search_fields = ('teacher__user__email', 'teacher__user__full_name', 'booking__student__email', 'reason')
    readonly_fields = ('created_at',)
