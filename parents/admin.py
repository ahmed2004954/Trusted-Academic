from django.contrib import admin

from .models import ParentProfile, ParentStudentLink


class ParentStudentLinkInline(admin.TabularInline):
    model = ParentStudentLink
    extra = 0


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_contact_method', 'receive_email_reports', 'created_at')
    list_filter = ('preferred_contact_method', 'receive_email_reports')
    search_fields = ('user__email', 'user__full_name')
    inlines = [ParentStudentLinkInline]


@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'created_at')
    search_fields = ('parent__user__email', 'parent__user__full_name', 'student__email', 'student__full_name')
