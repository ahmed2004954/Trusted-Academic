from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('booking', 'teacher', 'student', 'sent_to_parent_email', 'created_at')
    list_filter = ('sent_to_parent_email', 'created_at')
    search_fields = ('student__email', 'student__full_name', 'teacher__user__email', 'summary')
