"""
SQLAlchemy Model for Notifications.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotificationChannelEnum(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class NotificationPriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[NotificationChannelEnum] = mapped_column(
        SQLEnum(
    NotificationChannelEnum,
    name="notification_channel_enum",
    native_enum=True,
    values_callable=lambda enum_cls: [e.value for e in enum_cls],
),
        nullable=False,
        default=NotificationChannelEnum.IN_APP,
    )

    notification_type: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    related_entity_type: Mapped[Optional[str]] = mapped_column(
        String(60),
        nullable=True,
    )

    related_entity_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )

    priority: Mapped[NotificationPriorityEnum] = mapped_column(
        SQLEnum(
    NotificationPriorityEnum,
    name="priority_enum",
    native_enum=True,
    values_callable=lambda enum_cls: [e.value for e in enum_cls],
),
        nullable=False,
        default=NotificationPriorityEnum.MEDIUM,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )