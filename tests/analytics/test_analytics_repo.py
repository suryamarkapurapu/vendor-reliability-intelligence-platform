"""
Integration test for AnalyticsRepository (Phase 2B).
Tests read-only SQL aggregation queries across all 6 analytics sections:
- Executive Dashboard KPIs
- Procurement Analytics
- Invoice Financial Analytics
- Delivery & Logistics Analytics
- Vendor Analytics
- System & User Analytics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import sys

from app.database import SessionLocal
from app.repositories.analytics_repository import analytics_repository

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
        print("\n=== TEST 1: Executive Dashboard Metrics ===")
        dash = await analytics_repository.get_executive_dashboard_metrics(db)
        check("get_executive_dashboard_metrics returns dict", isinstance(dash, dict))
        check("Contains total_vendors", "total_vendors" in dash)
        check("Contains total_procurement_spend", "total_procurement_spend" in dash)

        # 2. Procurement Analytics
        print("\n=== TEST 2: Procurement Analytics ===")
        proc = await analytics_repository.get_procurement_analytics(db)
        check("get_procurement_analytics returns dict", isinstance(proc, dict))
        check("Contains orders_by_status", "orders_by_status" in proc)
        check("Contains monthly_spend_trend", isinstance(proc.get("monthly_spend_trend"), list))

        # 3. Invoice Analytics
        print("\n=== TEST 3: Invoice Analytics ===")
        inv = await analytics_repository.get_invoice_analytics(db)
        check("get_invoice_analytics returns dict", isinstance(inv, dict))
        check("Contains total_invoiced_amount", "total_invoiced_amount" in inv)

        # 4. Delivery Analytics
        print("\n=== TEST 4: Delivery Analytics ===")
        deliv = await analytics_repository.get_delivery_analytics(db)
        check("get_delivery_analytics returns dict", isinstance(deliv, dict))
        check("Contains on_time_delivery_rate", "on_time_delivery_rate" in deliv)

        # 5. Vendor Analytics
        print("\n=== TEST 5: Vendor Analytics ===")
        vendor_a = await analytics_repository.get_vendor_analytics(db)
        check("get_vendor_analytics returns dict", isinstance(vendor_a, dict))
        check("Contains top_vendors_by_spend", isinstance(vendor_a.get("top_vendors_by_spend"), list))

        # 6. System Analytics
        print("\n=== TEST 6: System Analytics ===")
        sys_a = await analytics_repository.get_system_analytics(db)
        check("get_system_analytics returns dict", isinstance(sys_a, dict))
        check("Contains users_by_role", "users_by_role" in sys_a)

    print(f"\n{'=' * 50}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'=' * 50}\n")
    return FAIL == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
