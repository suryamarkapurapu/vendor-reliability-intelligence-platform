"""
Unit tests for Reports Pydantic response DTO schemas — Phase 2A Improvements.
Covers:
  - Backward compatibility of ALL existing DTOs (Phase 2A baseline)
  - BaseReportResponse inheritance verification
  - ReportListResponse pagination (including computed total_pages)
  - Enhanced ReportExportResponse (download_available, file_size, mime_type)
  - Enhanced ReportSummaryResponse (temporal & status counters)
  - Package-level __init__.py export verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from datetime import date, datetime
import math
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

# =============================================================
# TEST 1: Enums & Package Exports (backward compat)
# =============================================================
print("\n=== TEST 1: Enums & Package Exports ===")

check("ReportCategory Enum value", ReportCategory.VENDOR_PERFORMANCE.value == "vendor_performance")
check("ReportStatus Enum value", ReportStatus.COMPLETED.value == "completed")
check("ReportFileType Enum value", ReportFileType.PDF.value == "pdf")

# Package-level export for new DTOs
from app.schemas import (
    BaseReportResponse as PkgBaseReportResponse,
    ReportCategory as PkgReportCategory,
    ReportListResponse as PkgReportListResponse,
    ReportMetadata as PkgReportMetadata,
)
check("Package export BaseReportResponse", PkgBaseReportResponse is BaseReportResponse)
check("Package export ReportListResponse", PkgReportListResponse is ReportListResponse)
check("Package export ReportCategory unchanged", PkgReportCategory is ReportCategory)
check("Package export ReportMetadata unchanged", PkgReportMetadata is ReportMetadata)


# =============================================================
# TEST 2: Common Metadata & Generic DTOs (backward compat)
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
check("ReportMetadata from_attributes", meta.model_config.get("from_attributes") is True)

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


# =============================================================
# TEST 3: ReportSummaryResponse (enhanced)
# =============================================================
print("\n=== TEST 3: ReportSummaryResponse (enhanced) ===")

# Backward compatible — existing fields only
summary_basic = ReportSummaryResponse(
    total_reports=10,
    completed_reports=8,
    failed_reports=2,
    reports_by_category={"vendor_performance": 5, "procurement": 5},
    reports_by_status={"completed": 8, "failed": 2},
    recent_reports=[list_item],
)
check("ReportSummaryResponse backward compat", summary_basic.total_reports == 10 and len(summary_basic.recent_reports) == 1)
check("ReportSummaryResponse new defaults - generated_today", summary_basic.generated_today == 0)
check("ReportSummaryResponse new defaults - generated_this_week", summary_basic.generated_this_week == 0)
check("ReportSummaryResponse new defaults - generated_this_month", summary_basic.generated_this_month == 0)
check("ReportSummaryResponse new defaults - pending_reports", summary_basic.pending_reports == 0)

# Full instantiation with new fields
summary_full = ReportSummaryResponse(
    total_reports=100,
    completed_reports=85,
    failed_reports=5,
    reports_by_category={"vendor_performance": 40, "procurement": 60},
    reports_by_status={"completed": 85, "failed": 5, "generating": 10},
    recent_reports=[],
    generated_today=12,
    generated_this_week=45,
    generated_this_month=100,
    pending_reports=10,
)
check("ReportSummaryResponse full instantiation", summary_full.generated_today == 12)
check("ReportSummaryResponse pending_reports value", summary_full.pending_reports == 10)
check("ReportSummaryResponse generated_this_month value", summary_full.generated_this_month == 100)


# =============================================================
# TEST 4: ReportExportResponse (enhanced)
# =============================================================
print("\n=== TEST 4: ReportExportResponse (enhanced) ===")

# Backward compatible instantiation — no new fields
export_basic = ReportExportResponse(
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
check("ReportExportResponse backward compat", export_basic.file_size_bytes == 1048576)
check("ReportExportResponse default download_available", export_basic.download_available is True)
check("ReportExportResponse default file_size", export_basic.file_size is None)
check("ReportExportResponse default mime_type", export_basic.mime_type is None)

# Full instantiation with new fields
export_full = ReportExportResponse(
    report_id=rep_id,
    report_name="Compliance Audit Report",
    category=ReportCategory.COMPLIANCE,
    file_type=ReportFileType.PDF,
    download_url="/api/v1/reports/export/789",
    file_size_bytes=1048576,
    expires_at=now,
    status=ReportStatus.COMPLETED,
    generated_at=now,
    download_available=True,
    file_size="1.0 MB",
    mime_type="application/pdf",
)
check("ReportExportResponse full instantiation", export_full.mime_type == "application/pdf")
check("ReportExportResponse file_size value", export_full.file_size == "1.0 MB")
check("ReportExportResponse download_available value", export_full.download_available is True)


# =============================================================
# TEST 5: ReportListResponse (NEW — pagination)
# =============================================================
print("\n=== TEST 5: ReportListResponse (pagination) ===")

paginated_empty = ReportListResponse()
check("ReportListResponse empty defaults", paginated_empty.items == [] and paginated_empty.total == 0)
check("ReportListResponse empty total_pages", paginated_empty.total_pages == 0)

paginated = ReportListResponse(
    items=[list_item],
    total=55,
    page=3,
    page_size=20,
)
check("ReportListResponse items count", len(paginated.items) == 1)
check("ReportListResponse total", paginated.total == 55)
check("ReportListResponse page", paginated.page == 3)
check("ReportListResponse page_size", paginated.page_size == 20)
check("ReportListResponse computed total_pages", paginated.total_pages == math.ceil(55 / 20))
check("ReportListResponse from_attributes", paginated.model_config.get("from_attributes") is True)

paginated_exact = ReportListResponse(total=40, page_size=20)
check("ReportListResponse exact division total_pages", paginated_exact.total_pages == 2)

paginated_one = ReportListResponse(total=1, page_size=20)
check("ReportListResponse single item total_pages", paginated_one.total_pages == 1)

# Verify JSON serialization includes total_pages
json_data = paginated.model_dump()
check("ReportListResponse model_dump includes total_pages", "total_pages" in json_data and json_data["total_pages"] == 3)


# =============================================================
# TEST 6: BaseReportResponse inheritance
# =============================================================
print("\n=== TEST 6: BaseReportResponse inheritance ===")

check("VendorPerformanceReportResponse inherits BaseReportResponse",
      issubclass(VendorPerformanceReportResponse, BaseReportResponse))
check("ProcurementReportResponse inherits BaseReportResponse",
      issubclass(ProcurementReportResponse, BaseReportResponse))
check("PurchaseOrderReportResponse inherits BaseReportResponse",
      issubclass(PurchaseOrderReportResponse, BaseReportResponse))
check("ComplianceReportResponse inherits BaseReportResponse",
      issubclass(ComplianceReportResponse, BaseReportResponse))
check("ContractReportResponse inherits BaseReportResponse",
      issubclass(ContractReportResponse, BaseReportResponse))

# BaseReportResponse has metadata field
base = BaseReportResponse(metadata=meta)
check("BaseReportResponse instantiation", base.metadata.report_name == "Q3 Vendor Reliability Summary")
check("BaseReportResponse from_attributes", base.model_config.get("from_attributes") is True)


# =============================================================
# TEST 7: Report Sub-DTOs (backward compat)
# =============================================================
print("\n=== TEST 7: Report Sub-DTOs ===")

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
# TEST 8: Category-Specific Report Responses (backward compat + inheritance)
# =============================================================
print("\n=== TEST 8: Category-Specific Report Responses ===")

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
check("VendorPerformanceReportResponse metadata access", vp_report.metadata.report_name == "Q3 Vendor Reliability Summary")

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
# TEST 9: ConfigDict(from_attributes=True) on all DTOs
# =============================================================
print("\n=== TEST 9: ConfigDict(from_attributes=True) on all DTOs ===")

all_models = [
    ReportMetadata, ReportListItem, ReportListResponse,
    ReportSummaryResponse, ReportExportResponse, BaseReportResponse,
    VendorPerformanceItem, ProcurementDepartmentSpend,
    PurchaseOrderStatusItem, ComplianceViolationItem, ContractStatusItem,
    VendorPerformanceReportResponse, ProcurementReportResponse,
    PurchaseOrderReportResponse, ComplianceReportResponse,
    ContractReportResponse,
]
for model_cls in all_models:
    check(
        f"{model_cls.__name__} has from_attributes=True",
        model_cls.model_config.get("from_attributes") is True,
        f"model_config={model_cls.model_config}",
    )


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
