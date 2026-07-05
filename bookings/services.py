from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from teachers.models import BookingMode, TeacherSubject

from .models import Booking


def calculate_booking_amounts(teacher_subject: TeacherSubject) -> tuple[Decimal, Decimal, Decimal]:
    price = teacher_subject.default_price
    commission_percentage = Decimal(str(settings.PLATFORM_COMMISSION_PERCENTAGE))
    platform_fee = (price * commission_percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    teacher_payout = (price - platform_fee).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return price, platform_fee, teacher_payout


@transaction.atomic
def create_booking(*, student, teacher_subject: TeacherSubject, scheduled_start, duration_minutes: int) -> Booking:
    teacher = teacher_subject.teacher_profile
    if not teacher.can_receive_bookings:
        raise ValidationError({'teacher': 'This teacher cannot receive bookings yet.'})
    if not teacher_subject.is_active:
        raise ValidationError({'teacher_subject': 'The selected offering is not active.'})

    price, platform_fee, teacher_payout = calculate_booking_amounts(teacher_subject)
    booking_mode = teacher.booking_mode
    booking_status = (
        Booking.BookingStatus.PENDING_TEACHER_ACCEPTANCE
        if booking_mode == BookingMode.MANUAL
        else Booking.BookingStatus.PENDING_PAYMENT
    )
    booking = Booking(
        student=student,
        teacher=teacher,
        subject=teacher_subject.subject,
        grade_level=teacher_subject.grade_level,
        teacher_subject=teacher_subject,
        lesson_type=teacher_subject.lesson_type,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_start + timedelta(minutes=duration_minutes),
        duration_minutes=duration_minutes,
        price=price,
        platform_fee=platform_fee,
        teacher_payout=teacher_payout,
        booking_status=booking_status,
        booking_mode=booking_mode,
    )
    booking.save()
    return booking
