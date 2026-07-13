import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def test_post_create_booking_with_valid_slot():
    auth = HTTPBasicAuth("admin@example.com", "Testpass123!")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Step 1: Get list of approved teachers to get a valid teacher_id
    teachers_resp = requests.get(f"{BASE_URL}/teachers/", headers=headers, auth=auth, timeout=30)
    assert teachers_resp.status_code == 200, f"Failed to get teachers list: {teachers_resp.text}"
    teachers = teachers_resp.json()
    assert isinstance(teachers, list) and len(teachers) > 0, "No approved teachers found"
    teacher_id = teachers[0].get("id") or teachers[0].get("pk") or teachers[0].get("teacher_id")
    assert teacher_id, "Teacher ID not found in response"

    # Step 2: Create a new student account and authenticate to use as booking user
    # Since no direct endpoint for student creation is given, reuse admin credentials for booking creation authorization.
    # The test uses basic token from admin so assuming admin can act as student, else test would fail here.
    # We'll proceed with admin auth to create booking.

    # Step 3: Prepare a valid non-overlapping slot for booking
    now = datetime.utcnow()
    start_time = (now + timedelta(days=1, hours=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    booking_payload = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z",
    }

    # Step 4: Create the booking
    create_booking_url = f"{BASE_URL}/bookings/create/{teacher_id}/"
    booking_resp = requests.post(create_booking_url, json=booking_payload, headers=headers, auth=auth, timeout=30)
    try:
        assert booking_resp.status_code == 201, f"Unexpected status code: {booking_resp.status_code}, response: {booking_resp.text}"

        content_type = booking_resp.headers.get('Content-Type', '')
        assert booking_resp.content and 'application/json' in content_type, f"Expected JSON response but got: {booking_resp.text}"

        try:
            booking = booking_resp.json()
        except Exception as e:
            assert False, f"Response is not valid JSON: {booking_resp.text}"

        booking_id = booking.get("id") or booking.get("pk")
        assert booking_id, "Booking ID missing in creation response"
        status = booking.get("status")
        assert status in ("pending payment", "awaiting teacher acceptance"), f"Unexpected booking status: {status}"

        assert booking.get("teacher_id") == teacher_id or str(booking.get("teacher_id")) == str(teacher_id)
        assert booking.get("start") == booking_payload["start"]
        assert booking.get("end") == booking_payload["end"]

    finally:
        if 'booking_id' in locals():
            delete_url = f"{BASE_URL}/bookings/{booking_id}/cancel/"
            del_resp = requests.post(delete_url, headers=headers, auth=auth, timeout=30)
            try:
                assert del_resp.status_code in (200, 204), f"Failed to cancel booking, status: {del_resp.status_code}, response: {del_resp.text}"
            except AssertionError:
                requests.delete(f"{BASE_URL}/bookings/{booking_id}/", headers=headers, auth=auth, timeout=30)


test_post_create_booking_with_valid_slot()
