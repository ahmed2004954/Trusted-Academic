import requests

def test_get_accounts_profile_without_authentication():
    base_url = "http://localhost:8000"
    url = f"{base_url}/accounts/profile/"
    timeout = 30

    try:
        response = requests.get(url, timeout=timeout, allow_redirects=False)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"

    # Expect either 403 Forbidden or redirect to login page (commonly 302 or 301)
    if response.status_code == 403:
        assert True  # Access forbidden as expected
    elif response.status_code in (301, 302):
        location = response.headers.get("Location", "")
        assert location.endswith("/accounts/login/") or "/accounts/login/" in location, \
            f"Redirect location unexpected: {location}"
    else:
        assert False, f"Expected 403 or redirect to login, got status code {response.status_code}"

test_get_accounts_profile_without_authentication()