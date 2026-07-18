# TestSprite AI Testing Report (MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** trust acadmy
- **Date:** 2026-07-17
- **Prepared by:** TestSprite AI Team
- **Test Type:** Backend (server-rendered Django app)
- **Target:** http://localhost:8000

---

## 2️⃣ Requirement Validation Summary

### Requirement: Authentication & Accounts — User Registration
Registration of a new user via `POST /accounts/register/` should validate input, create the account, log the user in, and redirect to the role dashboard.

#### Test TC001 post accounts register user with valid data and role
- **Test Code:** [TC001_post_accounts_register_user_with_valid_data_and_role.py](./TC001_post_accounts_register_user_with_valid_data_and_role.py)
- **Test Error:** `AssertionError: Expected 302 redirect on successful registration, got 200. Response content may contain validation errors.`
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/72ea7574-2cb7-467d-9504-787b723b9940/f83137d3-0f99-467f-8ea1-35ab784021ce
- **Status:** ❌ Failed
- **Analysis / Findings:** The failure is a **test-data mismatch, not an application defect**. The generated test posted `username`, `email`, `password1`, `password2`, and `role`. The actual `UserRegistrationForm` (`accounts/forms.py`) requires `full_name`, `email`, `phone`, `role`, `password1`, and `password2` — there is no `username` field, and `full_name`/`phone` are mandatory. Missing required fields caused the form to fail validation, so the view correctly re-rendered the page with `200` instead of redirecting. A manual verification with the correct fields confirmed the endpoint behaves as specified: `POST /accounts/register/` returned `302 → /dashboard/` and the account was created and logged in. **Recommended fix:** update the test to submit the real form fields (`full_name`, `phone`) and drop `username`.

---

## 3️⃣ Coverage & Matching Metrics

- **0.00%** of tests passed (0 of 1)
- The generated plan covered only 1 of the ~13 feature areas discovered in the codebase, so backend coverage is very shallow relative to the app surface.

| Requirement                          | Total Tests | ✅ Passed | ❌ Failed |
|--------------------------------------|-------------|-----------|-----------|
| Authentication & Accounts (Register) | 1           | 0         | 1         |

Feature areas in the codebase **not** covered by any generated test: Login/Logout, Profile, Core pages & dashboard routing, Teachers (directory + self-service), Students, Parents, Bookings, Payments & Wallet, Reviews, Reports, Complaints, Messaging, Subjects, Admin Panel.

---

## 4️⃣ Key Gaps / Risks

- **The single failing test is a false negative.** The endpoint works; the test used incorrect field names. Fix the test payload before treating this as a bug.
- **Coverage is very thin.** Only registration was exercised. High-value flows — login, booking create/cancel, payment verification, teacher approval in the admin panel — have no automated coverage. Consider expanding the test plan to include these.
- **Unmigrated model changes.** `manage.py migrate` reported that the `teachers` app has model changes not reflected in a migration. This does not affect the tested endpoint but could cause schema drift or runtime errors elsewhere. Run `makemigrations teachers` and `migrate`.
- **CSRF/session handling** worked correctly in the manual run; auto-generated tests should reuse a session and pull the `csrfmiddlewaretoken` from the form HTML (not only the cookie) to reliably drive Django POST endpoints.

---
