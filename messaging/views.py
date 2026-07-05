from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking

from .forms import MessageForm
from .models import Message, MessageThread


def unread_count_for_user(user) -> int:
    if not user.is_authenticated:
        return 0
    return Message.objects.filter(thread__participants__user=user, is_read=False).exclude(sender=user).count()


def user_can_message_booking(user, booking) -> bool:
    return user.is_authenticated and user.id in MessageThread.booking_participant_ids(booking)


def notify_other_participants(message) -> None:
    recipients = list(
        message.thread.participants.exclude(user=message.sender)
        .exclude(user__email='')
        .values_list('user__email', flat=True)
    )
    if not recipients:
        return

    send_mail(
        _('New message on Tutors Marketplace'),
        _('You have a new message from %(sender)s.') % {'sender': message.sender.get_full_name() or message.sender.email},
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )


@login_required
def inbox(request):
    threads = (
        MessageThread.objects.filter(participants__user=request.user)
        .select_related('booking__student', 'booking__teacher__user', 'booking__subject', 'booking__grade_level')
        .prefetch_related('participants__user')
        .annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)),
        )
        .order_by('-updated_at')
    )
    return render(request, 'messaging/inbox.html', {'threads': threads})


@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(
        MessageThread.objects.select_related(
            'booking__student',
            'booking__teacher__user',
            'booking__subject',
            'booking__grade_level',
        ).prefetch_related('participants__user'),
        pk=pk,
    )
    if not thread.user_can_access(request.user):
        raise PermissionDenied

    Message.objects.filter(thread=thread, is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            notify_other_participants(message)
            messages.success(request, _('Message sent.'))
            return redirect('messaging:thread_detail', pk=thread.pk)
    else:
        form = MessageForm()

    thread_messages = thread.messages.select_related('sender')
    return render(request, 'messaging/thread_detail.html', {'thread': thread, 'thread_messages': thread_messages, 'form': form})


@login_required
def booking_thread(request, booking_pk):
    booking = get_object_or_404(Booking.objects.select_related('student', 'teacher__user'), pk=booking_pk)
    if not user_can_message_booking(request.user, booking):
        raise PermissionDenied

    thread = MessageThread.get_or_create_for_booking(booking)
    return redirect('messaging:thread_detail', pk=thread.pk)
