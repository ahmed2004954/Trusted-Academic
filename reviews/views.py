from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking

from .forms import ReviewForm
from .models import Review


@login_required
def create_review(request, booking_pk):
    if request.user.role != 'student':
        raise PermissionDenied

    booking = get_object_or_404(
        Booking.objects.select_related('student', 'teacher__user', 'subject', 'grade_level'),
        pk=booking_pk,
        student=request.user,
    )
    if booking.booking_status != Booking.BookingStatus.COMPLETED:
        messages.error(request, _('يمكنك تقييم الحصة فقط بعد انتهائها.'))
        return redirect('bookings:student_detail', pk=booking.pk)
    if hasattr(booking, 'review'):
        messages.error(request, _('لقد قمت بتقييم هذه الحصة مسبقاً.'))
        return redirect('bookings:student_detail', pk=booking.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.student = request.user
            review.teacher = booking.teacher
            try:
                review.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, _('شكراً لك على تقييم حصتك.'))
                return redirect('bookings:student_detail', pk=booking.pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/create.html', {'form': form, 'booking': booking})
