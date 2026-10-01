"""
Schema-level unit tests for Vendor Pydantic schemas.
Tests: extra field rejection, correct serialization, category_name extraction.
No server or database needed - pure schema validation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import sys
import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

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


# ── Import schemas ──
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.models.vendors import VendorStatusEnum
from pydantic import ValidationError


# =============================================================
# TEST 1: VendorCreate rejects unknown fields
# =============================================================
print("\n=== TEST 1: VendorCreate rejects unknown fields ===")

try:
    VendorCreate(
        vendor_code="VEND-001",
        company_name="Test Corp",
        category_id=1,
        unknown_field="should_fail",
    )
    check("Rejects unknown field", False, "No error raised")
except ValidationError as e:
    error_str = str(e)
    check("Rejects unknown field", "extra" in error_str.lower() or "extra_forbidden" in error_str.lower(), error_str[:100])

# Valid create should still work
try:
    vc = VendorCreate(
        vendor_code="VEND-001",
        company_name="Test Corp",
        category_id=1,
    )
    check("Valid create works", vc.vendor_code == "VEND-001")
except Exception as e:
    check("Valid create works", False, str(e)[:100])

# Valid create with all optional fields
try:
    vc = VendorCreate(
        vendor_code="VEND-002",
        company_name="Full Corp",
        category_id=2,
        linked_user_id=str(uuid.uuid4()),
        tax_id="TX-123",
        website="https://example.com",
        address_line="123 Main St",
        city="Mumbai",
        state="Maharashtra",
        country="India",
        postal_code="400001",
    )
    check("Valid create with all fields works", vc.city == "Mumbai")
except Exception as e:
    check("Valid create with all fields works", False, str(e)[:100])


# =============================================================
# TEST 2: VendorUpdate rejects unknown fields
# =============================================================
print("\n=== TEST 2: VendorUpdate rejects unknown fields ===")

try:
    VendorUpdate(
        company_name="Updated Corp",
        status="approved",  # status is server-managed, should be rejected
    )
    check("Rejects unknown field (status)", False, "No error raised")
except ValidationError as e:
    error_str = str(e)
    check("Rejects unknown field (status)", "extra" in error_str.lower(), error_str[:100])

try:
    VendorUpdate(
        company_name="Updated Corp",
        hacker_field="injection",
    )
    check("Rejects arbitrary unknown field", False, "No error raised")
except ValidationError as e:
    check("Rejects arbitrary unknown field", True)

# Valid update should still work
try:
    vu = VendorUpdate(company_name="Updated Corp")
    check("Valid update works", vu.company_name == "Updated Corp")
except Exception as e:
    check("Valid update works", False, str(e)[:100])

# Empty update should still work (service handles validation)
try:
    vu = VendorUpdate()
    check("Empty update works (no fields)", True)
except Exception as e:
    check("Empty update works (no fields)", False, str(e)[:100])


# =============================================================
# TEST 3: VendorResponse serializes from dict (no ORM)
# =============================================================
print("\n=== TEST 3: VendorResponse serializes from dict ===")

test_id = uuid.uuid4()
now = datetime.now(timezone.utc)
resp_dict = {
    "vendor_id": test_id,
    "vendor_code": "VEND-TEST",
    "company_name": "Test Corp",
    "category_id": 1,
    "category_name": "Raw Material Suppliers",
    "linked_user_id": None,
    "tax_id": None,
    "website": None,
    "address_line": None,
    "city": None,
    "state": None,
    "country": None,
    "postal_code": None,
    "status": "pending",
    "approved_by": None,
    "approved_at": None,
    "registration_date": date.today(),
    "created_at": now,
    "updated_at": now,
}

try:
    vr = VendorResponse(**resp_dict)
    check("Dict serialization works", vr.vendor_id == test_id)
    check("category_name from dict", vr.category_name == "Raw Material Suppliers")
    check("status is enum", isinstance(vr.status, VendorStatusEnum))
except Exception as e:
    check("Dict serialization works", False, str(e)[:150])
    check("category_name from dict", False)
    check("status is enum", False)


# =============================================================
# TEST 4: VendorResponse extracts category_name from ORM mock
# =============================================================
print("\n=== TEST 4: VendorResponse extracts category_name from ORM ===")

# Mock a SQLAlchemy Vendor ORM object with category relationship
mock_category = MagicMock()
mock_category.category_name = "IT Vendors"

mock_vendor = MagicMock()
mock_vendor.vendor_id = uuid.uuid4()
mock_vendor.vendor_code = "VEND-ORM"
mock_vendor.company_name = "ORM Test Corp"
mock_vendor.category_id = 3
mock_vendor.category = mock_category
mock_vendor.linked_user_id = None
mock_vendor.tax_id = "TX-ORM-123"
mock_vendor.website = "https://orm.example.com"
mock_vendor.address_line = "456 Test Ave"
mock_vendor.city = "Delhi"
mock_vendor.state = "Delhi"
mock_vendor.country = "India"
mock_vendor.postal_code = "110001"
mock_vendor.status = VendorStatusEnum.APPROVED
mock_vendor.approved_by = uuid.uuid4()
mock_vendor.approved_at = now
mock_vendor.registration_date = date.today()
mock_vendor.created_at = now
mock_vendor.updated_at = now

try:
    vr = VendorResponse.model_validate(mock_vendor, from_attributes=True)
    check("ORM serialization works", vr.vendor_code == "VEND-ORM")
    check("category_name extracted from ORM", vr.category_name == "IT Vendors")
    check("tax_id preserved", vr.tax_id == "TX-ORM-123")
    check("city preserved", vr.city == "Delhi")
    check("status enum correct", vr.status == VendorStatusEnum.APPROVED)
    check("approved_by UUID present", vr.approved_by is not None)
except Exception as e:
    check("ORM serialization works", False, str(e)[:200])
    check("category_name extracted from ORM", False)
    check("tax_id preserved", False)
    check("city preserved", False)
    check("status enum correct", False)
    check("approved_by UUID present", False)


# =============================================================
# TEST 5: VendorResponse handles None category (no relationship loaded)
# =============================================================
print("\n=== TEST 5: VendorResponse handles None category ===")

mock_vendor_no_cat = MagicMock()
mock_vendor_no_cat.vendor_id = uuid.uuid4()
mock_vendor_no_cat.vendor_code = "VEND-NOCAT"
mock_vendor_no_cat.company_name = "No Cat Corp"
mock_vendor_no_cat.category_id = 1
mock_vendor_no_cat.category = None  # relationship not loaded
mock_vendor_no_cat.linked_user_id = None
mock_vendor_no_cat.tax_id = None
mock_vendor_no_cat.website = None
mock_vendor_no_cat.address_line = None
mock_vendor_no_cat.city = None
mock_vendor_no_cat.state = None
mock_vendor_no_cat.country = None
mock_vendor_no_cat.postal_code = None
mock_vendor_no_cat.status = VendorStatusEnum.PENDING
mock_vendor_no_cat.approved_by = None
mock_vendor_no_cat.approved_at = None
mock_vendor_no_cat.registration_date = date.today()
mock_vendor_no_cat.created_at = now
mock_vendor_no_cat.updated_at = now

try:
    vr = VendorResponse.model_validate(mock_vendor_no_cat, from_attributes=True)
    check("Handles None category gracefully", True)
    check("category_name defaults to None", vr.category_name is None)
except Exception as e:
    check("Handles None category gracefully", False, str(e)[:200])
    check("category_name defaults to None", False)


# =============================================================
# TEST 6: VendorCreate existing validation still works
# =============================================================
print("\n=== TEST 6: Existing validations not broken ===")

try:
    VendorCreate(
        vendor_code="",  # min_length=1
        company_name="Test",
        category_id=1,
    )
    check("vendor_code min_length enforced", False, "No error raised")
except ValidationError:
    check("vendor_code min_length enforced", True)

try:
    VendorCreate(
        vendor_code="VEND-001",
        company_name="Test",
        category_id=0,  # gt=0
    )
    check("category_id gt=0 enforced", False, "No error raised")
except ValidationError:
    check("category_id gt=0 enforced", True)

try:
    VendorCreate(
        vendor_code="VEND-001",
        company_name="Test",
        category_id=-1,  # gt=0
    )
    check("category_id rejects negative", False, "No error raised")
except ValidationError:
    check("category_id rejects negative", True)


# =============================================================
# TEST 7: VendorResponse does NOT enforce input validations
# =============================================================
print("\n=== TEST 7: VendorResponse no input validation leakage ===")

resp_dict_edge = {
    "vendor_id": uuid.uuid4(),
    "vendor_code": "",  # Empty string would fail VendorBase min_length=1
    "company_name": "",  # Same
    "category_id": 0,  # Would fail VendorBase gt=0
    "status": "pending",
    "registration_date": date.today(),
    "created_at": now,
    "updated_at": now,
}

try:
    vr = VendorResponse(**resp_dict_edge)
    check("Empty vendor_code allowed in response", vr.vendor_code == "")
    check("Zero category_id allowed in response", vr.category_id == 0)
except ValidationError as e:
    # If it fails, that means input validations are leaking
    check("Empty vendor_code allowed in response", False, "Input validation leaked into response")
    check("Zero category_id allowed in response", False, "Input validation leaked into response")


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
