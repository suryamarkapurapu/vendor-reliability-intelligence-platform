"""
Unit tests for Analytics Pydantic response DTO schemas (Phase 2A).
Tests DTO instantiation, default factory behavior, and field structures.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import sys
import uuid

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


from app.schemas.analytics import (
    MonthlyTrendPoint,
    VendorSpendResponse,
    ExecutiveDashboardResponse,
    ProcurementAnalyticsResponse,
    InvoiceAnalyticsResponse,
    DeliveryAnalyticsResponse,
    VendorAnalyticsResponse,
    SystemAnalyticsResponse,
)


# =============================================================
# TEST 1: Sub-DTO Instantiation
# =============================================================
print("\n=== TEST 1: Sub-DTO Instantiation ===")

trend = MonthlyTrendPoint(month="2026-07", total_amount=15000.50, count=5)
check("MonthlyTrendPoint instantiates", trend.month == "2026-07" and trend.total_amount == 15000.50)

v_spend = VendorSpendResponse(
    vendor_id=uuid.uuid4(),
    vendor_name="Acme Corp",
    vendor_code="V-ACME",
    total_spend=50000.0,
    total_orders=10,
)
check("VendorSpendResponse instantiates", v_spend.total_spend == 50000.0)


# =============================================================
# TEST 2: High-Level Analytics DTO Instantiation
# =============================================================
print("\n=== TEST 2: High-Level Analytics DTO Instantiation ===")

dash = ExecutiveDashboardResponse(
    total_vendors=25,
    active_vendors=20,
    total_purchase_orders=100,
    total_procurement_spend=450000.0,
    overall_on_time_delivery_rate=94.5,
)
check("ExecutiveDashboardResponse instantiates", dash.total_procurement_spend == 450000.0)

proc_analytics = ProcurementAnalyticsResponse(
    total_requests=50,
    total_purchase_orders=40,
    total_spend=300000.0,
    orders_by_status={"ordered": 20, "completed": 20},
    monthly_spend_trend=[trend],
)
check("ProcurementAnalyticsResponse instantiates with monthly trend", len(proc_analytics.monthly_spend_trend) == 1)

inv_analytics = InvoiceAnalyticsResponse(
    total_invoices=30,
    total_invoiced_amount=250000.0,
    total_paid_amount=200000.0,
    total_pending_amount=50000.0,
)
check("InvoiceAnalyticsResponse instantiates", inv_analytics.total_paid_amount == 200000.0)

deliv_analytics = DeliveryAnalyticsResponse(
    total_deliveries=60,
    delivered_count=55,
    on_time_count=50,
    on_time_delivery_rate=90.9,
)
check("DeliveryAnalyticsResponse instantiates", deliv_analytics.on_time_delivery_rate == 90.9)

vendor_analytics = VendorAnalyticsResponse(
    total_vendors=25,
    active_vendors=20,
    top_vendors_by_spend=[v_spend],
)
check("VendorAnalyticsResponse instantiates with top vendors", len(vendor_analytics.top_vendors_by_spend) == 1)

sys_analytics = SystemAnalyticsResponse(
    total_users=15,
    active_users=12,
    users_by_role={"ADMIN": 2, "PROCUREMENT_MANAGER": 5},
)
check("SystemAnalyticsResponse instantiates", sys_analytics.users_by_role.get("ADMIN") == 2)


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
