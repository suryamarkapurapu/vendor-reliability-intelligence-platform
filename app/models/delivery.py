"""
SQLAlchemy 2.0 Model for 'delivery_tracking' table.
"""

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.procurement import PurchaseOrder


class DeliveryStatusEnum(str, enum.Enum):
    NOT_DISPATCHED = "not_dispatched"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    RETURNED = "returned"


class DeliveryTracking(Base):
    """
    Represents the 'delivery_tracking' table in PostgreSQL.
    Tracks shipments/deliveries associated with a PurchaseOrder.
    """

    __tablename__ = "delivery_tracking"

    delivery_id: Mapped[uuid.UUID] = mapped_column(
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
    tracking_number: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )
    carrier: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    dispatch_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    expected_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    delivered_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    delivery_status: Mapped[DeliveryStatusEnum] = mapped_column(
        SQLEnum(
            DeliveryStatusEnum,
            name="delivery_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'not_dispatched'"),
        index=True,
    )
    remarks: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder",
        back_populates="deliveries",
        foreign_keys=[po_id],
    )
