from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from parents.models import ParentStudentLink
from teachers.models import TeacherProfile

from .forms import ReportCreateForm
from .models import Report


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@teacher_required
def create_report(request, booking_pk):
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=booking_pk,
        teacher=teacher,
        booking_status=Booking.BookingStatus.COMPLETED,
    )
    if hasattr(booking, 'report'):
        messages.info(request, _('يوجد تقرير بالفعل لهذا الحجز.'))
        return redirect('reports:detail', pk=booking.report.pk)

    if request.method == 'POST':
        form = ReportCreateForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.booking = booking
            report.teacher = teacher
            report.student = booking.student
            report.save()
            report.sent_to_parent_email = send_report_email(report)
            report.save(update_fields=['sent_to_parent_email'])
            messages.success(request, _('تم إنشاء تقرير ما بعد الحصة بنجاح.'))
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportCreateForm()
    return render(request, 'reports/create.html', {'form': form, 'booking': booking})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related('booking__subject', 'booking__grade_level', 'teacher__user', 'student'),
        pk=pk,
    )
    if not user_can_view_report(request.user, report):
        raise PermissionDenied
    return render(request, 'reports/detail.html', {'report': report})


def user_can_view_report(user, report):
    if user.role == 'student':
        return report.student_id == user.id
    if user.role == 'teacher':
        return report.teacher.user_id == user.id
    if user.role == 'parent':
        return ParentStudentLink.objects.filter(parent__user=user, student=report.student).exists()
    return user.is_staff


def send_report_email(report):
    links = ParentStudentLink.objects.filter(
        student=report.student,
        parent__receive_email_reports=True,
    ).select_related('parent__user')
    recipients = [link.parent.user.email for link in links if link.parent.user.email]
    if not recipients:
        return False

    send_mail(
        _('New lesson report available'),
        _('A new lesson report for %(student)s is available in your parent dashboard.') % {
            'student': report.student.get_full_name(),
        },
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )
    return True
