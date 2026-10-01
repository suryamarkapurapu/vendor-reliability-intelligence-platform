"""
Service layer for Invoice business logic operations.
Delegates database access strictly to repositories.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidInvoiceDataError,
    InvoiceNotFoundError,
    PurchaseOrderNotFoundError,
    VendorNotFoundError,
)
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.procurement import PurchaseOrderStatusEnum
from app.models.vendors import VendorStatusEnum
from app.repositories.invoice_repository import (
    InvoiceRepository,
    invoice_repository,
)
from app.repositories.procurement_repository import (
    ProcurementRepository,
    procurement_repository,
)
from app.repositories.vendor_repository import (
    VendorRepository,
    vendor_repository,
)
from app.schemas.invoices import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    """
    Service class executing business rules for Invoice Management.
    """

    def __init__(
        self,
        repo: InvoiceRepository | None = None,
        procurement_repo: ProcurementRepository | None = None,
        vendor_repo: VendorRepository | None = None,
    ) -> None:
        self.repo = repo or invoice_repository
        self.procurement_repo = procurement_repo or procurement_repository
        self.vendor_repo = vendor_repo or vendor_repository

    # ------------------------------------------------------------------
    # Private helpers — number generator
    # ------------------------------------------------------------------

    async def _generate_invoice_number(self, db: AsyncSession) -> str:
        """
        Generates a unique invoice number (e.g. INV-2026-A1B2C3D4).
        """
        year = datetime.now(timezone.utc).year
        suffix = str(uuid.uuid4())[:8].upper()
        invoice_number = f"INV-{year}-{suffix}"

        # Guarantee uniqueness
        existing = await self.repo.get_invoice_by_number(db, invoice_number)
        if existing:
            return await self._generate_invoice_number(db)

        return invoice_number

    # ==================================================================
    # INVOICE BUSINESS LOGIC & LIFECYCLE
    # ==================================================================

    async def create_invoice(
        self,
        db: AsyncSession,
        invoice_in: InvoiceCreate,
    ) -> Invoice:
        """
        Creates a new Invoice after validating PO status, vendor alignment, and amount constraints.
        """
        # Business Rule 1: Purchase Order must exist
        po = await self.procurement_repo.get_po_by_id(db, invoice_in.po_id)
        if not po:
            raise PurchaseOrderNotFoundError(str(invoice_in.po_id))

        # Business Rule 2: Purchase Order status must be ORDERED, DELIVERED, or COMPLETED
        eligible_statuses = [
            PurchaseOrderStatusEnum.ORDERED,
            PurchaseOrderStatusEnum.DELIVERED,
            PurchaseOrderStatusEnum.COMPLETED,
        ]
        if po.status not in eligible_statuses:
            raise InvalidInvoiceDataError(
                f"Cannot create invoice for Purchase Order '{invoice_in.po_id}' with status '{po.status.value}'. Order must be ordered, delivered, or completed."
            )

        # Business Rule 3: Invoice vendor_id MUST match Purchase Order vendor_id
        if invoice_in.vendor_id != po.vendor_id:
            raise InvalidInvoiceDataError(
                f"Invoice vendor '{invoice_in.vendor_id}' does not match Purchase Order vendor '{po.vendor_id}'."
            )

        # Business Rule 4: Vendor must exist and not be suspended/blacklisted
        vendor = await self.vendor_repo.get_vendor_by_id(db, invoice_in.vendor_id)
        if not vendor:
            raise VendorNotFoundError(str(invoice_in.vendor_id))

        if vendor.status in [VendorStatusEnum.SUSPENDED, VendorStatusEnum.BLACKLISTED]:
            raise InvalidInvoiceDataError(
                f"Cannot create invoice for vendor '{invoice_in.vendor_id}' with status '{vendor.status.value}'."
            )

        # Business Rule 5: Invoice net amount cannot exceed Purchase Order total amount
        if invoice_in.amount > po.total_amount:
            raise InvalidInvoiceDataError(
                f"Invoice amount ({invoice_in.amount}) cannot exceed Purchase Order total amount ({po.total_amount})."
            )

        # Generate unique invoice number
        invoice_number = await self._generate_invoice_number(db)

        # Prepare invoice record data
        invoice_data = invoice_in.model_dump(exclude_unset=True)
        invoice_data.update({
            "invoice_number": invoice_number,
            "status": InvoiceStatusEnum.PENDING,
        })

        return await self.repo.create_invoice(db, invoice_data)

    async def get_invoice_by_id(
        self,
        db: AsyncSession,
        invoice_id: UUID,
    ) -> Invoice:
        """
        Retrieves an Invoice by UUID.
        """
        invoice = await self.repo.get_invoice_by_id(db, invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(str(invoice_id))
        return invoice

    async def get_invoice_by_number(
        self,
        db: AsyncSession,
        invoice_number: str,
    ) -> Invoice:
        """
        Retrieves an Invoice by invoice number.
        """
        invoice = await self.repo.get_invoice_by_number(db, invoice_number)
        if not invoice:
            raise InvoiceNotFoundError(invoice_number)
        return invoice

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
        Retrieves a paginated list of Invoices with optional filters.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_invoices(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
            vendor_id=vendor_id,
            po_id=po_id,
            status=status,
        )

    async def update_invoice(
        self,
        db: AsyncSession,
        invoice_id: UUID,
        invoice_in: InvoiceUpdate,
    ) -> Invoice:
        """
        Updates an existing Invoice details.
        """
        db_invoice = await self.get_invoice_by_id(db, invoice_id)

        # Terminal state protection
        if db_invoice.status == InvoiceStatusEnum.PAID:
            raise InvalidInvoiceDataError(
                f"Invoice '{invoice_id}' is paid and cannot be modified."
            )

        update_data = invoice_in.model_dump(exclude_unset=True)
        if not update_data:
            raise InvalidInvoiceDataError(
                "At least one field must be provided for update."
            )

        # Amount validation against PO if amount is updated
        if "amount" in update_data:
            new_amount = update_data["amount"]
            po = await self.procurement_repo.get_po_by_id(db, db_invoice.po_id)
            if po and new_amount > po.total_amount:
                raise InvalidInvoiceDataError(
                    f"Updated invoice amount ({new_amount}) cannot exceed Purchase Order total amount ({po.total_amount})."
                )

        return await self.repo.update_invoice(db, db_invoice, update_data)

    async def update_invoice_status(
        self,
        db: AsyncSession,
        invoice_id: UUID,
        new_status: InvoiceStatusEnum,
    ) -> Invoice:
        """
        Updates Invoice status and automatically sets paid_date if status becomes PAID.
        """
        db_invoice = await self.get_invoice_by_id(db, invoice_id)

        # Terminal state protection
        if db_invoice.status == InvoiceStatusEnum.PAID:
            raise InvalidInvoiceDataError(
                f"Invoice '{invoice_id}' is already paid and cannot be modified."
            )

        update_data = {"status": new_status}

        # Payment Workflow Rule: Automatically set paid_date when status becomes PAID
        if new_status == InvoiceStatusEnum.PAID:
            update_data["paid_date"] = date.today()

        return await self.repo.update_invoice(db, db_invoice, update_data)


# Singleton instance
invoice_service = InvoiceService()
