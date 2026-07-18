from django.test import TestCase
from django.urls import reverse

from bookings.models import Booking
from core.test_helpers import create_student, create_test_booking
from reviews.models import Review


class CreateReviewTests(TestCase):
    def test_student_reviews_completed_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('reviews:create', args=[booking.pk]),
            {'rating': 5, 'comment': 'Excellent lesson'},
        )

        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(booking=booking)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.teacher, booking.teacher)

    def test_review_recalculates_teacher_rating(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        self.client.force_login(booking.student)

        self.client.post(
            reverse('reviews:create', args=[booking.pk]),
            {'rating': 4, 'comment': 'Good'},
        )

        teacher = booking.teacher
        teacher.refresh_from_db()
        self.assertEqual(teacher.total_reviews, 1)
        self.assertEqual(teacher.average_rating, 4)

    def test_cannot_review_incomplete_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.CONFIRMED)
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('reviews:create', args=[booking.pk]),
            {'rating': 5, 'comment': 'Too early'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(booking=booking).exists())

    def test_cannot_review_booking_twice(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        Review.objects.create(
            booking=booking,
            student=booking.student,
            teacher=booking.teacher,
            rating=5,
            comment='First',
        )
        self.client.force_login(booking.student)

        response = self.client.post(
            reverse('reviews:create', args=[booking.pk]),
            {'rating': 1, 'comment': 'Second'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(booking=booking).count(), 1)

    def test_non_student_cannot_create_review(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        self.client.force_login(booking.teacher.user)

        response = self.client.get(reverse('reviews:create', args=[booking.pk]))

        self.assertEqual(response.status_code, 403)

    def test_student_cannot_review_someone_elses_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.COMPLETED)
        intruder = create_student(email='review-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('reviews:create', args=[booking.pk]))

        self.assertEqual(response.status_code, 404)
