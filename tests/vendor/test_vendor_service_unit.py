"""
Unit tests for VendorService (Phase 2C).
Tests VendorService methods directly using AsyncSession.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid

from app.database import SessionLocal
from app.services.vendor_service import vendor_service
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.models.vendors import VendorStatusEnum
from app.core.exceptions import (
    UserNotFoundError,
    VendorAlreadyExistsError,
    VendorCategoryNotFoundError,
    VendorNotFoundError,
    InvalidVendorDataError,
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

        # -------------------------------------------------------------
        # TEST 1: create_vendor baseline
        # -------------------------------------------------------------
        print("\n=== TEST 1: create_vendor (baseline) ===")
        vc = VendorCreate(
            vendor_code=f"SVC-{u}",
            company_name=f"Service Corp {u}",
            category_id=1,
            city="Mumbai",
        )
        vendor = await vendor_service.create_vendor(db, vc)
        check("create_vendor returns Vendor", vendor is not None)
        check("status is PENDING", vendor.status == VendorStatusEnum.PENDING)
        check("category loaded", vendor.category is not None)
        check("category_name loaded", vendor.category.category_name == "Raw Material Suppliers")
        vendor_id = vendor.vendor_id

        # -------------------------------------------------------------
        # TEST 2: Duplicate vendor_code
        # -------------------------------------------------------------
        print("\n=== TEST 2: Duplicate vendor_code ===")
        vc_dup = VendorCreate(
            vendor_code=f"SVC-{u}",
            company_name="Dup Corp",
            category_id=1,
        )
        try:
            await vendor_service.create_vendor(db, vc_dup)
            check("Raises VendorAlreadyExistsError", False, "No exception raised")
        except VendorAlreadyExistsError as e:
            check("Raises VendorAlreadyExistsError", True, str(e))

        # -------------------------------------------------------------
        # TEST 3: Invalid category_id
        # -------------------------------------------------------------
        print("\n=== TEST 3: Invalid category_id ===")
        vc_bad_cat = VendorCreate(
            vendor_code=f"CAT-{u}",
            company_name="Bad Cat Corp",
            category_id=9999,
        )
        try:
            await vendor_service.create_vendor(db, vc_bad_cat)
            check("Raises VendorCategoryNotFoundError", False, "No exception raised")
        except VendorCategoryNotFoundError as e:
            check("Raises VendorCategoryNotFoundError", True, str(e))

        # -------------------------------------------------------------
        # TEST 4: Invalid linked_user_id
        # -------------------------------------------------------------
        print("\n=== TEST 4: Invalid linked_user_id ===")
        fake_uid = uuid.uuid4()
        vc_bad_user = VendorCreate(
            vendor_code=f"USR-{u}",
            company_name="Bad User Corp",
            category_id=1,
            linked_user_id=fake_uid,
        )
        try:
            await vendor_service.create_vendor(db, vc_bad_user)
            check("Raises UserNotFoundError for invalid linked_user_id", False, "No exception raised")
        except UserNotFoundError as e:
            check("Raises UserNotFoundError for invalid linked_user_id", True, str(e))

        # -------------------------------------------------------------
        # TEST 5: update_vendor
        # -------------------------------------------------------------
        print("\n=== TEST 5: update_vendor ===")
        vu = VendorUpdate(company_name=f"Updated Corp {u}", city="Delhi")
        updated = await vendor_service.update_vendor(db, vendor_id, vu)
        check("update_vendor updates company_name", updated.company_name == f"Updated Corp {u}")
        check("update_vendor updates city", updated.city == "Delhi")

        # -------------------------------------------------------------
        # TEST 6: update_vendor with invalid linked_user_id
        # -------------------------------------------------------------
        print("\n=== TEST 6: update_vendor with invalid linked_user_id ===")
        vu_bad_user = VendorUpdate(linked_user_id=uuid.uuid4())
        try:
            await vendor_service.update_vendor(db, vendor_id, vu_bad_user)
            check("Raises UserNotFoundError on update", False, "No exception raised")
        except UserNotFoundError as e:
            check("Raises UserNotFoundError on update", True, str(e))

        # -------------------------------------------------------------
        # TEST 7: delete_vendor (soft delete -> SUSPENDED)
        # -------------------------------------------------------------
        print("\n=== TEST 7: delete_vendor (soft delete) ===")
        deleted = await vendor_service.delete_vendor(db, vendor_id)
        check("delete_vendor sets status to SUSPENDED", deleted.status == VendorStatusEnum.SUSPENDED)

        # -------------------------------------------------------------
        # TEST 8: delete_vendor already suspended
        # -------------------------------------------------------------
        print("\n=== TEST 8: delete_vendor already suspended ===")
        try:
            await vendor_service.delete_vendor(db, vendor_id)
            check("Raises InvalidVendorDataError when already suspended", False, "No exception raised")
        except InvalidVendorDataError as e:
            check("Raises InvalidVendorDataError when already suspended", True, str(e))

        # -------------------------------------------------------------
        # TEST 9: delete_vendor non-existing
        # -------------------------------------------------------------
        print("\n=== TEST 9: delete_vendor non-existing ===")
        try:
            await vendor_service.delete_vendor(db, uuid.uuid4())
            check("Raises VendorNotFoundError for non-existing ID", False, "No exception raised")
        except VendorNotFoundError as e:
            check("Raises VendorNotFoundError for non-existing ID", True, str(e))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
