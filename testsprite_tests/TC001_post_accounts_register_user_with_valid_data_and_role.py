import requests
import time
from requests.auth import HTTPBasicAuth

def test_post_accounts_register_user_with_valid_data_and_role():
    base_url = "http://localhost:8000"
    session = requests.Session()
    timeout = 30

    # Add unique suffix to username and email to avoid duplicate errors
    unique_suffix = str(int(time.time()))

    # Step 1: Get registration page to fetch CSRF token
    try:
        get_response = session.get(f"{base_url}/accounts/register/", timeout=timeout)
        assert get_response.status_code == 200, f"Expected 200 from GET /accounts/register/, got {get_response.status_code}"
        # Extract CSRF token from cookies or HTML
        csrf_token = session.cookies.get('csrftoken', None)
        assert csrf_token is not None, "CSRF token not found in cookies"

        # Prepare registration data with valid details
        register_data = {
            "username": f"testuser_valid_{unique_suffix}",
            "email": f"testuser_valid_{unique_suffix}@example.com",
            "password1": "ValidPass123!",
            "password2": "ValidPass123!",
            "role": "student"
        }

        headers = {
            "Referer": f"{base_url}/accounts/register/",
            "X-CSRFToken": csrf_token
        }

        # Step 2: POST to register endpoint
        post_response = session.post(
            f"{base_url}/accounts/register/",
            data=register_data,
            headers=headers,
            timeout=timeout,
            allow_redirects=False
        )

        # Expected 302 redirect to role dashboard on success
        assert post_response.status_code == 302, \
            f"Expected 302 redirect on successful registration, got {post_response.status_code}. Response content may contain validation errors."
        location = post_response.headers.get("Location", "")
        assert location != "", "Redirect Location header missing"
        # Verify redirection location contains dashboard path related to the role (student assumed here)
        assert any(role_path in location for role_path in ["/students/dashboard/", "/teachers/dashboard/", "/parents/dashboard/"]), \
            f"Redirect location {location} is not a recognized role dashboard path"

    finally:
        # Cleanup placeholder
        pass

test_post_accounts_register_user_with_valid_data_and_role()
