from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'student', 'teacher', 'rating', 'is_visible', 'created_at')
    list_filter = ('is_visible', 'rating', 'created_at')
    search_fields = ('student__email', 'student__full_name', 'teacher__user__email', 'teacher__user__full_name', 'comment')
    readonly_fields = ('created_at',)
