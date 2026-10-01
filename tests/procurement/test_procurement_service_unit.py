"""
Unit tests for ProcurementService business logic (Phase 2D).
Tests:
- create_request with auto request_number
- approve_request, reject_request, cancel_request rules
- create_purchase_order with APPROVED vendor requirement
- rejection of PO creation for non-approved vendor
- rejection of PO creation for non-approved request
- automatic PR status conversion to CONVERTED_TO_PO
- PO line items total_amount calculation & relationship loading
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from decimal import Decimal

from app.database import SessionLocal
from app.services.procurement_service import procurement_service
from app.services.vendor_service import vendor_service
from app.repositories.user_repository import user_repository
from app.schemas.procurement import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    PurchaseOrderCreate,
    PurchaseOrderItemCreate,
)
from app.schemas.vendor import VendorCreate
from app.models.vendors import VendorStatusEnum
from app.models.procurement import RequestStatusEnum, PurchaseOrderStatusEnum
from app.core.exceptions import (
    InvalidProcurementDataError,
    ProcurementRequestNotFoundError,
    PurchaseOrderNotFoundError,
    VendorNotFoundError,
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

        # Get an active user
        users = await user_repository.get_all_users(db, limit=1)
        user_id = users[0].user_id

        # -------------------------------------------------------------
        # TEST 1: create_request (auto request_number)
        # -------------------------------------------------------------
        print("\n=== TEST 1: create_request Business Rules ===")
        prc = ProcurementRequestCreate(
            department="Operations",
            item_description="Generator 50kVA",
            quantity=Decimal("1.0"),
            estimated_cost=Decimal("25000.00"),
        )
        req = await procurement_service.create_request(db, prc, user_id)
        check("create_request auto-generates request_number", req.request_number.startswith("PR-"))
        check("status is PENDING", req.status == RequestStatusEnum.PENDING)
        check("requested_by matches current user", req.requested_by == user_id)
        req_id = req.request_id

        # -------------------------------------------------------------
        # TEST 2: approve_request workflow
        # -------------------------------------------------------------
        print("\n=== TEST 2: approve_request Business Rules ===")
        approved_req = await procurement_service.approve_request(db, req_id, user_id)
        check("approve_request sets status to APPROVED", approved_req.status == RequestStatusEnum.APPROVED)
        check("approved_by recorded", approved_req.approved_by == user_id)
        check("approved_at recorded", approved_req.approved_at is not None)

        # Cannot approve twice
        try:
            await procurement_service.approve_request(db, req_id, user_id)
            check("Rejects approving already approved request", False, "No exception raised")
        except InvalidProcurementDataError as e:
            check("Rejects approving already approved request", True, str(e))

        # -------------------------------------------------------------
        # TEST 3: Vendor validation for PO creation
        # -------------------------------------------------------------
        print("\n=== TEST 3: PO Vendor Status Validation ===")
        # Create a pending vendor (NOT approved)
        vc_pending = VendorCreate(
            vendor_code=f"VEND-PEND-{u}",
            company_name=f"Pending Vendor {u}",
            category_id=1,
        )
        pending_vendor = await vendor_service.create_vendor(db, vc_pending)
        check("Pending vendor created", pending_vendor.status == VendorStatusEnum.PENDING)

        # Attempt creating PO for PENDING vendor -> should fail
        poc_bad_vendor = PurchaseOrderCreate(
            vendor_id=pending_vendor.vendor_id,
            request_id=req_id,
            items=[PurchaseOrderItemCreate(item_name="Generator", quantity=Decimal("1"), unit_price=Decimal("25000"))],
        )
        try:
            await procurement_service.create_purchase_order(db, poc_bad_vendor, user_id)
            check("Rejects PO creation for non-APPROVED vendor", False, "No exception raised")
        except InvalidProcurementDataError as e:
            check("Rejects PO creation for non-APPROVED vendor", True, str(e))

        # Approve the vendor
        from app.repositories.vendor_repository import vendor_repository
        approved_vendor = await vendor_repository.update_vendor(db, pending_vendor, {"status": VendorStatusEnum.APPROVED})
        check("Vendor approved for PO creation", approved_vendor.status == VendorStatusEnum.APPROVED)

        # -------------------------------------------------------------
        # TEST 4: Create PO for non-approved PR -> should fail
        # -------------------------------------------------------------
        print("\n=== TEST 4: PO PR Status Validation ===")
        prc_pending = ProcurementRequestCreate(
            department="IT",
            item_description="Laptops 16GB",
            quantity=Decimal("10.0"),
        )
        unapproved_req = await procurement_service.create_request(db, prc_pending, user_id)

        poc_unapproved_pr = PurchaseOrderCreate(
            vendor_id=approved_vendor.vendor_id,
            request_id=unapproved_req.request_id,
            items=[PurchaseOrderItemCreate(item_name="Laptops", quantity=Decimal("10"), unit_price=Decimal("1000"))],
        )
        try:
            await procurement_service.create_purchase_order(db, poc_unapproved_pr, user_id)
            check("Rejects PO creation for non-APPROVED PR", False, "No exception raised")
        except InvalidProcurementDataError as e:
            check("Rejects PO creation for non-APPROVED PR", True, str(e))

        # -------------------------------------------------------------
        # TEST 5: Create PO for APPROVED PR -> success & PR status conversion
        # -------------------------------------------------------------
        print("\n=== TEST 5: PO Creation & PR Auto-Conversion ===")
        poc_valid = PurchaseOrderCreate(
            vendor_id=approved_vendor.vendor_id,
            request_id=req_id,
            payment_terms="Net 30",
            items=[
                PurchaseOrderItemCreate(item_name="Generator 50kVA", quantity=Decimal("1.0"), unit_price=Decimal("24000.00")),
                PurchaseOrderItemCreate(item_name="Installation Kit", quantity=Decimal("1.0"), unit_price=Decimal("1000.00")),
            ],
        )
        po = await procurement_service.create_purchase_order(db, poc_valid, user_id)
        check("create_purchase_order returns PO", po is not None)
        check("po_number auto-generated", po.po_number.startswith("PO-"))
        check("total_amount calculated (24000 + 1000 = 25000)", float(po.total_amount) == 25000.0)
        check("po.status defaults to PENDING", po.status == PurchaseOrderStatusEnum.PENDING)
        check("vendor relationship loaded", po.vendor is not None)
        check("items relationship loaded (2 items)", len(po.items) == 2)

        # Check PR status converted to CONVERTED_TO_PO
        updated_pr = await procurement_service.get_request_by_id(db, req_id)
        check("PR status auto-converted to CONVERTED_TO_PO", updated_pr.status == RequestStatusEnum.CONVERTED_TO_PO)

        # -------------------------------------------------------------
        # TEST 6: Terminal status modification rules
        # -------------------------------------------------------------
        print("\n=== TEST 6: Terminal Status Modification Rules ===")
        # Cannot update PR when CONVERTED_TO_PO
        try:
            await procurement_service.update_request(db, req_id, ProcurementRequestUpdate(department="New Dept"))
            check("Rejects updating PR in CONVERTED_TO_PO status", False, "No exception raised")
        except InvalidProcurementDataError as e:
            check("Rejects updating PR in CONVERTED_TO_PO status", True, str(e))

        # Cancel PO and verify terminal status
        cancelled_po = await procurement_service.update_po_status(db, po.po_id, PurchaseOrderStatusEnum.CANCELLED)
        check("PO status updated to CANCELLED", cancelled_po.status == PurchaseOrderStatusEnum.CANCELLED)

        try:
            await procurement_service.update_po_status(db, po.po_id, PurchaseOrderStatusEnum.ORDERED)
            check("Rejects modifying PO in terminal status CANCELLED", False, "No exception raised")
        except InvalidProcurementDataError as e:
            check("Rejects modifying PO in terminal status CANCELLED", True, str(e))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
