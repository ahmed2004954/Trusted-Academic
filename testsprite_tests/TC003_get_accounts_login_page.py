import requests
from requests.auth import HTTPBasicAuth

def test_get_accounts_login_page():
    base_url = "http://localhost:8000"
    url = f"{base_url}/accounts/login/"
    auth = HTTPBasicAuth("admin@example.com", "Testpass123!")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "python-requests/2.x"
    }
    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        # Verify response is HTML content of login page
        content_type = response.headers.get("Content-Type", "")
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        assert "text/html" in content_type, f"Expected 'text/html' in Content-Type but got {content_type}"
        assert "login" in response.text.lower(), "Response content does not appear to contain login page"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_accounts_login_page()