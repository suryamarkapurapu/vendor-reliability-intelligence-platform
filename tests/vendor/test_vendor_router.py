"""
End-to-end tests for Vendor Router Layer (Phase 2D).
Tests:
- POST /vendors (Create)
- GET /vendors (Get All)
- GET /vendors/code/{vendor_code} (Get By Code)
- GET /vendors/{vendor_id} (Get By ID)
- PUT /vendors/{vendor_id} (Update)
- DELETE /vendors/{vendor_id} (Soft-Delete)
- Invalid linked_user_id handling (404)
- Path conflict & route ordering validation
- OpenAPI / docs validation
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
# TEST 1: POST /vendors (Create)
# =============================================================
print("\n=== TEST 1: POST /vendors (Create) ===")
u = str(uuid.uuid4())[:8]
vendor_code = f"VND-{u}"
status, data = api("POST", "/vendors", {
    "vendor_code": vendor_code,
    "company_name": f"Router Test Corp {u}",
    "category_id": 1,
    "city": "Bengaluru",
})
check("POST /vendors returns 201 Created", status == 201, f"got {status}")
if status == 201:
    vendor_id = data.get("vendor_id")
    check("vendor_id present", vendor_id is not None)
    check("vendor_code matches", data.get("vendor_code") == vendor_code)
    check("status defaults to pending", data.get("status") == "pending")
    check("category_name present", data.get("category_name") is not None)
    print(f"  -> Created vendor_id: {vendor_id}")
else:
    vendor_id = None
    print(f"  -> Error: {data}")


# =============================================================
# TEST 2: GET /vendors (Get All)
# =============================================================
print("\n=== TEST 2: GET /vendors (Get All) ===")
status, data = api("GET", "/vendors")
check("GET /vendors returns 200 OK", status == 200, f"got {status}")
check("Returns a list", isinstance(data, list))
if isinstance(data, list) and len(data) > 0:
    check("Items have category_name", "category_name" in data[0])
    print(f"  -> Total vendors in DB: {len(data)}")


# =============================================================
# TEST 3: GET /vendors/code/{vendor_code} (Get By Code)
# =============================================================
print("\n=== TEST 3: GET /vendors/code/{vendor_code} (Get By Code) ===")
if vendor_code:
    status, data = api("GET", f"/vendors/code/{vendor_code}")
    check("GET /vendors/code/{code} returns 200 OK", status == 200, f"got {status}")
    if status == 200:
        check("vendor_code matches", data.get("vendor_code") == vendor_code)
        check("vendor_id matches", data.get("vendor_id") == vendor_id)
        check("category_name present", data.get("category_name") is not None)
        print(f"  -> Successfully fetched by code: {vendor_code}")
    else:
        print(f"  -> Error: {data}")
else:
    print("  [SKIP] No vendor_code")


# =============================================================
# TEST 4: GET /vendors/{vendor_id} (Get By ID)
# =============================================================
print("\n=== TEST 4: GET /vendors/{vendor_id} (Get By ID) ===")
if vendor_id:
    status, data = api("GET", f"/vendors/{vendor_id}")
    check("GET /vendors/{id} returns 200 OK", status == 200, f"got {status}")
    if status == 200:
        check("vendor_id matches", data.get("vendor_id") == vendor_id)
        check("city matches", data.get("city") == "Bengaluru")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 5: Verify Route Conflict Avoidance (code vs uuid)
# =============================================================
print("\n=== TEST 5: Path Conflict Verification ===")
status, data = api("GET", "/vendors/code/NON_EXISTENT_CODE_999")
check("GET non-existent code returns 404", status == 404, f"got {status}")
check("Error detail mentions not found", "not found" in str(data.get("detail", "")).lower())


# =============================================================
# TEST 6: PUT /vendors/{vendor_id} (Update)
# =============================================================
print("\n=== TEST 6: PUT /vendors/{vendor_id} (Update) ===")
if vendor_id:
    status, data = api("PUT", f"/vendors/{vendor_id}", {
        "company_name": f"Updated Router Corp {u}",
        "city": "Hyderabad",
    })
    check("PUT /vendors/{id} returns 200 OK", status == 200, f"got {status}")
    if status == 200:
        check("company_name updated", data.get("company_name") == f"Updated Router Corp {u}")
        check("city updated", data.get("city") == "Hyderabad")
        check("category_name preserved", data.get("category_name") is not None)
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 7: Invalid linked_user_id exception propagation (404)
# =============================================================
print("\n=== TEST 7: Invalid linked_user_id (404 handling) ===")
fake_uid = str(uuid.uuid4())
status, data = api("POST", "/vendors", {
    "vendor_code": f"BADUSR-{u}",
    "company_name": "Bad User Corp",
    "category_id": 1,
    "linked_user_id": fake_uid,
})
check("Invalid linked_user returns 404 (not 500)", status == 404, f"got {status}")
check("Detail mentions user not found", "user" in str(data.get("detail", "")).lower())


# =============================================================
# TEST 8: DELETE /vendors/{vendor_id} (Soft-Delete)
# =============================================================
print("\n=== TEST 8: DELETE /vendors/{vendor_id} (Soft-Delete) ===")
if vendor_id:
    status, data = api("DELETE", f"/vendors/{vendor_id}")
    check("DELETE /vendors/{id} returns 200 OK", status == 200, f"got {status}")
    if status == 200:
        check("status changed to suspended", data.get("status") == "suspended")
        check("vendor_id preserved", data.get("vendor_id") == vendor_id)
        check("category_name preserved", data.get("category_name") is not None)
        print(f"  -> Soft-deleted vendor status: {data.get('status')}")
else:
    print("  [SKIP] No vendor_id")


# =============================================================
# TEST 9: DELETE already suspended vendor (400)
# =============================================================
print("\n=== TEST 9: DELETE already suspended vendor (400) ===")
if vendor_id:
    status, data = api("DELETE", f"/vendors/{vendor_id}")
    check("Deleting already suspended vendor returns 400 Bad Request", status == 400, f"got {status}")
    check("Detail mentions suspended", "suspended" in str(data.get("detail", "")).lower())


# =============================================================
# TEST 10: DELETE non-existing vendor (404)
# =============================================================
print("\n=== TEST 10: DELETE non-existing vendor (404) ===")
status, data = api("DELETE", f"/vendors/{str(uuid.uuid4())}")
check("DELETE non-existing vendor returns 404", status == 404, f"got {status}")


# =============================================================
# TEST 11: OpenAPI Swagger Docs Check
# =============================================================
print("\n=== TEST 11: OpenAPI Docs renders correctly ===")
try:
    url = "http://127.0.0.1:8000/openapi.json"
    resp = urllib.request.urlopen(url)
    openapi_data = json.loads(resp.read().decode())
    check("OpenAPI spec loads 200 OK", resp.status == 200)
    paths = openapi_data.get("paths", {})
    check("/api/v1/vendors path registered", "/api/v1/vendors" in paths)
    check("/api/v1/vendors/code/{vendor_code} path registered", "/api/v1/vendors/code/{vendor_code}" in paths)
    check("/api/v1/vendors/{vendor_id} path registered", "/api/v1/vendors/{vendor_id}" in paths)
    delete_op = paths.get("/api/v1/vendors/{vendor_id}", {}).get("delete")
    check("DELETE operation registered under /vendors/{vendor_id}", delete_op is not None)
except Exception as e:
    check("OpenAPI spec loads", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
