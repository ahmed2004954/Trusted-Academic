import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
USERNAME = "admin@example.com"
PASSWORD = "Testpass123!"
TIMEOUT = 30

def test_get_teacher_profile_approved_teacher():
    # Step 1: Get list of approved teachers to get a valid teacher id
    try:
        response_list = requests.get(f"{BASE_URL}/teachers/", timeout=TIMEOUT)
        response_list.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Failed to get teachers list: {e}"
    
    teachers = response_list.json()
    assert isinstance(teachers, list), "Teachers list response is not a list"
    assert len(teachers) > 0, "No approved teachers found to test"

    teacher_id = teachers[0].get("id")
    assert teacher_id is not None, "Teacher id not found in listing"

    # Step 2: Query the detailed profile of the teacher by teacher_id
    try:
        response_profile = requests.get(f"{BASE_URL}/teachers/{teacher_id}/", timeout=TIMEOUT)
        response_profile.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Failed to get approved teacher profile: {e}"

    profile = response_profile.json()
    assert isinstance(profile, dict), "Teacher profile response is not a dictionary"
    assert profile.get("id") == teacher_id, "Returned teacher id does not match requested id"

    # Check for expected profile fields - some common fields that might appear
    expected_fields = ["id", "name", "subjects", "bio", "is_approved"]
    for field in expected_fields:
        assert field in profile, f"Expected profile field '{field}' missing"

    # The profile must be of an approved teacher
    assert profile.get("is_approved") is True, "Teacher profile is not marked as approved"

test_get_teacher_profile_approved_teacher()