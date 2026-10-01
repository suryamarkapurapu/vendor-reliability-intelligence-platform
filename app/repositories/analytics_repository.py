"""
Repository layer for Analytics dynamic aggregation queries using SQLAlchemy 2.0 Async.
Read-only repository executing high-performance SQL aggregate queries.
"""

from typing import Any

from sqlalchemy import (
    Case,
    Float,
    cast,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import DeliveryStatusEnum, DeliveryTracking
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.procurement import ProcurementRequest, PurchaseOrder, PurchaseOrderStatusEnum
from app.models.roles import Role
from app.models.users import User
from app.models.vendor_performance import IssueStatusEnum, VendorIssue, VendorRating
from app.models.vendors import Vendor, VendorStatusEnum


class AnalyticsRepository:
    """
    Read-only repository executing runtime SQL aggregate queries for Analytics dashboard & reports.
    """

    async def get_executive_dashboard_metrics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes parallelized aggregation for Executive Dashboard KPIs.
        """
        import asyncio

        # 1. Vendor Counts
        v_stmt = select(
            func.count(Vendor.vendor_id).label("total_vendors"),
            func.count(func.nullif(Vendor.status != VendorStatusEnum.APPROVED, True)).label("active_vendors"),
        )

        # 2. Procurement Spend & PO Count
        po_stmt = select(
            func.count(PurchaseOrder.po_id).label("total_pos"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("total_spend"),
        ).where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)

        # 3. Invoice Financials (amount + tax_amount)
        inv_stmt = select(
            func.count(Invoice.invoice_id).label("total_invoices"),
            func.coalesce(func.sum(Invoice.amount + Invoice.tax_amount), 0.0).label("total_invoiced"),
            func.coalesce(
                func.sum(
                    Case(
                        (Invoice.status == InvoiceStatusEnum.PAID, Invoice.amount + Invoice.tax_amount),
                        else_=0.0,
                    )
                ),
                0.0,
            ).label("total_paid"),
        )

        # 4. On-Time Delivery Rate
        deliv_stmt = select(
            func.count(DeliveryTracking.delivery_id).label("total_delivs"),
            func.count(
                func.nullif(
                    or_(
                        DeliveryTracking.delivery_status != DeliveryStatusEnum.DELIVERED,
                        DeliveryTracking.delivered_date > DeliveryTracking.expected_date,
                    ),
                    True,
                )
            ).label("on_time_delivs"),
        )

        # 5. Open Issues Count
        iss_stmt = select(
            func.count(VendorIssue.issue_id).label("open_issues")
        ).where(VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]))

        # Concurrent Execution
        v_res, po_res, inv_res, d_res, iss_res = await asyncio.gather(
            db.execute(v_stmt),
            db.execute(po_stmt),
            db.execute(inv_stmt),
            db.execute(deliv_stmt),
            db.execute(iss_stmt),
        )

        v_row = v_res.first()
        po_row = po_res.first()
        inv_row = inv_res.first()
        d_row = d_res.first()
        open_issues = iss_res.scalar_one_or_none() or 0

        total_delivs = d_row.total_delivs if d_row else 0
        on_time_delivs = d_row.on_time_delivs if d_row else 0
        on_time_rate = round((on_time_delivs / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0

        total_invoiced = float(inv_row.total_invoiced) if inv_row else 0.0
        total_paid = float(inv_row.total_paid) if inv_row else 0.0

        return {
            "total_vendors": v_row.total_vendors if v_row else 0,
            "active_vendors": v_row.active_vendors if v_row else 0,
            "total_purchase_orders": po_row.total_pos if po_row else 0,
            "total_procurement_spend": float(po_row.total_spend) if po_row else 0.0,
            "total_invoices": inv_row.total_invoices if inv_row else 0,
            "total_invoiced_amount": round(total_invoiced, 2),
            "total_paid_amount": round(total_paid, 2),
            "total_outstanding_balance": round(total_invoiced - total_paid, 2),
            "overall_on_time_delivery_rate": on_time_rate,
            "total_open_issues": open_issues,
        }

    async def get_procurement_analytics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes SQL aggregation for Procurement Analytics.
        """
        # Total Procurement Requests Count
        req_stmt = select(func.count(ProcurementRequest.request_id))
        total_requests = (await db.execute(req_stmt)).scalar_one_or_none() or 0

        # Purchase Orders Status & Spend Distribution
        po_stmt = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.po_id).label("status_count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("status_spend"),
        ).group_by(PurchaseOrder.status)
        po_rows = (await db.execute(po_stmt)).all()

        orders_by_status = {}
        spend_by_status = {}
        total_pos = 0
        total_spend = 0.0

        for row in po_rows:
            st_val = row.status.value if hasattr(row.status, "value") else str(row.status)
            orders_by_status[st_val] = row.status_count
            spend_by_status[st_val] = float(row.status_spend)
            total_pos += row.status_count
            if row.status != PurchaseOrderStatusEnum.CANCELLED:
                total_spend += float(row.status_spend)

        # Monthly Spend Trend (using text("'YYYY-MM'") to prevent asyncpg parameter mismatch)
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
                "total_amount": float(r.monthly_amount),
                "count": r.monthly_count,
            }
            for r in trend_rows
        ]

        return {
            "total_requests": total_requests,
            "total_purchase_orders": total_pos,
            "total_spend": round(total_spend, 2),
            "orders_by_status": orders_by_status,
            "spend_by_status": spend_by_status,
            "monthly_spend_trend": monthly_trend,
        }

    async def get_invoice_analytics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes SQL aggregation for Invoice Financial Analytics.
        """
        stmt = select(
            Invoice.status,
            func.count(Invoice.invoice_id).label("status_count"),
            func.coalesce(func.sum(Invoice.amount + Invoice.tax_amount), 0.0).label("total_invoiced"),
        ).group_by(Invoice.status)
        rows = (await db.execute(stmt)).all()

        invoices_by_status = {}
        amount_by_status = {}
        total_invoices = 0
        total_invoiced_amt = 0.0
        total_paid_amt = 0.0
        total_pending_amt = 0.0
        total_overdue_amt = 0.0

        for row in rows:
            st_val = row.status.value if hasattr(row.status, "value") else str(row.status)
            count = row.status_count
            invoiced = float(row.total_invoiced)

            invoices_by_status[st_val] = count
            amount_by_status[st_val] = round(invoiced, 2)

            total_invoices += count
            total_invoiced_amt += invoiced

            if row.status == InvoiceStatusEnum.PAID:
                total_paid_amt += invoiced
            elif row.status in [InvoiceStatusEnum.PENDING, InvoiceStatusEnum.PARTIALLY_PAID]:
                total_pending_amt += invoiced
            elif row.status == InvoiceStatusEnum.OVERDUE:
                total_overdue_amt += invoiced

        return {
            "total_invoices": total_invoices,
            "total_invoiced_amount": round(total_invoiced_amt, 2),
            "total_paid_amount": round(total_paid_amt, 2),
            "total_pending_amount": round(total_pending_amt, 2),
            "total_overdue_amount": round(total_overdue_amt, 2),
            "invoices_by_status": invoices_by_status,
            "amount_by_status": amount_by_status,
        }

    async def get_delivery_analytics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes SQL aggregation for Delivery & Logistics Analytics.
        """
        # Delivery status breakdown
        st_stmt = select(
            DeliveryTracking.delivery_status,
            func.count(DeliveryTracking.delivery_id).label("status_count"),
        ).group_by(DeliveryTracking.delivery_status)
        st_rows = (await db.execute(st_stmt)).all()

        deliveries_by_status = {}
        total_delivs = 0
        delivered_cnt = 0
        delayed_cnt = 0
        returned_cnt = 0

        for row in st_rows:
            st_val = row.delivery_status.value if hasattr(row.delivery_status, "value") else str(row.delivery_status)
            count = row.status_count
            deliveries_by_status[st_val] = count
            total_delivs += count

            if row.delivery_status == DeliveryStatusEnum.DELIVERED:
                delivered_cnt = count
            elif row.delivery_status == DeliveryStatusEnum.DELAYED:
                delayed_cnt = count
            elif row.delivery_status == DeliveryStatusEnum.RETURNED:
                returned_cnt = count

        # On-Time Delivery Count & Average Delay Days
        deliv_stmt = select(
            func.count(
                func.nullif(
                    or_(
                        DeliveryTracking.delivery_status != DeliveryStatusEnum.DELIVERED,
                        DeliveryTracking.delivered_date > DeliveryTracking.expected_date,
                    ),
                    True,
                )
            ).label("on_time_delivs"),
            func.avg(
                cast(
                    DeliveryTracking.delivered_date - DeliveryTracking.expected_date,
                    Float,
                )
            ).filter(
                DeliveryTracking.delivered_date > DeliveryTracking.expected_date
            ).label("avg_delay"),
        )
        d_row = (await db.execute(deliv_stmt)).first()

        on_time_cnt = d_row.on_time_delivs if d_row else 0
        avg_delay = float(d_row.avg_delay) if (d_row and d_row.avg_delay) else 0.0

        on_time_rate = round((on_time_cnt / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0
        success_rate = round((delivered_cnt / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0
        return_rate = round((returned_cnt / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0

        return {
            "total_deliveries": total_delivs,
            "delivered_count": delivered_cnt,
            "on_time_count": on_time_cnt,
            "delayed_count": delayed_cnt,
            "returned_count": returned_cnt,
            "on_time_delivery_rate": on_time_rate,
            "delivery_success_rate": success_rate,
            "return_rate": return_rate,
            "average_delay_days": round(avg_delay, 2),
            "deliveries_by_status": deliveries_by_status,
        }

    async def get_vendor_analytics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes SQL aggregation for Vendor Analytics and Top 5 Vendors by Spend.
        """
        # Vendor Status Counts
        st_stmt = select(
            Vendor.status,
            func.count(Vendor.vendor_id).label("status_count"),
        ).group_by(Vendor.status)
        st_rows = (await db.execute(st_stmt)).all()

        vendors_by_status = {}
        total_vendors = 0
        active_vendors = 0

        for row in st_rows:
            st_val = row.status.value if hasattr(row.status, "value") else str(row.status)
            count = row.status_count
            vendors_by_status[st_val] = count
            total_vendors += count
            if row.status == VendorStatusEnum.APPROVED:
                active_vendors = count

        # Top 5 Vendors by Spend
        top_stmt = (
            select(
                Vendor.vendor_id,
                Vendor.company_name,
                Vendor.vendor_code,
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).label("total_spend"),
                func.count(PurchaseOrder.po_id).label("total_orders"),
            )
            .join(PurchaseOrder, Vendor.vendor_id == PurchaseOrder.vendor_id)
            .where(PurchaseOrder.status != PurchaseOrderStatusEnum.CANCELLED)
            .group_by(Vendor.vendor_id, Vendor.company_name, Vendor.vendor_code)
            .order_by(func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0).desc())
            .limit(5)
        )
        top_rows = (await db.execute(top_stmt)).all()

        top_vendors = [
            {
                "vendor_id": r.vendor_id,
                "vendor_name": r.company_name,
                "vendor_code": r.vendor_code,
                "total_spend": float(r.total_spend),
                "total_orders": r.total_orders,
            }
            for r in top_rows
        ]

        # Average Overall Vendor Rating
        r_stmt = select(func.avg(VendorRating.overall_rating))
        avg_rating_val = (await db.execute(r_stmt)).scalar_one_or_none()
        avg_rating = round(float(avg_rating_val), 2) if avg_rating_val else 0.0

        return {
            "total_vendors": total_vendors,
            "active_vendors": active_vendors,
            "vendors_by_status": vendors_by_status,
            "top_vendors_by_spend": top_vendors,
            "average_vendor_rating": avg_rating,
        }

    async def get_system_analytics(self, db: AsyncSession) -> dict[str, Any]:
        """
        Executes SQL aggregation for System & User Analytics.
        """
        # User counts by Role
        u_stmt = (
            select(
                Role.role_name,
                func.count(User.user_id).label("user_count"),
            )
            .join(User, Role.role_id == User.role_id)
            .group_by(Role.role_name)
        )
        u_rows = (await db.execute(u_stmt)).all()

        users_by_role = {}
        total_users = 0

        for row in u_rows:
            users_by_role[row.role_name] = row.user_count
            total_users += row.user_count

        # Active users count
        act_stmt = select(func.count(User.user_id)).where(User.is_active == True)
        active_users = (await db.execute(act_stmt)).scalar_one_or_none() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "users_by_role": users_by_role,
            "total_activity_logs": 0,
        }


# Singleton instance
analytics_repository = AnalyticsRepository()
