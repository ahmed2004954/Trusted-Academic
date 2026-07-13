import requests
from requests.auth import HTTPBasicAuth
import uuid

BASE_URL = "http://localhost:8000"
AUTH = HTTPBasicAuth("admin@example.com", "Testpass123!")
TIMEOUT = 30

def test_post_create_booking_with_overlapping_slot():
    headers = {"Content-Type": "application/json"}
    # Step 1: Find an approved teacher to use
    teachers_resp = requests.get(f"{BASE_URL}/teachers/", timeout=TIMEOUT)
    assert teachers_resp.status_code == 200
    teachers = teachers_resp.json()
    assert isinstance(teachers, list) and len(teachers) > 0
    teacher_id = teachers[0]['id'] if 'id' in teachers[0] else None
    assert teacher_id is not None

    # Step 2: Create a booking with a valid slot to have an existing booking
    booking_payload_1 = {
        "date": "2026-08-01",
        "start_time": "10:00",
        "end_time": "11:00",
        "student_name": f"Test Student {uuid.uuid4().hex[:6]}"
    }
    booking_create_url = f"{BASE_URL}/bookings/create/{teacher_id}/"
    create_resp_1 = requests.post(booking_create_url, auth=AUTH, headers=headers, json=booking_payload_1, timeout=TIMEOUT)
    assert create_resp_1.status_code == 201 or create_resp_1.status_code == 200
    booking_1 = create_resp_1.json()
    booking_id_1 = booking_1.get("id")
    assert booking_id_1 is not None

    try:
        # Step 3: Attempt to create an overlapping booking (same date and overlapping time range)
        booking_payload_overlap = {
            "date": "2026-08-01",
            "start_time": "10:30",
            "end_time": "11:30",
            "student_name": f"Overlap Student {uuid.uuid4().hex[:6]}"
        }
        create_resp_2 = requests.post(booking_create_url, auth=AUTH, headers=headers, json=booking_payload_overlap, timeout=TIMEOUT)

        # Expect validation error preventing conflicting booking
        assert create_resp_2.status_code in (400, 409)

        # Safely parse JSON only if response is JSON and non-empty
        error_messages = []
        content_type = create_resp_2.headers.get('Content-Type', '')
        if 'application/json' in content_type and create_resp_2.text.strip():
            try:
                error_resp = create_resp_2.json()
                if isinstance(error_resp, dict):
                    if "error" in error_resp:
                        error_messages.append(str(error_resp["error"]))
                    if "detail" in error_resp:
                        error_messages.append(str(error_resp["detail"]))
                    for v in error_resp.values():
                        if isinstance(v, list):
                            error_messages.extend([str(i) for i in v])
                        elif isinstance(v, str):
                            error_messages.append(v)
            except Exception:
                pass

        assert any("overlap" in msg.lower() or "conflict" in msg.lower() or "slot" in msg.lower() for msg in error_messages), \
            "Error messages should indicate overlapping slot conflict"
    finally:
        # Clean up created booking 1 if possible
        if booking_id_1:
            cancel_url = f"{BASE_URL}/bookings/{booking_id_1}/cancel/"
            try:
                cancel_resp = requests.post(cancel_url, auth=AUTH, timeout=TIMEOUT)
                # Accept 200 or 204 or 202 as success for cancellation
                assert cancel_resp.status_code in (200, 202, 204)
            except Exception:
                pass

test_post_create_booking_with_overlapping_slot()
