from django.test import TestCase
from django.urls import reverse

from bookings.models import Booking
from core.test_helpers import create_parent, create_student, create_teacher, create_test_booking
from reports.models import Report


class CreateReportTests(TestCase):
    def test_teacher_creates_report_for_completed_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        self.client.force_login(booking.teacher.user)

        response = self.client.post(
            reverse('reports:create', args=[booking.pk]),
            {
                'summary': 'Covered algebra basics.',
                'strengths': 'Quick learner',
                'weaknesses': 'Needs practice',
                'homework': 'Chapter 3 exercises',
                'next_steps': 'Review fractions',
            },
        )

        self.assertEqual(response.status_code, 302)
        report = Report.objects.get(booking=booking)
        self.assertEqual(report.teacher, booking.teacher)
        self.assertEqual(report.student, booking.student)

    def test_non_teacher_cannot_create_report(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        self.client.force_login(booking.student)

        response = self.client.get(reverse('reports:create', args=[booking.pk]))

        self.assertEqual(response.status_code, 403)

    def test_cannot_report_incomplete_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        self.client.force_login(booking.teacher.user)

        response = self.client.get(reverse('reports:create', args=[booking.pk]))

        self.assertEqual(response.status_code, 404)


class ReportDetailAccessTests(TestCase):
    def _make_report(self, booking):
        return Report.objects.create(
            booking=booking,
            teacher=booking.teacher,
            student=booking.student,
            summary='Summary text',
        )

    def test_student_can_view_own_report(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        report = self._make_report(booking)
        self.client.force_login(booking.student)

        response = self.client.get(reverse('reports:detail', args=[report.pk]))

        self.assertEqual(response.status_code, 200)

    def test_teacher_can_view_own_report(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        report = self._make_report(booking)
        self.client.force_login(booking.teacher.user)

        response = self.client.get(reverse('reports:detail', args=[report.pk]))

        self.assertEqual(response.status_code, 200)

    def test_unrelated_student_cannot_view_report(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        report = self._make_report(booking)
        intruder = create_student(email='report-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('reports:detail', args=[report.pk]))

        self.assertEqual(response.status_code, 403)

    def test_report_detail_requires_login(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        report = self._make_report(booking)

        response = self.client.get(reverse('reports:detail', args=[report.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
