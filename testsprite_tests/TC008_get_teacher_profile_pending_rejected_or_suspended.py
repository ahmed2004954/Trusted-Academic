import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_teacher_profile_pending_rejected_or_suspended():
    # Known teacher IDs for statuses (these should be replaced with actual test data in a real environment)
    # Here we assume these IDs do not exist or represent teachers with restricted status
    teacher_ids_to_test = [9999, 8888, 7777]
    
    for teacher_id in teacher_ids_to_test:
        get_url = f"{BASE_URL}/teachers/{teacher_id}/"
        response = requests.get(get_url, timeout=TIMEOUT)
        # Verify the profile is not accessible: expect 404 error
        assert response.status_code == 404, (
            f"Expected 404 for teacher with id '{teacher_id}', got {response.status_code}"
        )

test_get_teacher_profile_pending_rejected_or_suspended()