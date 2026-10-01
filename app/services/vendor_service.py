"""
Service layer for Vendor business logic operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidVendorDataError,
    UserNotFoundError,
    VendorAlreadyExistsError,
    VendorCategoryNotFoundError,
    VendorNotFoundError,
)

from app.models.vendors import Vendor, VendorStatusEnum

from app.repositories.user_repository import (
    UserRepository,
    user_repository,
)

from app.repositories.vendor_repository import (
    VendorRepository,
    vendor_repository,
)

from app.schemas.vendor import VendorCreate, VendorUpdate

from app.services.activity_log_service import activity_log_service


class VendorService:
    """
    Service class executing business rules for the Vendor module.
    Delegates database access strictly to VendorRepository.
    """

    def __init__(
        self,
        repo: VendorRepository | None = None,
        user_repo: UserRepository | None = None,
    ) -> None:
        self.repo = repo or vendor_repository
        self.user_repo = user_repo or user_repository

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _validate_linked_user(
        self,
        db: AsyncSession,
        linked_user_id: UUID,
    ) -> None:
        """
        Validates that a linked_user_id references an existing user.

        Raises:
            UserNotFoundError: If the user does not exist.
        """

        user = await self.user_repo.get_user_by_id(
            db,
            linked_user_id,
        )

        if not user:
            raise UserNotFoundError(
                f"Linked user '{linked_user_id}' not found."
            )

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    async def create_vendor(
        self,
        db: AsyncSession,
        vendor_in: VendorCreate,
        current_user_id: UUID,
    ) -> Vendor:
        """
        Creates a new vendor after validating business rules.

        Raises:
            VendorAlreadyExistsError:
                If vendor_code already exists.

            VendorCategoryNotFoundError:
                If category_id does not exist.

            UserNotFoundError:
                If linked_user_id does not reference an existing user.
        """

        # Business Rule 1: Vendor code must be unique
        existing_vendor = await self.repo.get_vendor_by_code(
            db,
            vendor_in.vendor_code,
        )

        if existing_vendor:
            raise VendorAlreadyExistsError(vendor_in.vendor_code)

        # Business Rule 2: Category must exist
        category = await self.repo.get_category_by_id(
            db,
            vendor_in.category_id,
        )

        if not category:
            raise VendorCategoryNotFoundError(
                vendor_in.category_id
            )

        # Business Rule 3: linked_user_id must reference an existing user
        if vendor_in.linked_user_id is not None:
            await self._validate_linked_user(
                db,
                vendor_in.linked_user_id,
            )

        vendor_data = vendor_in.model_dump(
            exclude_unset=True
        )

        try:
            vendor = await self.repo.create_vendor(
                db,
                vendor_data,
            )

            # Activity Log
            await activity_log_service.log_activity(
                db,
                user_id=current_user_id,
                entity_type="vendor",
                entity_id=vendor.vendor_id,
                action="created",
                description=f'Vendor "{vendor.company_name}" was created',
            )

            # Commit the activity log
            await db.commit()

            return vendor

        except IntegrityError as exc:
            error_detail = str(exc).lower()

            if "vendor_code" in error_detail:
                raise VendorAlreadyExistsError(
                    vendor_in.vendor_code
                ) from exc

            if "category_id" in error_detail:
                raise VendorCategoryNotFoundError(
                    vendor_in.category_id
                ) from exc

            if "linked_user_id" in error_detail or "user_id" in error_detail:
                raise UserNotFoundError(
                    f"Linked user '{vendor_in.linked_user_id}' not found."
                ) from exc

            raise

    async def get_vendor_by_id(
        self,
        db: AsyncSession,
        vendor_id: UUID,
    ) -> Vendor:
        """
        Retrieves a vendor by UUID.
        """

        vendor = await self.repo.get_vendor_by_id(
            db,
            vendor_id,
        )

        if not vendor:
            raise VendorNotFoundError(str(vendor_id))

        return vendor

    async def get_vendor_by_code(
        self,
        db: AsyncSession,
        vendor_code: str,
    ) -> Vendor:
        """
        Retrieves a vendor by vendor code.
        """

        vendor = await self.repo.get_vendor_by_code(
            db,
            vendor_code,
        )

        if not vendor:
            raise VendorNotFoundError(vendor_code)

        return vendor

    async def get_all_vendors(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Vendor]:
        """
        Retrieves a paginated list of vendors.
        """

        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_vendors(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
        )

    async def update_vendor(
        self,
        db: AsyncSession,
        vendor_id: UUID,
        vendor_in: VendorUpdate,
        current_user_id:UUID,
    ) -> Vendor:
        """
        Updates an existing vendor.

        Raises:
            VendorNotFoundError
            VendorAlreadyExistsError
            VendorCategoryNotFoundError
            UserNotFoundError
            InvalidVendorDataError
        """

        db_vendor = await self.repo.get_vendor_by_id(
            db,
            vendor_id,
        )

        if not db_vendor:
            raise VendorNotFoundError(str(vendor_id))

        update_data = vendor_in.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise InvalidVendorDataError(
                "At least one field must be provided for update."
            )

        # Business Rule: vendor_code must remain unique
        if (
            "vendor_code" in update_data
            and update_data["vendor_code"] != db_vendor.vendor_code
        ):
            existing_vendor = await self.repo.get_vendor_by_code(
                db,
                update_data["vendor_code"],
            )

            if (
                existing_vendor
                and existing_vendor.vendor_id != vendor_id
            ):
                raise VendorAlreadyExistsError(
                    update_data["vendor_code"]
                )

        # Business Rule: category must exist
        if (
            "category_id" in update_data
            and update_data["category_id"] != db_vendor.category_id
        ):
            category = await self.repo.get_category_by_id(
                db,
                update_data["category_id"],
            )

            if not category:
                raise VendorCategoryNotFoundError(
                    update_data["category_id"]
                )

        # Business Rule: linked_user_id must reference an existing user
        if (
            "linked_user_id" in update_data
            and update_data["linked_user_id"] is not None
            and update_data["linked_user_id"] != db_vendor.linked_user_id
        ):
            await self._validate_linked_user(
                db,
                update_data["linked_user_id"],
            )

        try:
            return await self.repo.update_vendor(
                db,
                db_vendor,
                update_data,
            )

        except IntegrityError as exc:
            error_detail = str(exc).lower()

            if "vendor_code" in error_detail:
                raise VendorAlreadyExistsError(
                    update_data.get("vendor_code", "")
                ) from exc

            if "category_id" in error_detail:
                raise VendorCategoryNotFoundError(
                    update_data.get("category_id", 0)
                ) from exc

            if "linked_user_id" in error_detail or "user_id" in error_detail:
                raise UserNotFoundError(
                    f"Linked user '{update_data.get('linked_user_id')}' not found."
                ) from exc

            raise

    async def delete_vendor(
        self,
        db: AsyncSession,
        vendor_id: UUID,
    ) -> None:
        """
        Deletes a vendor and cleans up dependent records.

        Raises:
            VendorNotFoundError: If vendor does not exist.
        """

        from sqlalchemy import text

        db_vendor = await self.repo.get_vendor_by_id(
            db,
            vendor_id,
        )

        if not db_vendor:
            raise VendorNotFoundError(str(vendor_id))

        # Clean any dependent records first to avoid foreign key violations
        try:
            await db.execute(
                text(
                    "DELETE FROM message_attachments "
                    "WHERE message_id IN "
                    "(SELECT message_id FROM messages WHERE vendor_id = :vid)"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM messages "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM delivery_tracking "
                    "WHERE po_id IN "
                    "(SELECT po_id FROM purchase_orders WHERE vendor_id = :vid)"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM invoices "
                    "WHERE po_id IN "
                    "(SELECT po_id FROM purchase_orders WHERE vendor_id = :vid)"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM purchase_order_items "
                    "WHERE po_id IN "
                    "(SELECT po_id FROM purchase_orders WHERE vendor_id = :vid)"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM purchase_orders "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM contracts "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_ratings "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_issues "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_performance_metrics "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_reliability_scores "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM reliability_score_history "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM certifications "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM compliance_records "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_documents "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

            await db.execute(
                text(
                    "DELETE FROM vendor_contacts "
                    "WHERE vendor_id = :vid"
                ),
                {"vid": vendor_id},
            )

        except Exception:
            pass

        await self.repo.delete_vendor(
            db,
            db_vendor,
        )

    async def approve_vendor(
        self,
        db: AsyncSession,
        vendor_id: UUID,
        approved_by: UUID,
    ) -> Vendor:
        """
        Approves a vendor by updating its status to 'approved'
        and recording the approver.
        """

        db_vendor = await self.repo.get_vendor_by_id(
            db,
            vendor_id,
        )

        if not db_vendor:
            raise VendorNotFoundError(str(vendor_id))

        if db_vendor.status == VendorStatusEnum.APPROVED:
            return db_vendor

        return await self.repo.update_vendor(
            db,
            db_vendor,
            {
                "status": VendorStatusEnum.APPROVED,
                "approved_by": approved_by,
                "approved_at": datetime.now(timezone.utc),
            },
        )


# Singleton instance
vendor_service = VendorService()