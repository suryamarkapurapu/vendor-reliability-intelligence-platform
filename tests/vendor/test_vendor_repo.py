"""
End-to-end tests for Vendor Repository improvements (Phase 2B).
Tests: create, get_by_id, get_all, update — verifying category_name
serialization and no MissingGreenlet errors.
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
# TEST 1: Create vendor
# =============================================================
print("\n=== TEST 1: POST /vendors (create) ===")
unique = str(uuid.uuid4())[:8]
status, data = api("POST", "/vendors", {
    "vendor_code": f"VR-{unique}",
    "company_name": f"RepoTest Corp {unique}",
    "category_id": 1,
    "tax_id": "TAX-123",
    "city": "Mumbai",
    "country": "India",
})
check("Create returns 201", status == 201, f"got {status}")
if status == 201:
    check("vendor_id present", data.get("vendor_id") is not None)
    check("vendor_code correct", data.get("vendor_code") == f"VR-{unique}")
    check("category_id correct", data.get("category_id") == 1)
    check("category_name present", data.get("category_name") is not None, f"got {data.get('category_name')}")
    check("category_name is a string", isinstance(data.get("category_name"), str))
    check("status is pending", data.get("status") == "pending")
    check("created_at present", data.get("created_at") is not None)
    check("updated_at present", data.get("updated_at") is not None)
    vendor_id = data["vendor_id"]
    print(f"  -> category_name = {data.get('category_name')}")
    print(f"  -> vendor_id = {vendor_id}")
else:
    print(f"  -> Error: {data}")
    vendor_id = None


# =============================================================
# TEST 2: Get vendor by ID
# =============================================================
print("\n=== TEST 2: GET /vendors/{{id}} ===")
if vendor_id:
    status, data = api("GET", f"/vendors/{vendor_id}")
    check("GET by ID returns 200", status == 200, f"got {status}")
    check("vendor_id matches", data.get("vendor_id") == vendor_id)
    check("category_name present", data.get("category_name") is not None)
    check("city preserved", data.get("city") == "Mumbai")
    check("tax_id preserved", data.get("tax_id") == "TAX-123")
    print(f"  -> category_name = {data.get('category_name')}")
else:
    print("  [SKIP] No vendor_id from create")


# =============================================================
# TEST 3: Get all vendors
# =============================================================
print("\n=== TEST 3: GET /vendors (list) ===")
status, data = api("GET", "/vendors")
check("GET all returns 200", status == 200, f"got {status}")
check("Returns a list", isinstance(data, list))
if isinstance(data, list) and len(data) > 0:
    first = data[0]
    check("First vendor has category_name", "category_name" in first, f"keys: {list(first.keys())}")
    check("category_name is populated", first.get("category_name") is not None)
    print(f"  -> {len(data)} vendors returned")
    print(f"  -> First vendor category_name = {first.get('category_name')}")
else:
    check("Has at least one vendor", False, f"got {len(data) if isinstance(data, list) else 'not a list'}")


# =============================================================
# TEST 4: Update vendor
# =============================================================
print("\n=== TEST 4: PUT /vendors/{{id}} (update) ===")
if vendor_id:
    status, data = api("PUT", f"/vendors/{vendor_id}", {
        "company_name": f"Updated Corp {unique}",
        "city": "Delhi",
    })
    check("UPDATE returns 200", status == 200, f"got {status}")
    if status == 200:
        check("company_name updated", data.get("company_name") == f"Updated Corp {unique}")
        check("city updated", data.get("city") == "Delhi")
        check("category_name still present after update", data.get("category_name") is not None)
        check("updated_at present", data.get("updated_at") is not None)
        check("created_at still present", data.get("created_at") is not None)
        print(f"  -> category_name = {data.get('category_name')}")
    else:
        print(f"  -> Error: {data}")
else:
    print("  [SKIP] No vendor_id from create")


# =============================================================
# TEST 5: Verify no MissingGreenlet (check server logs)
# =============================================================
print("\n=== TEST 5: Verify no HTTP 500 errors ===")
if vendor_id:
    # Re-fetch to verify serialization works cleanly
    status, data = api("GET", f"/vendors/{vendor_id}")
    check("Final GET returns 200 (no 500)", status == 200, f"got {status}")
    check("All fields serialize correctly", all(k in data for k in [
        "vendor_id", "vendor_code", "company_name", "category_id",
        "category_name", "status", "created_at", "updated_at"
    ]))


# =============================================================
# TEST 6: User module regression check
# =============================================================
print("\n=== TEST 6: User module regression check ===")
status, data = api("GET", "/users")
check("GET /users still works", status == 200, f"got {status}")
if isinstance(data, list) and len(data) > 0:
    first_user = data[0]
    check("User has role_name", "role_name" in first_user)
    print(f"  -> {len(data)} users, first role_name = {first_user.get('role_name')}")


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
