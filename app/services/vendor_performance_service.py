"""
Service layer for Vendor Performance business logic operations.
Delegates database queries and SQL aggregations strictly to repositories.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidVendorPerformanceDataError,
    PurchaseOrderNotFoundError,
    VendorIssueNotFoundError,
    VendorNotFoundError,
    VendorRatingNotFoundError,
)
from app.models.vendor_performance import (
    IssueStatusEnum,
    VendorIssue,
    VendorPerformanceMetric,
    VendorRating,
)
from app.repositories.procurement_repository import (
    ProcurementRepository,
    procurement_repository,
)
from app.repositories.vendor_performance_repository import (
    VendorPerformanceRepository,
    vendor_performance_repository,
)
from app.repositories.vendor_repository import (
    VendorRepository,
    vendor_repository,
)
from app.schemas.vendor_performance import (
    VendorIssueCreate,
    VendorIssueUpdate,
    VendorPerformanceMetricCreate,
    VendorRatingCreate,
)


class VendorPerformanceService:
    """
    Service executing business rules for Vendor Performance, ratings, issues, and rankings.
    """

    def __init__(
        self,
        repo: VendorPerformanceRepository | None = None,
        vendor_repo: VendorRepository | None = None,
        procurement_repo: ProcurementRepository | None = None,
    ) -> None:
        self.repo = repo or vendor_performance_repository
        self.vendor_repo = vendor_repo or vendor_repository
        self.procurement_repo = procurement_repo or procurement_repository

    # ==================================================================
    # 1. VENDOR RATING BUSINESS LOGIC
    # ==================================================================

    async def create_rating(
        self,
        db: AsyncSession,
        rating_in: VendorRatingCreate,
        rated_by: UUID,
    ) -> VendorRating:
        """
        Creates a new VendorRating after validating vendor/PO existence and calculating overall_rating.
        """
        # Business Rule 1: Vendor must exist
        vendor = await self.vendor_repo.get_vendor_by_id(db, rating_in.vendor_id)
        if not vendor:
            raise VendorNotFoundError(str(rating_in.vendor_id))

        # Business Rule 2: If PO is provided, PO must exist and match vendor_id
        if rating_in.po_id is not None:
            po = await self.procurement_repo.get_po_by_id(db, rating_in.po_id)
            if not po:
                raise PurchaseOrderNotFoundError(str(rating_in.po_id))

            if po.vendor_id != rating_in.vendor_id:
                raise InvalidVendorPerformanceDataError(
                    f"Purchase Order vendor '{po.vendor_id}' does not match rating vendor_id '{rating_in.vendor_id}'."
                )

        # Business Rule 3: Ensure at least one rating metric is provided
        provided_ratings = [
            r
            for r in [
                rating_in.quality_rating,
                rating_in.delivery_rating,
                rating_in.communication_rating,
            ]
            if r is not None
        ]
        if not provided_ratings:
            raise InvalidVendorPerformanceDataError(
                "At least one rating (quality, delivery, or communication) must be provided."
            )

        # Business Rule 4: Automatically calculate overall_rating = average(provided_ratings)
        overall_rating = round(sum(provided_ratings) / len(provided_ratings), 2)

        rating_data = rating_in.model_dump(exclude_unset=True)
        rating_data.update({
            "rated_by": rated_by,
            "overall_rating": overall_rating,
        })

        return await self.repo.create_rating(db, rating_data)

    async def get_rating_by_id(
        self,
        db: AsyncSession,
        rating_id: UUID,
    ) -> VendorRating:
        """
        Retrieves a VendorRating by UUID.
        """
        rating = await self.repo.get_rating_by_id(db, rating_id)
        if not rating:
            raise VendorRatingNotFoundError(str(rating_id))
        return rating

    async def get_all_ratings(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        po_id: UUID | None = None,
    ) -> list[VendorRating]:
        """
        Retrieves a paginated list of VendorRating records.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_ratings(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
            vendor_id=vendor_id,
            po_id=po_id,
        )

    # ==================================================================
    # 2. VENDOR ISSUE BUSINESS LOGIC
    # ==================================================================

    async def create_issue(
        self,
        db: AsyncSession,
        issue_in: VendorIssueCreate,
        reported_by: UUID,
    ) -> VendorIssue:
        """
        Creates a new VendorIssue record after validating vendor and PO existence.
        """
        # Business Rule 1: Vendor must exist
        vendor = await self.vendor_repo.get_vendor_by_id(db, issue_in.vendor_id)
        if not vendor:
            raise VendorNotFoundError(str(issue_in.vendor_id))

        # Business Rule 2: If PO is provided, PO must exist and match vendor_id
        if issue_in.po_id is not None:
            po = await self.procurement_repo.get_po_by_id(db, issue_in.po_id)
            if not po:
                raise PurchaseOrderNotFoundError(str(issue_in.po_id))

            if po.vendor_id != issue_in.vendor_id:
                raise InvalidVendorPerformanceDataError(
                    f"Purchase Order vendor '{po.vendor_id}' does not match issue vendor_id '{issue_in.vendor_id}'."
                )

        issue_data = issue_in.model_dump(exclude_unset=True)
        issue_data.update({
            "reported_by": reported_by,
            "status": IssueStatusEnum.OPEN,
        })

        return await self.repo.create_issue(db, issue_data)

    async def get_issue_by_id(
        self,
        db: AsyncSession,
        issue_id: UUID,
    ) -> VendorIssue:
        """
        Retrieves a VendorIssue by UUID.
        """
        issue = await self.repo.get_issue_by_id(db, issue_id)
        if not issue:
            raise VendorIssueNotFoundError(str(issue_id))
        return issue

    async def get_all_issues(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        status: IssueStatusEnum | None = None,
    ) -> list[VendorIssue]:
        """
        Retrieves a paginated list of VendorIssue records.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_issues(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
            vendor_id=vendor_id,
            status=status,
        )

    async def update_issue(
        self,
        db: AsyncSession,
        issue_id: UUID,
        issue_in: VendorIssueUpdate,
    ) -> VendorIssue:
        """
        Updates an existing VendorIssue and automatically assigns resolved_at when status becomes RESOLVED.
        """
        db_issue = await self.get_issue_by_id(db, issue_id)

        update_data = issue_in.model_dump(exclude_unset=True)
        if not update_data:
            raise InvalidVendorPerformanceDataError(
                "At least one field must be provided for update."
            )

        # Issue Workflow Rule: Automatically assign resolved_at when status becomes RESOLVED
        if (
            update_data.get("status") == IssueStatusEnum.RESOLVED
            and db_issue.resolved_at is None
        ):
            update_data["resolved_at"] = datetime.now(timezone.utc)

        return await self.repo.update_issue(db, db_issue, update_data)

    # ==================================================================
    # 3. VENDOR PERFORMANCE METRICS BUSINESS LOGIC
    # ==================================================================

    async def create_metric(
        self,
        db: AsyncSession,
        metric_in: VendorPerformanceMetricCreate,
        recorded_by: UUID | None = None,
    ) -> VendorPerformanceMetric:
        """
        Records a new VendorPerformanceMetric entry.
        """
        vendor = await self.vendor_repo.get_vendor_by_id(db, metric_in.vendor_id)
        if not vendor:
            raise VendorNotFoundError(str(metric_in.vendor_id))

        metric_data = metric_in.model_dump(exclude_unset=True)
        if recorded_by is not None:
            metric_data["recorded_by"] = recorded_by

        return await self.repo.create_metric(db, metric_data)

    async def get_all_metrics(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        metric_type: str | None = None,
    ) -> list[VendorPerformanceMetric]:
        """
        Retrieves a paginated list of VendorPerformanceMetric entries.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_all_metrics(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
            vendor_id=vendor_id,
            metric_type=metric_type,
        )

    # ==================================================================
    # 4. PERFORMANCE SUMMARY & RANKING DELEGATION
    # ==================================================================

    async def get_vendor_performance_summary(
        self,
        db: AsyncSession,
        vendor_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieves the real-time aggregated performance summary for a vendor.
        """
        vendor = await self.vendor_repo.get_vendor_by_id(db, vendor_id)
        if not vendor:
            raise VendorNotFoundError(str(vendor_id))

        summary = await self.repo.get_vendor_performance_summary(db, vendor_id)
        if not summary:
            raise VendorNotFoundError(str(vendor_id))

        return summary

    async def get_vendor_rankings(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Retrieves the vendor performance leaderboard ranking.
        """
        bounded_skip = max(0, skip)
        bounded_limit = min(max(1, limit), 1000)

        return await self.repo.get_vendor_rankings(
            db,
            skip=bounded_skip,
            limit=bounded_limit,
        )


# Singleton instance
vendor_performance_service = VendorPerformanceService()
