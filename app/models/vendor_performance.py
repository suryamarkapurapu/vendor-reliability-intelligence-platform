"""
SQLAlchemy 2.0 Models for Vendor Performance domain.
Covers 'vendor_performance_metrics', 'vendor_ratings', and 'vendor_issues' tables.
"""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue

from app.database import Base

if TYPE_CHECKING:
    from app.models.procurement import PurchaseOrder
    from app.models.users import User
    from app.models.vendors import Vendor


class IssueStatusEnum(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class VendorPerformanceMetric(Base):
    """
    Represents the 'vendor_performance_metrics' table in PostgreSQL.
    Tracks individual metric measurements for vendors.
    """

    __tablename__ = "vendor_performance_metrics"

    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    po_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.po_id"),
        nullable=True,
    )
    metric_type: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )
    metric_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    recorded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True,
    )
    recorded_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        foreign_keys=[vendor_id],
    )
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(
        "PurchaseOrder",
        foreign_keys=[po_id],
    )
    recorder: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[recorded_by],
    )


class VendorRating(Base):
    """
    Represents the 'vendor_ratings' table in PostgreSQL.
    Tracks performance ratings submitted for vendors.
    """

    __tablename__ = "vendor_ratings"

    rating_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    po_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.po_id"),
        nullable=True,
    )
    rated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )
    quality_rating: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    delivery_rating: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    communication_rating: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    overall_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    comments: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    rating_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        foreign_keys=[vendor_id],
    )
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(
        "PurchaseOrder",
        foreign_keys=[po_id],
    )
    rater: Mapped["User"] = relationship(
        "User",
        foreign_keys=[rated_by],
    )


class VendorIssue(Base):
    """
    Represents the 'vendor_issues' table in PostgreSQL.
    Tracks issues logged against vendors.
    """

    __tablename__ = "vendor_issues"

    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    po_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.po_id"),
        nullable=True,
    )
    reported_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )
    issue_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[IssueStatusEnum] = mapped_column(
        SQLEnum(
            IssueStatusEnum,
            name="issue_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'open'"),
        index=True,
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolution_time_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        server_default=FetchedValue(),
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        foreign_keys=[vendor_id],
    )
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(
        "PurchaseOrder",
        foreign_keys=[po_id],
    )
    reporter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reported_by],
    )
