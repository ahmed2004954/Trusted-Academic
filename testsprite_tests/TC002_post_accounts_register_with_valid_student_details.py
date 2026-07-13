import requests
from requests.auth import HTTPBasicAuth

def test_post_accounts_register_with_valid_student_details():
    base_url = "http://localhost:8000"
    register_url = f"{base_url}/accounts/register/"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Sample valid student registration details
    payload = {
        "username": "teststudent123",
        "email": "teststudent123@example.com",
        "password1": "StrongPassw0rd!",
        "password2": "StrongPassw0rd!",
        "first_name": "Test",
        "last_name": "Student"
    }

    # Try registering the user, then verify creation and redirect
    try:
        response = requests.post(register_url, json=payload, headers=headers, timeout=30, allow_redirects=False)
        # Assert status code is 302 redirect or 201 created depending on implementation
        assert response.status_code in (201, 302), f"Unexpected status code: {response.status_code}"
        # If redirect, check location header leads to dashboard
        if response.status_code == 302:
            location = response.headers.get("Location", "")
            assert "dashboard" in location.lower(), f"Redirect location does not indicate dashboard: {location}"
        else:
            # If 201 or similar success without redirect, consider valid
            # Optionally parse body and check account detail returned
            json_resp = response.json()
            assert json_resp.get("username") == payload["username"]
    finally:
        # Cleanup: Attempt to delete the created user to keep test idempotent
        # Assuming an admin endpoint to delete user by username or user id is available
        # Since not provided, attempt to login and then delete if possible
        # Here we try a delete endpoint: /accounts/delete/<username> (hypothetical)
        auth = HTTPBasicAuth("admin@example.com", "Testpass123!")
        delete_url = f"{base_url}/accounts/delete/{payload['username']}/"
        try:
            del_resp = requests.delete(delete_url, auth=auth, timeout=30)
            assert del_resp.status_code in (200, 204, 404), f"Unexpected delete status code: {del_resp.status_code}"
        except Exception:
            pass

test_post_accounts_register_with_valid_student_details()
