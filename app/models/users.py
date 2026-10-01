"""
SQLAlchemy 2.0 Async Model for the 'users' table.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, BigInteger, func, text
from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.roles import Role
    from app.models.vendors import Vendor


class User(Base):
    """
    SQLAlchemy model representing the 'users' table.
    """

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("roles.role_id"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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

    # ----------------------------
    # Relationships
    # ----------------------------

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
    )

    linked_vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor",
        foreign_keys="Vendor.linked_user_id",
        back_populates="linked_user",
    )

    approved_vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor",
        foreign_keys="Vendor.approved_by",
        back_populates="approver",
    )

    def __repr__(self) -> str:
        return (
            f"<User(user_id={self.user_id}, "
            f"username={self.username!r}, "
            f"email={self.email!r}, "
            f"role_id={self.role_id})>"
        )