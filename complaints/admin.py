from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'created_by', 'against_user', 'category', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'category', 'created_at', 'resolved_at')
    search_fields = ('id', 'booking__id', 'created_by__email', 'against_user__email', 'description')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
