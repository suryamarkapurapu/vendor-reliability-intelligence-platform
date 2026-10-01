"""
Unit tests for InvoiceService business logic (Phase 2D).
Tests:
- create_invoice auto invoice_number generation
- PO status validation (ORDERED, DELIVERED, COMPLETED required)
- Vendor alignment validation (invoice vendor == PO vendor)
- Amount cap validation (invoice amount <= PO total_amount)
- Automatic paid_date assignment on status=PAID
- Terminal status protection on PAID invoices
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.services.invoice_service import invoice_service
from app.services.procurement_service import procurement_service
from app.services.vendor_service import vendor_service
from app.repositories.user_repository import user_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.procurement_repository import procurement_repository
from app.schemas.invoices import InvoiceCreate, InvoiceUpdate
from app.models.vendors import VendorStatusEnum
from app.models.procurement import PurchaseOrderStatusEnum
from app.models.invoices import InvoiceStatusEnum
from app.core.exceptions import (
    InvalidInvoiceDataError,
    InvoiceNotFoundError,
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

        # Get active user
        users = await user_repository.get_all_users(db, limit=1)
        user_id = users[0].user_id

        # Create approved vendor
        vendor = await vendor_repository.create_vendor(db, {
            "vendor_code": f"VSRV-{u}",
            "company_name": f"Service Vendor {u}",
            "category_id": 1,
            "status": VendorStatusEnum.APPROVED,
        })
        vendor_id = vendor.vendor_id

        # Create PO with status PENDING ($10,000 total)
        po_pending = await procurement_repository.create_purchase_order(
            db,
            {
                "po_number": f"PO-SRV-P-{u}",
                "vendor_id": vendor_id,
                "created_by": user_id,
                "status": PurchaseOrderStatusEnum.PENDING,
            },
            [{"item_name": "Equipment", "quantity": 1.0, "unit_price": 10000.00}],
        )

        # -------------------------------------------------------------
        # TEST 1: Reject Invoice for PENDING PO
        # -------------------------------------------------------------
        print("\n=== TEST 1: PO Status Validation ===")
        ic_pending_po = InvoiceCreate(
            po_id=po_pending.po_id,
            vendor_id=vendor_id,
            invoice_date=date.today(),
            amount=Decimal("5000.00"),
        )
        try:
            await invoice_service.create_invoice(db, ic_pending_po)
            check("Rejects invoice for PENDING PO", False, "No exception raised")
        except InvalidInvoiceDataError as e:
            check("Rejects invoice for PENDING PO", True, str(e))

        # Update PO status to ORDERED
        po_ordered = await procurement_repository.update_purchase_order(
            db, po_pending, {"status": PurchaseOrderStatusEnum.ORDERED}
        )

        # -------------------------------------------------------------
        # TEST 2: Vendor Alignment Validation
        # -------------------------------------------------------------
        print("\n=== TEST 2: Vendor Alignment Validation ===")
        wrong_vendor_id = uuid.uuid4()
        ic_wrong_vendor = InvoiceCreate(
            po_id=po_ordered.po_id,
            vendor_id=wrong_vendor_id,
            invoice_date=date.today(),
            amount=Decimal("5000.00"),
        )
        try:
            await invoice_service.create_invoice(db, ic_wrong_vendor)
            check("Rejects invoice with mismatched vendor_id", False, "No exception raised")
        except InvalidInvoiceDataError as e:
            check("Rejects invoice with mismatched vendor_id", True, str(e))

        # -------------------------------------------------------------
        # TEST 3: Amount Cap Validation
        # -------------------------------------------------------------
        print("\n=== TEST 3: Amount Cap Validation ===")
        ic_over_amount = InvoiceCreate(
            po_id=po_ordered.po_id,
            vendor_id=vendor_id,
            invoice_date=date.today(),
            amount=Decimal("15000.00"),  # Exceeds PO total $10,000
        )
        try:
            await invoice_service.create_invoice(db, ic_over_amount)
            check("Rejects invoice amount exceeding PO total_amount", False, "No exception raised")
        except InvalidInvoiceDataError as e:
            check("Rejects invoice amount exceeding PO total_amount", True, str(e))

        # -------------------------------------------------------------
        # TEST 4: Successful Invoice Creation
        # -------------------------------------------------------------
        print("\n=== TEST 4: Successful Invoice Creation ===")
        ic_valid = InvoiceCreate(
            po_id=po_ordered.po_id,
            vendor_id=vendor_id,
            invoice_date=date.today(),
            amount=Decimal("8000.00"),
            tax_amount=Decimal("1440.00"),
        )
        inv = await invoice_service.create_invoice(db, ic_valid)
        check("create_invoice succeeds", inv is not None)
        check("invoice_number generated", inv.invoice_number.startswith("INV-"))
        check("status defaults to PENDING", inv.status == InvoiceStatusEnum.PENDING)
        inv_id = inv.invoice_id

        # -------------------------------------------------------------
        # TEST 5: Payment Workflow & Automatic paid_date
        # -------------------------------------------------------------
        print("\n=== TEST 5: Payment Workflow & Terminal Status ===")
        paid_inv = await invoice_service.update_invoice_status(db, inv_id, InvoiceStatusEnum.PAID)
        check("status updated to PAID", paid_inv.status == InvoiceStatusEnum.PAID)
        check("paid_date set automatically to today", paid_inv.paid_date == date.today())

        # Attempt updating PAID invoice -> should fail
        try:
            await invoice_service.update_invoice(db, inv_id, InvoiceUpdate(amount=Decimal("7000.00")))
            check("Rejects modifying PAID invoice", False, "No exception raised")
        except InvalidInvoiceDataError as e:
            check("Rejects modifying PAID invoice", True, str(e))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
