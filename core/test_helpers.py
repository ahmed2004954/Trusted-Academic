from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from bookings.models import Booking
from bookings.services import create_booking
from parents.models import ParentProfile, ParentStudentLink
from payments.models import Payment
from subjects.models import GradeLevel, Subject
from teachers.models import BookingMode, LessonType, PlatformPricingRange, TeacherProfile, TeacherSubject


PASSWORD = 'DemoPass123!'


def create_user(email, role='student', full_name='Test User', **extra_fields):
    return get_user_model().objects.create_user(
        email=email,
        full_name=full_name,
        password=PASSWORD,
        role=role,
        **extra_fields,
    )


def create_subject_setup(subject_name='رياضيات', grade_name='أولى ثانوي'):
    subject, _ = Subject.objects.get_or_create(name=subject_name)
    grade, _ = GradeLevel.objects.get_or_create(
        name=grade_name,
        defaults={'category': GradeLevel.Category.SECONDARY, 'order': 10},
    )
    PlatformPricingRange.objects.get_or_create(
        subject=subject,
        grade_level=grade,
        lesson_type=LessonType.ONE_TO_ONE,
        defaults={'min_price': Decimal('100.00'), 'max_price': Decimal('300.00')},
    )
    return subject, grade


def create_teacher(email='teacher@example.com', approved=True, booking_mode=BookingMode.AUTOMATIC, full_name='Demo Teacher'):
    teacher_user = create_user(email, role='teacher', full_name=full_name)
    return TeacherProfile.objects.create(
        user=teacher_user,
        headline='Math specialist',
        bio='Experienced teacher',
        experience_years=5,
        approval_status=TeacherProfile.ApprovalStatus.APPROVED if approved else TeacherProfile.ApprovalStatus.PENDING,
        booking_mode=booking_mode,
    )


def create_offering(teacher=None, default_price=Decimal('200.00')):
    subject, grade = create_subject_setup()
    teacher = teacher or create_teacher()
    return TeacherSubject.objects.create(
        teacher_profile=teacher,
        subject=subject,
        grade_level=grade,
        lesson_type=LessonType.ONE_TO_ONE,
        price_min=Decimal('150.00'),
        price_max=Decimal('250.00'),
        default_price=default_price,
        is_active=True,
    )


def create_student(email='student@example.com'):
    return create_user(email, role='student', full_name='Demo Student')


def create_parent(email='parent@example.com', student=None):
    parent_user = create_user(email, role='parent', full_name='Demo Parent')
    profile = ParentProfile.objects.create(user=parent_user)
    if student:
        ParentStudentLink.objects.create(parent=profile, student=student)
    return parent_user


def create_test_booking(student=None, offering=None, scheduled_start=None, parent=None, status=None):
    student = student or create_student()
    offering = offering or create_offering()
    scheduled_start = scheduled_start or timezone.now() + timedelta(days=1)
    booking = create_booking(
        student=student,
        teacher_subject=offering,
        scheduled_start=scheduled_start,
        duration_minutes=60,
        parent=parent,
    )
    if status:
        booking.booking_status = status
        booking.save(update_fields=['booking_status', 'updated_at'])
    return booking


def create_payment(booking, status=Payment.PaymentStatus.AWAITING_VERIFICATION):
    return Payment.objects.create(
        booking=booking,
        amount=booking.price,
        currency='EGP',
        payment_method=Payment.PaymentMethod.VODAFONE_CASH,
        payment_status=status,
    )
