"""
SQLAlchemy 2.0 Models for Procurement Management.
Covers 'procurement_requests', 'purchase_orders', and 'purchase_order_items' tables.
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
    String,
    Text,
    func,
    text,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.delivery import DeliveryTracking
    from app.models.users import User
    from app.models.vendors import Vendor


class RequestStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_PO = "converted_to_po"
    CANCELLED = "cancelled"


class PurchaseOrderStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ProcurementRequest(Base):
    """
    Represents the 'procurement_requests' table in PostgreSQL.
    """

    __tablename__ = "procurement_requests"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    request_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    item_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    estimated_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )
    priority: Mapped[PriorityEnum] = mapped_column(
        SQLEnum(
            PriorityEnum,
            name="priority_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'medium'"),
    )
    required_by_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    status: Mapped[RequestStatusEnum] = mapped_column(
        SQLEnum(
            RequestStatusEnum,
            name="request_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'pending'"),
        index=True,
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requested_by],
    )
    approver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[approved_by],
    )
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(
        "PurchaseOrder",
        back_populates="request",
    )


class PurchaseOrder(Base):
    """
    Represents the 'purchase_orders' table in PostgreSQL.
    """

    __tablename__ = "purchase_orders"

    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    po_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )
    request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("procurement_requests.request_id"),
        nullable=True,
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )
    order_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    payment_terms: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0"),
    )
    status: Mapped[PurchaseOrderStatusEnum] = mapped_column(
        SQLEnum(
            PurchaseOrderStatusEnum,
            name="po_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'pending'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    request: Mapped[Optional["ProcurementRequest"]] = relationship(
        "ProcurementRequest",
        back_populates="purchase_orders",
    )
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )
    items: Mapped[list["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )
    deliveries: Mapped[list["DeliveryTracking"]] = relationship(
        "DeliveryTracking",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )


class PurchaseOrderItem(Base):
    """
    Represents the 'purchase_order_items' table in PostgreSQL.
    """

    __tablename__ = "purchase_order_items"

    po_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.po_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(400),
        nullable=True,
    )
    uom: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    total_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2),
        server_default=FetchedValue(),
    )

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder",
        back_populates="items",
    )
