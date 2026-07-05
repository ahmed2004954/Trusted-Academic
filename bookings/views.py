from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from parents.models import ParentStudentLink
from teachers.models import TeacherProfile, TeacherSubject
from complaints.models import Complaint
from complaints.services import user_can_create_complaint, visible_complaint_filter

from .forms import BookingCancellationForm, BookingCreateForm, BookingRescheduleForm
from .models import Booking
from .services import (
    cancel_booking_by_student,
    cancel_booking_by_teacher,
    estimate_student_refund,
    reschedule_booking_by_student,
    reschedule_booking_by_teacher,
)


def student_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'student':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def parent_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'parent':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@student_required
def booking_create(request, teacher_pk):
    teacher = get_object_or_404(
        TeacherProfile.objects.select_related('user').prefetch_related('subjects__subject', 'subjects__grade_level'),
        pk=teacher_pk,
    )
    if not teacher.can_receive_bookings:
        raise PermissionDenied

    initial_offering = None
    offering_id = request.GET.get('offering')
    if offering_id and offering_id.isdigit():
        initial_offering = TeacherSubject.objects.filter(pk=offering_id, teacher_profile=teacher, is_active=True).first()

    if request.method == 'POST':
        form = BookingCreateForm(request.POST, teacher=teacher, student=request.user)
        if form.is_valid():
            try:
                booking = form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking request created successfully.'))
                return redirect('bookings:student_detail', pk=booking.pk)
    else:
        form = BookingCreateForm(teacher=teacher, student=request.user, initial_offering=initial_offering)

    return render(request, 'bookings/create.html', {'form': form, 'teacher': teacher})


@parent_required
def parent_booking_create(request, teacher_pk, student_pk):
    link = get_object_or_404(ParentStudentLink.objects.select_related('student'), parent__user=request.user, student_id=student_pk)
    teacher = get_object_or_404(
        TeacherProfile.objects.select_related('user').prefetch_related('subjects__subject', 'subjects__grade_level'),
        pk=teacher_pk,
    )
    if not teacher.can_receive_bookings:
        raise PermissionDenied

    initial_offering = None
    offering_id = request.GET.get('offering')
    if offering_id and offering_id.isdigit():
        initial_offering = TeacherSubject.objects.filter(pk=offering_id, teacher_profile=teacher, is_active=True).first()

    if request.method == 'POST':
        form = BookingCreateForm(request.POST, teacher=teacher, student=link.student, parent=request.user)
        if form.is_valid():
            try:
                booking = form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking request created for linked student.'))
                return redirect('parents:student_booking_history', student_pk=link.student_id)
    else:
        form = BookingCreateForm(teacher=teacher, student=link.student, parent=request.user, initial_offering=initial_offering)

    return render(request, 'bookings/create.html', {'form': form, 'teacher': teacher, 'parent_student': link.student})


@student_required
def student_booking_list(request):
    bookings = Booking.objects.filter(student=request.user).select_related(
        'teacher__user', 'subject', 'grade_level', 'teacher_subject'
    )
    return render(request, 'bookings/student_list.html', {'bookings': bookings})


@student_required
def student_booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('teacher__user', 'subject', 'grade_level', 'teacher_subject'),
        pk=pk,
        student=request.user,
    )
    complaints = Complaint.objects.filter(visible_complaint_filter(request.user), booking=booking).distinct()
    return render(
        request,
        'bookings/detail.html',
        {
            'booking': booking,
            'is_teacher_view': False,
            'can_create_complaint': user_can_create_complaint(request.user, booking),
            'complaints': complaints,
        },
    )


@teacher_required
def teacher_booking_list(request):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    bookings = Booking.objects.filter(teacher=profile).select_related('student', 'subject', 'grade_level', 'teacher_subject')
    return render(request, 'bookings/teacher_list.html', {'bookings': bookings, 'profile': profile})


@teacher_required
def teacher_booking_detail(request, pk):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'subject', 'grade_level', 'teacher_subject'),
        pk=pk,
        teacher=profile,
    )
    complaints = Complaint.objects.filter(visible_complaint_filter(request.user), booking=booking).distinct()
    return render(
        request,
        'bookings/detail.html',
        {
            'booking': booking,
            'is_teacher_view': True,
            'can_create_complaint': user_can_create_complaint(request.user, booking),
            'complaints': complaints,
        },
    )


@teacher_required
def teacher_attendance_code(request, pk):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'subject', 'grade_level', 'teacher__user'),
        pk=pk,
        teacher=profile,
    )
    if not booking.can_use_attendance_code():
        messages.error(request, _('Attendance code is available only during the lesson attendance window.'))
        return redirect('bookings:teacher_detail', pk=booking.pk)
    return render(request, 'bookings/teacher_attendance_code.html', {'booking': booking})


@student_required
def student_confirm_attendance(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('teacher__user', 'subject', 'grade_level'),
        pk=pk,
        student=request.user,
    )
    if request.method == 'POST':
        code = request.POST.get('attendance_code', '')
        try:
            booking.complete_with_attendance(code)
        except ValidationError as exc:
            messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
        else:
            messages.success(request, _('Attendance confirmed and lesson completed.'))
            return redirect('bookings:student_detail', pk=booking.pk)
    elif not booking.can_use_attendance_code():
        messages.error(request, _('Attendance can only be confirmed during the lesson attendance window.'))
        return redirect('bookings:student_detail', pk=booking.pk)
    return render(request, 'bookings/student_confirm_attendance.html', {'booking': booking})


@student_required
def student_cancel_booking(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=pk,
        student=request.user,
    )
    refund_estimate = estimate_student_refund(booking)
    if request.method == 'POST':
        form = BookingCancellationForm(request.POST)
        if form.is_valid():
            try:
                cancel_booking_by_student(booking.pk, form.cleaned_data['reason'])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking cancelled. Refund amount has been recorded.'))
                return redirect('bookings:student_detail', pk=booking.pk)
    else:
        form = BookingCancellationForm()
    return render(
        request,
        'bookings/cancel.html',
        {'booking': booking, 'form': form, 'refund_estimate': refund_estimate, 'is_teacher_view': False},
    )


@student_required
def student_reschedule_booking(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=pk,
        student=request.user,
    )
    if request.method == 'POST':
        form = BookingRescheduleForm(request.POST)
        if form.is_valid():
            try:
                reschedule_booking_by_student(booking.pk, form.cleaned_data['scheduled_start'], form.cleaned_data['reason'])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking rescheduled.'))
                return redirect('bookings:student_detail', pk=booking.pk)
    else:
        form = BookingRescheduleForm()
    return render(request, 'bookings/reschedule.html', {'booking': booking, 'form': form, 'is_teacher_view': False})


@teacher_required
def teacher_cancel_booking(request, pk):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=pk,
        teacher=profile,
    )
    if request.method == 'POST':
        form = BookingCancellationForm(request.POST)
        if form.is_valid():
            try:
                cancel_booking_by_teacher(booking.pk, form.cleaned_data['reason'])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking cancelled and teacher violation recorded.'))
                return redirect('bookings:teacher_detail', pk=booking.pk)
    else:
        form = BookingCancellationForm()
    return render(
        request,
        'bookings/cancel.html',
        {'booking': booking, 'form': form, 'refund_estimate': booking.price, 'is_teacher_view': True},
    )


@teacher_required
def teacher_reschedule_booking(request, pk):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=pk,
        teacher=profile,
    )
    if request.method == 'POST':
        form = BookingRescheduleForm(request.POST)
        if form.is_valid():
            try:
                reschedule_booking_by_teacher(booking.pk, form.cleaned_data['scheduled_start'], form.cleaned_data['reason'])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('Booking rescheduled and teacher violation recorded.'))
                return redirect('bookings:teacher_detail', pk=booking.pk)
    else:
        form = BookingRescheduleForm()
    return render(request, 'bookings/reschedule.html', {'booking': booking, 'form': form, 'is_teacher_view': True})


@teacher_required
def teacher_booking_action(request, pk, action):
    if request.method != 'POST':
        raise PermissionDenied
    profile = get_object_or_404(TeacherProfile, user=request.user)
    booking = get_object_or_404(Booking, pk=pk, teacher=profile)
    try:
        if action == 'accept':
            booking.accept_by_teacher()
            messages.success(request, _('Booking request accepted.'))
        elif action == 'reject':
            booking.reject_by_teacher(request.POST.get('reason', '').strip())
            messages.success(request, _('Booking request rejected.'))
        else:
            raise PermissionDenied
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
    return redirect('bookings:teacher_detail', pk=booking.pk)
