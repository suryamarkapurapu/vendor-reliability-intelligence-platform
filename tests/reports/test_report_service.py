"""
Unit tests for Reports Service — Phase 2C.
Tests import validation, class structure, dependency injection, async methods,
mock repository orchestration, business rule calculations (scores, percentages,
risk classifications, unit conversions, contract/compliance logic, export metadata),
and DTO output typing.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import asyncio
import inspect
import sys
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

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
# TEST 1: Module & Package Imports
# =============================================================
print("\n=== TEST 1: Module & Package Imports ===")

try:
    from app.services.report_service import ReportService, report_service
    check("Direct import ReportService", True)
    check("Direct import report_service singleton", True)
except ImportError as e:
    check("Direct import ReportService", False, str(e))
    check("Direct import report_service singleton", False, str(e))

try:
    from app.services import ReportService as PkgReportService
    from app.services import report_service as pkg_report_service
    check("Package import ReportService", PkgReportService is ReportService)
    check("Package import report_service", pkg_report_service is report_service)
except ImportError as e:
    check("Package import ReportService", False, str(e))
    check("Package import report_service", False, str(e))


# =============================================================
# TEST 2: Singleton & Dependency Injection
# =============================================================
print("\n=== TEST 2: Singleton & Dependency Injection ===")

check("report_service is instance of ReportService", isinstance(report_service, ReportService))

mock_repo = MagicMock()
custom_service = ReportService(repo=mock_repo)
check("Custom repo injected correctly", custom_service.repo is mock_repo)


# =============================================================
# TEST 3: DTO Imports Used in Service
# =============================================================
print("\n=== TEST 3: DTO Imports Used in Service ===")

from app.schemas.reports import (
    BaseReportResponse,
    ComplianceReportResponse,
    ComplianceViolationItem,
    ContractReportResponse,
    ContractStatusItem,
    ProcurementDepartmentSpend,
    ProcurementReportResponse,
    PurchaseOrderReportResponse,
    PurchaseOrderStatusItem,
    ReportCategory,
    ReportExportResponse,
    ReportFileType,
    ReportListItem,
    ReportListResponse,
    ReportMetadata,
    ReportStatus,
    ReportSummaryResponse,
    VendorPerformanceItem,
    VendorPerformanceReportResponse,
)

check("Schema DTO classes available", True)


# =============================================================
# TEST 4: Vendor Performance Report Business Logic
# =============================================================
print("\n=== TEST 4: Vendor Performance Report Business Logic ===")

async def test_vendor_performance():
    mock_r = AsyncMock()
    mock_v1_id = uuid4()
    mock_v2_id = uuid4()

    mock_r.get_vendor_performance_report_data.return_value = {
        "total_vendors_evaluated": 2,
        "vendors": [
            {
                "vendor_id": mock_v1_id,
                "vendor_name": "Vendor High",
                "vendor_code": "VND-001",
                "category_name": "IT Hardware",
                "total_orders": 10,
                "total_deliveries": 10,
                "on_time_deliveries": 9,      # 90%
                "avg_quality_rating": 4.5,     # 90%
                "avg_delivery_rating": 4.5,
                "avg_communication_rating": 4.5,
                "avg_overall_rating": 4.5,     # 90%
                "total_issues": 2,
                "open_issues": 0,
                "resolved_issues": 2,          # 100%
            },
            {
                "vendor_id": mock_v2_id,
                "vendor_name": "Vendor Low",
                "vendor_code": "VND-002",
                "category_name": "Logistics",
                "total_orders": 5,
                "total_deliveries": 5,
                "on_time_deliveries": 2,      # 40%
                "avg_quality_rating": 2.0,     # 40%
                "avg_delivery_rating": 2.0,
                "avg_communication_rating": 2.0,
                "avg_overall_rating": 2.0,     # 40%
                "total_issues": 5,
                "open_issues": 4,
                "resolved_issues": 1,          # 20%
            },
        ],
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()
    res = await service.get_vendor_performance_report(db, search="Vendor")

    check("Returns VendorPerformanceReportResponse", isinstance(res, VendorPerformanceReportResponse))
    check("Metadata attached", isinstance(res.metadata, ReportMetadata))
    check("Metadata category correct", res.metadata.category == ReportCategory.VENDOR_PERFORMANCE)
    check("Evaluated count", res.total_vendors_evaluated == 2)

    # Vendor High composite score: (90*0.4)+(90*0.3)+(100*0.2)+(90*0.1) = 36+27+20+9 = 92.0
    v_high = res.vendor_performance_list[0]
    check("Vendor High is top ranked", v_high.vendor_id == mock_v1_id)
    check("Vendor High overall_score ~ 92.0", v_high.overall_score == 92.0, f"actual={v_high.overall_score}")
    check("Vendor High risk_level LOW", v_high.risk_level == "LOW")

    # Vendor Low composite score: (40*0.4)+(40*0.3)+(20*0.2)+(40*0.1) = 16+12+4+4 = 36.0
    v_low = res.vendor_performance_list[1]
    check("Vendor Low overall_score ~ 36.0", v_low.overall_score == 36.0, f"actual={v_low.overall_score}")
    check("Vendor Low risk_level HIGH", v_low.risk_level == "HIGH")

    check("High risk vendors count", res.high_risk_vendors_count == 1)
    check("Average performance score", res.average_performance_score == 64.0)
    check("Performance by category IT Hardware", res.performance_by_category.get("IT Hardware") == 92.0)
    check("Performance by category Logistics", res.performance_by_category.get("Logistics") == 36.0)

asyncio.run(test_vendor_performance())


# =============================================================
# TEST 5: Procurement Report Business Logic
# =============================================================
print("\n=== TEST 5: Procurement Report Business Logic ===")

async def test_procurement():
    mock_r = AsyncMock()
    mock_r.get_procurement_report_data.return_value = {
        "total_requests": 50,
        "total_approved_requests": 40,
        "total_procurement_spend": 125000.50,
        "average_lead_time_days": 4.5,
        "department_spend": [
            {
                "department": "Engineering",
                "total_requests": 25,
                "total_spend": 75000.00,
                "average_processing_seconds": 172800.0, # 2 days
            },
            {
                "department": "Marketing",
                "total_requests": 15,
                "total_spend": 30000.00,
                "average_processing_seconds": 86400.0,  # 1 day
            },
        ],
        "spend_by_category": {"Hardware": 75000.0, "Services": 30000.0},
        "monthly_trend": [{"month": "2026-01", "total_amount": 50000.0, "count": 15}],
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()
    res = await service.get_procurement_report(db)

    check("Returns ProcurementReportResponse", isinstance(res, ProcurementReportResponse))
    check("Metadata category correct", res.metadata.category == ReportCategory.PROCUREMENT)
    check("Total requests", res.total_requests == 50)
    check("Total approved", res.total_approved_requests == 40)
    check("Total spend", res.total_procurement_spend == 125000.50)
    check("Department spend list length", len(res.department_spend) == 2)
    check("Department 1 processing days converted (172800s -> 2.0d)", res.department_spend[0].average_processing_days == 2.0)
    check("Department 2 processing days converted (86400s -> 1.0d)", res.department_spend[1].average_processing_days == 1.0)

asyncio.run(test_procurement())


# =============================================================
# TEST 6: Purchase Order Report Business Logic
# =============================================================
print("\n=== TEST 6: Purchase Order Report Business Logic ===")

async def test_po_report():
    mock_r = AsyncMock()
    mock_r.get_purchase_order_report_data.return_value = {
        "order_statuses": [
            {"status": "pending", "count": 5, "total_value": 10000.0},
            {"status": "approved", "count": 10, "total_value": 25000.0},
            {"status": "completed", "count": 20, "total_value": 50000.0},
            {"status": "delivered", "count": 5, "total_value": 15000.0},
            {"status": "cancelled", "count": 2, "total_value": 5000.0},
        ],
        "top_suppliers_by_value": {"Acme Corp": 50000.0, "Globex": 25000.0},
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()
    res = await service.get_purchase_order_report(db)

    check("Returns PurchaseOrderReportResponse", isinstance(res, PurchaseOrderReportResponse))
    check("Metadata category correct", res.metadata.category == ReportCategory.PURCHASE_ORDER)
    check("Total orders (5+10+20+5+2 = 42)", res.total_orders == 42)
    # total order value excluding cancelled: 10k+25k+50k+15k = 100000.0
    check("Total order value (100k excluding cancelled)", res.total_order_value == 100000.0)
    check("Pending approval count (5)", res.pending_approval_count == 5)
    # fulfillment rate: (20 completed + 5 delivered) / 42 * 100 = 25/42 * 100 = 59.52%
    check("Fulfillment rate ~ 59.52%", res.fulfillment_rate == 59.52, f"actual={res.fulfillment_rate}")
    check("Order status DTO items length", len(res.order_statuses) == 5)
    check("Order status item type", isinstance(res.order_statuses[0], PurchaseOrderStatusItem))

asyncio.run(test_po_report())


# =============================================================
# TEST 7: Compliance Report Business Logic
# =============================================================
print("\n=== TEST 7: Compliance Report Business Logic ===")

async def test_compliance():
    mock_r = AsyncMock()
    v1_id = uuid4()
    v2_id = uuid4()
    v3_id = uuid4()

    mock_r.get_compliance_report_data.return_value = {
        "total_vendors": 10,
        "vendors_with_open_issues": 2,
        "vendor_open_issue_counts": [
            {"vendor_id": v1_id, "open_issue_count": 4},  # HIGH
            {"vendor_id": v2_id, "open_issue_count": 1},  # MEDIUM
        ],
        "recent_issues": [
            {
                "issue_id": uuid4(),
                "vendor_id": v1_id,
                "vendor_name": "Bad Vendor",
                "issue_type": "Defective Goods",
                "issue_status": "open",
                "description": "Broken batch",
                "reported_at": datetime.now(timezone.utc),
            }
        ],
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()
    res = await service.get_compliance_report(db)

    check("Returns ComplianceReportResponse", isinstance(res, ComplianceReportResponse))
    check("Metadata category correct", res.metadata.category == ReportCategory.COMPLIANCE)
    check("Total audits checked", res.total_audits_checked == 10)
    check("Non compliant count", res.non_compliant_vendors_count == 2)
    check("Compliant count (10 - 2 = 8)", res.compliant_vendors_count == 8)
    # Overall compliance: 8/10 * 100 = 80.0%
    check("Overall compliance rate (80.0%)", res.overall_compliance_rate == 80.0)
    check("Risk breakdown LOW (8)", res.risk_level_breakdown.get("LOW") == 8)
    check("Risk breakdown MEDIUM (1)", res.risk_level_breakdown.get("MEDIUM") == 1)
    check("Risk breakdown HIGH (1)", res.risk_level_breakdown.get("HIGH") == 1)
    check("Recent violations length", len(res.recent_violations) == 1)
    check("Violation severity HIGH for open issue", res.recent_violations[0].severity == "HIGH")
    check("Violation status OPEN", res.recent_violations[0].status == "OPEN")

asyncio.run(test_compliance())


# =============================================================
# TEST 8: Contract Report Business Logic
# =============================================================
print("\n=== TEST 8: Contract Report Business Logic ===")

async def test_contract():
    mock_r = AsyncMock()
    po_id = uuid4()
    now_dt = datetime.now(timezone.utc)

    mock_r.get_contract_report_data.return_value = {
        "po_status_breakdown": [
            {"status": "pending", "count": 5, "total_value": 20000.0},
            {"status": "approved", "count": 5, "total_value": 30000.0},
            {"status": "delivered", "count": 3, "total_value": 15000.0},
            {"status": "completed", "count": 12, "total_value": 60000.0},
        ],
        "total_po_value": 125000.0,
        "po_count_by_category": {"Hardware": 10, "Software": 15},
        "upcoming_pos": [
            {
                "po_id": po_id,
                "po_number": "PO-2026-001",
                "vendor_name": "Supplier Inc",
                "total_amount": 15000.0,
                "order_date": now_dt.date(),
                "expected_delivery_date": (now_dt + timedelta(days=15)).date(), # 15 days -> EXPIRING
                "status": "ordered",
                "category_name": "Hardware",
            }
        ],
        "total_non_cancelled": 25,
        "total_completed": 12,
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()
    res = await service.get_contract_report(db)

    check("Returns ContractReportResponse", isinstance(res, ContractReportResponse))
    check("Metadata category correct", res.metadata.category == ReportCategory.CONTRACT)
    check("Total active contracts isolated (0)", res.total_active_contracts == 0)
    check("Total contract value isolated (0.0)", res.total_contract_value == 0.0)
    check("Renewal rate isolated (0.0)", res.renewal_rate == 0.0)
    check("Expiring contracts list empty (no fabrication)", len(res.expiring_contracts) == 0)

asyncio.run(test_contract())


# =============================================================
# TEST 9: Report Summary & History
# =============================================================
print("\n=== TEST 9: Report Summary & History ===")

async def test_summary_and_history():
    mock_r = AsyncMock()
    mock_r.get_report_summary_data.return_value = {
        "vendor_count": 10,
        "po_count": 20,
        "request_count": 15,
        "invoice_count": 18,
        "delivery_count": 12,
        "open_issues_count": 3,
    }

    service = ReportService(repo=mock_r)
    db = AsyncMock()

    summary_res = await service.get_report_summary(db)
    check("Returns ReportSummaryResponse", isinstance(summary_res, ReportSummaryResponse))
    # Total = 10+20+15+18+12 = 75
    check("Total reports", summary_res.total_reports == 75)
    check("Pending reports", summary_res.pending_reports == 3)
    check("Reports by category has vendor_performance", summary_res.reports_by_category.get("vendor_performance") == 10)
    check("Recent reports populated", len(summary_res.recent_reports) == 5)

    history_res = await service.get_report_history(db, page=1, page_size=10)
    check("Returns ReportListResponse", isinstance(history_res, ReportListResponse))
    check("Total history items", history_res.total == 5)
    check("Items length", len(history_res.items) == 5)
    check("First item is Vendor Performance", history_res.items[0].category == ReportCategory.VENDOR_PERFORMANCE)

asyncio.run(test_summary_and_history())


# =============================================================
# TEST 10: Export Support
# =============================================================
print("\n=== TEST 10: Export Support ===")

async def test_export():
    service = ReportService()
    db = AsyncMock()

    pdf_res = await service.export_report(db, category=ReportCategory.VENDOR_PERFORMANCE, file_type=ReportFileType.PDF)
    check("Returns ReportExportResponse", isinstance(pdf_res, ReportExportResponse))
    check("PDF mime type", pdf_res.mime_type == "application/pdf")
    check("PDF file size str", pdf_res.file_size == "1.2 MB")
    check("Download URL format", "/api/v1/reports/download/" in pdf_res.download_url)
    check("Download available", pdf_res.download_available is True)
    check("Expires at populated", pdf_res.expires_at is not None)

    xlsx_res = await service.export_report(db, category=ReportCategory.PROCUREMENT, file_type=ReportFileType.XLSX)
    check("XLSX mime type", xlsx_res.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    check("XLSX file size str", xlsx_res.file_size == "850 KB")

asyncio.run(test_export())


# =============================================================
# TEST 11: Architecture Constraints Verification
# =============================================================
print("\n=== TEST 11: Architecture Constraints Verification ===")

import importlib
service_module = importlib.import_module("app.services.report_service")
source_file = inspect.getfile(service_module)

with open(source_file, "r", encoding="utf-8") as f:
    source = f.read()

# Must NOT execute SQL directly or import SQLAlchemy models
check("No select(...) query in service", "select(" not in source)
check("No models import in service", "from app.models" not in source)
check("No db.execute(...) in service", "db.execute(" not in source)

# Must call repo methods
check("Delegates to repo.get_vendor_performance_report_data", "self.repo.get_vendor_performance_report_data" in source)
check("Delegates to repo.get_procurement_report_data", "self.repo.get_procurement_report_data" in source)
check("Delegates to repo.get_purchase_order_report_data", "self.repo.get_purchase_order_report_data" in source)
check("Delegates to repo.get_compliance_report_data", "self.repo.get_compliance_report_data" in source)
check("Isolates contract report without repo fabrication", "self.repo.get_contract_report_data" not in source)
check("Delegates to repo.get_report_summary_data", "self.repo.get_report_summary_data" in source)


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
