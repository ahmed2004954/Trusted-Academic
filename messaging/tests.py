from django.test import TestCase
from django.urls import reverse

from core.test_helpers import create_student, create_test_booking
from messaging.models import Message, MessageThread


class InboxViewTests(TestCase):
    def test_inbox_requires_login(self):
        response = self.client.get(reverse('messaging:inbox'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_student_can_view_inbox(self):
        student = create_student(email='inbox-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('messaging:inbox'))

        self.assertEqual(response.status_code, 200)


class BookingThreadTests(TestCase):
    def test_booking_participant_gets_thread(self):
        booking = create_test_booking()
        self.client.force_login(booking.student)

        response = self.client.get(reverse('messaging:booking_thread', args=[booking.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(MessageThread.objects.filter(booking=booking).exists())

    def test_non_participant_cannot_open_booking_thread(self):
        booking = create_test_booking()
        intruder = create_student(email='msg-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('messaging:booking_thread', args=[booking.pk]))

        self.assertEqual(response.status_code, 403)


class ThreadMessageTests(TestCase):
    def test_participant_can_post_message(self):
        booking = create_test_booking()
        thread = MessageThread.get_or_create_for_booking(booking)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('messaging:thread_detail', args=[thread.pk]),
            {'body': 'Hello teacher'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Message.objects.filter(thread=thread, sender=booking.student, body='Hello teacher').exists()
        )

    def test_empty_message_is_rejected(self):
        booking = create_test_booking()
        thread = MessageThread.get_or_create_for_booking(booking)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('messaging:thread_detail', args=[thread.pk]),
            {'body': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Message.objects.filter(thread=thread).exists())

    def test_non_participant_cannot_view_thread(self):
        booking = create_test_booking()
        thread = MessageThread.get_or_create_for_booking(booking)
        intruder = create_student(email='thread-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('messaging:thread_detail', args=[thread.pk]))

        self.assertEqual(response.status_code, 403)
