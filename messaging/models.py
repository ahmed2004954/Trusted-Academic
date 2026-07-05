from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class MessageThread(models.Model):
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='message_thread',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        if self.booking_id:
            return f'Thread for booking #{self.booking_id}'
        return f'Thread #{self.pk}'

    @staticmethod
    def booking_participant_ids(booking) -> set[int]:
        participant_ids = {booking.student_id, booking.teacher.user_id}
        if booking.parent_id:
            participant_ids.add(booking.parent_id)

        linked_parent_ids = booking.student.parent_links.values_list('parent__user_id', flat=True)
        participant_ids.update(linked_parent_ids)
        return {participant_id for participant_id in participant_ids if participant_id}

    @classmethod
    def get_or_create_for_booking(cls, booking):
        thread, _ = cls.objects.get_or_create(booking=booking)
        thread.sync_booking_participants()
        return thread

    def sync_booking_participants(self) -> None:
        if not self.booking_id:
            return

        for user_id in self.booking_participant_ids(self.booking):
            MessageThreadParticipant.objects.get_or_create(thread=self, user_id=user_id)

    def user_can_access(self, user) -> bool:
        if not user.is_authenticated:
            return False
        if self.booking_id and user.id in self.booking_participant_ids(self.booking):
            MessageThreadParticipant.objects.get_or_create(thread=self, user=user)
            return True
        return self.participants.filter(user=user).exists()


class MessageThreadParticipant(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_threads')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['thread', 'user'], name='unique_message_thread_participant'),
        ]

    def __str__(self) -> str:
        return f'{self.user} in {self.thread}'


class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='message_attachments/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['sender', 'is_read']),
        ]

    def __str__(self) -> str:
        return f'Message #{self.pk} from {self.sender}'

    def clean(self) -> None:
        super().clean()
        if not self.body and not self.attachment:
            raise ValidationError(_('Enter a message or attach a file.'))
        if self.thread_id and self.sender_id and not self.thread.user_can_access(self.sender):
            raise ValidationError({'sender': _('Sender must be a thread participant.')})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
        self.thread.save(update_fields=['updated_at'])
