"""
Service layer for Procurement business logic operations.
Delegates database operations strictly to repositories.
"""

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidProcurementDataError,
    ProcurementRequestNotFoundError,
    PurchaseOrderNotFoundError,
    VendorNotFoundError,
)

from app.models.procurement import (
    PriorityEnum,
    ProcurementRequest,
    PurchaseOrder,
    PurchaseOrderStatusEnum,
    RequestStatusEnum,
)

from app.models.vendors import VendorStatusEnum

from app.repositories.procurement_repository import (
    ProcurementRepository,
    procurement_repository,
)

from app.repositories.user_repository import (
    UserRepository,
    user_repository,
)

from app.repositories.vendor_repository import (
    VendorRepository,
    vendor_repository,
)

from app.schemas.procurement import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
)

from app.services.activity_log_service import activity_log_service


class ProcurementService:
    """
    Service class executing business rules for Procurement Management.
    """

    def __init__(
        self,
        repo: ProcurementRepository | None = None,
        vendor_repo: VendorRepository | None = None,
        user_repo: UserRepository | None = None,
    ) -> None:
        self.repo = repo or procurement_repository
        self.vendor_repo = vendor_repo or vendor_repository
        self.user_repo = user_repo or user_repository

    # ------------------------------------------------------------------
    # Private helpers — number generators
    # ------------------------------------------------------------------

    async def _generate_request_number(self, db: AsyncSession) -> str:
        """
        Generates a unique procurement request number
        (e.g. PR-2026-A1B2C3D4).
        """

        year = datetime.now(timezone.utc).year
        suffix = str(uuid.uuid4())[:8].upper()
        request_number = f"PR-{year}-{suffix}"

        # Guarantee uniqueness
        existing = await self.repo.get_request_by_number(
            db,
            request_number,
        )

        if existing:
            return await self._generate_request_number(db)

        return request_number

    async def _generate_po_number(self, db: AsyncSession) -> str:
        """
        Generates a unique purchase order number
        (e.g. PO-2026-E5F6G7H8).
        """

        year = datetime.now(timezone.utc).year
        suffix = str(uuid.uuid4())[:8].upper()
        po_number = f"PO-{year}-{suffix}"

        # Guarantee uniqueness
        existing = await self.repo.get_po_by_number(
            db,
            po_number,
        )

        if existing:
            return await self._generate_po_number(db)

        return po_number

    # ==================================================================
    # 1. PROCUREMENT REQUEST BUSINESS LOGIC
    # ==================================================================

    async def create_request(
        self,
        db: AsyncSession,
        request_in: ProcurementRequestCreate,
        requested_by: UUID,
    ) -> ProcurementRequest:
        """
        Creates a new ProcurementRequest after generating a unique
        request number.
        """

        request_number = await self._generate_request_number(db)

        request_data = request_in.model_dump(
            exclude_unset=True
        )

        request_data.update({
            "request_number": request_number,
            "requested_by": requested_by,
            "status": RequestStatusEnum.PENDING,
        })

        # Create procurement request
        request = await self.repo.create_request(
            db,
            request_data,
        )

        # Activity Log
        await activity_log_service.log_activity(
            db,
            user_id=requested_by,
            entity_type="procurement_request",
            entity_id=request.request_id,
            action="created",
            description=(
                f'Procurement Request '
                f'"{request.request_number}" was created'
            ),
        )

        # Commit the activity log
        await db.commit()

        return request

    async def get_request_by_id(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> ProcurementRequest:
        """
        Retrieves a ProcurementRequest by UUID.
        """

        request = await self.repo.get_request_by_id(
            db,
            request_id,
        )

        if not request:
            raise ProcurementRequestNotFoundError(
                str(request_id)
            )

        return request

    async def get_request_by_number(
        self,
        db: AsyncSession,
        request_number: str,
    ) -> ProcurementRequest:
        """
        Retrieves a ProcurementRequest by request number.
        """

        request = await self.repo.get_request_by_number(
            db,
            request_number,
        )

        if not request:
            raise ProcurementRequestNotFoundError(
                request_number
            )

        return request

    async def get_all_requests(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """
        Retrieves a paginated list of ProcurementRequests.
        """

        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_requests(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
        )

    async def update_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        request_in: ProcurementRequestUpdate,
    ) -> ProcurementRequest:
        """
        Updates an existing ProcurementRequest after validating
        status rules.
        """

        db_request = await self.get_request_by_id(
            db,
            request_id,
        )

        if db_request.status in [
            RequestStatusEnum.CONVERTED_TO_PO,
            RequestStatusEnum.CANCELLED,
            RequestStatusEnum.REJECTED,
        ]:
            raise InvalidProcurementDataError(
                f"Cannot update procurement request "
                f"'{request_id}' with status "
                f"'{db_request.status.value}'."
            )

        update_data = request_in.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise InvalidProcurementDataError(
                "At least one field must be provided for update."
            )

        return await self.repo.update_request(
            db,
            db_request,
            update_data,
        )

    async def approve_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        approved_by: UUID,
    ) -> ProcurementRequest:
        """
        Approves a ProcurementRequest in PENDING status.
        """

        db_request = await self.get_request_by_id(
            db,
            request_id,
        )

        if db_request.status == RequestStatusEnum.APPROVED:
            raise InvalidProcurementDataError(
                f"Procurement request "
                f"'{request_id}' is already approved."
            )

        if db_request.status in [
            RequestStatusEnum.CONVERTED_TO_PO,
            RequestStatusEnum.CANCELLED,
            RequestStatusEnum.REJECTED,
        ]:
            raise InvalidProcurementDataError(
                f"Cannot approve procurement request "
                f"'{request_id}' in status "
                f"'{db_request.status.value}'."
            )

        update_data = {
            "status": RequestStatusEnum.APPROVED,
            "approved_by": approved_by,
            "approved_at": datetime.now(timezone.utc),
        }

        return await self.repo.update_request(
            db,
            db_request,
            update_data,
        )

    async def reject_request(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> ProcurementRequest:
        """
        Rejects a ProcurementRequest.
        """

        db_request = await self.get_request_by_id(
            db,
            request_id,
        )

        if db_request.status in [
            RequestStatusEnum.CONVERTED_TO_PO,
            RequestStatusEnum.CANCELLED,
            RequestStatusEnum.REJECTED,
        ]:
            raise InvalidProcurementDataError(
                f"Cannot reject procurement request "
                f"'{request_id}' in status "
                f"'{db_request.status.value}'."
            )

        return await self.repo.update_request(
            db,
            db_request,
            {
                "status": RequestStatusEnum.REJECTED
            },
        )

    async def cancel_request(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> ProcurementRequest:
        """
        Cancels a ProcurementRequest.
        """

        db_request = await self.get_request_by_id(
            db,
            request_id,
        )

        if db_request.status in [
            RequestStatusEnum.CONVERTED_TO_PO,
            RequestStatusEnum.CANCELLED,
        ]:
            raise InvalidProcurementDataError(
                f"Cannot cancel procurement request "
                f"'{request_id}' in status "
                f"'{db_request.status.value}'."
            )

        return await self.repo.update_request(
            db,
            db_request,
            {
                "status": RequestStatusEnum.CANCELLED
            },
        )

    # ==================================================================
    # 2. PURCHASE ORDER BUSINESS LOGIC
    # ==================================================================

    async def create_purchase_order(
        self,
        db: AsyncSession,
        po_in: PurchaseOrderCreate,
        created_by: UUID,
    ) -> PurchaseOrder:
        """
        Creates a new PurchaseOrder after validating vendor and
        request business rules.
        """

        # Business Rule 1: Vendor must exist
        vendor = await self.vendor_repo.get_vendor_by_id(
            db,
            po_in.vendor_id,
        )

        if not vendor:
            raise VendorNotFoundError(
                str(po_in.vendor_id)
            )

        # Business Rule 2: Vendor must be in APPROVED status
        if vendor.status != VendorStatusEnum.APPROVED:
            raise InvalidProcurementDataError(
                f"Cannot create purchase order for vendor "
                f"'{po_in.vendor_id}' with status "
                f"'{vendor.status.value}'. Vendor must be approved."
            )

        # Business Rule 3: If request_id is supplied,
        # request must exist and be APPROVED
        if po_in.request_id is not None:
            request = await self.repo.get_request_by_id(
                db,
                po_in.request_id,
            )

            if not request:
                raise ProcurementRequestNotFoundError(
                    str(po_in.request_id)
                )

            if request.status != RequestStatusEnum.APPROVED:
                raise InvalidProcurementDataError(
                    f"Cannot create purchase order for procurement "
                    f"request '{po_in.request_id}' with status "
                    f"'{request.status.value}'. Request must be approved."
                )

            # Update request status to CONVERTED_TO_PO
            await self.repo.update_request(
                db,
                request,
                {
                    "status": RequestStatusEnum.CONVERTED_TO_PO
                },
            )

        # Generate unique PO number
        po_number = await self._generate_po_number(db)

        # Prepare PO data
        po_dict = po_in.model_dump(
            exclude={"items"},
            exclude_unset=True,
        )

        po_dict.update({
            "po_number": po_number,
            "created_by": created_by,
            "status": PurchaseOrderStatusEnum.PENDING,
        })

        # Prepare line items data
        items_data = [
            item.model_dump(exclude_unset=True)
            for item in po_in.items
        ]

        # Delegate atomic PO + line items insertion
        # and total calculation to repository
        purchase_order = await self.repo.create_purchase_order(
            db,
            po_dict,
            items_data,
        )

        # Activity Log
        await activity_log_service.log_activity(
            db,
            user_id=created_by,
            entity_type="purchase_order",
            entity_id=purchase_order.po_id,
            action="created",
            description=(
                f'Purchase Order '
                f'"{purchase_order.po_number}" was created'
            ),
        )

        # Commit the activity log
        await db.commit()

        return purchase_order

    async def get_po_by_id(
        self,
        db: AsyncSession,
        po_id: UUID,
    ) -> PurchaseOrder:
        """
        Retrieves a PurchaseOrder by UUID.
        """

        po = await self.repo.get_po_by_id(
            db,
            po_id,
        )

        if not po:
            raise PurchaseOrderNotFoundError(
                str(po_id)
            )

        return po

    async def get_po_by_number(
        self,
        db: AsyncSession,
        po_number: str,
    ) -> PurchaseOrder:
        """
        Retrieves a PurchaseOrder by PO number.
        """

        po = await self.repo.get_po_by_number(
            db,
            po_number,
        )

        if not po:
            raise PurchaseOrderNotFoundError(
                po_number
            )

        return po

    async def get_all_pos(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PurchaseOrder]:
        """
        Retrieves a paginated list of PurchaseOrders.
        """

        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_pos(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
        )

    async def update_purchase_order(
        self,
        db: AsyncSession,
        po_id: UUID,
        po_in: PurchaseOrderUpdate,
    ) -> PurchaseOrder:
        """
        Updates an existing PurchaseOrder.
        """

        db_po = await self.get_po_by_id(
            db,
            po_id,
        )

        if db_po.status in [
            PurchaseOrderStatusEnum.COMPLETED,
            PurchaseOrderStatusEnum.CANCELLED,
        ]:
            raise InvalidProcurementDataError(
                f"Cannot update purchase order "
                f"'{po_id}' in terminal status "
                f"'{db_po.status.value}'."
            )

        update_data = po_in.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise InvalidProcurementDataError(
                "At least one field must be provided for update."
            )

        return await self.repo.update_purchase_order(
            db,
            db_po,
            update_data,
        )

    async def update_po_status(
        self,
        db: AsyncSession,
        po_id: UUID,
        new_status: PurchaseOrderStatusEnum,
    ) -> PurchaseOrder:
        """
        Updates PurchaseOrder status verifying transition rules.
        """

        db_po = await self.get_po_by_id(
            db,
            po_id,
        )

        if db_po.status in [
            PurchaseOrderStatusEnum.COMPLETED,
            PurchaseOrderStatusEnum.CANCELLED,
        ]:
            raise InvalidProcurementDataError(
                f"Purchase order '{po_id}' is in terminal status "
                f"'{db_po.status.value}' and cannot be modified."
            )

        return await self.repo.update_purchase_order(
            db,
            db_po,
            {
                "status": new_status
            },
        )


# Singleton instance
procurement_service = ProcurementService()