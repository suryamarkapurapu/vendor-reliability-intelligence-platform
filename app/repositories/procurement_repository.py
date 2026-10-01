"""
Repository layer for Procurement database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.procurement import (
    ProcurementRequest,
    PurchaseOrder,
    PurchaseOrderItem,
)


class ProcurementRepository:
    """
    Repository class executing atomic CRUD operations on Procurement model entities.
    Encapsulates transaction management and database query logic.
    """

    # ==================================================================
    # 1. PROCUREMENT REQUEST OPERATIONS
    # ==================================================================

    async def create_request(
        self,
        db: AsyncSession,
        request_data: dict[str, Any],
    ) -> ProcurementRequest:
        """
        Creates a new ProcurementRequest record within a transaction boundary.
        """
        try:
            db_request = ProcurementRequest(**request_data)

            db.add(db_request)

            await db.commit()

            await db.refresh(db_request)

            return db_request

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_request_by_id(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> ProcurementRequest | None:
        """
        Retrieves a ProcurementRequest by primary key (UUID).
        """
        stmt = select(ProcurementRequest).where(
            ProcurementRequest.request_id == request_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_request_by_number(
        self,
        db: AsyncSession,
        request_number: str,
    ) -> ProcurementRequest | None:
        """
        Retrieves a ProcurementRequest by unique request_number.
        """
        stmt = select(ProcurementRequest).where(
            ProcurementRequest.request_number == request_number
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_requests(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """
        Retrieves a paginated list of ProcurementRequests ordered deterministically.
        """
        stmt = (
            select(ProcurementRequest)
            .order_by(
                ProcurementRequest.created_at.desc(),
                ProcurementRequest.request_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_request(
        self,
        db: AsyncSession,
        db_request: ProcurementRequest,
        update_data: dict[str, Any],
    ) -> ProcurementRequest:
        """
        Updates an existing ProcurementRequest within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_request, field):
                    setattr(db_request, field, value)

            await db.commit()

            await db.refresh(db_request)

            return db_request

        except SQLAlchemyError:
            await db.rollback()
            raise

    # ==================================================================
    # 2. PURCHASE ORDER & LINE ITEM ATOMIC OPERATIONS
    # ==================================================================

    async def create_purchase_order(
        self,
        db: AsyncSession,
        po_data: dict[str, Any],
        items_data: list[dict[str, Any]],
    ) -> PurchaseOrder:
        """
        Creates a new PurchaseOrder and its line items atomically.
        If any insert fails, the entire transaction is rolled back.
        """
        try:
            db_po = PurchaseOrder(**po_data)

            db.add(db_po)

            await db.flush()  # Assigns po_id to db_po before adding child items

            total_amount = 0.0
            for item in items_data:
                db_item = PurchaseOrderItem(
                    po_id=db_po.po_id,
                    **item,
                )
                db.add(db_item)
                qty = float(item.get("quantity", 0))
                price = float(item.get("unit_price", 0))
                total_amount += qty * price

            db_po.total_amount = total_amount

            await db.commit()

            await db.refresh(db_po)

            await db.refresh(db_po, attribute_names=["items", "vendor"])

            return db_po

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_po_by_id(
        self,
        db: AsyncSession,
        po_id: UUID,
    ) -> PurchaseOrder | None:
        """
        Retrieves a PurchaseOrder by primary key with line items and vendor loaded.
        """
        stmt = (
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.vendor),
            )
            .where(PurchaseOrder.po_id == po_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_po_by_number(
        self,
        db: AsyncSession,
        po_number: str,
    ) -> PurchaseOrder | None:
        """
        Retrieves a PurchaseOrder by unique po_number with line items and vendor loaded.
        """
        stmt = (
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.vendor),
            )
            .where(PurchaseOrder.po_number == po_number)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_pos(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PurchaseOrder]:
        """
        Retrieves a paginated list of PurchaseOrders with line items and vendor loaded.
        """
        stmt = (
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.vendor),
            )
            .order_by(
                PurchaseOrder.created_at.desc(),
                PurchaseOrder.po_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_purchase_order(
        self,
        db: AsyncSession,
        db_po: PurchaseOrder,
        update_data: dict[str, Any],
    ) -> PurchaseOrder:
        """
        Updates an existing PurchaseOrder within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_po, field):
                    setattr(db_po, field, value)

            await db.commit()

            await db.refresh(db_po)

            await db.refresh(db_po, attribute_names=["items", "vendor"])

            return db_po

        except SQLAlchemyError:
            await db.rollback()
            raise


# Singleton instance
procurement_repository = ProcurementRepository()
