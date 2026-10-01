"""
SQLAlchemy 2.0 Model for 'vendors' table.
"""

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, SmallInteger, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.vendor_categories import VendorCategory


class VendorStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class Vendor(Base):
    """
    Represents the 'vendors' table in PostgreSQL.
    """

    __tablename__ = "vendors"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vendor_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    company_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("vendor_categories.category_id"),
        nullable=False,
        index=True,
    )
    linked_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    address_line: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )
    state: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )
    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    status: Mapped[VendorStatusEnum] = mapped_column(
        SQLEnum(
            VendorStatusEnum,
            name="vendor_status_enum",
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
    registration_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
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
    category: Mapped["VendorCategory"] = relationship(
        "VendorCategory",
        back_populates="vendors",
    )
    linked_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[linked_user_id],
        back_populates="linked_vendors",
    )
    approver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[approved_by],
        back_populates="approved_vendors",
    )
    contracts = relationship("Contract", back_populates="vendor")

