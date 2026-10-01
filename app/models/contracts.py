"""
SQLAlchemy Model for Contracts.
"""

import enum
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class Contract(Base):
    __tablename__ = "contracts"

    contract_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    contract_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    vendor_id: Mapped[UUID] = mapped_column(
        ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
    )
    contract_type: Mapped[Optional[str]] = mapped_column(String(80))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    contract_value: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))
    status: Mapped[ContractStatus] = mapped_column(
        SQLEnum(
            ContractStatus,
            name="contract_status_enum",
            native_enum=True,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ContractStatus.DRAFT,
        nullable=False,
    )
    document_path: Mapped[Optional[str]] = mapped_column(String(400))
    created_by: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.user_id"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vendor = relationship("Vendor", back_populates="contracts")
