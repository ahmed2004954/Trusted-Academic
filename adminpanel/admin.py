from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'actor', 'action', 'target_label')
    list_filter = ('action', 'created_at')
    search_fields = ('actor__email', 'actor__full_name', 'action', 'target_label')
    readonly_fields = ('actor', 'action', 'target_label', 'target_url', 'metadata', 'created_at')
