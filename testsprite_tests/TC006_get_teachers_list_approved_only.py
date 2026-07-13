import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_teachers_list_approved_only():
    url = f"{BASE_URL}/teachers/"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        teachers = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(teachers, list), f"Expected response to be a list, got {type(teachers)}"

    for teacher in teachers:
        assert isinstance(teacher, dict), f"Each teacher should be a dict, got {type(teacher)}"
        status_keys = ['status', 'approval_status', 'state', 'is_approved']
        status_checked = False
        for key in status_keys:
            if key in teacher:
                status_checked = True
                value = teacher[key]
                if isinstance(value, str):
                    assert value.lower() == "approved", f"Teacher status not approved: {value}"
                elif isinstance(value, bool):
                    assert value is True, f"Teacher approval boolean is not True: {value}"
                else:
                    pass
                break
        if not status_checked:
            teacher_values = " ".join(str(v).lower() for v in teacher.values() if isinstance(v, str))
            assert all(x not in teacher_values for x in ["pending", "rejected", "suspended"]), \
                f"Teacher entry contains disallowed state words in values: {teacher_values}"

test_get_teachers_list_approved_only()
