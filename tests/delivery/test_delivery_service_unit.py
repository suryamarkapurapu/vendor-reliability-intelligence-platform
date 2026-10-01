"""
Unit tests for DeliveryService business logic (Phase 2D).
Tests:
- PO status validation (ORDERED status required)
- Dispatch workflow (NOT_DISPATCHED -> IN_TRANSIT with auto dispatch_date)
- Multi-shipment completion & PO status synchronization (PO becomes DELIVERED ONLY when ALL shipments DELIVERED)
- Terminal status protection (DELIVERED & RETURNED cannot be modified)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from datetime import date

from app.database import SessionLocal
from app.services.delivery_service import delivery_service
from app.repositories.procurement_repository import procurement_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.schemas.delivery import DeliveryTrackingCreate, DeliveryTrackingUpdate
from app.models.vendors import VendorStatusEnum
from app.models.procurement import PurchaseOrderStatusEnum
from app.models.delivery import DeliveryStatusEnum
from app.core.exceptions import (
    DeliveryNotFoundError,
    InvalidDeliveryDataError,
    PurchaseOrderNotFoundError,
)

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

        # Get active user & vendor
        users = await user_repository.get_all_users(db, limit=1)
        user_id = users[0].user_id

        vendor = await vendor_repository.create_vendor(db, {
            "vendor_code": f"VDS-PO-{u}",
            "company_name": f"Delivery Sync Vendor {u}",
            "category_id": 1,
            "status": VendorStatusEnum.APPROVED,
        })
        vendor_id = vendor.vendor_id

        # Create PO with PENDING status
        po_pending = await procurement_repository.create_purchase_order(
            db,
            {
                "po_number": f"PO-DS-P-{u}",
                "vendor_id": vendor_id,
                "created_by": user_id,
                "status": PurchaseOrderStatusEnum.PENDING,
            },
            [{"item_name": "Solar Panels", "quantity": 10.0, "unit_price": 500.0}],
        )

        # -------------------------------------------------------------
        # TEST 1: Reject delivery creation for PENDING PO
        # -------------------------------------------------------------
        print("\n=== TEST 1: PO Status Validation ===")
        dtc_pending = DeliveryTrackingCreate(
            po_id=po_pending.po_id,
            tracking_number="TRK-PENDING",
            carrier="DHL",
        )
        try:
            await delivery_service.create_delivery(db, dtc_pending)
            check("Rejects delivery for PENDING PO", False, "No exception raised")
        except InvalidDeliveryDataError as e:
            check("Rejects delivery for PENDING PO", True, str(e))

        # Update PO to ORDERED status
        po_ordered = await procurement_repository.update_purchase_order(
            db, po_pending, {"status": PurchaseOrderStatusEnum.ORDERED}
        )

        # -------------------------------------------------------------
        # TEST 2: Successful delivery creation & dispatch
        # -------------------------------------------------------------
        print("\n=== TEST 2: Delivery Creation & Dispatch Workflow ===")
        dtc1 = DeliveryTrackingCreate(
            po_id=po_ordered.po_id,
            tracking_number=f"TRK1-{u}",
            carrier="DHL Express",
        )
        deliv1 = await delivery_service.create_delivery(db, dtc1)
        check("create_delivery succeeds", deliv1 is not None)
        check("status defaults to NOT_DISPATCHED", deliv1.delivery_status == DeliveryStatusEnum.NOT_DISPATCHED)

        # Dispatch deliv1
        dispatched1 = await delivery_service.dispatch_delivery(db, deliv1.delivery_id)
        check("dispatch_delivery sets status to IN_TRANSIT", dispatched1.delivery_status == DeliveryStatusEnum.IN_TRANSIT)
        check("dispatch_date set automatically to today", dispatched1.dispatch_date == date.today())

        # -------------------------------------------------------------
        # TEST 3: Multi-Shipment Completion & PO Status Synchronization
        # -------------------------------------------------------------
        print("\n=== TEST 3: Multi-Shipment PO Status Synchronization ===")
        # Create second shipment linked to same PO
        dtc2 = DeliveryTrackingCreate(
            po_id=po_ordered.po_id,
            tracking_number=f"TRK2-{u}",
            carrier="FedEx Ground",
        )
        deliv2 = await delivery_service.create_delivery(db, dtc2)
        await delivery_service.dispatch_delivery(db, deliv2.delivery_id)

        # Mark 1st shipment as DELIVERED -> PO status should REMAIN ORDERED (deliv2 still in_transit)
        await delivery_service.mark_delivered(db, deliv1.delivery_id)
        po_after_first = await procurement_repository.get_po_by_id(db, po_ordered.po_id)
        check("PO status remains ORDERED after partial shipment delivery", po_after_first.status == PurchaseOrderStatusEnum.ORDERED)

        # Mark 2nd shipment as DELIVERED -> ALL shipments delivered -> PO status should become DELIVERED!
        await delivery_service.mark_delivered(db, deliv2.delivery_id)
        po_after_all = await procurement_repository.get_po_by_id(db, po_ordered.po_id)
        check("PO status auto-synced to DELIVERED when ALL shipments DELIVERED", po_after_all.status == PurchaseOrderStatusEnum.DELIVERED)

        # -------------------------------------------------------------
        # TEST 4: Terminal Status Protection
        # -------------------------------------------------------------
        print("\n=== TEST 4: Terminal Status Protection ===")
        try:
            await delivery_service.update_delivery(db, deliv1.delivery_id, DeliveryTrackingUpdate(remarks="Attempt update"))
            check("Rejects modifying DELIVERED shipment", False, "No exception raised")
        except InvalidDeliveryDataError as e:
            check("Rejects modifying DELIVERED shipment", True, str(e))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
