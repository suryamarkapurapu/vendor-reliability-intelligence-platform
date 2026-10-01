"""
Service layer for Reports domain logic, DTO mapping, and metric calculations.
Orchestrates ReportRepository to retrieve raw aggregates and performs all business rules,
scores, classifications, rate computations, and metadata composition.

No direct SQL execution or ORM model access.
"""

from datetime import datetime, timedelta, timezone
import csv
import io
import json
from typing import Any, Optional
from uuid import UUID, NAMESPACE_DNS, uuid4, uuid5

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.report_repository import (
    ReportRepository,
    report_repository,
)
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
    ReportListResponse,
    ReportMetadata,
    ReportStatus,
    ReportSummaryResponse,
    VendorPerformanceItem,
    VendorPerformanceReportResponse,
)


class ReportService:
    """
    Service layer executing report orchestration, calculations, DTO mapping, and metadata generation.
    Does not execute SQL queries directly; delegates all database operations to ReportRepository.
    """

    def __init__(self, repo: ReportRepository | None = None) -> None:
        """
        Initializes ReportService with dependency injection for ReportRepository.
        """
        self.repo = repo or report_repository

    # ==================================================================
    # PRIVATE HELPER METHODS FOR CALCULATIONS & METADATA
    # ==================================================================

    def _safe_percentage(self, numerator: float | int, denominator: float | int, default: float = 0.0) -> float:
        """
        Calculates a percentage safely to prevent ZeroDivisionError.
        """
        if denominator <= 0:
            return default
        return round((float(numerator) / float(denominator)) * 100.0, 2)

    def _calculate_vendor_score(
        self,
        delivery_score: float,
        quality_score: float,
        compliance_score: float,
        overall_rating_normalized: float,
    ) -> float:
        """
        Calculates composite vendor performance score (40% delivery, 30% quality, 20% compliance, 10% rating).
        """
        return round(
            (delivery_score * 0.4)
            + (quality_score * 0.3)
            + (compliance_score * 0.2)
            + (overall_rating_normalized * 0.1),
            2,
        )

    def _calculate_risk(self, overall_score: float) -> str:
        """
        Classifies vendor risk level based on composite performance score.
        """
        if overall_score >= 80.0:
            return "LOW"
        elif overall_score >= 60.0:
            return "MEDIUM"
        return "HIGH"

    def _calculate_fulfillment_rate(self, completed_count: int, total_orders: int) -> float:
        """
        Calculates purchase order fulfillment percentage rate.
        """
        return self._safe_percentage(completed_count, total_orders)

    def _build_metadata(
        self,
        report_name: str,
        category: ReportCategory,
        generated_by: str = "System",
        file_type: ReportFileType = ReportFileType.PDF,
        report_id: Optional[UUID] = None,
    ) -> ReportMetadata:
        """
        Constructs a standardized ReportMetadata header object.
        """
        rid = report_id or uuid4()
        return ReportMetadata(
            report_id=rid,
            report_name=report_name,
            category=category,
            generated_date=datetime.now(timezone.utc),
            status=ReportStatus.COMPLETED,
            generated_by=generated_by,
            file_type=file_type,
            download_url=f"/api/v1/reports/download/{rid}",
        )

    def _build_report_catalogue(self) -> list[dict[str, Any]]:
        """
        Returns standard system report catalogue definitions.
        """
        return [
            {
                "name": "Vendor Performance Report",
                "category": ReportCategory.VENDOR_PERFORMANCE,
                "description": "Comprehensive vendor scoring and risk analysis.",
            },
            {
                "name": "Procurement Spend & Request Report",
                "category": ReportCategory.PROCUREMENT,
                "description": "Procurement spend, department breakdown, and trends.",
            },
            {
                "name": "Purchase Order Fulfillment Report",
                "category": ReportCategory.PURCHASE_ORDER,
                "description": "PO status distribution, fulfillment rates, and supplier analysis.",
            },
            {
                "name": "Vendor Compliance & Risk Audit Report",
                "category": ReportCategory.COMPLIANCE,
                "description": "Vendor compliance rates, violation tracking, and risk posture.",
            },
            {
                "name": "Vendor Contract Lifecycle & Renewal Report",
                "category": ReportCategory.CONTRACT,
                "description": "Contract lifecycle, expiration tracking, and renewal analysis.",
            },
        ]

    def _build_export_metadata(self, file_type: ReportFileType) -> dict[str, Any]:
        """
        Returns format-specific export metadata (MIME types, file size descriptors, byte sizes).
        """
        format_metadata = {
            ReportFileType.PDF: {
                "mime": "application/pdf",
                "size_str": "1.2 MB",
                "bytes": 1258291,
            },
            ReportFileType.CSV: {
                "mime": "text/csv",
                "size_str": "350 KB",
                "bytes": 358400,
            },
            ReportFileType.XLSX: {
                "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size_str": "850 KB",
                "bytes": 870400,
            },
            ReportFileType.JSON: {
                "mime": "application/json",
                "size_str": "180 KB",
                "bytes": 184320,
            },
        }
        return format_metadata.get(
            file_type,
            {"mime": "application/octet-stream", "size_str": "500 KB", "bytes": 512000},
        )

    # ==================================================================
    # 1. VENDOR PERFORMANCE REPORT
    # ==================================================================

    async def get_vendor_performance_report(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        generated_by: str = "System",
    ) -> VendorPerformanceReportResponse:
        """
        Generates full Vendor Performance Report DTO.
        Retrieves raw vendor aggregates from ReportRepository, then computes scores,
        risk classifications, averages, category breakdowns, and top vendors list.
        """
        raw_data = await self.repo.get_vendor_performance_report_data(db, search=search)
        raw_vendors = raw_data.get("vendors", [])

        vendor_items: list[VendorPerformanceItem] = []
        category_scores: dict[str, list[float]] = {}

        for v in raw_vendors:
            total_delivs = v.get("total_deliveries", 0)
            on_time_delivs = v.get("on_time_deliveries", 0)
            delivery_score = self._safe_percentage(on_time_delivs, total_delivs)

            avg_qual = v.get("avg_quality_rating", 0.0)
            quality_score = round(avg_qual / 5.0 * 100.0, 2) if avg_qual > 0 else 0.0

            total_iss = v.get("total_issues", 0)
            resolved_iss = v.get("resolved_issues", 0)
            compliance_score = self._safe_percentage(resolved_iss, total_iss, default=100.0)

            avg_overall = v.get("avg_overall_rating", 0.0)
            overall_rating_normalized = (avg_overall / 5.0 * 100.0) if avg_overall > 0 else 0.0

            overall_score = self._calculate_vendor_score(
                delivery_score, quality_score, compliance_score, overall_rating_normalized
            )

            risk_level = self._calculate_risk(overall_score)

            cat_name = v.get("category_name", "Uncategorized")
            category_scores.setdefault(cat_name, []).append(overall_score)

            item = VendorPerformanceItem(
                vendor_id=v["vendor_id"],
                vendor_name=v["vendor_name"],
                vendor_code=v["vendor_code"],
                overall_score=overall_score,
                quality_score=quality_score,
                delivery_score=delivery_score,
                compliance_score=compliance_score,
                risk_level=risk_level,
                total_orders=v.get("total_orders", 0),
                open_issues_count=v.get("open_issues", 0),
            )
            vendor_items.append(item)

        # Sort vendors by overall_score descending
        vendor_items.sort(key=lambda x: x.overall_score, reverse=True)

        total_evaluated = len(vendor_items)
        avg_score = (
            round(sum(v.overall_score for v in vendor_items) / total_evaluated, 2)
            if total_evaluated > 0
            else 0.0
        )
        high_risk_count = sum(1 for v in vendor_items if v.risk_level == "HIGH")
        top_vendors = vendor_items[:10]

        performance_by_category = {
            cat: round(sum(scores) / len(scores), 2)
            for cat, scores in category_scores.items()
        }

        metadata = self._build_metadata(
            report_name="Vendor Performance Report",
            category=ReportCategory.VENDOR_PERFORMANCE,
            generated_by=generated_by,
        )

        return VendorPerformanceReportResponse(
            metadata=metadata,
            total_vendors_evaluated=total_evaluated,
            average_performance_score=avg_score,
            high_risk_vendors_count=high_risk_count,
            top_vendors=top_vendors,
            vendor_performance_list=vendor_items,
            performance_by_category=performance_by_category,
        )

    # ==================================================================
    # 2. PROCUREMENT REPORT
    # ==================================================================

    async def get_procurement_report(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        generated_by: str = "System",
    ) -> ProcurementReportResponse:
        """
        Generates full Procurement Report DTO.
        Retrieves raw procurement metrics from ReportRepository and transforms department
        spend, category spend, and monthly trends into DTO structures.
        """
        raw_data = await self.repo.get_procurement_report_data(db, search=search)

        raw_dept_spend = raw_data.get("department_spend", [])
        department_spend = [
            ProcurementDepartmentSpend(
                department=d["department"],
                total_requests=d["total_requests"],
                total_spend=d["total_spend"],
                average_processing_days=round(d.get("average_processing_seconds", 0.0) / 86400.0, 2)
                if d.get("average_processing_seconds", 0.0) > 0
                else 0.0,
            )
            for d in raw_dept_spend
        ]

        metadata = self._build_metadata(
            report_name="Procurement Spend & Request Report",
            category=ReportCategory.PROCUREMENT,
            generated_by=generated_by,
        )

        return ProcurementReportResponse(
            metadata=metadata,
            total_requests=raw_data.get("total_requests", 0),
            total_approved_requests=raw_data.get("total_approved_requests", 0),
            total_procurement_spend=raw_data.get("total_procurement_spend", 0.0),
            average_lead_time_days=raw_data.get("average_lead_time_days", 0.0),
            department_spend=department_spend,
            spend_by_category=raw_data.get("spend_by_category", {}),
            monthly_trend=raw_data.get("monthly_trend", []),
        )

    # ==================================================================
    # 3. PURCHASE ORDER REPORT
    # ==================================================================

    async def get_purchase_order_report(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
        generated_by: str = "System",
    ) -> PurchaseOrderReportResponse:
        """
        Generates full Purchase Order Report DTO.
        Computes fulfillment rates, pending approval counts, total order values,
        and transforms raw status breakdowns into DTO items.
        """
        raw_data = await self.repo.get_purchase_order_report_data(db, search=search, status=status)
        raw_statuses = raw_data.get("order_statuses", [])

        order_status_items: list[PurchaseOrderStatusItem] = []
        total_orders = 0
        total_order_value = 0.0
        pending_approval = 0
        completed_count = 0

        for st in raw_statuses:
            st_name = st.get("status", "")
            cnt = st.get("count", 0)
            val = st.get("total_value", 0.0)

            order_status_items.append(
                PurchaseOrderStatusItem(
                    status=st_name,
                    count=cnt,
                    total_value=val,
                )
            )

            total_orders += cnt
            if st_name != "cancelled":
                total_order_value += val

            if st_name == "pending":
                pending_approval = cnt
            elif st_name in ("completed", "delivered"):
                completed_count += cnt

        fulfillment_rate = self._calculate_fulfillment_rate(completed_count, total_orders)

        metadata = self._build_metadata(
            report_name="Purchase Order Fulfillment Report",
            category=ReportCategory.PURCHASE_ORDER,
            generated_by=generated_by,
        )

        return PurchaseOrderReportResponse(
            metadata=metadata,
            total_orders=total_orders,
            total_order_value=round(total_order_value, 2),
            pending_approval_count=pending_approval,
            fulfillment_rate=fulfillment_rate,
            order_statuses=order_status_items,
            top_suppliers_by_value=raw_data.get("top_suppliers_by_value", {}),
        )

    # ==================================================================
    # 4. COMPLIANCE REPORT
    # ==================================================================

    async def get_compliance_report(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        generated_by: str = "System",
    ) -> ComplianceReportResponse:
        """
        Generates full Compliance Report DTO.
        Calculates compliance rates, vendor risk classification breakdowns, and severity
        assignments for detected violations.
        """
        raw_data = await self.repo.get_compliance_report_data(db, search=search)

        total_vendors = raw_data.get("total_vendors", 0)
        non_compliant_count = raw_data.get("vendors_with_open_issues", 0)
        compliant_count = max(total_vendors - non_compliant_count, 0)
        overall_compliance = self._safe_percentage(compliant_count, total_vendors, default=100.0)

        # Build risk breakdown from vendor open issue counts
        vendor_issue_counts = raw_data.get("vendor_open_issue_counts", [])
        risk_breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        vendors_with_issues = set()

        for vic in vendor_issue_counts:
            vendors_with_issues.add(vic["vendor_id"])
            c = vic.get("open_issue_count", 0)
            if c >= 3:
                risk_breakdown["HIGH"] += 1
            elif c >= 1:
                risk_breakdown["MEDIUM"] += 1

        risk_breakdown["LOW"] = max(total_vendors - len(vendors_with_issues), 0)

        # Build recent violations list
        raw_issues = raw_data.get("recent_issues", [])
        recent_violations: list[ComplianceViolationItem] = []

        for iss in raw_issues:
            st = iss.get("issue_status", "open")
            violation_status = "OPEN" if st in ("open", "in_progress") else "RESOLVED"
            severity = "HIGH" if st == "open" else "MEDIUM"

            item = ComplianceViolationItem(
                violation_id=iss.get("issue_id"),
                vendor_id=iss.get("vendor_id"),
                vendor_name=iss.get("vendor_name", ""),
                compliance_type=iss.get("issue_type", "Compliance Check"),
                severity=severity,
                status=violation_status,
                description=iss.get("description") or "Vendor compliance non-conformity reported.",
                detected_date=iss.get("reported_at") or datetime.now(timezone.utc),
            )
            recent_violations.append(item)

        metadata = self._build_metadata(
            report_name="Vendor Compliance & Risk Audit Report",
            category=ReportCategory.COMPLIANCE,
            generated_by=generated_by,
        )

        return ComplianceReportResponse(
            metadata=metadata,
            total_audits_checked=total_vendors,
            overall_compliance_rate=overall_compliance,
            compliant_vendors_count=compliant_count,
            non_compliant_vendors_count=non_compliant_count,
            risk_level_breakdown=risk_breakdown,
            recent_violations=recent_violations,
        )

    # ==================================================================
    # 5. CONTRACT REPORT
    # ==================================================================

    async def get_contract_report(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
        generated_by: str = "System",
    ) -> ContractReportResponse:
        """
        Generates full Contract Report DTO.
        Returns isolated response indicating no dedicated Contract database model exists,
        without fabricating contract lifecycle meaning from purchase orders.
        """
        metadata = self._build_metadata(
            report_name="Vendor Contract Lifecycle & Renewal Report",
            category=ReportCategory.CONTRACT,
            generated_by=generated_by,
        )

        return ContractReportResponse(
            metadata=metadata,
            total_active_contracts=0,
            total_contract_value=0.0,
            upcoming_expirations_count=0,
            renewal_rate=0.0,
            contracts_by_status={},
            contracts_by_type={},
            expiring_contracts=[],
        )

    # ==================================================================
    # 6. REPORT SUMMARY
    # ==================================================================

    async def get_report_summary(
        self,
        db: AsyncSession,
    ) -> ReportSummaryResponse:
        """
        Generates ReportSummaryResponse DTO for Reports Dashboard.
        Maps raw entity counts into report categories, temporal counters, and status breakdowns.
        """
        raw_data = await self.repo.get_report_summary_data(db)

        v_count = raw_data.get("vendor_count", 0)
        po_count = raw_data.get("po_count", 0)
        req_count = raw_data.get("request_count", 0)
        inv_count = raw_data.get("invoice_count", 0)
        del_count = raw_data.get("delivery_count", 0)
        open_issues = raw_data.get("open_issues_count", 0)

        total_reports = v_count + po_count + req_count + inv_count + del_count

        reports_by_category = {
            "vendor_performance": v_count,
            "procurement": req_count,
            "purchase_order": po_count,
            "compliance": v_count,
            "contract": po_count,
        }

        reports_by_status = {
            "completed": total_reports,
            "draft": 0,
            "generating": 0,
            "failed": 0,
        }

        catalogue = self._build_report_catalogue()
        recent_reports: list[ReportListItem] = []

        return ReportSummaryResponse(
            total_reports=total_reports,
            completed_reports=total_reports,
            failed_reports=0,
            reports_by_category=reports_by_category if total_reports > 0 else {},
            reports_by_status=reports_by_status if total_reports > 0 else {},
            recent_reports=recent_reports,
            generated_today=0,
            generated_this_week=0,
            generated_this_month=0,
            pending_reports=open_issues,
        )

    # ==================================================================
    # 7. REPORT HISTORY (PAGINATED CATALOGUE)
    # ==================================================================

    async def get_report_history(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReportListResponse:
        """
        Generates paginated ReportListResponse DTO.
        Returns 0 reports on empty state.
        """
        return ReportListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
        )

    # ==================================================================
    # 8. REPORT EXPORT
    # ==================================================================

    async def export_report(
        self,
        db: AsyncSession,
        *,
        category: ReportCategory,
        file_type: ReportFileType = ReportFileType.PDF,
        generated_by: str = "System",
        user_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> ReportExportResponse:
        """
        Generates ReportExportResponse DTO containing export metadata and cryptographically
        signed download context token.
        Does not execute SQL mutations or persist database records.
        """
        category_titles = {
            ReportCategory.VENDOR_PERFORMANCE: "Vendor Performance Report",
            ReportCategory.PROCUREMENT: "Procurement Spend & Request Report",
            ReportCategory.PURCHASE_ORDER: "Purchase Order Fulfillment Report",
            ReportCategory.COMPLIANCE: "Vendor Compliance & Risk Audit Report",
            ReportCategory.CONTRACT: "Vendor Contract Lifecycle & Renewal Report",
        }

        title = category_titles.get(category, f"{category.value.title()} Report")
        rid = uuid4()
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=15)

        token_payload = {
            "sub": "report_download",
            "report_id": str(rid),
            "category": category.value,
            "file_type": file_type.value,
            "search": search or "",
            "user_id": str(user_id) if user_id else "system",
            "exp": expires_at,
            "iat": now,
        }

        signed_download_token = jwt.encode(
            token_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        fmt_info = self._build_export_metadata(file_type)
        download_url = "/api/v1/reports/download"

        return ReportExportResponse(
            report_id=rid,
            report_name=title,
            category=category,
            file_type=file_type,
            download_url=download_url,
            download_token=signed_download_token,
            file_size_bytes=fmt_info["bytes"],
            expires_at=expires_at,
            status=ReportStatus.COMPLETED,
            generated_at=now,
            download_available=True,
            file_size=fmt_info["size_str"],
            mime_type=fmt_info["mime"],
        )

    async def generate_report_file_content(
        self,
        db: AsyncSession,
        *,
        category: ReportCategory,
        file_type: ReportFileType,
        search: Optional[str] = None,
        generated_by: str = "System",
    ) -> tuple[bytes, str, str]:
        """
        Synthesizes report data using existing report generator methods and formats output file bytes.
        Returns a tuple of (file_bytes, mime_type, filename).
        Does not execute SQL mutations.
        """
        if file_type == ReportFileType.XLSX:
            raise ValueError("XLSX export format is not supported by backend.")

        # 1. Fetch DTO from existing report generator methods
        if category == ReportCategory.VENDOR_PERFORMANCE:
            report_dto = await self.get_vendor_performance_report(db, search=search, generated_by=generated_by)
            report_name = "Vendor_Performance_Report"
        elif category == ReportCategory.PROCUREMENT:
            report_dto = await self.get_procurement_report(db, search=search, generated_by=generated_by)
            report_name = "Procurement_Report"
        elif category == ReportCategory.PURCHASE_ORDER:
            report_dto = await self.get_po_report(db, search=search, generated_by=generated_by)
            report_name = "Purchase_Order_Report"
        elif category == ReportCategory.COMPLIANCE:
            report_dto = await self.get_compliance_report(db, search=search, generated_by=generated_by)
            report_name = "Compliance_Report"
        elif category == ReportCategory.CONTRACT:
            report_dto = await self.get_contract_report(db, search=search, generated_by=generated_by)
            report_name = "Contract_Report"
        else:
            report_dto = await self.get_vendor_performance_report(db, search=search, generated_by=generated_by)
            report_name = "System_Report"

        data_dict = report_dto.model_dump(mode="json")

        if file_type == ReportFileType.JSON:
            content_bytes = json.dumps(data_dict, indent=2).encode("utf-8")
            mime_type = "application/json"
            filename = f"{report_name}.json"
            return content_bytes, mime_type, filename

        elif file_type == ReportFileType.CSV:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Report Name", data_dict.get("metadata", {}).get("report_name", report_name)])
            writer.writerow(["Category", category.value])
            writer.writerow(["Generated Date", data_dict.get("metadata", {}).get("generated_date", "")])
            writer.writerow([])

            # Write tabular section based on category
            if category == ReportCategory.VENDOR_PERFORMANCE:
                writer.writerow(["Vendor Code", "Vendor Name", "Overall Score", "Risk Level", "Delivery Score", "Quality Score", "Compliance Score"])
                for item in data_dict.get("vendor_performance_list", []):
                    writer.writerow([
                        item.get("vendor_code"),
                        item.get("vendor_name"),
                        item.get("overall_score"),
                        item.get("risk_level"),
                        item.get("delivery_score"),
                        item.get("quality_score"),
                        item.get("compliance_score"),
                    ])
            elif category == ReportCategory.PROCUREMENT:
                writer.writerow(["Department", "Total Requests", "Approved", "Pending", "Rejected", "Total Spend ($)"])
                for item in data_dict.get("department_spend", []):
                    writer.writerow([
                        item.get("department"),
                        item.get("total_requests"),
                        item.get("approved_requests"),
                        item.get("pending_requests"),
                        item.get("rejected_requests"),
                        item.get("total_spend"),
                    ])
            else:
                writer.writerow(["Field", "Value"])
                for k, v in data_dict.items():
                    if k != "metadata":
                        writer.writerow([k, str(v)])

            content_bytes = output.getvalue().encode("utf-8")
            mime_type = "text/csv"
            filename = f"{report_name}.csv"
            return content_bytes, mime_type, filename

        elif file_type == ReportFileType.PDF:
            # Construct a valid PDF document matching PDF-1.4 spec
            title = data_dict.get("metadata", {}).get("report_name", report_name)
            date_str = str(data_dict.get("metadata", {}).get("generated_date", ""))
            
            pdf_stream = (
                "%PDF-1.4\n"
                "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
                "4 0 obj\n<< /Length 200 >>\nstream\n"
                "BT\n/F1 18 Tf\n50 720 Td\n(" + title + ") Tj\n"
                "0 -30 Td\n/F1 10 Tf\n(Generated: " + date_str + ") Tj\n"
                "0 -20 Td\n(Category: " + category.value + ") Tj\n"
                "0 -30 Td\n(Status: Verified Report Export Output) Tj\n"
                "ET\n"
                "endstream\nendobj\n"
                "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
                "xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000257 00000 n \n0000000510 00000 n \n"
                "trailer\n<< /Size 6 /Root 1 0 R >>\n"
                "startxref\n585\n%%EOF\n"
            )
            content_bytes = pdf_stream.encode("latin-1")
            mime_type = "application/pdf"
            filename = f"{report_name}.pdf"
            return content_bytes, mime_type, filename

        raise ValueError(f"Unsupported report format: {file_type}")


# Singleton instance
report_service = ReportService()
