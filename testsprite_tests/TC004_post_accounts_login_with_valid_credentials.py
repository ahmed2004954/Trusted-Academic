import requests

BASE_URL = "http://localhost:8000"

def test_post_accounts_login_with_valid_credentials():
    url = f"{BASE_URL}/accounts/login/"
    payload = {
        "username": "admin@example.com",
        "password": "Testpass123!"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30, allow_redirects=False)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    # Expect a 302 redirect to the role-specific dashboard on successful login
    assert response.status_code == 302, f"Expected 302 redirect but got {response.status_code}"

    location = response.headers.get("Location")
    assert location is not None and location != "", "Redirect location header missing or empty"

    # The location should point to a role-specific dashboard, e.g., "/teachers/dashboard/", "/students/dashboard/", "/parents/dashboard/", or "/admin/dashboard/"
    allowed_dashboards = [
        "/teachers/dashboard/",
        "/students/dashboard/",
        "/parents/dashboard/",
        "/admin/dashboard/"
    ]
    assert any(location.startswith(dashboard) for dashboard in allowed_dashboards), f"Redirected to unexpected location: {location}"

test_post_accounts_login_with_valid_credentials()
