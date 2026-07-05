from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from teachers.forms import TeacherReviewForm
from teachers.models import TeacherProfile
from payments.models import Payment


@staff_member_required
def dashboard(request):
    pending_count = TeacherProfile.objects.filter(approval_status=TeacherProfile.ApprovalStatus.PENDING).count()
    pending_payment_count = Payment.objects.filter(payment_status=Payment.PaymentStatus.AWAITING_VERIFICATION).count()
    return render(
        request,
        'adminpanel/dashboard.html',
        {'pending_count': pending_count, 'pending_payment_count': pending_payment_count},
    )


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
                messages.success(request, _('Teacher profile approved.'))
            elif action == 'reject':
                profile.reject(notes)
                messages.success(request, _('Teacher profile rejected.'))
            elif action == 'suspend':
                profile.suspend(notes)
                messages.success(request, _('Teacher profile suspended.'))
            return redirect('adminpanel:review_teacher', profile_id=profile.pk)
    else:
        form = TeacherReviewForm(instance=profile)

    return render(request, 'adminpanel/review_teacher.html', {'profile': profile, 'form': form})
