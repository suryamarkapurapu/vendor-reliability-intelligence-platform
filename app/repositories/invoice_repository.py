"""
Repository layer for Invoice database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.invoices import Invoice, InvoiceStatusEnum


class InvoiceRepository:
    """
    Repository class executing atomic CRUD operations on Invoice model entities.
    Encapsulates transaction management and database query logic.
    """

    async def create_invoice(
        self,
        db: AsyncSession,
        invoice_data: dict[str, Any],
    ) -> Invoice:
        """
        Creates a new Invoice record within a transaction boundary.
        """
        try:
            db_invoice = Invoice(**invoice_data)

            db.add(db_invoice)

            await db.commit()

            await db.refresh(db_invoice)

            await db.refresh(
                db_invoice,
                attribute_names=["purchase_order", "vendor"],
            )

            return db_invoice

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_invoice_by_id(
        self,
        db: AsyncSession,
        invoice_id: UUID,
    ) -> Invoice | None:
        """
        Retrieves an Invoice by primary key with purchase_order and vendor loaded.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.purchase_order),
                selectinload(Invoice.vendor),
            )
            .where(Invoice.invoice_id == invoice_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_invoice_by_number(
        self,
        db: AsyncSession,
        invoice_number: str,
    ) -> Invoice | None:
        """
        Retrieves an Invoice by unique invoice_number with purchase_order and vendor loaded.
        """
        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.purchase_order),
                selectinload(Invoice.vendor),
            )
            .where(Invoice.invoice_number == invoice_number)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_invoices(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        po_id: UUID | None = None,
        status: InvoiceStatusEnum | None = None,
    ) -> list[Invoice]:
        """
        Retrieves a paginated list of Invoices with optional filters and eager loading.
        """
        stmt = select(Invoice).options(
            selectinload(Invoice.purchase_order),
            selectinload(Invoice.vendor),
        )

        if vendor_id is not None:
            stmt = stmt.where(Invoice.vendor_id == vendor_id)

        if po_id is not None:
            stmt = stmt.where(Invoice.po_id == po_id)

        if status is not None:
            stmt = stmt.where(Invoice.status == status)

        stmt = stmt.order_by(
            Invoice.created_at.desc(),
            Invoice.invoice_id.desc(),
        ).offset(skip).limit(limit)

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_invoice(
        self,
        db: AsyncSession,
        db_invoice: Invoice,
        update_data: dict[str, Any],
    ) -> Invoice:
        """
        Updates an existing Invoice within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_invoice, field):
                    setattr(db_invoice, field, value)

            await db.commit()

            await db.refresh(db_invoice)

            await db.refresh(
                db_invoice,
                attribute_names=["purchase_order", "vendor"],
            )

            return db_invoice

        except SQLAlchemyError:
            await db.rollback()
            raise


# Singleton instance
invoice_repository = InvoiceRepository()
