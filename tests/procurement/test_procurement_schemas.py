"""
Schema-level unit tests for Procurement Pydantic schemas (Phase 2B).
Tests: extra field rejection, exclusion of server-managed fields, ORM mock serialization.
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


from app.schemas.procurement import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    ProcurementRequestResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderItemCreate,
    PurchaseOrderItemResponse,
)
from app.models.procurement import RequestStatusEnum, PurchaseOrderStatusEnum, PriorityEnum


# =============================================================
# TEST 1: ProcurementRequestCreate extra field rejection & field exclusions
# =============================================================
print("\n=== TEST 1: ProcurementRequestCreate Rejects Extra Fields ===")

try:
    ProcurementRequestCreate(
        item_description="Lathe machine",
        quantity=Decimal("2.0"),
        request_number="PR-FORBIDDEN-001",  # Server-managed field, extra=forbid should reject
    )
    check("Rejects server-managed field request_number", False, "No error raised")
except ValidationError:
    check("Rejects server-managed field request_number", True)

try:
    ProcurementRequestCreate(
        item_description="Lathe machine",
        quantity=Decimal("2.0"),
        status="approved",  # Server-managed field
    )
    check("Rejects server-managed field status", False, "No error raised")
except ValidationError:
    check("Rejects server-managed field status", True)

# Valid create
try:
    prc = ProcurementRequestCreate(
        department="Engineering",
        item_description="Heavy duty machine",
        quantity=Decimal("5.0"),
        estimated_cost=Decimal("12000.00"),
        priority=PriorityEnum.HIGH,
    )
    check("Valid ProcurementRequestCreate works", prc.quantity == Decimal("5.0"))
except Exception as e:
    check("Valid ProcurementRequestCreate works", False, str(e))


# =============================================================
# TEST 2: PurchaseOrderCreate & Line Items
# =============================================================
print("\n=== TEST 2: PurchaseOrderCreate Validation ===")

try:
    PurchaseOrderCreate(
        vendor_id=uuid.uuid4(),
        po_number="PO-FORBIDDEN-001",  # Server-managed field
        items=[PurchaseOrderItemCreate(item_name="Item 1", quantity=Decimal("10"), unit_price=Decimal("5.0"))],
    )
    check("Rejects server-managed field po_number", False, "No error raised")
except ValidationError:
    check("Rejects server-managed field po_number", True)

try:
    PurchaseOrderCreate(
        vendor_id=uuid.uuid4(),
        items=[
            PurchaseOrderItemCreate(
                item_name="Item 1",
                quantity=Decimal("10"),
                unit_price=Decimal("5.0"),
                total_price=Decimal("50.0"),  # Server/DB-managed field
            )
        ],
    )
    check("Rejects total_price on PurchaseOrderItemCreate", False, "No error raised")
except ValidationError:
    check("Rejects total_price on PurchaseOrderItemCreate", True)

# Valid PurchaseOrderCreate
try:
    poc = PurchaseOrderCreate(
        vendor_id=uuid.uuid4(),
        payment_terms="Net 30 Days",
        items=[
            PurchaseOrderItemCreate(
                item_name="Steel Bars 12mm",
                description="High grade steel",
                uom="PCS",
                quantity=Decimal("50.0"),
                unit_price=Decimal("150.00"),
            )
        ],
    )
    check("Valid PurchaseOrderCreate works", len(poc.items) == 1)
except Exception as e:
    check("Valid PurchaseOrderCreate works", False, str(e))


# =============================================================
# TEST 3: PurchaseOrderResponse ORM Serialization with Model Validator
# =============================================================
print("\n=== TEST 3: PurchaseOrderResponse ORM Mock Serialization ===")

now = datetime.now(timezone.utc)
po_id = uuid.uuid4()
v_id = uuid.uuid4()

mock_vendor = MagicMock()
mock_vendor.company_name = "Acme Supplies Ltd"

mock_item = MagicMock()
mock_item.po_item_id = uuid.uuid4()
mock_item.po_id = po_id
mock_item.item_name = "Steel Bars"
mock_item.description = "Line item desc"
mock_item.uom = "PCS"
mock_item.quantity = Decimal("50.0")
mock_item.unit_price = Decimal("150.00")
mock_item.total_price = Decimal("7500.00")

mock_po = MagicMock()
mock_po.po_id = po_id
mock_po.po_number = "PO-2026-0001"
mock_po.request_id = None
mock_po.vendor_id = v_id
mock_po.vendor = mock_vendor
mock_po.created_by = uuid.uuid4()
mock_po.order_date = date.today()
mock_po.expected_delivery_date = date.today()
mock_po.actual_delivery_date = None
mock_po.payment_terms = "Net 30"
mock_po.total_amount = Decimal("7500.00")
mock_po.status = PurchaseOrderStatusEnum.PENDING
mock_po.items = [mock_item]
mock_po.created_at = now
mock_po.updated_at = now

try:
    por = PurchaseOrderResponse.model_validate(mock_po, from_attributes=True)
    check("PurchaseOrderResponse ORM serialization works", por.po_number == "PO-2026-0001")
    check("vendor_name extracted cleanly", por.vendor_name == "Acme Supplies Ltd")
    check("items list converted cleanly", len(por.items) == 1)
    check("item total_price exposed", por.items[0].total_price == Decimal("7500.00"))
except Exception as e:
    check("PurchaseOrderResponse ORM serialization works", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
