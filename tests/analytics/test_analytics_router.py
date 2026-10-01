"""
Comprehensive End-to-End integration tests for Analytics Routers (Phase 2D).
Tests all 6 endpoints:
- GET /analytics/dashboard (200 OK)
- GET /analytics/procurement (200 OK)
- GET /analytics/invoices (200 OK)
- GET /analytics/deliveries (200 OK)
- GET /analytics/vendors (200 OK)
- GET /analytics/system (200 OK)
- OpenAPI spec check (/openapi.json)
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


def api(method, path, body=None, token=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
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
# SETUP: Admin Auth
# =============================================================
print("\n=== SETUP: Admin Auth Setup ===")

u_suffix = str(uuid.uuid4())[:6]

# Create Admin user
api("POST", "/users", {
    "username": f"admin_anl_{u_suffix}",
    "full_name": "Analytics Admin",
    "email": f"admin_anl_{u_suffix}@example.com",
    "password": "Password123!",
    "role_id": 1
})

# Login Admin
_, admin_resp = api("POST", "/auth/login", {
    "username": f"admin_anl_{u_suffix}",
    "password": "Password123!"
})
token = admin_resp.get("access_token")
check("Admin token obtained", token is not None)


# =============================================================
# SECTION 1: ANALYTICS ENDPOINTS
# =============================================================
print("\n=== SECTION 1: Analytics Endpoints ===")

# 1. GET /analytics/dashboard
status, dash_data = api("GET", "/analytics/dashboard", token=token)
check("GET /analytics/dashboard returns 200 OK", status == 200, f"got {status}")
check("Contains total_vendors field", "total_vendors" in dash_data)
check("Contains total_procurement_spend field", "total_procurement_spend" in dash_data)

# 2. GET /analytics/procurement
status, proc_data = api("GET", "/analytics/procurement", token=token)
check("GET /analytics/procurement returns 200 OK", status == 200, f"got {status}")
check("Contains orders_by_status field", "orders_by_status" in proc_data)

# 3. GET /analytics/invoices
status, inv_data = api("GET", "/analytics/invoices", token=token)
check("GET /analytics/invoices returns 200 OK", status == 200, f"got {status}")
check("Contains total_invoiced_amount field", "total_invoiced_amount" in inv_data)

# 4. GET /analytics/deliveries
status, deliv_data = api("GET", "/analytics/deliveries", token=token)
check("GET /analytics/deliveries returns 200 OK", status == 200, f"got {status}")
check("Contains on_time_delivery_rate field", "on_time_delivery_rate" in deliv_data)

# 5. GET /analytics/vendors
status, vendor_data = api("GET", "/analytics/vendors", token=token)
check("GET /analytics/vendors returns 200 OK", status == 200, f"got {status}")
check("Contains top_vendors_by_spend field", "top_vendors_by_spend" in vendor_data)

# 6. GET /analytics/system
status, sys_data = api("GET", "/analytics/system", token=token)
check("GET /analytics/system returns 200 OK", status == 200, f"got {status}")
check("Contains users_by_role field", "users_by_role" in sys_data)


# =============================================================
# SECTION 2: OPENAPI SPECIFICATION
# =============================================================
print("\n=== SECTION 2: OpenAPI Specification ===")

try:
    url = "http://127.0.0.1:8000/openapi.json"
    resp = urllib.request.urlopen(url)
    openapi_data = json.loads(resp.read().decode())
    check("OpenAPI spec loads 200 OK", resp.status == 200)
    paths = openapi_data.get("paths", {})
    check("/api/v1/analytics/dashboard registered in OpenAPI", "/api/v1/analytics/dashboard" in paths)
    check("/api/v1/analytics/system registered in OpenAPI", "/api/v1/analytics/system" in paths)
except Exception as e:
    check("OpenAPI spec registered", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
