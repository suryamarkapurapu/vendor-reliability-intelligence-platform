"""
Repository layer for Vendor database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vendor_categories import VendorCategory
from app.models.vendors import Vendor, VendorStatusEnum


class VendorRepository:
    """
    Repository class executing atomic CRUD operations on the Vendor model.
    Encapsulates transaction management and database query logic.
    """

    async def create_vendor(
        self,
        db: AsyncSession,
        vendor_data: dict[str, Any],
    ) -> Vendor:
        """
        Creates a new vendor record in the database within a transaction boundary.
        """
        try:
            db_vendor = Vendor(**vendor_data)

            db.add(db_vendor)

            await db.commit()

            await db.refresh(db_vendor)

            await db.refresh(db_vendor, attribute_names=["category"])

            return db_vendor

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_vendor_by_id(
        self,
        db: AsyncSession,
        vendor_id: UUID,
    ) -> Vendor | None:
        """
        Retrieves a vendor by primary key (UUID).
        """
        stmt = (
            select(Vendor)
            .options(selectinload(Vendor.category))
            .where(Vendor.vendor_id == vendor_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_vendor_by_code(
        self,
        db: AsyncSession,
        vendor_code: str,
    ) -> Vendor | None:
        """
        Retrieves a vendor by its unique vendor code.
        """
        stmt = (
            select(Vendor)
            .options(selectinload(Vendor.category))
            .where(Vendor.vendor_code == vendor_code)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_category_by_id(
        self,
        db: AsyncSession,
        category_id: int,
    ) -> VendorCategory | None:
        """
        Retrieves a vendor category by primary key.
        """
        stmt = select(VendorCategory).where(
            VendorCategory.category_id == category_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_vendors(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Vendor]:
        """
        Retrieves a list of vendors with deterministic ordering and pagination.
        """
        stmt = (
            select(Vendor)
            .options(selectinload(Vendor.category))
            .order_by(
                Vendor.created_at.desc(),
                Vendor.vendor_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_vendor(
        self,
        db: AsyncSession,
        db_vendor: Vendor,
        update_data: dict[str, Any],
    ) -> Vendor:
        """
        Updates an existing vendor's attributes within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_vendor, field):
                    setattr(db_vendor, field, value)

            await db.commit()

            await db.refresh(db_vendor)

            await db.refresh(db_vendor, attribute_names=["category"])

            return db_vendor

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def delete_vendor(
        self,
        db: AsyncSession,
        db_vendor: Vendor,
    ) -> None:
        """
        Deletes a vendor record from the database.
        """
        try:
            await db.delete(db_vendor)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise


# Singleton instance
vendor_repository = VendorRepository()
