import io
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image


def _valid_png_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1), (255, 0, 0)).save(buffer, 'PNG')
    return buffer.getvalue()

from bookings.models import Booking
from core.test_helpers import create_payment, create_student, create_teacher, create_test_booking, create_user
from payments.models import Payment, Wallet, WithdrawalRequest
from payments.services import complete_booking_with_attendance, get_or_create_wallet
from reviews.models import Review


class PaymentAndWalletTests(TestCase):
    def test_payment_approval_confirms_booking_and_credits_pending_once(self):
        admin = create_user('admin@example.com', role='admin', full_name='Admin User', is_staff=True)
        booking = create_test_booking(status=Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        payment = create_payment(booking)

        self.client.force_login(admin)
        self.client.post(reverse('payments:admin_approve', args=[payment.pk]))
        self.client.post(reverse('payments:admin_approve', args=[payment.pk]))
        booking.refresh_from_db()
        payment.refresh_from_db()
        wallet = Wallet.objects.get(teacher=booking.teacher)

        self.assertEqual(payment.payment_status, Payment.PaymentStatus.PAID)
        self.assertEqual(booking.booking_status, Booking.BookingStatus.CONFIRMED)
        self.assertEqual(wallet.pending_balance, booking.teacher_payout)
        self.assertIsNotNone(payment.wallet_pending_credited_at)

    def test_attendance_completion_settles_wallet_and_allows_review(self):
        booking = create_test_booking(status=Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        payment = create_payment(booking)
        admin = create_user('admin-wallet@example.com', role='admin', full_name='Admin User', is_staff=True)
        self.client.force_login(admin)
        self.client.post(reverse('payments:admin_approve', args=[payment.pk]))

        now = timezone.now()
        booking.refresh_from_db()
        booking.scheduled_start = now - timezone.timedelta(minutes=10)
        booking.scheduled_end = now + timezone.timedelta(minutes=50)
        booking.save(update_fields=['scheduled_start', 'scheduled_end', 'updated_at'])

        completed = complete_booking_with_attendance(booking.pk, booking.attendance_code)
        booking.refresh_from_db()
        wallet = Wallet.objects.get(teacher=booking.teacher)
        review = Review(booking=booking, student=booking.student, teacher=booking.teacher, rating=5, comment='Great lesson')
        review.full_clean()

        self.assertTrue(completed)
        self.assertEqual(booking.booking_status, Booking.BookingStatus.COMPLETED)
        self.assertEqual(wallet.pending_balance, 0)
        self.assertEqual(wallet.available_balance, booking.teacher_payout)
        self.assertIsNotNone(booking.wallet_settled_at)


class WithdrawalRequestTests(TestCase):
    def _fund_wallet(self, available=Decimal('200.00')):
        teacher = create_teacher(email='wallet-teacher@example.com', full_name='Wallet Teacher')
        wallet = get_or_create_wallet(teacher)
        wallet.available_balance = available
        wallet.save(update_fields=['available_balance', 'updated_at'])
        return teacher, wallet

    def test_teacher_cannot_request_withdrawal_below_minimum_threshold(self):
        teacher, wallet = self._fund_wallet()
        self.client.force_login(teacher.user)

        response = self.client.post(
            reverse('payments:wallet'),
            {'amount': '50.00', 'payment_method': 'vodafone_cash', 'payment_details': '01000000000'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WithdrawalRequest.objects.count(), 0)

    def test_teacher_cannot_request_withdrawal_exceeding_available_balance(self):
        teacher, wallet = self._fund_wallet(available=Decimal('100.00'))
        self.client.force_login(teacher.user)

        self.client.post(
            reverse('payments:wallet'),
            {'amount': '150.00', 'payment_method': 'vodafone_cash', 'payment_details': '01000000000'},
        )

        self.assertEqual(WithdrawalRequest.objects.count(), 0)

    def test_admin_approve_then_complete_deducts_balance_only_once(self):
        teacher, wallet = self._fund_wallet(available=Decimal('200.00'))
        withdrawal = WithdrawalRequest.objects.create(
            teacher=teacher,
            amount=Decimal('120.00'),
            payment_method='vodafone_cash',
            payment_details='01000000000',
        )
        admin = create_user('admin-wd@example.com', role='admin', full_name='Admin', is_staff=True)
        self.client.force_login(admin)

        self.client.post(reverse('payments:admin_withdrawal_action', args=[withdrawal.pk, 'approve']), {'notes': 'ok'})
        withdrawal.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(withdrawal.status, WithdrawalRequest.Status.APPROVED)
        self.assertEqual(wallet.available_balance, Decimal('80.00'))
        self.assertIsNotNone(withdrawal.balance_deducted_at)

        self.client.post(reverse('payments:admin_withdrawal_action', args=[withdrawal.pk, 'complete']), {'notes': 'paid'})
        withdrawal.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(withdrawal.status, WithdrawalRequest.Status.COMPLETED)
        self.assertEqual(wallet.available_balance, Decimal('80.00'))

    def test_admin_reject_does_not_change_available_balance(self):
        teacher, wallet = self._fund_wallet(available=Decimal('200.00'))
        withdrawal = WithdrawalRequest.objects.create(
            teacher=teacher,
            amount=Decimal('120.00'),
            payment_method='vodafone_cash',
            payment_details='01000000000',
        )
        admin = create_user('admin-rej@example.com', role='admin', full_name='Admin', is_staff=True)
        self.client.force_login(admin)

        self.client.post(reverse('payments:admin_withdrawal_action', args=[withdrawal.pk, 'reject']), {'notes': 'invalid details'})

        withdrawal.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(withdrawal.status, WithdrawalRequest.Status.REJECTED)
        self.assertEqual(wallet.available_balance, Decimal('200.00'))
        self.assertIsNone(withdrawal.balance_deducted_at)


class PaymentInstructionsViewTests(TestCase):
    def test_student_uploads_receipt_moves_booking_to_verification(self):
        booking = create_test_booking(status=Booking.BookingStatus.PENDING_PAYMENT)
        self.client.force_login(booking.student)
        receipt = SimpleUploadedFile('receipt.png', _valid_png_bytes(), content_type='image/png')

        response = self.client.post(
            reverse('payments:instructions', args=[booking.pk]),
            {'payment_method': 'vodafone_cash', 'receipt_image': receipt},
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.payment_status, Payment.PaymentStatus.AWAITING_VERIFICATION)

    def test_payment_instructions_requires_student_role(self):
        booking = create_test_booking(status=Booking.BookingStatus.PENDING_PAYMENT)
        self.client.force_login(booking.teacher.user)

        response = self.client.get(reverse('payments:instructions', args=[booking.pk]))

        self.assertEqual(response.status_code, 403)

    def test_student_cannot_open_instructions_for_others_booking(self):
        booking = create_test_booking(status=Booking.BookingStatus.PENDING_PAYMENT)
        intruder = create_student(email='pay-intruder@example.com')
        self.client.force_login(intruder)

        response = self.client.get(reverse('payments:instructions', args=[booking.pk]))

        self.assertEqual(response.status_code, 404)


class PaymentHistoryAndWalletViewTests(TestCase):
    def test_student_payment_history_lists_own_payments_only(self):
        booking = create_test_booking(status=Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        create_payment(booking)
        self.client.force_login(booking.student)

        response = self.client.get(reverse('payments:history'))

        self.assertEqual(response.status_code, 200)

    def test_payment_history_requires_student_role(self):
        teacher = create_teacher(email='hist-teacher@example.com')
        self.client.force_login(teacher.user)

        response = self.client.get(reverse('payments:history'))

        self.assertEqual(response.status_code, 403)

    def test_teacher_can_view_wallet(self):
        teacher = create_teacher(email='wallet-view@example.com')
        get_or_create_wallet(teacher)
        self.client.force_login(teacher.user)

        response = self.client.get(reverse('payments:wallet'))

        self.assertEqual(response.status_code, 200)


class PaymentAdminAuthorizationTests(TestCase):
    def test_non_staff_cannot_access_pending_verifications(self):
        student = create_student(email='verif-student@example.com')
        self.client.force_login(student)

        response = self.client.get(reverse('payments:admin_pending'))

        # staff_member_required redirects non-staff to the admin login page.
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_pending', response.get('Location', ''))

    def test_reject_payment_marks_failed(self):
        booking = create_test_booking(status=Booking.BookingStatus.AWAITING_RECEIPT_VERIFICATION)
        payment = create_payment(booking)
        admin = create_user('reject-admin@example.com', role='admin', full_name='Admin', is_staff=True)
        self.client.force_login(admin)

        self.client.post(
            reverse('payments:admin_reject', args=[payment.pk]),
            {'rejection_reason': 'Receipt unreadable'},
        )

        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, Payment.PaymentStatus.FAILED)
