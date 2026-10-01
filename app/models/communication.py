"""
SQLAlchemy Model for Messages / Communication.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    sender_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    receiver_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    vendor_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("vendors.vendor_id"),
    )
    po_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("purchase_orders.po_id"),
    )
    subject: Mapped[Optional[str]] = mapped_column(String(200))
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
