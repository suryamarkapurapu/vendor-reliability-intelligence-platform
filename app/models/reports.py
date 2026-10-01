"""
SQLAlchemy 2.0 Model for generated reports / report history.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class Report(Base):
    """
    SQLAlchemy model representing generated report history.
    """

    __tablename__ = "reports"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    report_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        index=True,
    )

    generated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    generated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="completed",
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pdf",
    )

    download_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ----------------------------
    # Relationships
    # ----------------------------

    generated_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[generated_by],
    )

    def __repr__(self) -> str:
        return (
            f"<Report("
            f"report_id={self.report_id}, "
            f"report_name={self.report_name!r}, "
            f"category={self.category!r}, "
            f"status={self.status!r}"
            f")>"
        )