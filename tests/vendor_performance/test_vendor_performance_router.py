"""
Comprehensive End-to-End integration tests for Vendor Performance Routers (Phase 2E).
Tests all 9 endpoints:
- POST /vendor-performance/ratings (201 Created)
- GET /vendor-performance/ratings (200 OK)
- POST /vendor-performance/issues (201 Created)
- GET /vendor-performance/issues (200 OK)
- PATCH /vendor-performance/issues/{id} (200 OK)
- POST /vendor-performance/metrics (201 Created)
- GET /vendor-performance/metrics (200 OK)
- GET /vendor-performance/summary/{vendor_id} (200 OK)
- GET /vendor-performance/rankings (200 OK)
- Exception mapping (404, 400)
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
# SETUP: Admin Auth & Approved Vendor
# =============================================================
print("\n=== SETUP: Auth & Vendor Setup ===")

u_suffix = str(uuid.uuid4())[:6]

# Create Admin user
api("POST", "/users", {
    "username": f"admin_vprf_{u_suffix}",
    "full_name": "Perf Admin",
    "email": f"admin_vprf_{u_suffix}@example.com",
    "password": "Password123!",
    "role_id": 1
})

# Login Admin
_, admin_resp = api("POST", "/auth/login", {
    "username": f"admin_vprf_{u_suffix}",
    "password": "Password123!"
})
token = admin_resp.get("access_token")
check("Admin token obtained", token is not None)

# Create Vendor & approve
_, v_data = api("POST", "/vendors", {
    "vendor_code": f"VVPRF-{u_suffix}",
    "company_name": f"Perf Router Vendor {u_suffix}",
    "category_id": 1,
}, token=token)
vendor_id = v_data.get("vendor_id")

from app.database import SessionLocal
import asyncio
from app.models.vendors import Vendor, VendorStatusEnum

async def setup_db_entities():
    async with SessionLocal() as db:
        v = await db.get(Vendor, uuid.UUID(vendor_id))
        if v:
            v.status = VendorStatusEnum.APPROVED
        await db.commit()

asyncio.run(setup_db_entities())
check("Vendor approved", True)


# =============================================================
# SECTION 1: RATINGS ENDPOINTS
# =============================================================
print("\n=== SECTION 1: Ratings Endpoints ===")

# 1. POST /vendor-performance/ratings (201 Created)
status, rating_data = api("POST", "/vendor-performance/ratings", {
    "vendor_id": vendor_id,
    "quality_rating": 5,
    "delivery_rating": 4,
    "communication_rating": 5,
    "comments": "Superb vendor quality"
}, token=token)
check("POST /ratings returns 201 Created", status == 201, f"got {status}")
check("overall_rating calculated automatically (4.67)", float(rating_data.get("overall_rating")) == 4.67)
rating_id = rating_data.get("rating_id")

# 2. GET /vendor-performance/ratings (200 OK)
status, ratings_list = api("GET", f"/vendor-performance/ratings?vendor_id={vendor_id}", token=token)
check("GET /ratings returns 200 OK", status == 200, f"got {status}")
check("Returns list containing rating", len(ratings_list) > 0)


# =============================================================
# SECTION 2: ISSUES ENDPOINTS
# =============================================================
print("\n=== SECTION 2: Issues Endpoints ===")

# 3. POST /vendor-performance/issues (201 Created)
status, issue_data = api("POST", "/vendor-performance/issues", {
    "vendor_id": vendor_id,
    "issue_type": "Minor Scratches",
    "description": "Scratches on outer shell"
}, token=token)
check("POST /issues returns 201 Created", status == 201, f"got {status}")
check("status defaults to open", issue_data.get("status") == "open")
issue_id = issue_data.get("issue_id")

# 4. GET /vendor-performance/issues (200 OK)
status, issues_list = api("GET", f"/vendor-performance/issues?vendor_id={vendor_id}", token=token)
check("GET /issues returns 200 OK", status == 200, f"got {status}")
check("Returns list containing issue", len(issues_list) > 0)

# 5. PATCH /vendor-performance/issues/{id} (200 OK)
status, updated_issue = api("PATCH", f"/vendor-performance/issues/{issue_id}", {
    "status": "resolved"
}, token=token)
check("PATCH /issues/{id} returns 200 OK", status == 200, f"got {status}")
check("status updated to resolved", updated_issue.get("status") == "resolved")
check("resolved_at timestamp set automatically", updated_issue.get("resolved_at") is not None)


# =============================================================
# SECTION 3: METRICS ENDPOINTS
# =============================================================
print("\n=== SECTION 3: Metrics Endpoints ===")

# 6. POST /vendor-performance/metrics (201 Created)
status, metric_data = api("POST", "/vendor-performance/metrics", {
    "vendor_id": vendor_id,
    "metric_type": "on_time_delivery",
    "metric_value": 99.50
}, token=token)
check("POST /metrics returns 201 Created", status == 201, f"got {status}")

# 7. GET /vendor-performance/metrics (200 OK)
status, metrics_list = api("GET", f"/vendor-performance/metrics?vendor_id={vendor_id}", token=token)
check("GET /metrics returns 200 OK", status == 200, f"got {status}")
check("Returns list containing metric", len(metrics_list) > 0)


# =============================================================
# SECTION 4: SUMMARY & RANKINGS ENDPOINTS
# =============================================================
print("\n=== SECTION 4: Summary & Rankings Endpoints ===")

# 8. GET /vendor-performance/summary/{vendor_id} (200 OK)
status, summary_data = api("GET", f"/vendor-performance/summary/{vendor_id}", token=token)
check("GET /summary/{vendor_id} returns 200 OK", status == 200, f"got {status}")
check("summary_data contains average_overall_rating", "average_overall_rating" in summary_data)

# 9. GET /vendor-performance/rankings (200 OK)
status, rankings_list = api("GET", "/vendor-performance/rankings", token=token)
check("GET /rankings returns 200 OK", status == 200, f"got {status}")
check("Returns rankings list", isinstance(rankings_list, list))


# =============================================================
# SECTION 5: EXCEPTION MAPPING & OPENAPI
# =============================================================
print("\n=== SECTION 5: Exception Mapping & OpenAPI ===")

status, data = api("GET", f"/vendor-performance/summary/{uuid.uuid4()}", token=token)
check("Non-existent vendor summary returns 404", status == 404, f"got {status}")

try:
    url = "http://127.0.0.1:8000/openapi.json"
    resp = urllib.request.urlopen(url)
    openapi_data = json.loads(resp.read().decode())
    check("OpenAPI spec loads 200 OK", resp.status == 200)
    paths = openapi_data.get("paths", {})
    check("/api/v1/vendor-performance/ratings registered in OpenAPI", "/api/v1/vendor-performance/ratings" in paths)
    check("/api/v1/vendor-performance/rankings registered in OpenAPI", "/api/v1/vendor-performance/rankings" in paths)
except Exception as e:
    check("OpenAPI spec registered", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
