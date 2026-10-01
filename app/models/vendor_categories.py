"""
SQLAlchemy 2.0 Model for 'vendor_categories' table.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.vendors import Vendor


class VendorCategory(Base):
    """
    Represents the 'vendor_categories' table in PostgreSQL.
    """
    __tablename__ = "vendor_categories"

    category_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        autoincrement=True,
    )
    category_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    vendors: Mapped[List["Vendor"]] = relationship(
        "Vendor",
        back_populates="category",
    )
