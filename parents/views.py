from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from reports.models import Report
from students.models import StudentProfile

from .forms import LinkStudentForm, ManagedStudentCreateForm
from .models import ParentProfile, ParentStudentLink


def parent_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'parent':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def get_parent_profile(user):
    profile, _ = ParentProfile.objects.get_or_create(user=user)
    return profile


@parent_required
def dashboard(request):
    profile = get_parent_profile(request.user)
    linked_students = profile.students.select_related('student_profile__grade_level')
    student_ids = linked_students.values_list('id', flat=True)
    recent_bookings = Booking.objects.filter(student_id__in=student_ids).select_related(
        'student', 'teacher__user', 'subject', 'grade_level'
    )[:5]
    recent_reports = Report.objects.filter(student_id__in=student_ids).select_related(
        'student', 'teacher__user', 'booking'
    )[:5]
    return render(
        request,
        'parents/dashboard.html',
        {'profile': profile, 'linked_students': linked_students, 'recent_bookings': recent_bookings, 'recent_reports': recent_reports},
    )


@parent_required
def create_student(request):
    profile = get_parent_profile(request.user)
    if request.method == 'POST':
        form = ManagedStudentCreateForm(request.POST)
        if form.is_valid():
            student = form.save()
            ParentStudentLink.objects.get_or_create(parent=profile, student=student)
            messages.success(request, _('Managed student account created and linked.'))
            return redirect('parents:dashboard')
    else:
        form = ManagedStudentCreateForm()
    return render(request, 'parents/create_student.html', {'form': form})


@parent_required
def link_student(request):
    profile = get_parent_profile(request.user)
    if request.method == 'POST':
        form = LinkStudentForm(request.POST)
        if form.is_valid():
            student_profile = StudentProfile.objects.filter(linking_code=form.cleaned_data['linking_code']).select_related('user').first()
            if not student_profile:
                form.add_error('linking_code', _('No student was found for this code.'))
            else:
                ParentStudentLink.objects.get_or_create(parent=profile, student=student_profile.user)
                messages.success(request, _('Student linked successfully.'))
                return redirect('parents:dashboard')
    else:
        form = LinkStudentForm()
    return render(request, 'parents/link_student.html', {'form': form})


@parent_required
def student_booking_history(request, student_pk):
    profile = get_parent_profile(request.user)
    student = get_object_or_404(profile.students.select_related('student_profile__grade_level'), pk=student_pk)
    bookings = Booking.objects.filter(student=student).select_related('teacher__user', 'subject', 'grade_level', 'report')
    return render(request, 'parents/student_booking_history.html', {'student': student, 'bookings': bookings})
