"""
Unit tests for Vendor Performance Pydantic schemas (Phase 2B).
Tests: extra field rejection, server-managed & calculated field exclusions, DTO serialization.
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


from app.schemas.vendor_performance import (
    VendorRatingCreate,
    VendorRatingResponse,
    VendorIssueCreate,
    VendorIssueUpdate,
    VendorIssueResponse,
    VendorPerformanceSummaryResponse,
    VendorRankingResponse,
)
from app.models.vendor_performance import IssueStatusEnum


# =============================================================
# TEST 1: VendorRatingCreate Rejects Calculated/Server Fields
# =============================================================
print("\n=== TEST 1: VendorRatingCreate Rejects Calculated/Server Fields ===")

vendor_id = uuid.uuid4()

try:
    VendorRatingCreate(
        vendor_id=vendor_id,
        quality_rating=5,
        overall_rating=Decimal("5.00"),  # Calculated by Service layer
    )
    check("Rejects overall_rating in Create schema", False, "No error raised")
except ValidationError:
    check("Rejects overall_rating in Create schema", True)

# Valid Rating Create
try:
    vrc = VendorRatingCreate(
        vendor_id=vendor_id,
        quality_rating=5,
        delivery_rating=4,
        communication_rating=5,
        comments="Excellent vendor performance",
    )
    check("Valid VendorRatingCreate works", vrc.quality_rating == 5)
except Exception as e:
    check("Valid VendorRatingCreate works", False, str(e))


# =============================================================
# TEST 2: VendorIssueCreate Rejects Server/Generated Fields
# =============================================================
print("\n=== TEST 2: VendorIssueCreate Rejects Server/Generated Fields ===")

try:
    VendorIssueCreate(
        vendor_id=vendor_id,
        issue_type="Packaging Defect",
        resolution_time_hours=Decimal("12.5"),  # Generated column
    )
    check("Rejects resolution_time_hours in Create schema", False, "No error raised")
except ValidationError:
    check("Rejects resolution_time_hours in Create schema", True)

# Valid Issue Create
try:
    vic = VendorIssueCreate(
        vendor_id=vendor_id,
        issue_type="Late Shipment",
        description="Shipment delayed by 3 days",
    )
    check("Valid VendorIssueCreate works", vic.issue_type == "Late Shipment")
except Exception as e:
    check("Valid VendorIssueCreate works", False, str(e))


# =============================================================
# TEST 3: Response DTO Serialization
# =============================================================
print("\n=== TEST 3: Summary & Ranking DTO Serialization ===")

try:
    summary = VendorPerformanceSummaryResponse(
        vendor_id=vendor_id,
        vendor_name="Acme Corp",
        vendor_code="V-ACME-01",
        total_purchase_orders=15,
        completed_purchase_orders=12,
        on_time_delivery_rate=92.5,
        average_overall_rating=4.75,
        open_issues_count=1,
    )
    check("VendorPerformanceSummaryResponse DTO works", summary.on_time_delivery_rate == 92.5)
except Exception as e:
    check("VendorPerformanceSummaryResponse DTO works", False, str(e))

try:
    ranking = VendorRankingResponse(
        rank=1,
        vendor_id=vendor_id,
        vendor_name="Acme Corp",
        vendor_code="V-ACME-01",
        overall_score=96.8,
        on_time_delivery_rate=95.0,
        average_overall_rating=4.8,
        resolved_issues_rate=100.0,
    )
    check("VendorRankingResponse DTO works", ranking.rank == 1)
except Exception as e:
    check("VendorRankingResponse DTO works", False, str(e))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
