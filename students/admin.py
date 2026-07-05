from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_level', 'school_name', 'created_by_parent', 'linking_code', 'created_at')
    list_filter = ('created_by_parent', 'grade_level')
    search_fields = ('user__email', 'user__full_name', 'school_name', 'linking_code')
