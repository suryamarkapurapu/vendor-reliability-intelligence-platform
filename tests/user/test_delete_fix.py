"""
End-to-end test for DELETE /api/v1/users/{id} fix.
Tests: delete active user, delete already inactive user, delete non-existing user,
       verify response body, verify HTTP status codes, verify update also works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import json
import urllib.request
import urllib.error
import uuid
import sys

BASE = "http://127.0.0.1:8000/api/v1"
PASS = 0
FAIL = 0


def api(method, path, body=None):
    """Make an API call, return (status_code, response_body_dict_or_str)."""
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body_text = e.read().decode()
            return e.code, json.loads(body_text)
        except Exception:
            return e.code, body_text


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")


# ── Test 1: Create a fresh user for deletion ──
print("\n=== TEST 1: Create fresh user for deletion ===")
unique = str(uuid.uuid4())[:8]
status, data = api("POST", "/users", {
    "username": f"deltest_{unique}",
    "full_name": "Delete Test User",
    "email": f"deltest_{unique}@example.com",
    "password": "SecurePass123!",
    "role_id": 1,
})
check("Create user returns 201", status == 201, f"got {status}")
check("User is active", data.get("is_active") is True)
user_id = data.get("user_id")
check("User ID returned", user_id is not None)
print(f"  -> Created user_id: {user_id}")


# ── Test 2: DELETE active user (the main bug fix) ──
print("\n=== TEST 2: DELETE active user (main fix) ===")
status, data = api("DELETE", f"/users/{user_id}")
check("DELETE returns 200", status == 200, f"got {status}")
check("Response has user_id", data.get("user_id") == user_id)
check("is_active is False", data.get("is_active") is False)
check("role_name present", data.get("role_name") is not None, f"got {data.get('role_name')}")
check("created_at present", data.get("created_at") is not None)
check("updated_at present", data.get("updated_at") is not None)
check("username preserved", data.get("username") == f"deltest_{unique}")
check("email preserved", data.get("email") == f"deltest_{unique}@example.com")
print(f"  -> Response body: {json.dumps(data, indent=2)}")


# ── Test 3: DELETE already inactive user ──
print("\n=== TEST 3: DELETE already inactive user ===")
status, data = api("DELETE", f"/users/{user_id}")
check("Returns 400 for already inactive", status == 400, f"got {status}")
check("Error message indicates already inactive", "already inactive" in str(data.get("detail", "")))
print(f"  -> Response: {data}")


# ── Test 4: DELETE non-existing user ──
print("\n=== TEST 4: DELETE non-existing user ===")
fake_id = str(uuid.uuid4())
status, data = api("DELETE", f"/users/{fake_id}")
check("Returns 404 for non-existing user", status == 404, f"got {status}")
check("Error message indicates not found", "not found" in str(data.get("detail", "")).lower())
print(f"  -> Response: {data}")


# ── Test 5: Verify database state via GET ──
print("\n=== TEST 5: Verify database state via GET ===")
status, data = api("GET", f"/users/{user_id}")
check("GET deleted user returns 200", status == 200, f"got {status}")
check("User still exists (soft delete)", data.get("user_id") == user_id)
check("is_active is False in DB", data.get("is_active") is False)
print(f"  -> User state in DB: is_active={data.get('is_active')}")


# ── Test 6: Update user also works (same fix) ──
print("\n=== TEST 6: UPDATE user (same fix applied) ===")
unique2 = str(uuid.uuid4())[:8]
status, data = api("POST", "/users", {
    "username": f"updtest_{unique2}",
    "full_name": "Update Test User",
    "email": f"updtest_{unique2}@example.com",
    "password": "SecurePass123!",
    "role_id": 1,
})
check("Create user for update returns 201", status == 201, f"got {status}")
upd_user_id = data.get("user_id")

status, data = api("PUT", f"/users/{upd_user_id}", {"full_name": "Updated Name"})
check("UPDATE returns 200", status == 200, f"got {status}")
check("full_name updated", data.get("full_name") == "Updated Name")
check("updated_at present after update", data.get("updated_at") is not None)
check("role_name present after update", data.get("role_name") is not None)
print(f"  -> Updated user response: {json.dumps(data, indent=2)}")

# Clean up: delete the update test user
api("DELETE", f"/users/{upd_user_id}")


# ── Summary ──
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
