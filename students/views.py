from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .models import StudentProfile


from django.utils import timezone
from datetime import datetime, time
from bookings.models import Booking
from reports.models import Report


@login_required
def dashboard(request):
    if request.user.role != 'student':
        raise PermissionDenied
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    
    # Get all student bookings
    bookings = Booking.objects.filter(student=request.user)
    
    # Upcoming bookings (not cancelled/rejected, scheduled for today or future)
    now = timezone.now()
    upcoming_lessons = bookings.filter(
        scheduled_start__gte=now
    ).exclude(
        booking_status__in=[
            Booking.BookingStatus.CANCELLED_BY_STUDENT,
            Booking.BookingStatus.CANCELLED_BY_TEACHER,
            Booking.BookingStatus.TEACHER_REJECTED
        ]
    ).select_related('teacher__user', 'subject', 'grade_level').order_by('scheduled_start')[:5]
    
    # Today's date range
    today_start = timezone.make_aware(datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(datetime.combine(now.date(), time.max))
    
    today_lessons_count = bookings.filter(
        scheduled_start__range=(today_start, today_end)
    ).exclude(
        booking_status__in=[
            Booking.BookingStatus.CANCELLED_BY_STUDENT,
            Booking.BookingStatus.CANCELLED_BY_TEACHER,
            Booking.BookingStatus.TEACHER_REJECTED
        ]
    ).count()
    
    # Tasks = payments that need verification or payment from student
    pending_tasks_count = bookings.filter(
        booking_status__in=[
            Booking.BookingStatus.PENDING_PAYMENT,
            Booking.BookingStatus.AWAITING_STUDENT_PAYMENT
        ]
    ).count()
    
    # Academic reports
    recent_reports = Report.objects.filter(student=request.user).select_related('teacher__user', 'booking__subject').order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'upcoming_lessons': upcoming_lessons,
        'today_lessons_count': today_lessons_count,
        'pending_tasks_count': pending_tasks_count,
        'recent_reports': recent_reports,
    }
    return render(request, 'students/dashboard.html', context)



@login_required
def linking_code(request):
    if request.user.role != 'student':
        raise PermissionDenied
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.linking_code = ''
        profile.generate_linking_code()
        messages.success(request, _('Linking code generated.'))
        return redirect('students:linking_code')
    if not profile.linking_code:
        profile.generate_linking_code()
    return render(request, 'students/linking_code.html', {'profile': profile})
