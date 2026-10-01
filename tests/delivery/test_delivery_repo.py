"""
Integration test for DeliveryRepository (Phase 2C).
Tests:
- create_delivery & scalar + relationship refresh
- get_delivery_by_id with nested eager loading selectinload(purchase_order).selectinload(vendor)
- get_deliveries_by_po_id
- get_all_deliveries with filtering
- update_delivery
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from datetime import date

from app.database import SessionLocal
from app.repositories.delivery_repository import delivery_repository
from app.repositories.procurement_repository import procurement_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.models.delivery import DeliveryStatusEnum

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

        # Get existing user & vendor
        users = await user_repository.get_all_users(db, limit=1)
        user_id = users[0].user_id

        vendors = await vendor_repository.get_all_vendors(db, limit=1)
        if not vendors:
            vendor = await vendor_repository.create_vendor(db, {
                "vendor_code": f"VDEL-{u}",
                "company_name": f"Delivery Vendor {u}",
                "category_id": 1,
            })
            vendor_id = vendor.vendor_id
        else:
            vendor_id = vendors[0].vendor_id

        # Get existing PO or create one
        pos = await procurement_repository.get_all_pos(db, limit=1)
        if not pos:
            po = await procurement_repository.create_purchase_order(
                db,
                {
                    "po_number": f"PO-DEL-{u}",
                    "vendor_id": vendor_id,
                    "created_by": user_id,
                },
                [{"item_name": "Cargo Box", "quantity": 10.0, "unit_price": 50.0}],
            )
            po_id = po.po_id
        else:
            po_id = pos[0].po_id

        # -------------------------------------------------------------
        # TEST 1: create_delivery & scalar/relationship refresh
        # -------------------------------------------------------------
        print("\n=== TEST 1: create_delivery ===")
        deliv = await delivery_repository.create_delivery(db, {
            "po_id": po_id,
            "tracking_number": f"TRK-{u}",
            "carrier": "FedEx Express",
            "expected_date": date.today(),
            "delivery_status": DeliveryStatusEnum.NOT_DISPATCHED,
            "remarks": "Handle with care",
        })
        check("create_delivery returns DeliveryTracking", deliv is not None)
        check("tracking_number matches", deliv.tracking_number == f"TRK-{u}")
        check("purchase_order relationship refreshed", deliv.purchase_order is not None)
        deliv_id = deliv.delivery_id

        # -------------------------------------------------------------
        # TEST 2: get_delivery_by_id with nested selectinload
        # -------------------------------------------------------------
        print("\n=== TEST 2: get_delivery_by_id with Eager Loading ===")
        fetched_deliv = await delivery_repository.get_delivery_by_id(db, deliv_id)
        check("get_delivery_by_id returns record", fetched_deliv is not None)
        check("po_number loaded via purchase_order relationship", fetched_deliv.purchase_order.po_number is not None)
        check("vendor_name loaded via purchase_order.vendor relationship", fetched_deliv.purchase_order.vendor is not None)

        # -------------------------------------------------------------
        # TEST 3: get_deliveries_by_po_id
        # -------------------------------------------------------------
        print("\n=== TEST 3: get_deliveries_by_po_id ===")
        po_deliveries = await delivery_repository.get_deliveries_by_po_id(db, po_id)
        check("get_deliveries_by_po_id returns list", isinstance(po_deliveries, list) and len(po_deliveries) > 0)
        check("Contains created delivery_id", any(d.delivery_id == deliv_id for d in po_deliveries))

        # -------------------------------------------------------------
        # TEST 4: get_all_deliveries with filters
        # -------------------------------------------------------------
        print("\n=== TEST 4: get_all_deliveries with Filtering ===")
        all_delivs = await delivery_repository.get_all_deliveries(
            db, po_id=po_id, status=DeliveryStatusEnum.NOT_DISPATCHED, carrier="FedEx"
        )
        check("get_all_deliveries with filters returns list", isinstance(all_delivs, list) and len(all_delivs) > 0)
        check("Filtered record carrier contains FedEx", "FedEx" in all_delivs[0].carrier)

        # -------------------------------------------------------------
        # TEST 5: update_delivery
        # -------------------------------------------------------------
        print("\n=== TEST 5: update_delivery ===")
        updated_deliv = await delivery_repository.update_delivery(db, fetched_deliv, {"remarks": "Fragile shipment"})
        check("update_delivery updates remarks", updated_deliv.remarks == "Fragile shipment")
        check("updated_deliv retains loaded purchase_order", updated_deliv.purchase_order is not None)

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
