"""
Pydantic v2 Response DTO Schemas for Analytics domain.
Dynamic aggregation response objects (no direct database table mapping).
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MonthlyTrendPoint(BaseModel):
    """
    Data point representing monthly spend or order count trend.
    """

    month: str = Field(..., description="Month label (e.g. '2026-07' or 'Jul 2026').")
    total_amount: float = Field(0.0, description="Total monetary amount for the month.")
    count: int = Field(0, description="Total transaction count for the month.")

    model_config = ConfigDict(from_attributes=True)


class VendorSpendResponse(BaseModel):
    """
    Data DTO representing vendor spend ranking item.
    """

    vendor_id: UUID
    vendor_name: str
    vendor_code: str
    total_spend: float = 0.0
    total_orders: int = 0

    model_config = ConfigDict(from_attributes=True)


class ExecutiveDashboardResponse(BaseModel):
    """
    Response DTO for executive high-level dashboard KPIs.
    """

    total_vendors: int = 0
    active_vendors: int = 0
    total_purchase_orders: int = 0
    total_procurement_spend: float = 0.0
    total_invoices: int = 0
    total_invoiced_amount: float = 0.0
    total_paid_amount: float = 0.0
    total_outstanding_balance: float = 0.0
    overall_on_time_delivery_rate: float = 0.0
    total_open_issues: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProcurementAnalyticsResponse(BaseModel):
    """
    Response DTO for procurement analytics.
    """

    total_requests: int = 0
    total_purchase_orders: int = 0
    total_spend: float = 0.0
    orders_by_status: dict[str, int] = Field(default_factory=dict)
    spend_by_status: dict[str, float] = Field(default_factory=dict)
    monthly_spend_trend: list[MonthlyTrendPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InvoiceAnalyticsResponse(BaseModel):
    """
    Response DTO for invoice and financial analytics.
    """

    total_invoices: int = 0
    total_invoiced_amount: float = 0.0
    total_paid_amount: float = 0.0
    total_pending_amount: float = 0.0
    total_overdue_amount: float = 0.0
    invoices_by_status: dict[str, int] = Field(default_factory=dict)
    amount_by_status: dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class DeliveryAnalyticsResponse(BaseModel):
    """
    Response DTO for delivery and logistics analytics.
    """

    total_deliveries: int = 0
    delivered_count: int = 0
    on_time_count: int = 0
    delayed_count: int = 0
    returned_count: int = 0
    on_time_delivery_rate: float = 0.0
    delivery_success_rate: float = 0.0
    return_rate: float = 0.0
    average_delay_days: float = 0.0
    deliveries_by_status: dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class VendorAnalyticsResponse(BaseModel):
    """
    Response DTO for vendor analytics.
    """

    total_vendors: int = 0
    active_vendors: int = 0
    vendors_by_status: dict[str, int] = Field(default_factory=dict)
    top_vendors_by_spend: list[VendorSpendResponse] = Field(default_factory=list)
    average_vendor_rating: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class SystemAnalyticsResponse(BaseModel):
    """
    Response DTO for system activity and user management analytics.
    """

    total_users: int = 0
    active_users: int = 0
    users_by_role: dict[str, int] = Field(default_factory=dict)
    total_activity_logs: int = 0

    model_config = ConfigDict(from_attributes=True)
