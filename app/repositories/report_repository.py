"""
Repository layer for Reports dynamic aggregation queries using SQLAlchemy 2.0 Async.
Read-only repository executing SQL aggregate queries across existing domain models
to retrieve raw counts and metrics for the service layer.

No ORM model. No database table. No write operations.
No business logic, scoring, classification, or rate calculations.
"""

from typing import Any, Optional

from sqlalchemy import (
    Float,
    cast,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import DeliveryStatusEnum, DeliveryTracking
from app.models.invoices import Invoice
from app.models.procurement import (
    ProcurementRequest,
    PurchaseOrder,
    PurchaseOrderStatusEnum,
    RequestStatusEnum,
)
from app.models.vendor_categories import VendorCategory
from app.models.vendor_performance import (
    IssueStatusEnum,
    VendorIssue,
    VendorRating,
)
from app.models.vendors import Vendor, VendorStatusEnum
from app.models.reports import Report


class ReportRepository:
    """
    Read-only repository executing runtime SQL aggregate queries for the Reports module.
    Returns raw counts, sums, and averages as plain Python dicts/lists.
    All business logic (scoring, classification, rate computation) belongs in the service layer.
    No write operations are performed.
    """

    # ==================================================================
    # 1. VENDOR PERFORMANCE REPORT — Raw Data
    # ==================================================================

    async def get_vendor_performance_report_data(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieves per-vendor raw aggregates across PurchaseOrders, DeliveryTracking,
        VendorRatings, and VendorIssues.

        Returns raw counts and averages per vendor. Does NOT compute scores,
        risk levels, or composite rankings — those belong in the service layer.
        """
        # --- Fetch approved vendors with category ---
        vendor_stmt = select(
            Vendor.vendor_id,
            Vendor.company_name,
            Vendor.vendor_code,
            VendorCategory.category_name,
        ).join(VendorCategory, Vendor.category_id == VendorCategory.category_id)

        if search:
            search_filter = f"%{search}%"
            vendor_stmt = vendor_stmt.where(
                or_(
                    Vendor.company_name.ilike(search_filter),
                    Vendor.vendor_code.ilike(search_filter),
                )
            )

        vendor_stmt = vendor_stmt.where(Vendor.status == VendorStatusEnum.APPROVED)
        vendor_rows = (await db.execute(vendor_stmt)).all()

        vendors: list[dict[str, Any]] = []

        for v_row in vendor_rows:
            vid = v_row.vendor_id

            # Purchase Orders count
            po_stmt = select(
                func.count(PurchaseOrder.po_id).label("total_orders"),
            ).where(PurchaseOrder.vendor_id == vid)
            po_row = (await db.execute(po_stmt)).first()
            total_orders = po_row.total_orders if po_row else 0

            # Delivery counts
            deliv_stmt = (
                select(
                    func.count(DeliveryTracking.delivery_id).label("total_deliveries"),
                    func.count(
                        func.nullif(
                            or_(
                                DeliveryTracking.delivery_status != DeliveryStatusEnum.DELIVERED,
                                DeliveryTracking.delivered_date > DeliveryTracking.expected_date,
                            ),
                            True,
                        )
                    ).label("on_time_deliveries"),
                )
                .select_from(DeliveryTracking)
                .join(PurchaseOrder, DeliveryTracking.po_id == PurchaseOrder.po_id)
                .where(PurchaseOrder.vendor_id == vid)
            )
            d_row = (await db.execute(deliv_stmt)).first()
            total_deliveries = d_row.total_deliveries if d_row else 0
            on_time_deliveries = d_row.on_time_deliveries if d_row else 0

            # Rating averages
            r_stmt = select(
                func.avg(VendorRating.quality_rating).label("avg_quality_rating"),
                func.avg(VendorRating.delivery_rating).label("avg_delivery_rating"),
                func.avg(VendorRating.communication_rating).label("avg_communication_rating"),
                func.avg(VendorRating.overall_rating).label("avg_overall_rating"),
            ).where(VendorRating.vendor_id == vid)
            r_row = (await db.execute(r_stmt)).first()
            avg_quality_rating = round(float(r_row.avg_quality_rating), 2) if (r_row and r_row.avg_quality_rating) else 0.0
            avg_delivery_rating = round(float(r_row.avg_delivery_rating), 2) if (r_row and r_row.avg_delivery_rating) else 0.0
            avg_communication_rating = round(float(r_row.avg_communication_rating), 2) if (r_row and r_row.avg_communication_rating) else 0.0
            avg_overall_rating = round(float(r_row.avg_overall_rating), 2) if (r_row and r_row.avg_overall_rating) else 0.0

            # Issue counts
            total_issues_stmt = select(
                func.count(VendorIssue.issue_id).label("total_issues"),
            ).where(VendorIssue.vendor_id == vid)
            total_issues = (await db.execute(total_issues_stmt)).scalar_one_or_none() or 0

            open_issues_stmt = select(
                func.count(VendorIssue.issue_id).label("open_issues"),
            ).where(
                VendorIssue.vendor_id == vid,
                VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]),
            )
            open_issues = (await db.execute(open_issues_stmt)).scalar_one_or_none() or 0

            resolved_issues_stmt = select(
                func.count(VendorIssue.issue_id).label("resolved_issues"),
            ).where(
                VendorIssue.vendor_id == vid,
                VendorIssue.status.in_([IssueStatusEnum.RESOLVED, IssueStatusEnum.CLOSED]),
            )
            resolved_issues = (await db.execute(resolved_issues_stmt)).scalar_one_or_none() or 0

            vendors.append({
                "vendor_id": vid,
                "vendor_name": v_row.company_name,
                "vendor_code": v_row.vendor_code,
                "category_name": v_row.category_name or "Uncategorized",
                "total_orders": total_orders,
                "total_deliveries": total_deliveries,
                "on_time_deliveries": on_time_deliveries,
                "avg_quality_rating": avg_quality_rating,
                "avg_delivery_rating": avg_delivery_rating,
                "avg_communication_rating": avg_communication_rating,
                "avg_overall_rating": avg_overall_rating,
                "total_issues": total_issues,
                "open_issues": open_issues,
                "resolved_issues": resolved_issues,
            })

        return {
            "total_vendors_evaluated": len(vendors),
            "vendors": vendors,
        }

    # ==================================================================
    # 2. PROCUREMENT REPORT — Raw Data
    # ==================================================================

    async def get_procurement_report_data(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieves procurement request counts, spend totals, department breakdowns,
        category spend, and monthly trends as raw aggregates.
        """
        # --- Total Requests ---
        req_stmt = select(func.count(ProcurementRequest.request_id))
        if search:
            search_filter = f"%{search}%"
            req_stmt = req_stmt.where(
                ProcurementRequest.item_description.ilike(search_filter)
            )
        total_requests = (await db.execute(req_stmt)).scalar_one_or_none() or 0

        # --- Approved Requests ---
        approved_stmt = select(func.count(ProcurementRequest.request_id)).where(
            ProcurementRequest.status.in_([
                RequestStatusEnum.APPROVED,
                RequestStatusEnum.CONVERTED_TO_PO,
            ])
        )
        total_approved = (await db.execute(approved_stmt)).scalar_one_or_none() or 0

        # --- Total PO Spend (non-cancelled) ---
        spend_stmt = select(
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("total_spend"),
        ).where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)
        total_spend = float((await db.execute(spend_stmt)).scalar_one_or_none() or 0.0)

        # --- Average Lead Time (order_date to actual_delivery_date for completed POs) ---
        lead_stmt = select(
            func.avg(
                cast(
                    PurchaseOrder.actual_delivery_date - PurchaseOrder.order_date,
                    Float,
                )
            ).label("avg_lead"),
        ).where(
            PurchaseOrder.status == PurchaseOrderStatusEnum.COMPLETED,
            PurchaseOrder.actual_delivery_date.isnot(None),
        )
        avg_lead_val = (await db.execute(lead_stmt)).scalar_one_or_none()
        avg_lead_time = round(float(avg_lead_val), 2) if avg_lead_val else 0.0

        # --- Department Spend Breakdown ---
        dept_stmt = (
            select(
                ProcurementRequest.department,
                func.count(ProcurementRequest.request_id).label("total_requests"),
                func.coalesce(func.sum(ProcurementRequest.estimated_cost), 0.0).label("total_spend"),
                func.avg(
                    func.extract("epoch", ProcurementRequest.updated_at - ProcurementRequest.created_at)
                ).label("avg_processing_seconds"),
            )
            .where(ProcurementRequest.department.isnot(None))
            .group_by(ProcurementRequest.department)
            .order_by(func.coalesce(func.sum(ProcurementRequest.estimated_cost), 0.0).desc())
        )
        dept_rows = (await db.execute(dept_stmt)).all()

        department_spend = [
            {
                "department": row.department,
                "total_requests": row.total_requests,
                "total_spend": round(float(row.total_spend), 2),
                "average_processing_seconds": float(row.avg_processing_seconds) if row.avg_processing_seconds else 0.0,
            }
            for row in dept_rows
        ]

        # --- Spend by Vendor Category ---
        cat_stmt = (
            select(
                VendorCategory.category_name,
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("cat_spend"),
            )
            .select_from(PurchaseOrder)
            .join(Vendor, PurchaseOrder.vendor_id == Vendor.vendor_id)
            .join(VendorCategory, Vendor.category_id == VendorCategory.category_id)
            .where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)
            .group_by(VendorCategory.category_name)
            .order_by(func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).desc())
        )
        cat_rows = (await db.execute(cat_stmt)).all()
        spend_by_category = {
            row.category_name: round(float(row.cat_spend), 2) for row in cat_rows
        }

        # --- Monthly Spend Trend ---
        month_expr = func.to_char(PurchaseOrder.created_at, text("'YYYY-MM'"))
        trend_stmt = (
            select(
                month_expr.label("month_label"),
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("monthly_amount"),
                func.count(PurchaseOrder.po_id).label("monthly_count"),
            )
            .where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)
            .group_by(month_expr)
            .order_by(month_expr)
        )
        trend_rows = (await db.execute(trend_stmt)).all()

        monthly_trend = [
            {
                "month": r.month_label,
                "total_amount": round(float(r.monthly_amount), 2),
                "count": r.monthly_count,
            }
            for r in trend_rows
        ]

        return {
            "total_requests": total_requests,
            "total_approved_requests": total_approved,
            "total_procurement_spend": round(total_spend, 2),
            "average_lead_time_days": avg_lead_time,
            "department_spend": department_spend,
            "spend_by_category": spend_by_category,
            "monthly_trend": monthly_trend,
        }

    # ==================================================================
    # 3. PURCHASE ORDER REPORT — Raw Data
    # ==================================================================

    async def get_purchase_order_report_data(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieves purchase order counts grouped by status, total values,
        and top suppliers by spend. Returns raw counts for the service layer
        to compute fulfillment rates and other derived metrics.
        """
        # --- Status Breakdown ---
        po_status_stmt = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.po_id).label("status_count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("status_value"),
        ).group_by(PurchaseOrder.status)

        if status:
            try:
                status_enum = PurchaseOrderStatusEnum(status)
                po_status_stmt = po_status_stmt.where(PurchaseOrder.status == status_enum)
            except ValueError:
                pass  # Invalid status filter — return all

        po_status_rows = (await db.execute(po_status_stmt)).all()

        order_statuses: list[dict[str, Any]] = []
        for row in po_status_rows:
            st_val = row.status.value if hasattr(row.status, "value") else str(row.status)
            order_statuses.append({
                "status": st_val,
                "count": row.status_count,
                "total_value": round(float(row.status_value), 2),
            })

        # --- Top Suppliers by PO Value ---
        top_stmt = (
            select(
                Vendor.company_name,
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("vendor_total"),
            )
            .join(Vendor, PurchaseOrder.vendor_id == Vendor.vendor_id)
            .where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)
            .group_by(Vendor.company_name)
            .order_by(func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).desc())
            .limit(10)
        )
        if search:
            search_filter = f"%{search}%"
            top_stmt = top_stmt.where(
                or_(
                    Vendor.company_name.ilike(search_filter),
                    PurchaseOrder.po_number.ilike(search_filter),
                )
            )

        top_rows = (await db.execute(top_stmt)).all()
        top_suppliers_by_value = {
            row.company_name: round(float(row.vendor_total), 2) for row in top_rows
        }

        return {
            "order_statuses": order_statuses,
            "top_suppliers_by_value": top_suppliers_by_value,
        }

    # ==================================================================
    # 4. COMPLIANCE REPORT — Raw Data
    # ==================================================================

    async def get_compliance_report_data(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieves vendor issue counts and vendor totals for compliance assessment.
        Returns raw counts — compliance rate, risk classification, and severity
        assignment belong in the service layer.
        """
        # --- Total approved vendors ---
        total_vendors_stmt = select(func.count(Vendor.vendor_id)).where(
            Vendor.status == VendorStatusEnum.APPROVED
        )
        total_vendors = (await db.execute(total_vendors_stmt)).scalar_one_or_none() or 0

        # --- Distinct vendors with open/in-progress issues ---
        vendors_with_open_issues_stmt = (
            select(func.count(func.distinct(VendorIssue.vendor_id)))
            .where(
                VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]),
            )
        )
        vendors_with_open_issues = (await db.execute(vendors_with_open_issues_stmt)).scalar_one_or_none() or 0

        # --- Per-vendor open issue counts (for service layer risk classification) ---
        open_issue_counts_stmt = (
            select(
                VendorIssue.vendor_id,
                func.count(VendorIssue.issue_id).label("open_issue_count"),
            )
            .where(
                VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]),
            )
            .group_by(VendorIssue.vendor_id)
        )
        open_issue_rows = (await db.execute(open_issue_counts_stmt)).all()
        vendor_open_issue_counts = [
            {
                "vendor_id": row.vendor_id,
                "open_issue_count": row.open_issue_count,
            }
            for row in open_issue_rows
        ]

        # --- Recent open issues with vendor info ---
        issues_stmt = (
            select(
                VendorIssue.issue_id,
                VendorIssue.vendor_id,
                Vendor.company_name,
                VendorIssue.issue_type,
                VendorIssue.status,
                VendorIssue.description,
                VendorIssue.reported_at,
            )
            .join(Vendor, VendorIssue.vendor_id == Vendor.vendor_id)
            .where(
                VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]),
            )
            .order_by(VendorIssue.reported_at.desc())
            .limit(20)
        )
        if search:
            search_filter = f"%{search}%"
            issues_stmt = issues_stmt.where(
                or_(
                    Vendor.company_name.ilike(search_filter),
                    VendorIssue.issue_type.ilike(search_filter),
                )
            )

        issue_rows = (await db.execute(issues_stmt)).all()

        recent_issues = [
            {
                "issue_id": row.issue_id,
                "vendor_id": row.vendor_id,
                "vendor_name": row.company_name,
                "issue_type": row.issue_type,
                "issue_status": row.status.value if hasattr(row.status, "value") else str(row.status),
                "description": row.description,
                "reported_at": row.reported_at,
            }
            for row in issue_rows
        ]

        return {
            "total_vendors": total_vendors,
            "vendors_with_open_issues": vendors_with_open_issues,
            "vendor_open_issue_counts": vendor_open_issue_counts,
            "recent_issues": recent_issues,
        }

    # ==================================================================
    # 5. CONTRACT REPORT — Raw Data
    # ==================================================================

    async def get_contract_report_data(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieves purchase order data that may serve as a basis for contract reporting.
        No contract model exists in the system; this method returns raw PO aggregates
        without mapping them to contract lifecycle semantics.

        The service layer is responsible for any PO-to-contract mapping if needed.
        """
        base_filter = PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED

        # --- PO Status Breakdown (raw, no contract mapping) ---
        po_status_stmt = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.po_id).label("status_count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("status_value"),
        ).where(base_filter).group_by(PurchaseOrder.status)

        po_status_rows = (await db.execute(po_status_stmt)).all()

        po_status_breakdown = [
            {
                "status": row.status.value if hasattr(row.status, "value") else str(row.status),
                "count": row.status_count,
                "total_value": round(float(row.status_value), 2),
            }
            for row in po_status_rows
        ]

        # --- Total PO Value (non-cancelled) ---
        value_stmt = select(
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("total_value"),
        ).where(base_filter)
        total_value = round(float((await db.execute(value_stmt)).scalar_one_or_none() or 0.0), 2)

        # --- PO Count by Vendor Category ---
        type_stmt = (
            select(
                VendorCategory.category_name,
                func.count(PurchaseOrder.po_id).label("type_count"),
            )
            .select_from(PurchaseOrder)
            .join(Vendor, PurchaseOrder.vendor_id == Vendor.vendor_id)
            .join(VendorCategory, Vendor.category_id == VendorCategory.category_id)
            .where(base_filter)
            .group_by(VendorCategory.category_name)
        )
        type_rows = (await db.execute(type_stmt)).all()
        po_count_by_category = {row.category_name: row.type_count for row in type_rows}

        # --- POs approaching expected delivery (within 90 days) ---
        upcoming_stmt = (
            select(
                PurchaseOrder.po_id,
                PurchaseOrder.po_number,
                Vendor.company_name,
                PurchaseOrder.total_amount,
                PurchaseOrder.order_date,
                PurchaseOrder.expected_delivery_date,
                PurchaseOrder.status,
                VendorCategory.category_name,
            )
            .join(Vendor, PurchaseOrder.vendor_id == Vendor.vendor_id)
            .join(VendorCategory, Vendor.category_id == VendorCategory.category_id)
            .where(
                base_filter,
                PurchaseOrder.expected_delivery_date.isnot(None),
                PurchaseOrder.expected_delivery_date >= func.current_date(),
                PurchaseOrder.expected_delivery_date <= func.current_date() + 90,
                PurchaseOrder.status.in_([
                    PurchaseOrderStatusEnum.PENDING,
                    PurchaseOrderStatusEnum.APPROVED,
                    PurchaseOrderStatusEnum.ORDERED,
                ]),
            )
            .order_by(PurchaseOrder.expected_delivery_date.asc())
            .limit(20)
        )
        if search:
            search_filter = f"%{search}%"
            upcoming_stmt = upcoming_stmt.where(
                or_(
                    Vendor.company_name.ilike(search_filter),
                    PurchaseOrder.po_number.ilike(search_filter),
                )
            )

        upcoming_rows = (await db.execute(upcoming_stmt)).all()

        upcoming_pos = [
            {
                "po_id": row.po_id,
                "po_number": row.po_number,
                "vendor_name": row.company_name,
                "total_amount": round(float(row.total_amount), 2),
                "order_date": row.order_date,
                "expected_delivery_date": row.expected_delivery_date,
                "status": row.status.value if hasattr(row.status, "value") else str(row.status),
                "category_name": row.category_name,
            }
            for row in upcoming_rows
        ]

        # --- Raw counts for service layer rate calculations ---
        total_non_cancelled_stmt = select(
            func.count(PurchaseOrder.po_id),
        ).where(base_filter)
        total_non_cancelled = (await db.execute(total_non_cancelled_stmt)).scalar_one_or_none() or 0

        completed_stmt = select(
            func.count(PurchaseOrder.po_id),
        ).where(PurchaseOrder.status == PurchaseOrderStatusEnum.COMPLETED)
        total_completed = (await db.execute(completed_stmt)).scalar_one_or_none() or 0

        return {
            "po_status_breakdown": po_status_breakdown,
            "total_po_value": total_value,
            "po_count_by_category": po_count_by_category,
            "upcoming_pos": upcoming_pos,
            "total_non_cancelled": total_non_cancelled,
            "total_completed": total_completed,
        }

    # ==================================================================
    # 6. REPORT SUMMARY — Raw Entity Counts
    # ==================================================================

    async def get_report_summary_data(
        self,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Retrieves raw entity counts across all domain modules.
        The service layer is responsible for mapping these counts into
        report-level summary semantics (e.g. total_reports, reports_by_category).
        """
        vendor_count = (await db.execute(
            select(func.count(Vendor.vendor_id))
        )).scalar_one_or_none() or 0

        po_count = (await db.execute(
            select(func.count(PurchaseOrder.po_id))
        )).scalar_one_or_none() or 0

        request_count = (await db.execute(
            select(func.count(ProcurementRequest.request_id))
        )).scalar_one_or_none() or 0

        invoice_count = (await db.execute(
            select(func.count(Invoice.invoice_id))
        )).scalar_one_or_none() or 0

        delivery_count = (await db.execute(
            select(func.count(DeliveryTracking.delivery_id))
        )).scalar_one_or_none() or 0

        open_issues_count = (await db.execute(
            select(func.count(VendorIssue.issue_id)).where(
                VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS])
            )
        )).scalar_one_or_none() or 0

        return {
            "vendor_count": vendor_count,
            "po_count": po_count,
            "request_count": request_count,
            "invoice_count": invoice_count,
            "delivery_count": delivery_count,
            "open_issues_count": open_issues_count,
        }

    # ==================================================================
    # 7. REPORT HISTORY — Data Retrieval Only
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
    ) -> dict[str, Any]:
        """
        Retrieves entity counts that the service layer can use to construct
        the report history / catalogue listing.

        Since there is no reports table, this method returns the raw data
        availability counts. The service layer is responsible for building
        the report catalogue, applying UI labels, and pagination logic.
        """
        vendor_count = (await db.execute(
            select(func.count(Vendor.vendor_id))
        )).scalar_one_or_none() or 0

        po_count = (await db.execute(
            select(func.count(PurchaseOrder.po_id))
        )).scalar_one_or_none() or 0

        request_count = (await db.execute(
            select(func.count(ProcurementRequest.request_id))
        )).scalar_one_or_none() or 0

        issue_count = (await db.execute(
            select(func.count(VendorIssue.issue_id))
        )).scalar_one_or_none() or 0

        return {
            "vendor_count": vendor_count,
            "po_count": po_count,
            "request_count": request_count,
            "issue_count": issue_count,
        }


# Singleton instance
report_repository = ReportRepository()
