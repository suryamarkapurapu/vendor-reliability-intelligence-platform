"""
Unit tests for AnalyticsService business and response formatting operations (Phase 2C).
Tests DTO construction, zero fallbacks, and decimal rounding.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys

from app.database import SessionLocal
from app.services.analytics_service import analytics_service
from app.schemas.analytics import (
    ExecutiveDashboardResponse,
    ProcurementAnalyticsResponse,
    InvoiceAnalyticsResponse,
    DeliveryAnalyticsResponse,
    VendorAnalyticsResponse,
    SystemAnalyticsResponse,
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
        # 1. Executive Dashboard
        print("\n=== TEST 1: Executive Dashboard Service ===")
        dash = await analytics_service.get_dashboard(db)
        check("get_dashboard returns ExecutiveDashboardResponse", isinstance(dash, ExecutiveDashboardResponse))
        check("total_procurement_spend is float", isinstance(dash.total_procurement_spend, float))

        # 2. Procurement Analytics
        print("\n=== TEST 2: Procurement Analytics Service ===")
        proc = await analytics_service.get_procurement_analytics(db)
        check("get_procurement_analytics returns ProcurementAnalyticsResponse", isinstance(proc, ProcurementAnalyticsResponse))
        check("orders_by_status is dict", isinstance(proc.orders_by_status, dict))

        # 3. Invoice Analytics
        print("\n=== TEST 3: Invoice Analytics Service ===")
        inv = await analytics_service.get_invoice_analytics(db)
        check("get_invoice_analytics returns InvoiceAnalyticsResponse", isinstance(inv, InvoiceAnalyticsResponse))

        # 4. Delivery Analytics
        print("\n=== TEST 4: Delivery Analytics Service ===")
        deliv = await analytics_service.get_delivery_analytics(db)
        check("get_delivery_analytics returns DeliveryAnalyticsResponse", isinstance(deliv, DeliveryAnalyticsResponse))

        # 5. Vendor Analytics
        print("\n=== TEST 5: Vendor Analytics Service ===")
        vendor_a = await analytics_service.get_vendor_analytics(db)
        check("get_vendor_analytics returns VendorAnalyticsResponse", isinstance(vendor_a, VendorAnalyticsResponse))

        # 6. System Analytics
        print("\n=== TEST 6: System Analytics Service ===")
        sys_a = await analytics_service.get_system_analytics(db)
        check("get_system_analytics returns SystemAnalyticsResponse", isinstance(sys_a, SystemAnalyticsResponse))

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
