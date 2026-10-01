"""
Unit tests for VendorPerformanceService business logic (Phase 2D).
Tests:
- Vendor existence validation for ratings and issues
- Automatic overall_rating calculation from component ratings
- Issue resolution workflow & automatic resolved_at timestamp assignment
- Performance summary & ranking leaderboard delegation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.database import SessionLocal
from app.services.vendor_performance_service import vendor_performance_service
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.schemas.vendor_performance import (
    VendorRatingCreate,
    VendorIssueCreate,
    VendorIssueUpdate,
)
from app.models.vendor_performance import IssueStatusEnum
from app.core.exceptions import (
    InvalidVendorPerformanceDataError,
    VendorIssueNotFoundError,
    VendorNotFoundError,
    VendorRatingNotFoundError,
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

        vendors = await vendor_repository.get_all_vendors(db, limit=1)
        if not vendors:
            vendor = await vendor_repository.create_vendor(db, {
                "vendor_code": f"VSRV-P-{u}",
                "company_name": f"Perf Service Vendor {u}",
                "category_id": 1,
            })
            vendor_id = vendor.vendor_id
        else:
            vendor_id = vendors[0].vendor_id

        # -------------------------------------------------------------
        # TEST 1: Rejects rating for non-existent vendor
        # -------------------------------------------------------------
        print("\n=== TEST 1: Vendor Existence Validation ===")
        bad_vendor_id = uuid.uuid4()
        vrc_bad = VendorRatingCreate(
            vendor_id=bad_vendor_id,
            quality_rating=4,
        )
        try:
            await vendor_performance_service.create_rating(db, vrc_bad, user_id)
            check("Rejects rating for non-existent vendor", False, "No exception raised")
        except VendorNotFoundError as e:
            check("Rejects rating for non-existent vendor", True, str(e))

        # -------------------------------------------------------------
        # TEST 2: Automatic overall_rating calculation
        # -------------------------------------------------------------
        print("\n=== TEST 2: Automatic overall_rating Calculation ===")
        vrc_valid = VendorRatingCreate(
            vendor_id=vendor_id,
            quality_rating=5,
            delivery_rating=4,
            communication_rating=5,  # Avg: (5+4+5)/3 = 4.67
        )
        rating = await vendor_performance_service.create_rating(db, vrc_valid, user_id)
        check("create_rating succeeds", rating is not None)
        check("overall_rating calculated automatically (4.67)", float(rating.overall_rating) == 4.67)

        # -------------------------------------------------------------
        # TEST 3: Issue Creation & Auto resolved_at Assignment
        # -------------------------------------------------------------
        print("\n=== TEST 3: Issue Resolution Workflow ===")
        vic = VendorIssueCreate(
            vendor_id=vendor_id,
            issue_type="Specification Mismatch",
            description="Motor RPM lower than spec",
        )
        issue = await vendor_performance_service.create_issue(db, vic, user_id)
        check("create_issue succeeds", issue is not None)
        check("status defaults to OPEN", issue.status == IssueStatusEnum.OPEN)
        check("resolved_at is initially None", issue.resolved_at is None)

        # Resolve issue
        resolved_issue = await vendor_performance_service.update_issue(
            db, issue.issue_id, VendorIssueUpdate(status=IssueStatusEnum.RESOLVED)
        )
        check("status updated to RESOLVED", resolved_issue.status == IssueStatusEnum.RESOLVED)
        check("resolved_at assigned automatically", resolved_issue.resolved_at is not None)

        # -------------------------------------------------------------
        # TEST 4: Performance Summary & Ranking Delegation
        # -------------------------------------------------------------
        print("\n=== TEST 4: Performance Summary & Ranking Delegation ===")
        summary = await vendor_performance_service.get_vendor_performance_summary(db, vendor_id)
        check("get_vendor_performance_summary returns summary dict", summary is not None)
        check("vendor_id matches", summary.get("vendor_id") == vendor_id)

        rankings = await vendor_performance_service.get_vendor_rankings(db, limit=5)
        check("get_vendor_rankings returns list", isinstance(rankings, list))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
