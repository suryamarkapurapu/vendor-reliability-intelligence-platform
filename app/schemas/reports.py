"""
Pydantic v2 Response DTO Schemas for Reports domain.
Read-only reporting layer objects dynamically generated from existing domain modules.
No direct database model or table mapping.
"""

from datetime import date, datetime
from enum import Enum
from math import ceil
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field


# ======================================================================
# 1. ENUMS & CONSTANTS
# ======================================================================

class ReportCategory(str, Enum):
    """
    Supported report categories across the system.
    """
    VENDOR_PERFORMANCE = "vendor_performance"
    PROCUREMENT = "procurement"
    PURCHASE_ORDER = "purchase_order"
    COMPLIANCE = "compliance"
    CONTRACT = "contract"


class ReportStatus(str, Enum):
    """
    Execution status for report generation.
    """
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportFileType(str, Enum):
    """
    Supported export file types for generated reports.
    """
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"


# ======================================================================
# 2. METADATA & REUSABLE SUB-DTOs
# ======================================================================

class ReportMetadata(BaseModel):
    """
    Common metadata header included in all generated report responses.
    """
    report_id: Optional[UUID] = Field(None, description="Unique identifier for the generated report instance.")
    report_name: str = Field(..., description="Human-readable title of the report.")
    category: ReportCategory = Field(..., description="Category of the report.")
    generated_date: datetime = Field(..., description="Timestamp when the report was generated.")
    status: ReportStatus = Field(ReportStatus.COMPLETED, description="Generation status of the report.")
    generated_by: str = Field(..., description="User or system entity that requested/generated the report.")
    file_type: ReportFileType = Field(ReportFileType.PDF, description="File format of the report.")
    download_url: Optional[str] = Field(None, description="URL path to download the generated report file.")

    model_config = ConfigDict(from_attributes=True)


class ReportListItem(BaseModel):
    """
    Item DTO for historical or available report listings.
    """
    report_id: UUID = Field(..., description="Unique report identifier.")
    report_name: str = Field(..., description="Report title.")
    category: ReportCategory = Field(..., description="Report category.")
    generated_date: datetime = Field(..., description="Timestamp of generation.")
    status: ReportStatus = Field(..., description="Report status.")
    generated_by: str = Field(..., description="Author or requestor.")
    file_type: ReportFileType = Field(..., description="File format.")
    download_url: Optional[str] = Field(None, description="Download URL if available.")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes.")

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    """
    Paginated report listing response for the Reports UI.
    Supports standard offset-based pagination.
    """
    items: list[ReportListItem] = Field(default_factory=list, description="Page of report list items.")
    total: int = Field(0, description="Total number of reports matching the query.")
    page: int = Field(1, ge=1, description="Current page number (1-indexed).")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page.")

    @computed_field(description="Total number of pages available.")
    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return ceil(self.total / self.page_size) if self.total > 0 else 0

    model_config = ConfigDict(from_attributes=True)


class ReportSummaryResponse(BaseModel):
    """
    High-level dashboard summary response of report generation statistics.
    """
    total_reports: int = Field(0, description="Total number of generated reports.")
    completed_reports: int = Field(0, description="Count of successfully generated reports.")
    failed_reports: int = Field(0, description="Count of failed report generations.")
    reports_by_category: dict[str, int] = Field(default_factory=dict, description="Breakdown of report counts by category.")
    reports_by_status: dict[str, int] = Field(default_factory=dict, description="Breakdown of report counts by status.")
    recent_reports: list[ReportListItem] = Field(default_factory=list, description="List of recently generated reports.")
    # --- Dashboard-friendly temporal and status counters ---
    generated_today: int = Field(0, description="Number of reports generated today.")
    generated_this_week: int = Field(0, description="Number of reports generated in the current week.")
    generated_this_month: int = Field(0, description="Number of reports generated in the current month.")
    pending_reports: int = Field(0, description="Number of reports currently generating or in draft state.")

    model_config = ConfigDict(from_attributes=True)


class ReportExportResponse(BaseModel):
    """
    DTO returned when exporting or requesting a download link for a report.
    """
    report_id: UUID = Field(..., description="Report identifier.")
    report_name: str = Field(..., description="Report title.")
    category: ReportCategory = Field(..., description="Report category.")
    file_type: ReportFileType = Field(..., description="Requested export format.")
    download_url: str = Field(..., description="Secure URL link to access/download the report file.")
    download_token: str = Field(..., description="Cryptographically signed download context token.")
    file_size_bytes: int = Field(0, description="Exported file size in bytes.")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for the download link.")
    status: ReportStatus = Field(ReportStatus.COMPLETED, description="Export status.")
    generated_at: datetime = Field(..., description="Generation timestamp.")
    # --- Production-ready export metadata ---
    download_available: bool = Field(True, description="Whether the download link is currently accessible.")
    file_size: Optional[str] = Field(None, description="Human-readable file size (e.g. '1.2 MB').")
    mime_type: Optional[str] = Field(None, description="MIME type of the exported file (e.g. 'application/pdf').")

    model_config = ConfigDict(from_attributes=True)


class ReportDownloadRequest(BaseModel):
    """
    Request payload DTO for authenticated POST report download.
    Contains only the required signed download token.
    """
    download_token: str = Field(..., min_length=1, description="Required non-empty cryptographically signed download context token.")

    model_config = ConfigDict(from_attributes=True)


# ======================================================================
# 2b. BASE REPORT RESPONSE
# ======================================================================

class BaseReportResponse(BaseModel):
    """
    Reusable base class for all category-specific report response DTOs.
    Centralises the shared metadata composition pattern and model configuration
    so that concrete report responses inherit a consistent structure without
    duplicating metadata field declarations.
    """
    metadata: ReportMetadata = Field(..., description="Report metadata header.")

    model_config = ConfigDict(from_attributes=True)


# ======================================================================
# 3. DETAILED REPORT SUB-DTOs
# ======================================================================

class VendorPerformanceItem(BaseModel):
    """
    Individual vendor performance metric row within a Vendor Performance Report.
    """
    vendor_id: UUID = Field(..., description="Vendor ID.")
    vendor_name: str = Field(..., description="Vendor company name.")
    vendor_code: str = Field(..., description="Unique vendor code.")
    overall_score: float = Field(0.0, description="Composite performance score (0-100).")
    quality_score: float = Field(0.0, description="Product/service quality rating (0-100).")
    delivery_score: float = Field(0.0, description="On-time delivery score (0-100).")
    compliance_score: float = Field(0.0, description="Compliance adherence score (0-100).")
    risk_level: str = Field("LOW", description="Assessed risk level (e.g. LOW, MEDIUM, HIGH).")
    total_orders: int = Field(0, description="Total purchase orders processed.")
    open_issues_count: int = Field(0, description="Count of unresolved vendor performance issues.")

    model_config = ConfigDict(from_attributes=True)


class ProcurementDepartmentSpend(BaseModel):
    """
    Departmental procurement spend breakdown item.
    """
    department: str = Field(..., description="Department name.")
    total_requests: int = Field(0, description="Number of procurement requests submitted.")
    total_spend: float = Field(0.0, description="Total monetary spend approved.")
    average_processing_days: float = Field(0.0, description="Average days to process requests.")

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderStatusItem(BaseModel):
    """
    Breakdown of purchase orders grouped by status.
    """
    status: str = Field(..., description="Purchase order status string.")
    count: int = Field(0, description="Number of orders in this status.")
    total_value: float = Field(0.0, description="Aggregate monetary value of orders.")

    model_config = ConfigDict(from_attributes=True)


class ComplianceViolationItem(BaseModel):
    """
    Individual compliance audit violation detail.
    """
    violation_id: Optional[UUID] = Field(None, description="Unique violation ID.")
    vendor_id: Optional[UUID] = Field(None, description="Associated vendor ID.")
    vendor_name: str = Field(..., description="Associated vendor name.")
    compliance_type: str = Field(..., description="Category of compliance check (e.g., ISO, Regulatory, Security).")
    severity: str = Field("MEDIUM", description="Severity rating (LOW, MEDIUM, HIGH, CRITICAL).")
    status: str = Field("OPEN", description="Violation status (OPEN, UNDER_REVIEW, RESOLVED).")
    description: str = Field(..., description="Detailed description of the compliance non-conformity.")
    detected_date: datetime = Field(..., description="Timestamp when the violation was detected.")

    model_config = ConfigDict(from_attributes=True)


class ContractStatusItem(BaseModel):
    """
    Contract record summary item within a Contract Report.
    """
    contract_id: Optional[UUID] = Field(None, description="Unique contract ID.")
    contract_number: str = Field(..., description="Contract reference number.")
    vendor_name: str = Field(..., description="Contracted vendor name.")
    title: str = Field(..., description="Contract title.")
    status: str = Field("ACTIVE", description="Current contract status (e.g. ACTIVE, EXPIRING, EXPIRED).")
    contract_type: str = Field(..., description="Type of contract (e.g., SLA, Master Service Agreement, Supply).")
    total_value: float = Field(0.0, description="Total value of the contract.")
    start_date: date = Field(..., description="Effective start date.")
    end_date: date = Field(..., description="Contract expiration date.")
    days_until_expiration: Optional[int] = Field(None, description="Days remaining until contract expires.")

    model_config = ConfigDict(from_attributes=True)


# ======================================================================
# 4. CATEGORY-SPECIFIC REPORT RESPONSES
# ======================================================================

class VendorPerformanceReportResponse(BaseReportResponse):
    """
    Full Vendor Performance Report response DTO.
    """
    total_vendors_evaluated: int = Field(0, description="Total count of vendors included in evaluation.")
    average_performance_score: float = Field(0.0, description="Average overall score across vendors.")
    high_risk_vendors_count: int = Field(0, description="Count of vendors classified as HIGH risk.")
    top_vendors: list[VendorPerformanceItem] = Field(default_factory=list, description="Top performing vendors.")
    vendor_performance_list: list[VendorPerformanceItem] = Field(default_factory=list, description="Full vendor performance list.")
    performance_by_category: dict[str, float] = Field(default_factory=dict, description="Average scores grouped by vendor category.")

    model_config = ConfigDict(from_attributes=True)


class ProcurementReportResponse(BaseReportResponse):
    """
    Full Procurement Report response DTO.
    """
    total_requests: int = Field(0, description="Total procurement requests.")
    total_approved_requests: int = Field(0, description="Approved procurement requests count.")
    total_procurement_spend: float = Field(0.0, description="Total monetary spend across requests.")
    average_lead_time_days: float = Field(0.0, description="Average procurement lead time in days.")
    department_spend: list[ProcurementDepartmentSpend] = Field(default_factory=list, description="Spend breakdown by department.")
    spend_by_category: dict[str, float] = Field(default_factory=dict, description="Spend breakdown by item category.")
    monthly_trend: list[dict[str, Any]] = Field(default_factory=list, description="Monthly procurement spend trend data points.")

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderReportResponse(BaseReportResponse):
    """
    Full Purchase Order Report response DTO.
    """
    total_orders: int = Field(0, description="Total purchase orders.")
    total_order_value: float = Field(0.0, description="Aggregate financial value of all purchase orders.")
    pending_approval_count: int = Field(0, description="Count of orders awaiting approval.")
    fulfillment_rate: float = Field(0.0, description="Overall order fulfillment percentage (0-100).")
    order_statuses: list[PurchaseOrderStatusItem] = Field(default_factory=list, description="Breakdown of orders by status.")
    top_suppliers_by_value: dict[str, float] = Field(default_factory=dict, description="Top suppliers by aggregate PO monetary value.")

    model_config = ConfigDict(from_attributes=True)


class ComplianceReportResponse(BaseReportResponse):
    """
    Full Compliance Report response DTO.
    """
    total_audits_checked: int = Field(0, description="Total compliance audit checks evaluated.")
    overall_compliance_rate: float = Field(0.0, description="Overall system compliance rate (0-100).")
    compliant_vendors_count: int = Field(0, description="Number of fully compliant vendors.")
    non_compliant_vendors_count: int = Field(0, description="Number of non-compliant vendors.")
    risk_level_breakdown: dict[str, int] = Field(default_factory=dict, description="Vendor count grouped by risk level.")
    recent_violations: list[ComplianceViolationItem] = Field(default_factory=list, description="List of detected compliance violations.")

    model_config = ConfigDict(from_attributes=True)


class ContractReportResponse(BaseReportResponse):
    """
    Full Contract Report response DTO.
    """
    total_active_contracts: int = Field(0, description="Total active vendor contracts.")
    total_contract_value: float = Field(0.0, description="Aggregate financial value of active contracts.")
    upcoming_expirations_count: int = Field(0, description="Count of contracts expiring within 30-90 days.")
    renewal_rate: float = Field(0.0, description="Contract renewal success rate percentage.")
    contracts_by_status: dict[str, int] = Field(default_factory=dict, description="Count of contracts grouped by status.")
    contracts_by_type: dict[str, int] = Field(default_factory=dict, description="Count of contracts grouped by contract type.")
    expiring_contracts: list[ContractStatusItem] = Field(default_factory=list, description="List of contracts expiring soon.")

    model_config = ConfigDict(from_attributes=True)
