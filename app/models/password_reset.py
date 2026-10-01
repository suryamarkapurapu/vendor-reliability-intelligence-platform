"""
SQLAlchemy 2.0 Async Model for the 'password_reset_tokens' table.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class PasswordResetToken(Base):
    """
    SQLAlchemy model representing the 'password_reset_tokens' table.
    Stores SHA-256 hashed password reset tokens with expiration and one-time use invalidation.
    """

    __tablename__ = "password_reset_tokens"

    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<PasswordResetToken(token_id={self.token_id}, "
            f"user_id={self.user_id}, "
            f"expires_at={self.expires_at}, "
            f"used_at={self.used_at})>"
        )
