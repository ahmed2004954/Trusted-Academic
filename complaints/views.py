from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from adminpanel.models import record_audit_log

from .forms import ComplaintCreateForm, ComplaintStaffUpdateForm
from .models import Complaint
from .services import mark_booking_disputed_if_needed, user_can_create_complaint, user_can_view_complaint, visible_complaint_filter


def get_visible_complaints(user):
    complaints = Complaint.objects.select_related(
        'booking__student',
        'booking__teacher__user',
        'booking__subject',
        'booking__grade_level',
        'created_by',
        'against_user',
        'resolved_by',
    )
    if user.is_staff:
        return complaints
    return complaints.filter(visible_complaint_filter(user)).distinct()


def send_complaint_created_email(complaint: Complaint) -> None:
    recipients = complaint_recipients(complaint)
    if recipients:
        send_mail(
            _('New complaint opened'),
            _(
                'Complaint #%(complaint_id)s was opened for booking #%(booking_id)s.\n\n'
                'Status: %(status)s\nCategory: %(category)s'
            ) % {
                'complaint_id': complaint.pk,
                'booking_id': complaint.booking_id,
                'status': complaint.get_status_display(),
                'category': complaint.get_category_display(),
            },
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )


def send_complaint_status_email(complaint: Complaint) -> None:
    recipients = complaint_recipients(complaint)
    if recipients:
        send_mail(
            _('Complaint status updated'),
            _(
                'Complaint #%(complaint_id)s is now %(status)s.\n\nResolution notes: %(notes)s'
            ) % {
                'complaint_id': complaint.pk,
                'status': complaint.get_status_display(),
                'notes': complaint.resolution_notes or '-',
            },
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )


def complaint_recipients(complaint: Complaint) -> list[str]:
    users = [complaint.created_by, complaint.against_user]
    if complaint.booking.parent_id:
        users.append(complaint.booking.parent)
    emails = {user.email for user in users if user and user.email}
    return list(emails)


@login_required
def complaint_list(request):
    complaints = get_visible_complaints(request.user)
    return render(request, 'complaints/list.html', {'complaints': complaints})


@login_required
def complaint_create(request, booking_pk):
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'parent', 'teacher__user', 'subject', 'grade_level'),
        pk=booking_pk,
    )
    if not user_can_create_complaint(request.user, booking):
        raise PermissionDenied

    if request.method == 'POST':
        form = ComplaintCreateForm(request.POST, booking=booking, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.booking = booking
            complaint.created_by = request.user
            try:
                with transaction.atomic():
                    complaint.save()
                    mark_booking_disputed_if_needed(booking)
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                send_complaint_created_email(complaint)
                messages.success(request, _('تم تقديم الشكوى بنجاح.'))
                return redirect('complaints:detail', pk=complaint.pk)
    else:
        form = ComplaintCreateForm(booking=booking, user=request.user)

    return render(request, 'complaints/create.html', {'form': form, 'booking': booking})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(get_visible_complaints(request.user), pk=pk)
    if not user_can_view_complaint(request.user, complaint):
        raise PermissionDenied
    return render(request, 'complaints/detail.html', {'complaint': complaint})


@staff_member_required
def staff_complaint_queue(request):
    complaints = get_visible_complaints(request.user)
    return render(request, 'complaints/staff_queue.html', {'complaints': complaints})


@staff_member_required
def staff_complaint_detail(request, pk):
    complaint = get_object_or_404(get_visible_complaints(request.user), pk=pk)
    if request.method == 'POST':
        old_status = complaint.status
        if request.POST.get('status') in {Complaint.Status.RESOLVED, Complaint.Status.REJECTED}:
            complaint.resolved_by = request.user
        form = ComplaintStaffUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            if complaint.status in {Complaint.Status.RESOLVED, Complaint.Status.REJECTED}:
                complaint.resolved_by = request.user
            try:
                with transaction.atomic():
                    complaint.save()
                    if complaint.status in {Complaint.Status.OPEN, Complaint.Status.UNDER_REVIEW}:
                        mark_booking_disputed_if_needed(complaint.booking)
                    if old_status != complaint.status:
                        record_audit_log(
                            request.user,
                            'complaint.status_update',
                            complaint,
                            {'old_status': old_status, 'new_status': complaint.status},
                        )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                if old_status != complaint.status:
                    send_complaint_status_email(complaint)
                messages.success(request, _('تم تحديث الشكوى بنجاح.'))
                return redirect('complaints:staff_detail', pk=complaint.pk)
    else:
        form = ComplaintStaffUpdateForm(instance=complaint)
    return render(request, 'complaints/staff_detail.html', {'complaint': complaint, 'form': form})
