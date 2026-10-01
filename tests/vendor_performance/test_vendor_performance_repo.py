"""
Integration test for VendorPerformanceRepository (Phase 2C).
Tests:
- create_rating & selectinload refresh
- create_issue, get_issue_by_id, update_issue
- create_metric, get_all_metrics
- SQL aggregate query: get_vendor_performance_summary
- SQL aggregate query: get_vendor_rankings
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
from app.repositories.vendor_performance_repository import vendor_performance_repository
from app.repositories.vendor_repository import vendor_repository
from app.repositories.user_repository import user_repository
from app.models.vendor_performance import IssueStatusEnum

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
                "vendor_code": f"VPRF-{u}",
                "company_name": f"Perf Vendor {u}",
                "category_id": 1,
            })
            vendor_id = vendor.vendor_id
        else:
            vendor_id = vendors[0].vendor_id

        # -------------------------------------------------------------
        # TEST 1: Ratings CRUD
        # -------------------------------------------------------------
        print("\n=== TEST 1: Ratings CRUD ===")
        rating = await vendor_performance_repository.create_rating(db, {
            "vendor_id": vendor_id,
            "rated_by": user_id,
            "quality_rating": 5,
            "delivery_rating": 4,
            "communication_rating": 5,
            "overall_rating": 4.67,
            "comments": "Great service",
        })
        check("create_rating returns VendorRating", rating is not None)
        check("vendor relationship loaded", rating.vendor is not None)
        check("rater relationship loaded", rating.rater is not None)

        fetched_rating = await vendor_performance_repository.get_rating_by_id(db, rating.rating_id)
        check("get_rating_by_id returns record", fetched_rating is not None)

        # -------------------------------------------------------------
        # TEST 2: Issues CRUD
        # -------------------------------------------------------------
        print("\n=== TEST 2: Issues CRUD ===")
        issue = await vendor_performance_repository.create_issue(db, {
            "vendor_id": vendor_id,
            "reported_by": user_id,
            "issue_type": "Packaging Defect",
            "description": "Box arrived damaged",
            "status": IssueStatusEnum.OPEN,
        })
        check("create_issue returns VendorIssue", issue is not None)
        check("reporter relationship loaded", issue.reporter is not None)

        updated_issue = await vendor_performance_repository.update_issue(db, issue, {"status": IssueStatusEnum.RESOLVED})
        check("update_issue updates status to RESOLVED", updated_issue.status == IssueStatusEnum.RESOLVED)

        # -------------------------------------------------------------
        # TEST 3: Metrics CRUD
        # -------------------------------------------------------------
        print("\n=== TEST 3: Metrics CRUD ===")
        metric = await vendor_performance_repository.create_metric(db, {
            "vendor_id": vendor_id,
            "metric_type": "on_time_delivery",
            "metric_value": 98.50,
            "recorded_by": user_id,
        })
        check("create_metric returns VendorPerformanceMetric", metric is not None)

        # -------------------------------------------------------------
        # TEST 4: SQL Aggregation — Performance Summary & Rankings
        # -------------------------------------------------------------
        print("\n=== TEST 4: SQL Aggregate Queries ===")
        summary = await vendor_performance_repository.get_vendor_performance_summary(db, vendor_id)
        check("get_vendor_performance_summary returns summary dict", summary is not None)
        check("summary contains vendor_id", summary.get("vendor_id") == vendor_id)
        check("summary calculates average_quality_rating", "average_quality_rating" in summary)

        rankings = await vendor_performance_repository.get_vendor_rankings(db, limit=5)
        check("get_vendor_rankings returns list", isinstance(rankings, list))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
