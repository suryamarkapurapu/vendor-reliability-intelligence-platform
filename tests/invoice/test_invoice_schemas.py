"""
Unit tests for Invoice Pydantic schemas (Phase 2B).
Tests: extra field rejection, server-managed field exclusions, ORM mock serialization, derived total_with_tax calculation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import sys
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock
from pydantic import ValidationError

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


from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
)
from app.models.invoices import InvoiceStatusEnum


# =============================================================
# TEST 1: InvoiceCreate Rejects Extra & Server-Managed Fields
# =============================================================
print("\n=== TEST 1: InvoiceCreate Rejects Extra Fields ===")

po_id = uuid.uuid4()
vendor_id = uuid.uuid4()

try:
    InvoiceCreate(
        po_id=po_id,
        vendor_id=vendor_id,
        invoice_date=date.today(),
        amount=Decimal("1000.00"),
        invoice_number="INV-FORBIDDEN-001",  # Server-managed field
    )
    check("Rejects server-managed field invoice_number", False, "No error raised")
except ValidationError:
    check("Rejects server-managed field invoice_number", True)

try:
    InvoiceCreate(
        po_id=po_id,
        vendor_id=vendor_id,
        invoice_date=date.today(),
        amount=Decimal("1000.00"),
        status="paid",  # Server-managed field
    )
    check("Rejects server-managed field status", False, "No error raised")
except ValidationError:
    check("Rejects server-managed field status", True)

# Valid Create
try:
    ic = InvoiceCreate(
        po_id=po_id,
        vendor_id=vendor_id,
        invoice_date=date.today(),
        amount=Decimal("5000.00"),
        tax_amount=Decimal("900.00"),
    )
    check("Valid InvoiceCreate works", ic.amount == Decimal("5000.00"))
except Exception as e:
    check("Valid InvoiceCreate works", False, str(e))


# =============================================================
# TEST 2: InvoiceResponse Derived & Nested Field Extraction
# =============================================================
print("\n=== TEST 2: InvoiceResponse Derived & Relationship Extraction ===")

mock_po = MagicMock()
mock_po.po_number = "PO-2026-TEST01"

mock_vendor = MagicMock()
mock_vendor.company_name = "Global Logistics Ltd"

mock_inv = MagicMock()
mock_inv.invoice_id = uuid.uuid4()
mock_inv.invoice_number = "INV-2026-TEST01"
mock_inv.po_id = po_id
mock_inv.purchase_order = mock_po
mock_inv.vendor_id = vendor_id
mock_inv.vendor = mock_vendor
mock_inv.invoice_date = date.today()
mock_inv.due_date = date.today()
mock_inv.amount = Decimal("10000.00")
mock_inv.tax_amount = Decimal("1800.00")
mock_inv.status = InvoiceStatusEnum.PENDING
mock_inv.paid_date = None
mock_inv.created_at = datetime.now(timezone.utc)

try:
    res = InvoiceResponse.model_validate(mock_inv, from_attributes=True)
    check("InvoiceResponse ORM serialization works", res.invoice_number == "INV-2026-TEST01")
    check("po_number extracted from purchase_order relationship", res.po_number == "PO-2026-TEST01")
    check("vendor_name extracted from vendor relationship", res.vendor_name == "Global Logistics Ltd")
    check("Derived total_with_tax calculated (10000 + 1800 = 11800)", res.total_with_tax == Decimal("11800.00"))
except Exception as e:
    check("InvoiceResponse ORM serialization works", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
