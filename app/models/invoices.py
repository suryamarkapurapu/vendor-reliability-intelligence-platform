"""
SQLAlchemy 2.0 Model for 'invoices' table.
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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.procurement import PurchaseOrder
    from app.models.vendors import Vendor


class InvoiceStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"


class Invoice(Base):
    """
    Represents the 'invoices' table in PostgreSQL.
    """

    __tablename__ = "invoices"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    invoice_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.po_id"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True,
    )
    invoice_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0"),
    )
    status: Mapped[InvoiceStatusEnum] = mapped_column(
        SQLEnum(
            InvoiceStatusEnum,
            name="invoice_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=text("'pending'"),
        index=True,
    )
    paid_date: Mapped[Optional[date]] = mapped_column(
        Date,
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
        foreign_keys=[po_id],
    )
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        foreign_keys=[vendor_id],
    )
