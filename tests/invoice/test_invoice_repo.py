"""
Integration test for InvoiceRepository (Phase 2C).
Tests:
- create_invoice & scalar + relationship refresh
- get_invoice_by_id with selectinload(purchase_order) and selectinload(vendor)
- get_invoice_by_number
- get_all_invoices with status & vendor filtering
- update_invoice
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
from app.repositories.invoice_repository import invoice_repository
from app.repositories.procurement_repository import procurement_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.models.invoices import InvoiceStatusEnum

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
                "vendor_code": f"VINV-{u}",
                "company_name": f"Invoice Vendor {u}",
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
                    "po_number": f"PO-INV-{u}",
                    "vendor_id": vendor_id,
                    "created_by": user_id,
                },
                [{"item_name": "Item A", "quantity": 5.0, "unit_price": 100.0}],
            )
            po_id = po.po_id
        else:
            po_id = pos[0].po_id

        # -------------------------------------------------------------
        # TEST 1: create_invoice & scalar/relationship refresh
        # -------------------------------------------------------------
        print("\n=== TEST 1: create_invoice ===")
        inv_num = f"INV-{u}"
        inv = await invoice_repository.create_invoice(db, {
            "invoice_number": inv_num,
            "po_id": po_id,
            "vendor_id": vendor_id,
            "invoice_date": date.today(),
            "amount": 5000.00,
            "tax_amount": 900.00,
            "status": InvoiceStatusEnum.PENDING,
        })
        check("create_invoice returns Invoice", inv is not None)
        check("invoice_number matches", inv.invoice_number == inv_num)
        check("purchase_order relationship refreshed", inv.purchase_order is not None)
        check("vendor relationship refreshed", inv.vendor is not None)
        inv_id = inv.invoice_id

        # -------------------------------------------------------------
        # TEST 2: get_invoice_by_id with selectinload
        # -------------------------------------------------------------
        print("\n=== TEST 2: get_invoice_by_id with Eager Loading ===")
        fetched_inv = await invoice_repository.get_invoice_by_id(db, inv_id)
        check("get_invoice_by_id returns Invoice", fetched_inv is not None)
        check("po_number loaded via purchase_order relationship", fetched_inv.purchase_order.po_number is not None)
        check("company_name loaded via vendor relationship", isinstance(fetched_inv.vendor.company_name, str))

        # -------------------------------------------------------------
        # TEST 3: get_invoice_by_number
        # -------------------------------------------------------------
        print("\n=== TEST 3: get_invoice_by_number ===")
        by_num = await invoice_repository.get_invoice_by_number(db, inv_num)
        check("get_invoice_by_number returns Invoice", by_num is not None)
        check("invoice_id matches", by_num.invoice_id == inv_id)

        # -------------------------------------------------------------
        # TEST 4: get_all_invoices with filters
        # -------------------------------------------------------------
        print("\n=== TEST 4: get_all_invoices with Filtering ===")
        all_invs = await invoice_repository.get_all_invoices(db, status=InvoiceStatusEnum.PENDING)
        check("get_all_invoices returns list", isinstance(all_invs, list) and len(all_invs) > 0)
        check("Filtered item has purchase_order relationship", all_invs[0].purchase_order is not None)

        # -------------------------------------------------------------
        # TEST 5: update_invoice
        # -------------------------------------------------------------
        print("\n=== TEST 5: update_invoice ===")
        updated_inv = await invoice_repository.update_invoice(db, fetched_inv, {"tax_amount": 950.00})
        check("update_invoice updates tax_amount", float(updated_inv.tax_amount) == 950.00)
        check("updated_inv retains loaded purchase_order", updated_inv.purchase_order is not None)

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
