"""
Unit tests for Delivery Tracking Pydantic schemas (Phase 2B).
Tests: extra field rejection, server-managed field exclusions, status restriction on update, ORM mock serialization, derived is_delivered flag.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import sys
import uuid
from datetime import date, datetime, timezone
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


from app.schemas.delivery import (
    DeliveryTrackingCreate,
    DeliveryTrackingUpdate,
    DeliveryTrackingResponse,
)
from app.models.delivery import DeliveryStatusEnum


# =============================================================
# TEST 1: DeliveryTrackingCreate Rejects Server-Managed Fields
# =============================================================
print("\n=== TEST 1: DeliveryTrackingCreate Rejects Server-Managed Fields ===")

po_id = uuid.uuid4()

try:
    DeliveryTrackingCreate(
        po_id=po_id,
        tracking_number="TRK123",
        delivery_status="in_transit",  # Server-managed field
    )
    check("Rejects delivery_status in Create schema", False, "No error raised")
except ValidationError:
    check("Rejects delivery_status in Create schema", True)

try:
    DeliveryTrackingCreate(
        po_id=po_id,
        tracking_number="TRK123",
        delivered_date=date.today(),  # Server-managed field
    )
    check("Rejects delivered_date in Create schema", False, "No error raised")
except ValidationError:
    check("Rejects delivered_date in Create schema", True)

# Valid Create
try:
    dtc = DeliveryTrackingCreate(
        po_id=po_id,
        tracking_number="DHL-889900",
        carrier="DHL Express",
        expected_date=date.today(),
    )
    check("Valid DeliveryTrackingCreate works", dtc.carrier == "DHL Express")
except Exception as e:
    check("Valid DeliveryTrackingCreate works", False, str(e))


# =============================================================
# TEST 2: DeliveryTrackingUpdate Rejects Status Field
# =============================================================
print("\n=== TEST 2: DeliveryTrackingUpdate Rejects Status Field ===")

try:
    DeliveryTrackingUpdate(
        carrier="FedEx",
        delivery_status="delivered",  # Not allowed in Update
    )
    check("Rejects delivery_status in Update schema", False, "No error raised")
except ValidationError:
    check("Rejects delivery_status in Update schema", True)

try:
    dtu = DeliveryTrackingUpdate(
        carrier="FedEx Freight",
        remarks="Gate 4 delivery",
    )
    check("Valid DeliveryTrackingUpdate works", dtu.carrier == "FedEx Freight")
except Exception as e:
    check("Valid DeliveryTrackingUpdate works", False, str(e))


# =============================================================
# TEST 3: DeliveryTrackingResponse Derived & Relationship Extraction
# =============================================================
print("\n=== TEST 3: DeliveryTrackingResponse Derived & Relationship Extraction ===")

mock_vendor = MagicMock()
mock_vendor.company_name = "Apex Industrial Supplies"

mock_po = MagicMock()
mock_po.po_number = "PO-2026-DELIV01"
mock_po.vendor = mock_vendor

mock_dt = MagicMock()
mock_dt.delivery_id = uuid.uuid4()
mock_dt.po_id = po_id
mock_dt.purchase_order = mock_po
mock_dt.tracking_number = "TRACK-999"
mock_dt.carrier = "BlueDart"
mock_dt.dispatch_date = date.today()
mock_dt.expected_date = date.today()
mock_dt.delivered_date = date.today()
mock_dt.delivery_status = DeliveryStatusEnum.DELIVERED
mock_dt.remarks = "Received in good condition"
mock_dt.created_at = datetime.now(timezone.utc)

try:
    res = DeliveryTrackingResponse.model_validate(mock_dt, from_attributes=True)
    check("DeliveryTrackingResponse ORM serialization works", res.tracking_number == "TRACK-999")
    check("po_number extracted from purchase_order relationship", res.po_number == "PO-2026-DELIV01")
    check("vendor_name extracted via purchase_order.vendor relationship", res.vendor_name == "Apex Industrial Supplies")
    check("Derived is_delivered boolean flag is True for DELIVERED status", res.is_delivered is True)
except Exception as e:
    check("DeliveryTrackingResponse ORM serialization works", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
