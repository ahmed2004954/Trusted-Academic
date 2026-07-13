from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from complaints.models import Complaint
from teachers.forms import TeacherReviewForm
from teachers.models import TeacherProfile
from payments.models import Payment, WithdrawalRequest

from .models import AuditLog, record_audit_log


@staff_member_required
def dashboard(request):
    metrics = dashboard_metrics()
    quick_actions = dashboard_quick_actions(metrics)

    return render(
        request,
        'adminpanel/dashboard.html',
        {
            'metrics': metrics,
            'quick_actions': quick_actions,
            'pending_count': metrics['teacher_counts']['pending'],
            'pending_payment_count': metrics['pending_payments'],
        },
    )


def dashboard_metrics():
    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=today.weekday())
    week_end = week_start + timezone.timedelta(days=7)
    User = get_user_model()

    users_by_role = User.objects.values('role').annotate(count=Count('id')).order_by('role')
    teacher_counts = dict(
        TeacherProfile.objects.values_list('approval_status').annotate(count=Count('id'))
    )
    pending_teacher_count = teacher_counts.get(TeacherProfile.ApprovalStatus.PENDING, 0)
    pending_payment_count = Payment.objects.filter(payment_status=Payment.PaymentStatus.AWAITING_VERIFICATION).count()
    open_complaint_count = Complaint.objects.filter(status__in=[Complaint.Status.OPEN, Complaint.Status.UNDER_REVIEW]).count()
    pending_withdrawal_count = WithdrawalRequest.objects.filter(status=WithdrawalRequest.Status.PENDING).count()

    return {
        'total_users': User.objects.count(),
        'users_by_role': users_by_role,
        'teacher_counts': {
            'pending': pending_teacher_count,
            'approved': teacher_counts.get(TeacherProfile.ApprovalStatus.APPROVED, 0),
            'rejected': teacher_counts.get(TeacherProfile.ApprovalStatus.REJECTED, 0),
            'suspended': teacher_counts.get(TeacherProfile.ApprovalStatus.SUSPENDED, 0),
        },
        'today_bookings': Booking.objects.filter(scheduled_start__date=today).count(),
        'week_bookings': Booking.objects.filter(scheduled_start__date__gte=week_start, scheduled_start__date__lt=week_end).count(),
        'pending_payments': pending_payment_count,
        'open_complaints': open_complaint_count,
        'pending_withdrawals': pending_withdrawal_count,
        'completed_bookings': Booking.objects.filter(booking_status=Booking.BookingStatus.COMPLETED).count(),
    }


def dashboard_quick_actions(metrics):
    return [
        {
            'label': _('Pending teacher review queue'),
            'url': reverse('adminpanel:pending_teachers'),
            'count': metrics['teacher_counts']['pending'],
        },
        {'label': _('Payment verification queue'), 'url': reverse('payments:admin_pending'), 'count': metrics['pending_payments']},
        {'label': _('Complaint queue'), 'url': reverse('complaints:staff_queue'), 'count': metrics['open_complaints']},
        {'label': _('Withdrawal queue'), 'url': reverse('payments:admin_withdrawal_queue'), 'count': metrics['pending_withdrawals']},
        {'label': _('Booking monitor'), 'url': reverse('adminpanel:booking_monitor'), 'count': None},
        {'label': _('User list/search'), 'url': reverse('adminpanel:user_list'), 'count': None},
        {'label': _('Django admin'), 'url': reverse('admin:index'), 'count': None},
        {'label': _('Audit log'), 'url': reverse('adminpanel:audit_logs'), 'count': None},
    ]


@staff_member_required
def pending_teachers(request):
    profiles = TeacherProfile.objects.select_related('user').filter(
        approval_status=TeacherProfile.ApprovalStatus.PENDING,
    )
    return render(request, 'adminpanel/pending_teachers.html', {'profiles': profiles})


@staff_member_required
def review_teacher(request, profile_id):
    profile = get_object_or_404(
        TeacherProfile.objects.select_related('user').prefetch_related('certificates'),
        pk=profile_id,
    )

    if request.method == 'POST':
        form = TeacherReviewForm(request.POST, instance=profile)
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data.get('verification_notes', '').strip()
            if action == 'approve':
                profile.approve(notes)
                record_audit_log(request.user, 'teacher.approve', profile, {'notes': notes})
                messages.success(request, _('Teacher profile approved.'))
            elif action == 'reject':
                profile.reject(notes)
                record_audit_log(request.user, 'teacher.reject', profile, {'notes': notes})
                messages.success(request, _('Teacher profile rejected.'))
            elif action == 'suspend':
                profile.suspend(notes)
                record_audit_log(request.user, 'teacher.suspend', profile, {'notes': notes})
                messages.success(request, _('Teacher profile suspended.'))
            return redirect('adminpanel:review_teacher', profile_id=profile.pk)
    else:
        form = TeacherReviewForm(instance=profile)

    return render(request, 'adminpanel/review_teacher.html', {'profile': profile, 'form': form})


@staff_member_required
def booking_monitor(request):
    bookings = filtered_bookings(request.GET)
    filters = {
        'status': request.GET.get('status', '').strip(),
        'teacher': request.GET.get('teacher', '').strip(),
        'student': request.GET.get('student', '').strip(),
        'date_from': request.GET.get('date_from', '').strip(),
        'date_to': request.GET.get('date_to', '').strip(),
    }

    return render(
        request,
        'adminpanel/booking_monitor.html',
        {'bookings': bookings[:100], 'status_choices': Booking.BookingStatus.choices, 'filters': filters},
    )


def filtered_bookings(filters):
    bookings = Booking.objects.select_related(
        'student',
        'parent',
        'teacher__user',
        'subject',
        'grade_level',
    )
    status = filters.get('status', '').strip()
    teacher = filters.get('teacher', '').strip()
    student = filters.get('student', '').strip()
    date_from = filters.get('date_from', '').strip()
    date_to = filters.get('date_to', '').strip()

    if status:
        bookings = bookings.filter(booking_status=status)
    if teacher:
        bookings = bookings.filter(
            Q(teacher__user__email__icontains=teacher) | Q(teacher__user__full_name__icontains=teacher)
        )
    if student:
        bookings = bookings.filter(Q(student__email__icontains=student) | Q(student__full_name__icontains=student))
    if date_from:
        bookings = bookings.filter(scheduled_start__date__gte=date_from)
    if date_to:
        bookings = bookings.filter(scheduled_start__date__lte=date_to)
    return bookings


@staff_member_required
def user_list(request):
    User = get_user_model()
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()

    return render(
        request,
        'adminpanel/user_list.html',
        {
            'users': filtered_users(query, role)[:100],
            'role_choices': User.Role.choices,
            'filters': {'q': query, 'role': role},
        },
    )


def filtered_users(query, role):
    User = get_user_model()
    users = User.objects.all()

    if query:
        users = users.filter(Q(email__icontains=query) | Q(full_name__icontains=query) | Q(phone__icontains=query))
    if role:
        users = users.filter(role=role)
    return users


@staff_member_required
def audit_logs(request):
    logs = AuditLog.objects.select_related('actor')[:100]
    return render(request, 'adminpanel/audit_logs.html', {'logs': logs})


@staff_member_required
def manage_subjects(request):
    from subjects.models import Subject, GradeLevel
    from teachers.models import PlatformPricingRange, LessonType
    subjects = Subject.objects.all()
    grade_levels = GradeLevel.objects.all()
    pricing_ranges = PlatformPricingRange.objects.select_related('subject', 'grade_level').all()
    return render(request, 'adminpanel/manage_subjects.html', {
        'subjects': subjects,
        'grade_levels': grade_levels,
        'pricing_ranges': pricing_ranges,
        'lesson_types': LessonType.choices,
    })


@staff_member_required
def add_subject(request):
    from subjects.models import Subject
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Subject.objects.create(name=name)
            messages.success(request, _('Subject created successfully.'))
            return redirect('adminpanel:manage_subjects')
        messages.error(request, _('Subject name is required.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def edit_subject(request, subject_id):
    from subjects.models import Subject
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        subject.name = request.POST.get('name', subject.name).strip()
        subject.is_active = request.POST.get('is_active') == 'on'
        subject.save()
        messages.success(request, _('Subject updated successfully.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def delete_subject(request, subject_id):
    from subjects.models import Subject
    if request.method == 'POST':
        Subject.objects.filter(pk=subject_id).delete()
        messages.success(request, _('Subject deleted.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def add_grade_level(request):
    from subjects.models import GradeLevel
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'secondary')
        order = request.POST.get('order', 0)
        if name:
            GradeLevel.objects.create(name=name, category=category, order=order)
            messages.success(request, _('Grade level created successfully.'))
            return redirect('adminpanel:manage_subjects')
        messages.error(request, _('Grade level name is required.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def edit_grade_level(request, gl_id):
    from subjects.models import GradeLevel
    gl = get_object_or_404(GradeLevel, pk=gl_id)
    if request.method == 'POST':
        gl.name = request.POST.get('name', gl.name).strip()
        gl.category = request.POST.get('category', gl.category)
        gl.order = request.POST.get('order', gl.order)
        gl.is_active = request.POST.get('is_active') == 'on'
        gl.save()
        messages.success(request, _('Grade level updated successfully.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def add_pricing_range(request):
    from subjects.models import Subject, GradeLevel
    from teachers.models import PlatformPricingRange, LessonType
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        grade_level_id = request.POST.get('grade_level')
        lesson_type = request.POST.get('lesson_type')
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')
        if all([subject_id, grade_level_id, lesson_type, min_price, max_price]):
            PlatformPricingRange.objects.create(
                subject_id=subject_id,
                grade_level_id=grade_level_id,
                lesson_type=lesson_type,
                min_price=min_price,
                max_price=max_price,
            )
            messages.success(request, _('Pricing range created successfully.'))
            return redirect('adminpanel:manage_subjects')
        messages.error(request, _('All fields are required.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def edit_pricing_range(request, pr_id):
    from teachers.models import PlatformPricingRange
    pr = get_object_or_404(PlatformPricingRange, pk=pr_id)
    if request.method == 'POST':
        pr.min_price = request.POST.get('min_price', pr.min_price)
        pr.max_price = request.POST.get('max_price', pr.max_price)
        pr.is_active = request.POST.get('is_active') == 'on'
        pr.save()
        messages.success(request, _('Pricing range updated successfully.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def delete_grade_level(request, gl_id):
    from subjects.models import GradeLevel
    if request.method == 'POST':
        GradeLevel.objects.filter(pk=gl_id).delete()
        messages.success(request, _('Grade level deleted successfully.'))
    return redirect('adminpanel:manage_subjects')


@staff_member_required
def delete_pricing_range(request, pr_id):
    from teachers.models import PlatformPricingRange
    if request.method == 'POST':
        PlatformPricingRange.objects.filter(pk=pr_id).delete()
        messages.success(request, _('Pricing range deleted successfully.'))
    return redirect('adminpanel:manage_subjects')

