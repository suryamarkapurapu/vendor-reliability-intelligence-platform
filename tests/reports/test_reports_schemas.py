"""
Unit tests for Reports Pydantic response DTO schemas (Phase 2A).
Tests DTO instantiation, default factory behavior, metadata fields, sub-DTOs, and export initialization.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from datetime import date, datetime
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


from app.schemas.reports import (
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
    ReportMetadata,
    ReportStatus,
    ReportSummaryResponse,
    VendorPerformanceItem,
    VendorPerformanceReportResponse,
)
from app.schemas import (
    ReportCategory as PackageReportCategory,
    ReportMetadata as PackageReportMetadata,
)

# =============================================================
# TEST 1: Enums & Package Exports
# =============================================================
print("\n=== TEST 1: Enums & Package Exports ===")

check("ReportCategory Enum value", ReportCategory.VENDOR_PERFORMANCE.value == "vendor_performance")
check("ReportStatus Enum value", ReportStatus.COMPLETED.value == "completed")
check("ReportFileType Enum value", ReportFileType.PDF.value == "pdf")
check("Package export match", PackageReportCategory == ReportCategory and PackageReportMetadata == ReportMetadata)


# =============================================================
# TEST 2: Common Metadata & Generic DTOs
# =============================================================
print("\n=== TEST 2: Common Metadata & Generic DTOs ===")

rep_id = uuid.uuid4()
now = datetime.now()

meta = ReportMetadata(
    report_id=rep_id,
    report_name="Q3 Vendor Reliability Summary",
    category=ReportCategory.VENDOR_PERFORMANCE,
    generated_date=now,
    status=ReportStatus.COMPLETED,
    generated_by="system_admin",
    file_type=ReportFileType.PDF,
    download_url="/api/v1/reports/download/123",
)
check("ReportMetadata instantiation", meta.report_name == "Q3 Vendor Reliability Summary" and meta.report_id == rep_id)

list_item = ReportListItem(
    report_id=rep_id,
    report_name="Monthly Procurement Spend",
    category=ReportCategory.PROCUREMENT,
    generated_date=now,
    status=ReportStatus.COMPLETED,
    generated_by="finance_lead",
    file_type=ReportFileType.CSV,
    download_url="/api/v1/reports/download/456",
    file_size_bytes=2048,
)
check("ReportListItem instantiation", list_item.file_size_bytes == 2048)

summary = ReportSummaryResponse(
    total_reports=10,
    completed_reports=8,
    failed_reports=2,
    reports_by_category={"vendor_performance": 5, "procurement": 5},
    reports_by_status={"completed": 8, "failed": 2},
    recent_reports=[list_item],
)
check("ReportSummaryResponse instantiation", summary.total_reports == 10 and len(summary.recent_reports) == 1)

export_dto = ReportExportResponse(
    report_id=rep_id,
    report_name="Compliance Audit Report",
    category=ReportCategory.COMPLIANCE,
    file_type=ReportFileType.XLSX,
    download_url="/api/v1/reports/export/789",
    file_size_bytes=1048576,
    expires_at=now,
    status=ReportStatus.COMPLETED,
    generated_at=now,
)
check("ReportExportResponse instantiation", export_dto.file_size_bytes == 1048576)


# =============================================================
# TEST 3: Report Sub-DTOs
# =============================================================
print("\n=== TEST 3: Report Sub-DTOs ===")

v_item = VendorPerformanceItem(
    vendor_id=uuid.uuid4(),
    vendor_name="Acme Supplies",
    vendor_code="V-100",
    overall_score=92.5,
    quality_score=95.0,
    delivery_score=90.0,
    compliance_score=92.5,
    risk_level="LOW",
    total_orders=45,
    open_issues_count=0,
)
check("VendorPerformanceItem instantiation", v_item.overall_score == 92.5)

dept_spend = ProcurementDepartmentSpend(
    department="Engineering",
    total_requests=12,
    total_spend=125000.00,
    average_processing_days=3.5,
)
check("ProcurementDepartmentSpend instantiation", dept_spend.total_spend == 125000.00)

po_status = PurchaseOrderStatusItem(
    status="APPROVED",
    count=25,
    total_value=500000.00,
)
check("PurchaseOrderStatusItem instantiation", po_status.count == 25)

violation = ComplianceViolationItem(
    violation_id=uuid.uuid4(),
    vendor_id=uuid.uuid4(),
    vendor_name="Global Logistics Corp",
    compliance_type="ISO-9001",
    severity="HIGH",
    status="OPEN",
    description="Expired quality certification doc.",
    detected_date=now,
)
check("ComplianceViolationItem instantiation", violation.severity == "HIGH")

contract_item = ContractStatusItem(
    contract_id=uuid.uuid4(),
    contract_number="CNT-2026-001",
    vendor_name="Acme Supplies",
    title="Master Services Agreement",
    status="ACTIVE",
    contract_type="MSA",
    total_value=250000.00,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 12, 31),
    days_until_expiration=157,
)
check("ContractStatusItem instantiation", contract_item.days_until_expiration == 157)


# =============================================================
# TEST 4: Category-Specific Report Responses
# =============================================================
print("\n=== TEST 4: Category-Specific Report Responses ===")

vp_report = VendorPerformanceReportResponse(
    metadata=meta,
    total_vendors_evaluated=50,
    average_performance_score=88.4,
    high_risk_vendors_count=3,
    top_vendors=[v_item],
    vendor_performance_list=[v_item],
    performance_by_category={"IT Services": 91.2, "Logistics": 85.0},
)
check("VendorPerformanceReportResponse instantiation", vp_report.total_vendors_evaluated == 50 and len(vp_report.top_vendors) == 1)

proc_report = ProcurementReportResponse(
    metadata=meta,
    total_requests=100,
    total_approved_requests=85,
    total_procurement_spend=750000.00,
    average_lead_time_days=4.2,
    department_spend=[dept_spend],
    spend_by_category={"Hardware": 400000.00, "Software": 350000.00},
    monthly_trend=[{"month": "2026-07", "spend": 100000.00}],
)
check("ProcurementReportResponse instantiation", proc_report.total_procurement_spend == 750000.00)

po_report = PurchaseOrderReportResponse(
    metadata=meta,
    total_orders=200,
    total_order_value=1500000.00,
    pending_approval_count=15,
    fulfillment_rate=94.2,
    order_statuses=[po_status],
    top_suppliers_by_value={"Acme Corp": 500000.00},
)
check("PurchaseOrderReportResponse instantiation", po_report.fulfillment_rate == 94.2)

comp_report = ComplianceReportResponse(
    metadata=meta,
    total_audits_checked=150,
    overall_compliance_rate=96.0,
    compliant_vendors_count=144,
    non_compliant_vendors_count=6,
    risk_level_breakdown={"LOW": 140, "MEDIUM": 7, "HIGH": 3},
    recent_violations=[violation],
)
check("ComplianceReportResponse instantiation", comp_report.overall_compliance_rate == 96.0)

contract_report = ContractReportResponse(
    metadata=meta,
    total_active_contracts=35,
    total_contract_value=3200000.00,
    upcoming_expirations_count=4,
    renewal_rate=88.5,
    contracts_by_status={"ACTIVE": 30, "EXPIRING": 5},
    contracts_by_type={"MSA": 20, "SLA": 15},
    expiring_contracts=[contract_item],
)
check("ContractReportResponse instantiation", contract_report.total_contract_value == 3200000.00)


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
