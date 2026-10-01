"""
Service layer for Analytics business and response formatting operations.
Delegates database queries and SQL aggregations strictly to AnalyticsRepository.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import (
    AnalyticsRepository,
    analytics_repository,
)
from app.schemas.analytics import (
    DeliveryAnalyticsResponse,
    ExecutiveDashboardResponse,
    InvoiceAnalyticsResponse,
    MonthlyTrendPoint,
    ProcurementAnalyticsResponse,
    SystemAnalyticsResponse,
    VendorAnalyticsResponse,
    VendorSpendResponse,
)


class AnalyticsService:
    """
    Service executing response DTO construction, zero fallbacks, and decimal rounding for Analytics.
    """

    def __init__(
        self,
        repo: AnalyticsRepository | None = None,
    ) -> None:
        self.repo = repo or analytics_repository

    async def get_dashboard(self, db: AsyncSession) -> ExecutiveDashboardResponse:
        """
        Retrieves high-level Executive Dashboard KPIs.
        """
        raw_data = await self.repo.get_executive_dashboard_metrics(db)

        return ExecutiveDashboardResponse(
            total_vendors=raw_data.get("total_vendors", 0),
            active_vendors=raw_data.get("active_vendors", 0),
            total_purchase_orders=raw_data.get("total_purchase_orders", 0),
            total_procurement_spend=round(float(raw_data.get("total_procurement_spend", 0.0)), 2),
            total_invoices=raw_data.get("total_invoices", 0),
            total_invoiced_amount=round(float(raw_data.get("total_invoiced_amount", 0.0)), 2),
            total_paid_amount=round(float(raw_data.get("total_paid_amount", 0.0)), 2),
            total_outstanding_balance=round(float(raw_data.get("total_outstanding_balance", 0.0)), 2),
            overall_on_time_delivery_rate=round(float(raw_data.get("overall_on_time_delivery_rate", 0.0)), 2),
            total_open_issues=raw_data.get("total_open_issues", 0),
        )

    async def get_procurement_analytics(self, db: AsyncSession) -> ProcurementAnalyticsResponse:
        """
        Retrieves Procurement Analytics.
        """
        raw_data = await self.repo.get_procurement_analytics(db)

        trend_points = [
            MonthlyTrendPoint(
                month=t.get("month", ""),
                total_amount=round(float(t.get("total_amount", 0.0)), 2),
                count=t.get("count", 0),
            )
            for t in raw_data.get("monthly_spend_trend", [])
        ]

        return ProcurementAnalyticsResponse(
            total_requests=raw_data.get("total_requests", 0),
            total_purchase_orders=raw_data.get("total_purchase_orders", 0),
            total_spend=round(float(raw_data.get("total_spend", 0.0)), 2),
            orders_by_status=raw_data.get("orders_by_status", {}),
            spend_by_status={
                k: round(float(v), 2) for k, v in raw_data.get("spend_by_status", {}).items()
            },
            monthly_spend_trend=trend_points,
        )

    async def get_invoice_analytics(self, db: AsyncSession) -> InvoiceAnalyticsResponse:
        """
        Retrieves Invoice & Financial Analytics.
        """
        raw_data = await self.repo.get_invoice_analytics(db)

        return InvoiceAnalyticsResponse(
            total_invoices=raw_data.get("total_invoices", 0),
            total_invoiced_amount=round(float(raw_data.get("total_invoiced_amount", 0.0)), 2),
            total_paid_amount=round(float(raw_data.get("total_paid_amount", 0.0)), 2),
            total_pending_amount=round(float(raw_data.get("total_pending_amount", 0.0)), 2),
            total_overdue_amount=round(float(raw_data.get("total_overdue_amount", 0.0)), 2),
            invoices_by_status=raw_data.get("invoices_by_status", {}),
            amount_by_status={
                k: round(float(v), 2) for k, v in raw_data.get("amount_by_status", {}).items()
            },
        )

    async def get_delivery_analytics(self, db: AsyncSession) -> DeliveryAnalyticsResponse:
        """
        Retrieves Delivery & Logistics Analytics.
        """
        raw_data = await self.repo.get_delivery_analytics(db)

        return DeliveryAnalyticsResponse(
            total_deliveries=raw_data.get("total_deliveries", 0),
            delivered_count=raw_data.get("delivered_count", 0),
            on_time_count=raw_data.get("on_time_count", 0),
            delayed_count=raw_data.get("delayed_count", 0),
            returned_count=raw_data.get("returned_count", 0),
            on_time_delivery_rate=round(float(raw_data.get("on_time_delivery_rate", 0.0)), 2),
            delivery_success_rate=round(float(raw_data.get("delivery_success_rate", 0.0)), 2),
            return_rate=round(float(raw_data.get("return_rate", 0.0)), 2),
            average_delay_days=round(float(raw_data.get("average_delay_days", 0.0)), 2),
            deliveries_by_status=raw_data.get("deliveries_by_status", {}),
        )

    async def get_vendor_analytics(self, db: AsyncSession) -> VendorAnalyticsResponse:
        """
        Retrieves Vendor Analytics.
        """
        raw_data = await self.repo.get_vendor_analytics(db)

        top_vendors = [
            VendorSpendResponse(
                vendor_id=v.get("vendor_id"),
                vendor_name=v.get("vendor_name", ""),
                vendor_code=v.get("vendor_code", ""),
                total_spend=round(float(v.get("total_spend", 0.0)), 2),
                total_orders=v.get("total_orders", 0),
            )
            for v in raw_data.get("top_vendors_by_spend", [])
        ]

        return VendorAnalyticsResponse(
            total_vendors=raw_data.get("total_vendors", 0),
            active_vendors=raw_data.get("active_vendors", 0),
            vendors_by_status=raw_data.get("vendors_by_status", {}),
            top_vendors_by_spend=top_vendors,
            average_vendor_rating=round(float(raw_data.get("average_vendor_rating", 0.0)), 2),
        )

    async def get_system_analytics(self, db: AsyncSession) -> SystemAnalyticsResponse:
        """
        Retrieves System Activity & User Analytics.
        """
        raw_data = await self.repo.get_system_analytics(db)

        return SystemAnalyticsResponse(
            total_users=raw_data.get("total_users", 0),
            active_users=raw_data.get("active_users", 0),
            users_by_role=raw_data.get("users_by_role", {}),
            total_activity_logs=raw_data.get("total_activity_logs", 0),
        )


# Singleton instance
analytics_service = AnalyticsService()
