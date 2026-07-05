from django.contrib import admin

from .models import Message, MessageThread, MessageThreadParticipant


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)


class MessageThreadParticipantInline(admin.TabularInline):
    model = MessageThreadParticipant
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'created_at', 'updated_at')
    search_fields = ('booking__student__email', 'booking__teacher__user__email')
    list_select_related = ('booking',)
    inlines = [MessageThreadParticipantInline, MessageInline]


@admin.register(MessageThreadParticipant)
class MessageThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'created_at')
    search_fields = ('user__email', 'user__full_name')
    list_select_related = ('thread', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('thread', 'sender', 'created_at', 'is_read', 'has_attachment')
    list_filter = ('is_read', 'created_at')
    search_fields = ('body', 'sender__email', 'sender__full_name')
    list_select_related = ('thread', 'sender')
    readonly_fields = ('created_at',)

    @admin.display(boolean=True, description='Attachment')
    def has_attachment(self, obj):
        return bool(obj.attachment)
