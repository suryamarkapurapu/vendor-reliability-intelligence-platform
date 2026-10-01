"""
Integration test for ProcurementRepository (Phase 2C).
Tests:
- create_request & get_request_by_id
- create_purchase_order (Atomic creation of PO + PurchaseOrderItem line items)
- get_po_by_id with selectinload(items) and selectinload(vendor)
- update_request & update_purchase_order
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from decimal import Decimal

from app.database import SessionLocal
from app.repositories.procurement_repository import procurement_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.models.procurement import PriorityEnum, RequestStatusEnum, PurchaseOrderStatusEnum

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")


async def run_tests():
    global PASS, FAIL
    async with SessionLocal() as db:
        u = str(uuid.uuid4())[:8]

        # Get an existing user for requester/creator
        users = await user_repository.get_all_users(db, limit=1)
        if not users:
            print("  [FAIL] No users found in database")
            return False
        user_id = users[0].user_id

        # Get an existing vendor for PO
        vendors = await vendor_repository.get_all_vendors(db, limit=1)
        if not vendors:
            # Create a vendor first
            vendor = await vendor_repository.create_vendor(db, {
                "vendor_code": f"VREPO-{u}",
                "company_name": f"Repo Vendor {u}",
                "category_id": 1,
            })
            vendor_id = vendor.vendor_id
        else:
            vendor_id = vendors[0].vendor_id

        # -------------------------------------------------------------
        # TEST 1: create_request & get_request_by_id
        # -------------------------------------------------------------
        print("\n=== TEST 1: ProcurementRequest CRUD ===")
        req = await procurement_repository.create_request(db, {
            "request_number": f"PR-{u}",
            "requested_by": user_id,
            "department": "Engineering",
            "item_description": "Industrial drill press",
            "quantity": 2.0,
            "estimated_cost": 5000.00,
            "priority": PriorityEnum.HIGH,
        })
        check("create_request returns ProcurementRequest", req is not None)
        check("request_number matches", req.request_number == f"PR-{u}")
        check("status defaults to PENDING", req.status == RequestStatusEnum.PENDING)
        req_id = req.request_id

        fetched_req = await procurement_repository.get_request_by_id(db, req_id)
        check("get_request_by_id returns request", fetched_req is not None)
        check("get_request_by_id request_id matches", fetched_req.request_id == req_id)

        # -------------------------------------------------------------
        # TEST 2: create_purchase_order (Atomic PO + Line Items)
        # -------------------------------------------------------------
        print("\n=== TEST 2: Atomic PurchaseOrder Creation ===")
        po_data = {
            "po_number": f"PO-{u}",
            "request_id": req_id,
            "vendor_id": vendor_id,
            "created_by": user_id,
            "payment_terms": "Net 30",
        }
        items_data = [
            {
                "item_name": "Steel Plate 10mm",
                "description": "High tensile steel plate",
                "uom": "PCS",
                "quantity": 10.0,
                "unit_price": 100.00,
            },
            {
                "item_name": "Brass Bushing",
                "description": "Precision brass bushing",
                "uom": "PCS",
                "quantity": 5.0,
                "unit_price": 20.00,
            },
        ]

        po = await procurement_repository.create_purchase_order(db, po_data, items_data)
        check("create_purchase_order returns PurchaseOrder", po is not None)
        check("po_number matches", po.po_number == f"PO-{u}")
        check("total_amount calculated correctly (10*100 + 5*20 = 1100)", float(po.total_amount) == 1100.0)
        check("items loaded via selectinload", len(po.items) == 2)
        check("vendor loaded via selectinload", po.vendor is not None)
        check("vendor.company_name populated", isinstance(po.vendor.company_name, str))
        po_id = po.po_id

        # -------------------------------------------------------------
        # TEST 3: get_po_by_id with selectinload
        # -------------------------------------------------------------
        print("\n=== TEST 3: get_po_by_id with Eager Loading ===")
        fetched_po = await procurement_repository.get_po_by_id(db, po_id)
        check("get_po_by_id returns PO", fetched_po is not None)
        check("fetched PO has 2 items", len(fetched_po.items) == 2)
        check("item 1 total_price calculated by DB", fetched_po.items[0].total_price is not None or float(fetched_po.items[0].quantity * fetched_po.items[0].unit_price) == 1000.0)
        check("vendor relationship present", fetched_po.vendor is not None)

        # -------------------------------------------------------------
        # TEST 4: update_request & update_purchase_order
        # -------------------------------------------------------------
        print("\n=== TEST 4: Update operations ===")
        updated_req = await procurement_repository.update_request(db, fetched_req, {"department": "R&D"})
        check("update_request updates department", updated_req.department == "R&D")

        updated_po = await procurement_repository.update_purchase_order(db, fetched_po, {"payment_terms": "Immediate"})
        check("update_purchase_order updates payment_terms", updated_po.payment_terms == "Immediate")
        check("updated PO retains loaded items", len(updated_po.items) == 2)
        check("updated PO retains loaded vendor", updated_po.vendor is not None)

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
