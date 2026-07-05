from django.db.models import Q

from bookings.models import Booking
from parents.models import ParentStudentLink


DISPUTABLE_BOOKING_STATUSES = {
    Booking.BookingStatus.CONFIRMED,
    Booking.BookingStatus.IN_PROGRESS,
    Booking.BookingStatus.NO_SHOW_STUDENT,
    Booking.BookingStatus.NO_SHOW_TEACHER,
}


def user_can_create_complaint(user, booking: Booking) -> bool:
    if user.is_staff:
        return True
    if user.role == 'student':
        return booking.student_id == user.id
    if user.role == 'teacher':
        return booking.teacher.user_id == user.id
    if user.role == 'parent':
        return ParentStudentLink.objects.filter(parent__user=user, student=booking.student).exists()
    return False


def user_can_view_complaint(user, complaint) -> bool:
    if user.is_staff:
        return True
    booking = complaint.booking
    participant_ids = {booking.student_id, booking.teacher.user_id}
    if booking.parent_id:
        participant_ids.add(booking.parent_id)
    is_linked_parent = user.role == 'parent' and ParentStudentLink.objects.filter(parent__user=user, student=booking.student).exists()
    if user.id not in participant_ids and not is_linked_parent:
        return False
    return complaint.created_by_id == user.id or complaint.against_user_id == user.id


def visible_complaint_filter(user) -> Q:
    return (
        Q(created_by=user, booking__student=user)
        | Q(created_by=user, booking__teacher__user=user)
        | Q(created_by=user, booking__parent=user)
        | Q(created_by=user, booking__student__parent_links__parent__user=user)
        | Q(against_user=user, booking__student=user)
        | Q(against_user=user, booking__teacher__user=user)
        | Q(against_user=user, booking__parent=user)
        | Q(against_user=user, booking__student__parent_links__parent__user=user)
    )


def mark_booking_disputed_if_needed(booking: Booking) -> None:
    if booking.booking_status in DISPUTABLE_BOOKING_STATUSES:
        booking.booking_status = Booking.BookingStatus.DISPUTED
        booking.save(update_fields=['booking_status', 'updated_at'])
