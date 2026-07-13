
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** trust acadmy
- **Date:** 2026-07-13
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 get accounts register page
- **Test Code:** [TC001_get_accounts_register_page.py](./TC001_get_accounts_register_page.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/a83a304d-8c8a-4aa1-bb26-54fd9fa53e3d
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 post accounts register with valid student details
- **Test Code:** [TC002_post_accounts_register_with_valid_student_details.py](./TC002_post_accounts_register_with_valid_student_details.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 49, in <module>
  File "<string>", line 26, in test_post_accounts_register_with_valid_student_details
AssertionError: Unexpected status code: 403

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/08495688-8216-48c3-abe1-309572a2094a
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 get accounts login page
- **Test Code:** [TC003_get_accounts_login_page.py](./TC003_get_accounts_login_page.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/4369a6a0-e260-4b55-8128-9c061202b00b
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 post accounts login with valid credentials
- **Test Code:** [TC004_post_accounts_login_with_valid_credentials.py](./TC004_post_accounts_login_with_valid_credentials.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 34, in <module>
  File "<string>", line 20, in test_post_accounts_login_with_valid_credentials
AssertionError: Expected 302 redirect but got 403

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/9447ff02-41ce-40bf-ae05-a85476010c6c
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 get accounts profile without authentication
- **Test Code:** [TC005_get_accounts_profile_without_authentication.py](./TC005_get_accounts_profile_without_authentication.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/64b134a3-8eba-484b-bc0c-00537fab3955
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 get teachers list approved only
- **Test Code:** [TC006_get_teachers_list_approved_only.py](./TC006_get_teachers_list_approved_only.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 974, in json
    return complexjson.loads(self.text, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/__init__.py", line 514, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 386, in decode
    obj, end = self.raw_decode(s)
               ^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 416, in raw_decode
    return self.scan_once(s, idx=_w(s, idx).end())
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
simplejson.errors.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 20, in test_get_teachers_list_approved_only
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 978, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 46, in <module>
  File "<string>", line 22, in test_get_teachers_list_approved_only
AssertionError: Response is not valid JSON

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/127a7dfc-e0d9-45da-9db0-99b8a19d10a9
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 get teacher profile approved teacher
- **Test Code:** [TC007_get_teacher_profile_approved_teacher.py](./TC007_get_teacher_profile_approved_teacher.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 974, in json
    return complexjson.loads(self.text, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/__init__.py", line 514, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 386, in decode
    obj, end = self.raw_decode(s)
               ^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 416, in raw_decode
    return self.scan_once(s, idx=_w(s, idx).end())
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
simplejson.errors.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 43, in <module>
  File "<string>", line 17, in test_get_teacher_profile_approved_teacher
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 978, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/570f8a8b-8e5b-4f42-8460-5ca60b4aae65
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 get teacher profile pending rejected or suspended
- **Test Code:** [TC008_get_teacher_profile_pending_rejected_or_suspended.py](./TC008_get_teacher_profile_pending_rejected_or_suspended.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/aec6689b-d590-4c00-889f-6c76ddee9231
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 post create booking with valid slot
- **Test Code:** [TC009_post_create_booking_with_valid_slot.py](./TC009_post_create_booking_with_valid_slot.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 974, in json
    return complexjson.loads(self.text, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/__init__.py", line 514, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 386, in decode
    obj, end = self.raw_decode(s)
               ^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 416, in raw_decode
    return self.scan_once(s, idx=_w(s, idx).end())
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
simplejson.errors.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 71, in <module>
  File "<string>", line 18, in test_post_create_booking_with_valid_slot
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 978, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/2a0db39e-cd2c-4e0d-a1a5-ff271031a97c
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 post create booking with overlapping slot
- **Test Code:** [TC010_post_create_booking_with_overlapping_slot.py](./TC010_post_create_booking_with_overlapping_slot.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 974, in json
    return complexjson.loads(self.text, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/__init__.py", line 514, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 386, in decode
    obj, end = self.raw_decode(s)
               ^^^^^^^^^^^^^^^^^^
  File "/var/lang/lib/python3.12/site-packages/simplejson/decoder.py", line 416, in raw_decode
    return self.scan_once(s, idx=_w(s, idx).end())
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
simplejson.errors.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 78, in <module>
  File "<string>", line 14, in test_post_create_booking_with_overlapping_slot
  File "/var/lang/lib/python3.12/site-packages/requests/models.py", line 978, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 2 column 1 (char 1)

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cd6dbe2a-2df5-4cae-ab5a-f78a1913daa7/09bd95d3-9d39-431f-9ea4-c2548e2d1a71
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **40.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---