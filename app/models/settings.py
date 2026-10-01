"""
SQLAlchemy 2.0 Async Model for the 'user_settings' table.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class UserSettings(Base):
    """
    SQLAlchemy model representing the 'user_settings' table.
    Persists system settings, notification preferences, company profile, and UI choices.
    """

    __tablename__ = "user_settings"

    setting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    company_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default="Enterprise Vendor Reliability Corp",
    )

    company_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    company_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    company_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    sms_notifications: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    vendor_alerts: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    contract_alerts: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    security_2fa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default="English",
    )

    theme: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default="light",
    )

    timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="Asia/Kolkata",
    )

    preferred_currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        default="INR",
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

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<UserSettings(setting_id={self.setting_id}, user_id={self.user_id})>"
