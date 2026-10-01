"""
Pydantic v2 Schemas for Vendor Performance domain.
Covers ratings, issues, metrics, and response-only summary/ranking DTOs.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.vendor_performance import IssueStatusEnum


# ======================================================================
# 1. VENDOR RATING SCHEMAS
# ======================================================================

class VendorRatingBase(BaseModel):
    """
    Base client input fields for a VendorRating record.
    """

    model_config = ConfigDict(extra="forbid")

    vendor_id: UUID = Field(
        ...,
        description="Foreign key referencing vendors table.",
    )
    po_id: Optional[UUID] = Field(
        None,
        description="Optional foreign key referencing purchase_orders table.",
    )
    quality_rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Product or service quality rating (1-5 scale).",
    )
    delivery_rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Delivery timeliness rating (1-5 scale).",
    )
    communication_rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Communication responsiveness rating (1-5 scale).",
    )
    comments: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional feedback or comments.",
    )


class VendorRatingCreate(VendorRatingBase):
    """
    Schema for creating a new VendorRating record (Client Input only).

    Excluded server/service-managed fields:
    - rating_id (Database UUID PK)
    - overall_rating (Calculated by Service layer)
    - rated_by (Resolved from authenticated user)
    - rating_date (Database-managed date)
    """

    pass


class VendorRatingResponse(BaseModel):
    """
    Response schema representing complete VendorRating entity.
    """

    rating_id: UUID
    vendor_id: UUID
    vendor_name: Optional[str] = None
    po_id: Optional[UUID] = None
    po_number: Optional[str] = None
    rated_by: UUID
    rater_name: Optional[str] = None
    quality_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    overall_rating: Optional[Decimal] = None
    comments: Optional[str] = None
    rating_date: date

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations(cls, data: Any) -> Any:
        if hasattr(data, "rating_id") and hasattr(data, "vendor_id"):
            vendor_name = None
            if hasattr(data, "vendor") and data.vendor is not None:
                if hasattr(data.vendor, "company_name"):
                    vendor_name = data.vendor.company_name

            po_number = None
            if hasattr(data, "purchase_order") and data.purchase_order is not None:
                if hasattr(data.purchase_order, "po_number"):
                    po_number = data.purchase_order.po_number

            rater_name = None
            if hasattr(data, "rater") and data.rater is not None:
                if hasattr(data.rater, "full_name"):
                    rater_name = data.rater.full_name

            return {
                "rating_id": data.rating_id,
                "vendor_id": data.vendor_id,
                "vendor_name": vendor_name,
                "po_id": data.po_id,
                "po_number": po_number,
                "rated_by": data.rated_by,
                "rater_name": rater_name,
                "quality_rating": data.quality_rating,
                "delivery_rating": data.delivery_rating,
                "communication_rating": data.communication_rating,
                "overall_rating": data.overall_rating,
                "comments": data.comments,
                "rating_date": data.rating_date,
            }
        return data


# ======================================================================
# 2. VENDOR ISSUE SCHEMAS
# ======================================================================

class VendorIssueBase(BaseModel):
    """
    Base client input fields for a VendorIssue record.
    """

    model_config = ConfigDict(extra="forbid")

    vendor_id: UUID = Field(
        ...,
        description="Foreign key referencing vendors table.",
    )
    po_id: Optional[UUID] = Field(
        None,
        description="Optional foreign key referencing purchase_orders table.",
    )
    issue_type: str = Field(
        ...,
        max_length=80,
        description="Type or classification of issue.",
        examples=["Quality Defect"],
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of reported issue.",
    )


class VendorIssueCreate(VendorIssueBase):
    """
    Schema for logging a new VendorIssue record (Client Input only).

    Excluded server-managed fields:
    - issue_id (Database UUID PK)
    - status (Server-managed: defaults to 'open')
    - reported_by (Resolved from authenticated user)
    - reported_at (Database timestamp)
    - resolved_at (Set upon resolution workflow action)
    - resolution_time_hours (PostgreSQL GENERATED column)
    """

    pass


class VendorIssueUpdate(BaseModel):
    """
    Schema for updating an existing VendorIssue record.
    """

    model_config = ConfigDict(extra="forbid")

    status: Optional[IssueStatusEnum] = Field(
        None,
        description="Updated issue status (e.g. in_progress, resolved, closed).",
    )
    description: Optional[str] = Field(
        None,
        description="Updated issue description.",
    )


class VendorIssueResponse(BaseModel):
    """
    Response schema representing complete VendorIssue entity.
    """

    issue_id: UUID
    vendor_id: UUID
    vendor_name: Optional[str] = None
    po_id: Optional[UUID] = None
    po_number: Optional[str] = None
    reported_by: UUID
    reporter_name: Optional[str] = None
    issue_type: str
    description: Optional[str] = None
    status: IssueStatusEnum
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_time_hours: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations(cls, data: Any) -> Any:
        if hasattr(data, "issue_id") and hasattr(data, "vendor_id"):
            vendor_name = None
            if hasattr(data, "vendor") and data.vendor is not None:
                if hasattr(data.vendor, "company_name"):
                    vendor_name = data.vendor.company_name

            po_number = None
            if hasattr(data, "purchase_order") and data.purchase_order is not None:
                if hasattr(data.purchase_order, "po_number"):
                    po_number = data.purchase_order.po_number

            reporter_name = None
            if hasattr(data, "reporter") and data.reporter is not None:
                if hasattr(data.reporter, "full_name"):
                    reporter_name = data.reporter.full_name

            return {
                "issue_id": data.issue_id,
                "vendor_id": data.vendor_id,
                "vendor_name": vendor_name,
                "po_id": data.po_id,
                "po_number": po_number,
                "reported_by": data.reported_by,
                "reporter_name": reporter_name,
                "issue_type": data.issue_type,
                "description": data.description,
                "status": data.status,
                "reported_at": data.reported_at,
                "resolved_at": data.resolved_at,
                "resolution_time_hours": data.resolution_time_hours,
            }
        return data


# ======================================================================
# 3. VENDOR PERFORMANCE METRIC SCHEMAS
# ======================================================================

class VendorPerformanceMetricBase(BaseModel):
    """
    Base client input fields for a VendorPerformanceMetric record.
    """

    model_config = ConfigDict(extra="forbid")

    vendor_id: UUID = Field(
        ...,
        description="Foreign key referencing vendors table.",
    )
    po_id: Optional[UUID] = Field(
        None,
        description="Optional foreign key referencing purchase_orders table.",
    )
    metric_type: str = Field(
        ...,
        max_length=60,
        description="Type of performance metric.",
        examples=["on_time_delivery"],
    )
    metric_value: Decimal = Field(
        ...,
        description="Numerical metric value.",
        examples=[95.50],
    )


class VendorPerformanceMetricCreate(VendorPerformanceMetricBase):
    """
    Schema for recording a VendorPerformanceMetric record.

    Excluded server-managed fields:
    - metric_id (Database UUID PK)
    - recorded_by (Resolved from authenticated user)
    - recorded_date (Database date)
    """

    pass


class VendorPerformanceMetricResponse(BaseModel):
    """
    Response schema representing VendorPerformanceMetric entity.
    """

    metric_id: UUID
    vendor_id: UUID
    vendor_name: Optional[str] = None
    po_id: Optional[UUID] = None
    po_number: Optional[str] = None
    metric_type: str
    metric_value: Decimal
    recorded_by: Optional[UUID] = None
    recorder_name: Optional[str] = None
    recorded_date: date

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations(cls, data: Any) -> Any:
        if hasattr(data, "metric_id") and hasattr(data, "vendor_id"):
            vendor_name = None
            if hasattr(data, "vendor") and data.vendor is not None:
                if hasattr(data.vendor, "company_name"):
                    vendor_name = data.vendor.company_name

            po_number = None
            if hasattr(data, "purchase_order") and data.purchase_order is not None:
                if hasattr(data.purchase_order, "po_number"):
                    po_number = data.purchase_order.po_number

            recorder_name = None
            if hasattr(data, "recorder") and data.recorder is not None:
                if hasattr(data.recorder, "full_name"):
                    recorder_name = data.recorder.full_name

            return {
                "metric_id": data.metric_id,
                "vendor_id": data.vendor_id,
                "vendor_name": vendor_name,
                "po_id": data.po_id,
                "po_number": po_number,
                "metric_type": data.metric_type,
                "metric_value": data.metric_value,
                "recorded_by": data.recorded_by,
                "recorder_name": recorder_name,
                "recorded_date": data.recorded_date,
            }
        return data


# ======================================================================
# 4. RESPONSE-ONLY SUMMARY & RANKING DTO SCHEMAS
# ======================================================================

class VendorPerformanceSummaryResponse(BaseModel):
    """
    Response DTO summarizing real-time aggregated performance metrics for a vendor.
    Does NOT correspond to a single database table.
    """

    vendor_id: UUID
    vendor_name: str
    vendor_code: str
    total_purchase_orders: int = 0
    completed_purchase_orders: int = 0
    total_deliveries: int = 0
    on_time_deliveries: int = 0
    delayed_deliveries: int = 0
    returned_deliveries: int = 0
    on_time_delivery_rate: float = 0.0
    delivery_success_rate: float = 0.0
    return_rate: float = 0.0
    average_delivery_delay_days: float = 0.0
    average_quality_rating: float = 0.0
    average_delivery_rating: float = 0.0
    average_communication_rating: float = 0.0
    average_overall_rating: float = 0.0
    total_issues_reported: int = 0
    open_issues_count: int = 0
    resolved_issues_count: int = 0
    average_issue_resolution_hours: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class VendorRankingResponse(BaseModel):
    """
    Response DTO for vendor leaderboard ranking items.
    Does NOT correspond to a single database table.
    """

    rank: int
    vendor_id: UUID
    vendor_name: str
    vendor_code: str
    overall_score: float
    on_time_delivery_rate: float
    average_overall_rating: float
    resolved_issues_rate: float

    model_config = ConfigDict(from_attributes=True)
