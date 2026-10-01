"""
Unit & Integration tests for Reports Router — Phase 2D.
Tests OpenAPI route registration, HTTP endpoints, query parameter handling,
FastAPI dependency injection overrides, RBAC security roles, validation error handling,
and architectural thin-router constraint enforcement.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import inspect
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")


# =============================================================
# TEST 1: Imports & Router Registration
# =============================================================
print("\n=== TEST 1: Imports & Router Registration ===")

try:
    from app.routers.report_router import router as report_router
    check("Direct import report_router", True)
except ImportError as e:
    check("Direct import report_router", False, str(e))

try:
    from app.routers import report_router as pkg_report_router
    check("Package import report_router", pkg_report_router is report_router)
except ImportError as e:
    check("Package import report_router", False, str(e))

from app.main import app

openapi_paths = list(app.openapi().get("paths", {}).keys())
expected_paths = [
    "/api/v1/reports/vendor-performance",
    "/api/v1/reports/procurement",
    "/api/v1/reports/purchase-orders",
    "/api/v1/reports/compliance",
    "/api/v1/reports/contracts",
    "/api/v1/reports/summary",
    "/api/v1/reports/history",
    "/api/v1/reports/export",
]

for path in expected_paths:
    check(f"Route registered in app: {path}", path in openapi_paths, f"openapi_paths={openapi_paths}")


# =============================================================
# TEST 2: Endpoint Route Signatures & HTTP Methods
# =============================================================
print("\n=== TEST 2: Endpoint Route Signatures & HTTP Methods ===")

router_paths_methods = {
    (r.path, tuple(r.methods)): r for r in report_router.routes
}

expected_router_routes = [
    ("/reports/vendor-performance", ("GET",)),
    ("/reports/procurement", ("GET",)),
    ("/reports/purchase-orders", ("GET",)),
    ("/reports/compliance", ("GET",)),
    ("/reports/contracts", ("GET",)),
    ("/reports/summary", ("GET",)),
    ("/reports/history", ("GET",)),
    ("/reports/export", ("POST",)),
]

for path, methods in expected_router_routes:
    found = any(r.path == path and set(methods).issubset(r.methods) for r in report_router.routes)
    check(f"Router route exists: {methods[0]} {path}", found)


# =============================================================
# TEST 3: TestClient Endpoint Execution & Mocking
# =============================================================
print("\n=== TEST 3: TestClient Endpoint Execution & Mocking ===")

from app.dependencies import get_current_user, get_db, get_report_service
from app.models.roles import Role
from app.models.users import User
from app.schemas.reports import (
    ComplianceReportResponse,
    ContractReportResponse,
    ProcurementReportResponse,
    PurchaseOrderReportResponse,
    ReportCategory,
    ReportExportResponse,
    ReportFileType,
    ReportListResponse,
    ReportMetadata,
    ReportStatus,
    ReportSummaryResponse,
    VendorPerformanceReportResponse,
)

# Mock authenticated admin user
mock_role = MagicMock(spec=Role)
mock_role.role_name = "ADMIN"
mock_user = MagicMock(spec=User)
mock_user.user_id = uuid4()
mock_user.email = "admin@example.com"
mock_user.full_name = "Admin User"
mock_user.is_active = True
mock_user.role = mock_role

# Mock db
mock_db = AsyncMock()

# Mock report service
mock_service = MagicMock()

def make_metadata(cat: ReportCategory, name: str) -> ReportMetadata:
    return ReportMetadata(
        report_id=uuid4(),
        report_name=name,
        category=cat,
        generated_date=datetime.now(timezone.utc),
        status=ReportStatus.COMPLETED,
        generated_by="Admin User",
        file_type=ReportFileType.PDF,
        download_url="/api/v1/reports/download/test",
    )

mock_service.get_vendor_performance_report = AsyncMock(
    return_value=VendorPerformanceReportResponse(
        metadata=make_metadata(ReportCategory.VENDOR_PERFORMANCE, "Vendor Performance Report"),
        total_vendors_evaluated=1,
        average_performance_score=85.0,
        high_risk_vendors_count=0,
        top_vendors=[],
        vendor_performance_list=[],
        performance_by_category={},
    )
)

mock_service.get_procurement_report = AsyncMock(
    return_value=ProcurementReportResponse(
        metadata=make_metadata(ReportCategory.PROCUREMENT, "Procurement Report"),
        total_requests=10,
        total_approved_requests=8,
        total_procurement_spend=50000.0,
        average_lead_time_days=3.0,
        department_spend=[],
        spend_by_category={},
        monthly_trend=[],
    )
)

mock_service.get_purchase_order_report = AsyncMock(
    return_value=PurchaseOrderReportResponse(
        metadata=make_metadata(ReportCategory.PURCHASE_ORDER, "Purchase Order Report"),
        total_orders=15,
        total_order_value=75000.0,
        pending_approval_count=2,
        fulfillment_rate=80.0,
        order_statuses=[],
        top_suppliers_by_value={},
    )
)

mock_service.get_compliance_report = AsyncMock(
    return_value=ComplianceReportResponse(
        metadata=make_metadata(ReportCategory.COMPLIANCE, "Compliance Report"),
        total_audits_checked=5,
        overall_compliance_rate=100.0,
        compliant_vendors_count=5,
        non_compliant_vendors_count=0,
        risk_level_breakdown={"LOW": 5, "MEDIUM": 0, "HIGH": 0},
        recent_violations=[],
    )
)

mock_service.get_contract_report = AsyncMock(
    return_value=ContractReportResponse(
        metadata=make_metadata(ReportCategory.CONTRACT, "Contract Report"),
        total_active_contracts=0,
        total_contract_value=0.0,
        upcoming_expirations_count=0,
        renewal_rate=0.0,
        contracts_by_status={},
        contracts_by_type={},
        expiring_contracts=[],
    )
)

mock_service.get_report_summary = AsyncMock(
    return_value=ReportSummaryResponse(
        total_reports=50,
        completed_reports=50,
        failed_reports=0,
        reports_by_category={"vendor_performance": 10},
        reports_by_status={"completed": 50},
        recent_reports=[],
        generated_today=5,
        generated_this_week=15,
        generated_this_month=50,
        pending_reports=0,
    )
)

mock_service.get_report_history = AsyncMock(
    return_value=ReportListResponse(
        items=[],
        total=0,
        page=1,
        page_size=20,
    )
)

mock_service.export_report = AsyncMock(
    return_value=ReportExportResponse(
        report_id=uuid4(),
        report_name="Vendor Performance Report",
        category=ReportCategory.VENDOR_PERFORMANCE,
        file_type=ReportFileType.PDF,
        download_url="/api/v1/reports/download/test",
        file_size_bytes=102400,
        expires_at=datetime.now(timezone.utc),
        status=ReportStatus.COMPLETED,
        generated_at=datetime.now(timezone.utc),
        download_available=True,
        file_size="1.2 MB",
        mime_type="application/pdf",
    )
)

# Apply dependency overrides
app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[get_db] = lambda: mock_db
app.dependency_overrides[get_report_service] = lambda: mock_service

client = TestClient(app)

# 1. GET /vendor-performance
resp = client.get("/api/v1/reports/vendor-performance?search=Tech")
check("GET /vendor-performance status 200", resp.status_code == 200, f"body={resp.text}")
check("GET /vendor-performance returns DTO fields", "total_vendors_evaluated" in resp.json())

# 2. GET /procurement
resp = client.get("/api/v1/reports/procurement?search=Hardware")
check("GET /procurement status 200", resp.status_code == 200)
check("GET /procurement returns DTO fields", "total_procurement_spend" in resp.json())

# 3. GET /purchase-orders
resp = client.get("/api/v1/reports/purchase-orders?status=pending")
check("GET /purchase-orders status 200", resp.status_code == 200)
check("GET /purchase-orders returns DTO fields", "fulfillment_rate" in resp.json())

# 4. GET /compliance
resp = client.get("/api/v1/reports/compliance")
check("GET /compliance status 200", resp.status_code == 200)
check("GET /compliance returns DTO fields", "overall_compliance_rate" in resp.json())

# 5. GET /contracts
resp = client.get("/api/v1/reports/contracts")
check("GET /contracts status 200", resp.status_code == 200)
check("GET /contracts returns DTO fields", "total_active_contracts" in resp.json())

# 6. GET /summary
resp = client.get("/api/v1/reports/summary")
check("GET /summary status 200", resp.status_code == 200)
check("GET /summary returns DTO fields", "total_reports" in resp.json())

# 7. GET /history
resp = client.get("/api/v1/reports/history?page=1&page_size=20")
check("GET /history status 200", resp.status_code == 200)
check("GET /history returns DTO fields", "total_pages" in resp.json())

# 8. POST /export
resp = client.post("/api/v1/reports/export?category=vendor_performance&file_type=pdf")
check("POST /export status 200", resp.status_code == 200)
check("POST /export returns DTO fields", "download_url" in resp.json())


# =============================================================
# TEST 4: Input Validation & Error Handling
# =============================================================
print("\n=== TEST 4: Input Validation & Error Handling ===")

# Invalid page number (page < 1)
resp = client.get("/api/v1/reports/history?page=0")
check("GET /history page=0 returns 422 Unprocessable Entity", resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY)

# Invalid page size (page_size > 100)
resp = client.get("/api/v1/reports/history?page_size=200")
check("GET /history page_size=200 returns 422 Unprocessable Entity", resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY)

# Invalid category in export
resp = client.post("/api/v1/reports/export?category=invalid_category&file_type=pdf")
check("POST /export invalid category returns 422", resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY)

# Invalid export file type
resp = client.post("/api/v1/reports/export?category=vendor_performance&file_type=invalid_format")
check("POST /export invalid file_type returns 422", resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY)


# =============================================================
# TEST 5: RBAC Role Protection Verification
# =============================================================
print("\n=== TEST 5: RBAC Role Protection Verification ===")

# Mock unauthorized user role (e.g. VENDOR)
unauth_role = MagicMock(spec=Role)
unauth_role.role_name = "VENDOR"
unauth_user = MagicMock(spec=User)
unauth_user.user_id = uuid4()
unauth_user.email = "vendor@example.com"
unauth_user.is_active = True
unauth_user.role = unauth_role

app.dependency_overrides[get_current_user] = lambda: unauth_user

resp = client.get("/api/v1/reports/vendor-performance")
check("GET /vendor-performance unauthorized role returns 403 Forbidden", resp.status_code == status.HTTP_403_FORBIDDEN)

resp = client.get("/api/v1/reports/summary")
check("GET /summary unauthorized role returns 403 Forbidden", resp.status_code == status.HTTP_403_FORBIDDEN)

resp = client.post("/api/v1/reports/export?category=vendor_performance&file_type=pdf")
check("POST /export unauthorized role returns 403 Forbidden", resp.status_code == status.HTTP_403_FORBIDDEN)

# Clean up overrides
app.dependency_overrides.clear()


# =============================================================
# TEST 6: Thin Router Architecture Verification
# =============================================================
print("\n=== TEST 6: Thin Router Architecture Verification ===")

import importlib
router_module = importlib.import_module("app.routers.report_router")
source_file = inspect.getfile(router_module)

with open(source_file, "r", encoding="utf-8") as f:
    source = f.read()

# Thin router constraint checks
check("No select(...) query in router", "select(" not in source)
check("No direct models import in router", "from app.models" not in source or "from app.models.users import User" in source)
check("No db.execute(...) in router", "db.execute(" not in source)
check("No business scoring formulas in router", "* 0.4" not in source and "* 0.3" not in source)
check("No PDF/Excel generation code in router", "ReportLab" not in source and "openpyxl" not in source)


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
