import requests
from requests.auth import HTTPBasicAuth

def test_get_accounts_register_page():
    base_url = "http://localhost:8000"
    url = f"{base_url}/accounts/register/"
    auth = HTTPBasicAuth("admin@example.com", "Testpass123!")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, f"Expected 'text/html' in Content-Type, got {content_type}"
    assert "register" in response.text.lower(), "Response content does not appear to be registration page"

test_get_accounts_register_page()