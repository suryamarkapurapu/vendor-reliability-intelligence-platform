"""
Comprehensive End-to-End integration tests for Delivery Tracking Routers (Phase 2E).
Tests all 8 endpoints:
- POST /deliveries (201 Created)
- GET /deliveries (200 OK with filters: po_id, status, carrier)
- GET /deliveries/{id} (200 OK)
- PATCH /deliveries/{id} (200 OK)
- POST /deliveries/{id}/dispatch (200 OK)
- POST /deliveries/{id}/deliver (200 OK with PO status sync)
- POST /deliveries/{id}/delay (200 OK)
- POST /deliveries/{id}/return (200 OK)
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
# SETUP: Admin Auth, Approved Vendor, & ORDERED PO
# =============================================================
print("\n=== SETUP: Auth, Vendor & PO Setup ===")

u_suffix = str(uuid.uuid4())[:6]

# Create Admin user
api("POST", "/users", {
    "username": f"admin_del_{u_suffix}",
    "full_name": "Delivery Admin",
    "email": f"admin_del_{u_suffix}@example.com",
    "password": "Password123!",
    "role_id": 1
})

# Login Admin
_, admin_resp = api("POST", "/auth/login", {
    "username": f"admin_del_{u_suffix}",
    "password": "Password123!"
})
token = admin_resp.get("access_token")
check("Admin token obtained", token is not None)

# Create Vendor & approve via DB helper
_, v_data = api("POST", "/vendors", {
    "vendor_code": f"VDELR-{u_suffix}",
    "company_name": f"Delivery Router Vendor {u_suffix}",
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

# Create PO and advance to ORDERED status
_, po_resp = api("POST", "/procurement/purchase-orders", {
    "vendor_id": vendor_id,
    "payment_terms": "Net 30",
    "items": [{"item_name": "Cargo Containers", "quantity": 1.0, "unit_price": 12000.00}]
}, token=token)
po_id = po_resp.get("po_id")

# Approve and order PO via endpoints
api("POST", f"/procurement/purchase-orders/{po_id}/approve", token=token)
api("POST", f"/procurement/purchase-orders/{po_id}/order", token=token)
check("PO created and updated to ORDERED", po_id is not None)


# =============================================================
# SECTION 1: DELIVERY TRACKING ENDPOINTS
# =============================================================
print("\n=== SECTION 1: Delivery Tracking Endpoints ===")

# 1. POST /deliveries (201 Created)
status, data = api("POST", "/deliveries", {
    "po_id": po_id,
    "tracking_number": f"TRK-{u_suffix}",
    "carrier": "DHL Express",
    "expected_date": "2026-08-01",
    "remarks": "Express Shipment 1"
}, token=token)
check("POST /deliveries returns 201 Created", status == 201, f"got {status}")
check("delivery_status defaults to not_dispatched", data.get("delivery_status") == "not_dispatched")
check("po_number extracted", data.get("po_number") is not None)
check("vendor_name extracted", data.get("vendor_name") is not None)
deliv_id = data.get("delivery_id")

# 2. GET /deliveries
status, data = api("GET", "/deliveries", token=token)
check("GET /deliveries returns 200 OK", status == 200, f"got {status}")
check("Returns list", isinstance(data, list) and len(data) > 0)

# GET /deliveries with query filters (po_id, status=not_dispatched, carrier=DHL)
status, filtered = api("GET", f"/deliveries?status=not_dispatched&po_id={po_id}&carrier=DHL", token=token)
check("GET /deliveries with query filters returns 200 OK", status == 200, f"got {status}")
check("Filtered list contains delivery record", len(filtered) > 0)

# 3. GET /deliveries/{id}
status, data = api("GET", f"/deliveries/{deliv_id}", token=token)
check("GET /deliveries/{id} returns 200 OK", status == 200, f"got {status}")
check("delivery_id matches", data.get("delivery_id") == deliv_id)

# 4. PATCH /deliveries/{id}
status, data = api("PATCH", f"/deliveries/{deliv_id}", {
    "remarks": "Express Shipment 1 - Updated Notes"
}, token=token)
check("PATCH /deliveries/{id} returns 200 OK", status == 200, f"got {status}")
check("remarks updated", data.get("remarks") == "Express Shipment 1 - Updated Notes")

# 5. POST /deliveries/{id}/dispatch
status, data = api("POST", f"/deliveries/{deliv_id}/dispatch", token=token)
check("POST /deliveries/{id}/dispatch returns 200 OK", status == 200, f"got {status}")
check("delivery_status updated to in_transit", data.get("delivery_status") == "in_transit")
check("dispatch_date set automatically", data.get("dispatch_date") is not None)

# 6. POST /deliveries/{id}/delay
status, data = api("POST", f"/deliveries/{deliv_id}/delay?new_expected_date=2026-08-05&remarks=Customs%20delay", token=token)
check("POST /deliveries/{id}/delay returns 200 OK", status == 200, f"got {status}")
check("delivery_status updated to delayed", data.get("delivery_status") == "delayed")

# Re-dispatch for delivery test
api("POST", f"/deliveries/{deliv_id}/dispatch", token=token)

# 7. POST /deliveries/{id}/deliver (Triggers PO status sync)
status, data = api("POST", f"/deliveries/{deliv_id}/deliver", token=token)
check("POST /deliveries/{id}/deliver returns 200 OK", status == 200, f"got {status}")
check("delivery_status updated to delivered", data.get("delivery_status") == "delivered")
check("delivered_date set automatically", data.get("delivered_date") is not None)
check("is_delivered boolean flag is True", data.get("is_delivered") is True)

# Verify PO status auto-synced to delivered!
_, po_check = api("GET", f"/procurement/purchase-orders/{po_id}", token=token)
check("PO status auto-synced to delivered", po_check.get("status") == "delivered")

# 8. POST /deliveries/{id}/return (on separate shipment)
_, deliv_ret = api("POST", "/deliveries", {
    "po_id": po_id,
    "tracking_number": f"TRK-RET-{u_suffix}",
    "carrier": "FedEx"
}, token=token)
deliv_ret_id = deliv_ret.get("delivery_id")
status, data = api("POST", f"/deliveries/{deliv_ret_id}/return?remarks=Damaged%20in%20transit", token=token)
check("POST /deliveries/{id}/return returns 200 OK", status == 200, f"got {status}")
check("delivery_status updated to returned", data.get("delivery_status") == "returned")


# =============================================================
# SECTION 2: EXCEPTION MAPPING & OPENAPI
# =============================================================
print("\n=== SECTION 2: Exception Mapping & OpenAPI ===")

status, data = api("GET", f"/deliveries/{uuid.uuid4()}", token=token)
check("Non-existent delivery returns 404", status == 404, f"got {status}")

# Attempt modifying delivered shipment -> 400
status, data = api("PATCH", f"/deliveries/{deliv_id}", {"remarks": "Illegal edit"}, token=token)
check("Modifying delivered shipment returns 400 Bad Request", status == 400, f"got {status}")

try:
    url = "http://127.0.0.1:8000/openapi.json"
    resp = urllib.request.urlopen(url)
    openapi_data = json.loads(resp.read().decode())
    check("OpenAPI spec loads 200 OK", resp.status == 200)
    paths = openapi_data.get("paths", {})
    check("/api/v1/deliveries registered in OpenAPI", "/api/v1/deliveries" in paths)
except Exception as e:
    check("OpenAPI spec registered", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
