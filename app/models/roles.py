"""
SQLAlchemy 2.0 Model for the 'roles' table.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class Role(Base):
    """
    Represents the 'roles' table.
    """

    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        autoincrement=True,
    )

    role_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(255),
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

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
    )

    def __repr__(self) -> str:
        return f"<Role(role_id={self.role_id}, role_name={self.role_name!r})>"