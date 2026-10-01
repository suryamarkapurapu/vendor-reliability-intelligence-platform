"""
Service layer for Delivery Tracking business logic operations.
Delegates database access strictly to repositories.
"""

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DeliveryNotFoundError,
    InvalidDeliveryDataError,
    PurchaseOrderNotFoundError,
)
from app.models.delivery import DeliveryStatusEnum, DeliveryTracking
from app.models.procurement import PurchaseOrderStatusEnum
from app.repositories.delivery_repository import (
    DeliveryRepository,
    delivery_repository,
)
from app.repositories.procurement_repository import (
    ProcurementRepository,
    procurement_repository,
)
from app.schemas.delivery import DeliveryTrackingCreate, DeliveryTrackingUpdate


class DeliveryService:
    """
    Service class executing business rules for Delivery Tracking and Purchase Order synchronization.
    """

    def __init__(
        self,
        repo: DeliveryRepository | None = None,
        procurement_repo: ProcurementRepository | None = None,
    ) -> None:
        self.repo = repo or delivery_repository
        self.procurement_repo = procurement_repo or procurement_repository

    # ==================================================================
    # 1. DELIVERY TRACKING BUSINESS LOGIC & CRUD
    # ==================================================================

    async def create_delivery(
        self,
        db: AsyncSession,
        delivery_in: DeliveryTrackingCreate,
    ) -> DeliveryTracking:
        """
        Creates a new DeliveryTracking record after validating Purchase Order status.
        """
        # Business Rule 1: Purchase Order must exist
        po = await self.procurement_repo.get_po_by_id(db, delivery_in.po_id)
        if not po:
            raise PurchaseOrderNotFoundError(str(delivery_in.po_id))

        # Business Rule 2: Delivery creation is allowed only when PO status is ORDERED (or DELIVERED/COMPLETED)
        eligible_po_statuses = [
            PurchaseOrderStatusEnum.ORDERED,
            PurchaseOrderStatusEnum.DELIVERED,
            PurchaseOrderStatusEnum.COMPLETED,
        ]
        if po.status not in eligible_po_statuses:
            raise InvalidDeliveryDataError(
                f"Cannot create delivery for Purchase Order '{delivery_in.po_id}' with status '{po.status.value}'. Order must be in ORDERED status."
            )

        delivery_data = delivery_in.model_dump(exclude_unset=True)
        delivery_data.update({
            "delivery_status": DeliveryStatusEnum.NOT_DISPATCHED,
        })

        return await self.repo.create_delivery(db, delivery_data)

    async def get_delivery_by_id(
        self,
        db: AsyncSession,
        delivery_id: UUID,
    ) -> DeliveryTracking:
        """
        Retrieves a DeliveryTracking record by UUID.
        """
        delivery = await self.repo.get_delivery_by_id(db, delivery_id)
        if not delivery:
            raise DeliveryNotFoundError(str(delivery_id))
        return delivery

    async def get_deliveries_by_po_id(
        self,
        db: AsyncSession,
        po_id: UUID,
    ) -> list[DeliveryTracking]:
        """
        Retrieves all DeliveryTracking records for a Purchase Order.
        """
        return await self.repo.get_deliveries_by_po_id(db, po_id)

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
        Retrieves a paginated list of DeliveryTracking records with optional filters.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_deliveries(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
            po_id=po_id,
            status=status,
            carrier=carrier,
        )

    async def update_delivery(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        delivery_in: DeliveryTrackingUpdate,
    ) -> DeliveryTracking:
        """
        Updates an existing DeliveryTracking record details.
        """
        db_delivery = await self.get_delivery_by_id(db, delivery_id)

        # Terminal state protection
        if db_delivery.delivery_status in [
            DeliveryStatusEnum.DELIVERED,
            DeliveryStatusEnum.RETURNED,
        ]:
            raise InvalidDeliveryDataError(
                f"Delivery '{delivery_id}' is in terminal status '{db_delivery.delivery_status.value}' and cannot be modified."
            )

        update_data = delivery_in.model_dump(exclude_unset=True)
        if not update_data:
            raise InvalidDeliveryDataError(
                "At least one field must be provided for update."
            )

        # Timeline validation: dispatch_date <= expected_date
        if "expected_date" in update_data and update_data["expected_date"] is not None:
            if db_delivery.dispatch_date and db_delivery.dispatch_date > update_data["expected_date"]:
                raise InvalidDeliveryDataError(
                    f"dispatch_date ({db_delivery.dispatch_date}) cannot be after expected_date ({update_data['expected_date']})."
                )

        return await self.repo.update_delivery(db, db_delivery, update_data)

    # ==================================================================
    # 2. WORKFLOW STATE TRANSITIONS & PO SYNCHRONIZATION
    # ==================================================================

    async def dispatch_delivery(
        self,
        db: AsyncSession,
        delivery_id: UUID,
    ) -> DeliveryTracking:
        """
        Dispatches a shipment (NOT_DISPATCHED -> IN_TRANSIT) and automatically sets dispatch_date.
        """
        db_delivery = await self.get_delivery_by_id(db, delivery_id)

        if db_delivery.delivery_status in [
            DeliveryStatusEnum.DELIVERED,
            DeliveryStatusEnum.RETURNED,
        ]:
            raise InvalidDeliveryDataError(
                f"Cannot dispatch delivery '{delivery_id}' in terminal status '{db_delivery.delivery_status.value}'."
            )

        update_data = {
            "delivery_status": DeliveryStatusEnum.IN_TRANSIT,
        }
        if db_delivery.dispatch_date is None:
            update_data["dispatch_date"] = date.today()

        return await self.repo.update_delivery(db, db_delivery, update_data)

    async def mark_delivered(
        self,
        db: AsyncSession,
        delivery_id: UUID,
    ) -> DeliveryTracking:
        """
        Marks a shipment as DELIVERED, automatically sets delivered_date, validates timelines,
        and synchronizes PurchaseOrder status to DELIVERED if ALL linked shipments are completed.
        """
        db_delivery = await self.get_delivery_by_id(db, delivery_id)

        if db_delivery.delivery_status in [
            DeliveryStatusEnum.DELIVERED,
            DeliveryStatusEnum.RETURNED,
        ]:
            raise InvalidDeliveryDataError(
                f"Delivery '{delivery_id}' is already in terminal status '{db_delivery.delivery_status.value}'."
            )

        today_date = date.today()

        # Date timeline validation: delivered_date >= dispatch_date
        if db_delivery.dispatch_date and today_date < db_delivery.dispatch_date:
            raise InvalidDeliveryDataError(
                f"delivered_date ({today_date}) cannot be before dispatch_date ({db_delivery.dispatch_date})."
            )

        update_data = {
            "delivery_status": DeliveryStatusEnum.DELIVERED,
            "delivered_date": today_date,
        }

        updated_delivery = await self.repo.update_delivery(db, db_delivery, update_data)

        # Purchase Order Synchronization Logic:
        # Check if ALL deliveries linked to this Purchase Order are DELIVERED
        all_po_deliveries = await self.repo.get_deliveries_by_po_id(db, db_delivery.po_id)
        all_completed = len(all_po_deliveries) > 0 and all(
            d.delivery_status == DeliveryStatusEnum.DELIVERED for d in all_po_deliveries
        )

        if all_completed:
            po = await self.procurement_repo.get_po_by_id(db, db_delivery.po_id)
            if po and po.status != PurchaseOrderStatusEnum.DELIVERED:
                await self.procurement_repo.update_purchase_order(
                    db, po, {"status": PurchaseOrderStatusEnum.DELIVERED}
                )

        return updated_delivery

    async def mark_delayed(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        new_expected_date: date | None = None,
        remarks: str | None = None,
    ) -> DeliveryTracking:
        """
        Marks a shipment as DELAYED and optionally updates expected_date or remarks.
        """
        db_delivery = await self.get_delivery_by_id(db, delivery_id)

        if db_delivery.delivery_status in [
            DeliveryStatusEnum.DELIVERED,
            DeliveryStatusEnum.RETURNED,
        ]:
            raise InvalidDeliveryDataError(
                f"Cannot mark delivery '{delivery_id}' as delayed in terminal status '{db_delivery.delivery_status.value}'."
            )

        update_data = {
            "delivery_status": DeliveryStatusEnum.DELAYED,
        }
        if new_expected_date is not None:
            update_data["expected_date"] = new_expected_date
        if remarks is not None:
            update_data["remarks"] = remarks

        return await self.repo.update_delivery(db, db_delivery, update_data)

    async def mark_returned(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        remarks: str | None = None,
    ) -> DeliveryTracking:
        """
        Marks a shipment as RETURNED.
        """
        db_delivery = await self.get_delivery_by_id(db, delivery_id)

        if db_delivery.delivery_status in [
            DeliveryStatusEnum.DELIVERED,
            DeliveryStatusEnum.RETURNED,
        ]:
            raise InvalidDeliveryDataError(
                f"Cannot mark delivery '{delivery_id}' as returned in terminal status '{db_delivery.delivery_status.value}'."
            )

        update_data = {
            "delivery_status": DeliveryStatusEnum.RETURNED,
        }
        if remarks is not None:
            update_data["remarks"] = remarks

        return await self.repo.update_delivery(db, db_delivery, update_data)


# Singleton instance
delivery_service = DeliveryService()
