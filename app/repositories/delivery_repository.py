"""
Repository layer for Delivery Tracking database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery import DeliveryStatusEnum, DeliveryTracking
from app.models.procurement import PurchaseOrder


class DeliveryRepository:
    """
    Repository class executing atomic CRUD operations on DeliveryTracking model entities.
    Encapsulates transaction management and database query logic.
    """

    async def create_delivery(
        self,
        db: AsyncSession,
        delivery_data: dict[str, Any],
    ) -> DeliveryTracking:
        """
        Creates a new DeliveryTracking record within a transaction boundary.
        """
        try:
            db_delivery = DeliveryTracking(**delivery_data)

            db.add(db_delivery)

            await db.commit()

            await db.refresh(db_delivery)

            await db.refresh(
                db_delivery,
                attribute_names=["purchase_order"],
            )

            return db_delivery

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_delivery_by_id(
        self,
        db: AsyncSession,
        delivery_id: UUID,
    ) -> DeliveryTracking | None:
        """
        Retrieves a DeliveryTracking record by primary key with purchase_order and vendor loaded.
        """
        stmt = (
            select(DeliveryTracking)
            .options(
                selectinload(DeliveryTracking.purchase_order).selectinload(
                    PurchaseOrder.vendor
                )
            )
            .where(DeliveryTracking.delivery_id == delivery_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_deliveries_by_po_id(
        self,
        db: AsyncSession,
        po_id: UUID,
    ) -> list[DeliveryTracking]:
        """
        Retrieves all DeliveryTracking records associated with a specific PurchaseOrder ID.
        """
        stmt = (
            select(DeliveryTracking)
            .options(
                selectinload(DeliveryTracking.purchase_order).selectinload(
                    PurchaseOrder.vendor
                )
            )
            .where(DeliveryTracking.po_id == po_id)
            .order_by(
                DeliveryTracking.created_at.desc(),
                DeliveryTracking.delivery_id.desc(),
            )
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def get_all_deliveries(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        po_id: UUID | None = None,
        status: DeliveryStatusEnum | None = None,
        carrier: str | None = None,
    ) -> list[DeliveryTracking]:
        """
        Retrieves a paginated list of DeliveryTracking records with optional filters and eager loading.
        """
        stmt = select(DeliveryTracking).options(
            selectinload(DeliveryTracking.purchase_order).selectinload(
                PurchaseOrder.vendor
            )
        )

        if po_id is not None:
            stmt = stmt.where(DeliveryTracking.po_id == po_id)

        if status is not None:
            stmt = stmt.where(DeliveryTracking.delivery_status == status)

        if carrier is not None:
            stmt = stmt.where(DeliveryTracking.carrier.ilike(f"%{carrier}%"))

        stmt = (
            stmt.order_by(
                DeliveryTracking.created_at.desc(),
                DeliveryTracking.delivery_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_delivery(
        self,
        db: AsyncSession,
        db_delivery: DeliveryTracking,
        update_data: dict[str, Any],
    ) -> DeliveryTracking:
        """
        Updates an existing DeliveryTracking record within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_delivery, field):
                    setattr(db_delivery, field, value)

            await db.commit()

            await db.refresh(db_delivery)

            await db.refresh(
                db_delivery,
                attribute_names=["purchase_order"],
            )

            return db_delivery

        except SQLAlchemyError:
            await db.rollback()
            raise


# Singleton instance
delivery_repository = DeliveryRepository()
