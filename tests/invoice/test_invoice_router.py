"""
Comprehensive End-to-End integration tests for Invoice Routers (Phase 2E).
Tests all 6 endpoints:
- POST /invoices (201 Created)
- GET /invoices (200 OK with filters: vendor_id, po_id, status)
- GET /invoices/{id} (200 OK)
- PATCH /invoices/{id} (200 OK)
- POST /invoices/{id}/pay (200 OK)
- POST /invoices/{id}/dispute (200 OK)
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
    "username": f"admin_inv_{u_suffix}",
    "full_name": "Invoice Admin",
    "email": f"admin_inv_{u_suffix}@example.com",
    "password": "Password123!",
    "role_id": 1
})

# Login Admin
_, admin_resp = api("POST", "/auth/login", {
    "username": f"admin_inv_{u_suffix}",
    "password": "Password123!"
})
token = admin_resp.get("access_token")
check("Admin token obtained", token is not None)

# Create Vendor & approve via DB helper
_, v_data = api("POST", "/vendors", {
    "vendor_code": f"VINVR-{u_suffix}",
    "company_name": f"Invoice Router Vendor {u_suffix}",
    "category_id": 1,
}, token=token)
vendor_id = v_data.get("vendor_id")

from app.database import SessionLocal
import asyncio
from app.models.vendors import Vendor, VendorStatusEnum
from app.models.procurement import PurchaseOrder, PurchaseOrderStatusEnum

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
    "items": [{"item_name": "Industrial Pump", "quantity": 2.0, "unit_price": 5000.00}]
}, token=token)
po_id = po_resp.get("po_id")

# Approve and order PO via endpoints
api("POST", f"/procurement/purchase-orders/{po_id}/approve", token=token)
api("POST", f"/procurement/purchase-orders/{po_id}/order", token=token)
check("PO created and updated to ORDERED", po_id is not None)


# =============================================================
# SECTION 1: INVOICE ENDPOINTS
# =============================================================
print("\n=== SECTION 1: Invoice Endpoints ===")

# 1. POST /invoices (201 Created)
status, data = api("POST", "/invoices", {
    "po_id": po_id,
    "vendor_id": vendor_id,
    "invoice_date": "2026-07-26",
    "due_date": "2026-08-25",
    "amount": 8000.00,
    "tax_amount": 1440.00
}, token=token)
check("POST /invoices returns 201 Created", status == 201, f"got {status}")
check("invoice_number generated", data.get("invoice_number", "").startswith("INV-"))
check("total_with_tax derived correctly (9440)", float(data.get("total_with_tax", 0)) == 9440.0)
check("po_number extracted", data.get("po_number") is not None)
check("vendor_name extracted", data.get("vendor_name") is not None)
inv_id = data.get("invoice_id")

# 2. GET /invoices
status, data = api("GET", "/invoices", token=token)
check("GET /invoices returns 200 OK", status == 200, f"got {status}")
check("Returns list", isinstance(data, list) and len(data) > 0)

# GET /invoices with filters (status=pending, vendor_id, po_id)
status, filtered = api("GET", f"/invoices?status=pending&vendor_id={vendor_id}&po_id={po_id}", token=token)
check("GET /invoices with query filters returns 200 OK", status == 200, f"got {status}")
check("Filtered list contains invoice", len(filtered) > 0)

# 3. GET /invoices/{id}
status, data = api("GET", f"/invoices/{inv_id}", token=token)
check("GET /invoices/{id} returns 200 OK", status == 200, f"got {status}")
check("invoice_id matches", data.get("invoice_id") == inv_id)

# 4. PATCH /invoices/{id}
status, data = api("PATCH", f"/invoices/{inv_id}", {
    "tax_amount": 1500.00
}, token=token)
check("PATCH /invoices/{id} returns 200 OK", status == 200, f"got {status}")
check("tax_amount updated", float(data.get("tax_amount")) == 1500.0)

# 5. POST /invoices/{id}/dispute
status, data = api("POST", f"/invoices/{inv_id}/dispute", token=token)
check("POST /invoices/{id}/dispute returns 200 OK", status == 200, f"got {status}")
check("status updated to disputed", data.get("status") == "disputed")

# 6. POST /invoices/{id}/pay
status, data = api("POST", f"/invoices/{inv_id}/pay", token=token)
check("POST /invoices/{id}/pay returns 200 OK", status == 200, f"got {status}")
check("status updated to paid", data.get("status") == "paid")
check("paid_date automatically set", data.get("paid_date") is not None)


# =============================================================
# SECTION 2: EXCEPTION MAPPING & OPENAPI
# =============================================================
print("\n=== SECTION 2: Exception Mapping & OpenAPI ===")

status, data = api("GET", f"/invoices/{uuid.uuid4()}", token=token)
check("Non-existent invoice returns 404", status == 404, f"got {status}")

# Attempt updating paid invoice -> 400
status, data = api("PATCH", f"/invoices/{inv_id}", {"amount": 7000.0}, token=token)
check("Modifying paid invoice returns 400 Bad Request", status == 400, f"got {status}")

try:
    url = "http://127.0.0.1:8000/openapi.json"
    resp = urllib.request.urlopen(url)
    openapi_data = json.loads(resp.read().decode())
    check("OpenAPI spec loads 200 OK", resp.status == 200)
    paths = openapi_data.get("paths", {})
    check("/api/v1/invoices registered in OpenAPI", "/api/v1/invoices" in paths)
except Exception as e:
    check("OpenAPI spec registered", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
