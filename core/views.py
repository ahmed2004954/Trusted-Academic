from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from subjects.models import Subject
from teachers.models import TeacherProfile


def home(request):
    """Public homepage."""
    active_subjects = Subject.objects.filter(is_active=True, teacher_subjects__is_active=True).distinct()[:8]
    featured_teachers = (
        TeacherProfile.objects.filter(
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
            subjects__is_active=True,
        )
        .select_related('user')
        .prefetch_related('subjects__subject', 'subjects__grade_level')
        .distinct()
        .order_by('-average_rating', '-total_reviews', 'user__full_name')[:3]
    )
    return render(
        request,
        'core/home.html',
        {'active_subjects': active_subjects, 'featured_teachers': featured_teachers},
    )


def about(request):
    """About us page."""
    return render(request, 'core/about.html')


def faq(request):
    """Frequently asked questions page."""
    return render(request, 'core/faq.html')


def contact(request):
    """Contact us page with form handling."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if all([name, email, subject, message]):
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                f'Contact: {subject}',
                f'From: {name} ({email})\n\n{message}',
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, _('Your message has been sent. We will get back to you soon.'))
            return redirect('core:contact')
        messages.error(request, _('Please fill in all fields.'))
    return render(request, 'core/contact.html')


def terms(request):
    """Terms and conditions page."""
    return render(request, 'core/terms.html')


def privacy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy.html')


@login_required
def dashboard(request):
    """Redirect user to the appropriate role-based dashboard."""
    role = request.user.role

    if role == 'admin':
        return redirect('adminpanel:dashboard')
    if role == 'teacher':
        return redirect('teachers:dashboard')
    if role == 'parent':
        return redirect('parents:dashboard')
    return redirect('students:dashboard')
