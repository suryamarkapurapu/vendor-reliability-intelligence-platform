"""
End-to-end tests for Vendor Service improvements (Phase 2C).
Tests: create, update, delete, duplicate code, invalid category,
invalid linked user, already suspended, already blacklisted, non-existing vendor.
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


# =============================================================
# TEST 1: Create vendor (baseline)
# =============================================================
print("\n=== TEST 1: Create vendor (baseline) ===")
u = str(uuid.uuid4())[:8]
status, data = api("POST", "/vendors", {
    "vendor_code": f"SVC-{u}",
    "company_name": f"Service Test Corp {u}",
    "category_id": 1,
    "city": "Mumbai",
})
check("Create returns 201", status == 201, f"got {status}")
vendor_id = data.get("vendor_id") if status == 201 else None
if status == 201:
    check("status is pending", data.get("status") == "pending")
    check("category_name present", data.get("category_name") is not None)
    print(f"  -> vendor_id = {vendor_id}")
else:
    print(f"  -> Error: {data}")


# =============================================================
# TEST 2: Duplicate vendor code
# =============================================================
print("\n=== TEST 2: Duplicate vendor code ===")
status, data = api("POST", "/vendors", {
    "vendor_code": f"SVC-{u}",  # same code as TEST 1
    "company_name": "Duplicate Corp",
    "category_id": 1,
})
check("Duplicate code returns 409", status == 409, f"got {status}")
check("Error message mentions vendor code", "already exists" in str(data.get("detail", "")).lower())
print(f"  -> Response: {data}")


# =============================================================
# TEST 3: Invalid category
# =============================================================
print("\n=== TEST 3: Invalid category_id ===")
status, data = api("POST", "/vendors", {
    "vendor_code": f"CAT-{str(uuid.uuid4())[:8]}",
    "company_name": "Bad Cat Corp",
    "category_id": 9999,
})
check("Invalid category returns 404", status == 404, f"got {status}")
check("Error message mentions category", "category" in str(data.get("detail", "")).lower())
print(f"  -> Response: {data}")


# =============================================================
# TEST 4: Invalid linked_user_id
# =============================================================
print("\n=== TEST 4: Invalid linked_user_id ===")
fake_user_id = str(uuid.uuid4())
status, data = api("POST", "/vendors", {
    "vendor_code": f"LNK-{str(uuid.uuid4())[:8]}",
    "company_name": "Bad Link Corp",
    "category_id": 1,
    "linked_user_id": fake_user_id,
})
check("Invalid linked_user returns error (not 500)", status != 500, f"got {status}")
check("Returns 404 for missing user", status == 404, f"got {status}")
check("Error message mentions user", "not found" in str(data.get("detail", "")).lower())
print(f"  -> Response: {data}")


# =============================================================
# TEST 5: Create vendor with valid linked_user_id
# =============================================================
print("\n=== TEST 5: Create vendor with valid linked_user_id ===")
# First get an existing user
_, users = api("GET", "/users")
active_users = [u for u in users if u.get("is_active")]
if active_users:
    real_user_id = active_users[0]["user_id"]
    u2 = str(uuid.uuid4())[:8]
    status, data = api("POST", "/vendors", {
        "vendor_code": f"LNK-{u2}",
        "company_name": f"Linked Corp {u2}",
        "category_id": 1,
        "linked_user_id": real_user_id,
    })
    check("Create with valid linked_user returns 201", status == 201, f"got {status}")
    if status == 201:
        check("linked_user_id matches", data.get("linked_user_id") == real_user_id)
        linked_vendor_id = data["vendor_id"]
    else:
        print(f"  -> Error: {data}")
        linked_vendor_id = None
else:
    print("  [SKIP] No active users found")
    linked_vendor_id = None


# =============================================================
# TEST 6: Update vendor
# =============================================================
print("\n=== TEST 6: Update vendor ===")
if vendor_id:
    status, data = api("PUT", f"/vendors/{vendor_id}", {
        "company_name": f"Updated SVC Corp {u}",
    })
    check("Update returns 200", status == 200, f"got {status}")
    if status == 200:
        check("company_name updated", data.get("company_name") == f"Updated SVC Corp {u}")
        check("category_name still present", data.get("category_name") is not None)
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 7: Update with invalid linked_user_id
# =============================================================
print("\n=== TEST 7: Update with invalid linked_user_id ===")
if vendor_id:
    fake_uid = str(uuid.uuid4())
    status, data = api("PUT", f"/vendors/{vendor_id}", {
        "linked_user_id": fake_uid,
    })
    check("Update with invalid linked_user returns error (not 500)", status != 500, f"got {status}")
    check("Returns 404 for missing user", status == 404, f"got {status}")
    print(f"  -> Response: {data}")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 8: Update with duplicate vendor_code
# =============================================================
print("\n=== TEST 8: Update with duplicate vendor_code ===")
if vendor_id and linked_vendor_id:
    status, data = api("PUT", f"/vendors/{vendor_id}", {
        "vendor_code": f"LNK-{u2}",  # code belongs to linked_vendor
    })
    check("Duplicate code on update returns 409", status == 409, f"got {status}")
    print(f"  -> Response: {data}")
else:
    print("  [SKIP] Missing vendor IDs")


# =============================================================
# TEST 9: Delete vendor (soft-delete -> suspended)
# =============================================================
print("\n=== TEST 9: DELETE /vendors/{id} (soft-delete) ===")
if vendor_id:
    status, data = api("DELETE", f"/vendors/{vendor_id}")
    check("Delete returns 200", status == 200, f"got {status}")
    if status == 200:
        check("status is suspended", data.get("status") == "suspended")
        check("vendor_id preserved", data.get("vendor_id") == vendor_id)
        check("category_name still present", data.get("category_name") is not None)
        check("created_at present", data.get("created_at") is not None)
        check("updated_at present", data.get("updated_at") is not None)
        print(f"  -> Response status = {data.get('status')}")
    else:
        print(f"  -> Error: {data}")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 10: Delete already suspended vendor
# =============================================================
print("\n=== TEST 10: Delete already suspended vendor ===")
if vendor_id:
    status, data = api("DELETE", f"/vendors/{vendor_id}")
    check("Already suspended returns 400", status == 400, f"got {status}")
    check("Error mentions suspended", "suspended" in str(data.get("detail", "")).lower())
    print(f"  -> Response: {data}")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 11: Delete non-existing vendor
# =============================================================
print("\n=== TEST 11: Delete non-existing vendor ===")
fake_vid = str(uuid.uuid4())
status, data = api("DELETE", f"/vendors/{fake_vid}")
check("Non-existing vendor returns 404", status == 404, f"got {status}")
check("Error mentions not found", "not found" in str(data.get("detail", "")).lower())
print(f"  -> Response: {data}")


# =============================================================
# TEST 12: Verify database state (soft-delete preserved)
# =============================================================
print("\n=== TEST 12: Verify soft-deleted vendor in DB ===")
if vendor_id:
    status, data = api("GET", f"/vendors/{vendor_id}")
    check("GET suspended vendor returns 200", status == 200, f"got {status}")
    check("Vendor still exists in DB", data.get("vendor_id") == vendor_id)
    check("status is suspended in DB", data.get("status") == "suspended")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 13: User module regression
# =============================================================
print("\n=== TEST 13: User module regression ===")
status, data = api("GET", "/users")
check("GET /users still works", status == 200, f"got {status}")
if isinstance(data, list) and len(data) > 0:
    check("User has role_name", "role_name" in data[0])


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
