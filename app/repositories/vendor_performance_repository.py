"""
Repository layer for Vendor Performance database operations using SQLAlchemy 2.0 Async.
Includes CRUD operations and complex SQL aggregations for summaries and leaderboards.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import (
    Case,
    Float,
    Integer,
    Numeric,
    cast,
    func,
    or_,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery import DeliveryStatusEnum, DeliveryTracking
from app.models.procurement import PurchaseOrder, PurchaseOrderStatusEnum
from app.models.vendor_performance import (
    IssueStatusEnum,
    VendorIssue,
    VendorPerformanceMetric,
    VendorRating,
)
from app.models.vendors import Vendor


class VendorPerformanceRepository:
    """
    Repository class executing CRUD operations and SQL aggregate metrics for Vendor Performance.
    """

    # ==================================================================
    # 1. VENDOR RATINGS CRUD
    # ==================================================================

    async def create_rating(
        self,
        db: AsyncSession,
        rating_data: dict[str, Any],
    ) -> VendorRating:
        """
        Creates a new VendorRating record within a transaction boundary.
        """
        try:
            db_rating = VendorRating(**rating_data)

            db.add(db_rating)

            await db.commit()

            await db.refresh(db_rating)

            await db.refresh(
                db_rating,
                attribute_names=["vendor", "purchase_order", "rater"],
            )

            return db_rating

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_rating_by_id(
        self,
        db: AsyncSession,
        rating_id: UUID,
    ) -> VendorRating | None:
        """
        Retrieves a VendorRating by primary key with vendor, purchase_order, and rater loaded.
        """
        stmt = (
            select(VendorRating)
            .options(
                selectinload(VendorRating.vendor),
                selectinload(VendorRating.purchase_order),
                selectinload(VendorRating.rater),
            )
            .where(VendorRating.rating_id == rating_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_ratings(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        po_id: UUID | None = None,
    ) -> list[VendorRating]:
        """
        Retrieves a paginated list of VendorRating records with optional filters.
        """
        stmt = select(VendorRating).options(
            selectinload(VendorRating.vendor),
            selectinload(VendorRating.purchase_order),
            selectinload(VendorRating.rater),
        )

        if vendor_id is not None:
            stmt = stmt.where(VendorRating.vendor_id == vendor_id)

        if po_id is not None:
            stmt = stmt.where(VendorRating.po_id == po_id)

        stmt = (
            stmt.order_by(
                VendorRating.rating_date.desc(),
                VendorRating.rating_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    # ==================================================================
    # 2. VENDOR ISSUES CRUD
    # ==================================================================

    async def create_issue(
        self,
        db: AsyncSession,
        issue_data: dict[str, Any],
    ) -> VendorIssue:
        """
        Creates a new VendorIssue record within a transaction boundary.
        """
        try:
            db_issue = VendorIssue(**issue_data)

            db.add(db_issue)

            await db.commit()

            await db.refresh(db_issue)

            await db.refresh(
                db_issue,
                attribute_names=["vendor", "purchase_order", "reporter"],
            )

            return db_issue

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_issue_by_id(
        self,
        db: AsyncSession,
        issue_id: UUID,
    ) -> VendorIssue | None:
        """
        Retrieves a VendorIssue by primary key with vendor, purchase_order, and reporter loaded.
        """
        stmt = (
            select(VendorIssue)
            .options(
                selectinload(VendorIssue.vendor),
                selectinload(VendorIssue.purchase_order),
                selectinload(VendorIssue.reporter),
            )
            .where(VendorIssue.issue_id == issue_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_issues(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        status: IssueStatusEnum | None = None,
    ) -> list[VendorIssue]:
        """
        Retrieves a paginated list of VendorIssue records with optional filters.
        """
        stmt = select(VendorIssue).options(
            selectinload(VendorIssue.vendor),
            selectinload(VendorIssue.purchase_order),
            selectinload(VendorIssue.reporter),
        )

        if vendor_id is not None:
            stmt = stmt.where(VendorIssue.vendor_id == vendor_id)

        if status is not None:
            stmt = stmt.where(VendorIssue.status == status)

        stmt = (
            stmt.order_by(
                VendorIssue.reported_at.desc(),
                VendorIssue.issue_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_issue(
        self,
        db: AsyncSession,
        db_issue: VendorIssue,
        update_data: dict[str, Any],
    ) -> VendorIssue:
        """
        Updates an existing VendorIssue record within a transaction boundary.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_issue, field):
                    setattr(db_issue, field, value)

            await db.commit()

            await db.refresh(db_issue)

            await db.refresh(
                db_issue,
                attribute_names=["vendor", "purchase_order", "reporter"],
            )

            return db_issue

        except SQLAlchemyError:
            await db.rollback()
            raise

    # ==================================================================
    # 3. VENDOR PERFORMANCE METRICS CRUD
    # ==================================================================

    async def create_metric(
        self,
        db: AsyncSession,
        metric_data: dict[str, Any],
    ) -> VendorPerformanceMetric:
        """
        Creates a new VendorPerformanceMetric record within a transaction boundary.
        """
        try:
            db_metric = VendorPerformanceMetric(**metric_data)

            db.add(db_metric)

            await db.commit()

            await db.refresh(db_metric)

            await db.refresh(
                db_metric,
                attribute_names=["vendor", "purchase_order", "recorder"],
            )

            return db_metric

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_all_metrics(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vendor_id: UUID | None = None,
        metric_type: str | None = None,
    ) -> list[VendorPerformanceMetric]:
        """
        Retrieves a paginated list of VendorPerformanceMetric records.
        """
        stmt = select(VendorPerformanceMetric).options(
            selectinload(VendorPerformanceMetric.vendor),
            selectinload(VendorPerformanceMetric.purchase_order),
            selectinload(VendorPerformanceMetric.recorder),
        )

        if vendor_id is not None:
            stmt = stmt.where(VendorPerformanceMetric.vendor_id == vendor_id)

        if metric_type is not None:
            stmt = stmt.where(VendorPerformanceMetric.metric_type == metric_type)

        stmt = (
            stmt.order_by(
                VendorPerformanceMetric.recorded_date.desc(),
                VendorPerformanceMetric.metric_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    # ==================================================================
    # 4. SQL AGGREGATION QUERIES (SUMMARY & RANKINGS)
    # ==================================================================

    async def get_vendor_performance_summary(
        self,
        db: AsyncSession,
        vendor_id: UUID,
    ) -> dict[str, Any] | None:
        """
        Executes SQL aggregate queries across PurchaseOrders, DeliveryTracking, VendorRatings,
        and VendorIssues to compile a comprehensive real-time performance summary for a vendor.
        """
        # 1. Fetch Vendor details
        v_stmt = select(Vendor).where(Vendor.vendor_id == vendor_id)
        v_res = await db.execute(v_stmt)
        vendor = v_res.scalar_one_or_none()
        if not vendor:
            return None

        # 2. Aggregate Purchase Orders
        po_stmt = select(
            func.count(PurchaseOrder.po_id).label("total_pos"),
            func.count(
                func.nullif(
                    PurchaseOrder.status != PurchaseOrderStatusEnum.COMPLETED,
                    True,
                )
            ).label("completed_pos"),
        ).where(PurchaseOrder.vendor_id == vendor_id)
        po_res = await db.execute(po_stmt)
        po_row = po_res.first()
        total_pos = po_row.total_pos if po_row else 0
        completed_pos = po_row.completed_pos if po_row else 0

        # 3. Aggregate Deliveries (joined via PurchaseOrder)
        deliv_stmt = (
            select(
                func.count(DeliveryTracking.delivery_id).label("total_delivs"),
                func.count(
                    func.nullif(
                        DeliveryTracking.delivery_status != DeliveryStatusEnum.DELIVERED,
                        True,
                    )
                ).label("delivered_delivs"),
                func.count(
                    func.nullif(
                        or_(
                            DeliveryTracking.delivery_status != DeliveryStatusEnum.DELIVERED,
                            DeliveryTracking.delivered_date > DeliveryTracking.expected_date,
                        ),
                        True,
                    )
                ).label("on_time_delivs"),
                func.count(
                    func.nullif(
                        DeliveryTracking.delivery_status != DeliveryStatusEnum.DELAYED,
                        True,
                    )
                ).label("delayed_delivs"),
                func.count(
                    func.nullif(
                        DeliveryTracking.delivery_status != DeliveryStatusEnum.RETURNED,
                        True,
                    )
                ).label("returned_delivs"),
                func.avg(
                    cast(
                        DeliveryTracking.delivered_date - DeliveryTracking.expected_date,
                        Float,
                    )
                ).filter(
                    DeliveryTracking.delivered_date > DeliveryTracking.expected_date
                ).label("avg_delay"),
            )
            .select_from(DeliveryTracking)
            .join(PurchaseOrder, DeliveryTracking.po_id == PurchaseOrder.po_id)
            .where(PurchaseOrder.vendor_id == vendor_id)
        )
        deliv_res = await db.execute(deliv_stmt)
        d_row = deliv_res.first()

        total_delivs = d_row.total_delivs if d_row else 0
        delivered_delivs = d_row.delivered_delivs if d_row else 0
        on_time_delivs = d_row.on_time_delivs if d_row else 0
        delayed_delivs = d_row.delayed_delivs if d_row else 0
        returned_delivs = d_row.returned_delivs if d_row else 0
        avg_delay = float(d_row.avg_delay) if (d_row and d_row.avg_delay) else 0.0

        # Calculate delivery rates safely
        on_time_rate = round((on_time_delivs / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0
        success_rate = round((delivered_delivs / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0
        return_rate = round((returned_delivs / total_delivs * 100.0), 2) if total_delivs > 0 else 0.0

        # 4. Aggregate Ratings
        r_stmt = select(
            func.avg(VendorRating.quality_rating).label("avg_quality"),
            func.avg(VendorRating.delivery_rating).label("avg_delivery"),
            func.avg(VendorRating.communication_rating).label("avg_comm"),
            func.avg(VendorRating.overall_rating).label("avg_overall"),
        ).where(VendorRating.vendor_id == vendor_id)
        r_res = await db.execute(r_stmt)
        r_row = r_res.first()

        avg_quality = round(float(r_row.avg_quality), 2) if (r_row and r_row.avg_quality) else 0.0
        avg_delivery = round(float(r_row.avg_delivery), 2) if (r_row and r_row.avg_delivery) else 0.0
        avg_comm = round(float(r_row.avg_comm), 2) if (r_row and r_row.avg_comm) else 0.0
        avg_overall = round(float(r_row.avg_overall), 2) if (r_row and r_row.avg_overall) else 0.0

        # 5. Aggregate Issues
        iss_stmt = select(
            func.count(VendorIssue.issue_id).label("total_issues"),
            func.count(
                func.nullif(
                    ~VendorIssue.status.in_([IssueStatusEnum.OPEN, IssueStatusEnum.IN_PROGRESS]),
                    True,
                )
            ).label("open_issues"),
            func.count(
                func.nullif(
                    ~VendorIssue.status.in_([IssueStatusEnum.RESOLVED, IssueStatusEnum.CLOSED]),
                    True,
                )
            ).label("resolved_issues"),
            func.avg(cast(VendorIssue.resolution_time_hours, Float)).label("avg_res_hrs"),
        ).where(VendorIssue.vendor_id == vendor_id)
        iss_res = await db.execute(iss_stmt)
        i_row = iss_res.first()

        total_issues = i_row.total_issues if i_row else 0
        open_issues = i_row.open_issues if i_row else 0
        resolved_issues = i_row.resolved_issues if i_row else 0
        avg_res_hrs = round(float(i_row.avg_res_hrs), 2) if (i_row and i_row.avg_res_hrs) else 0.0

        return {
            "vendor_id": vendor.vendor_id,
            "vendor_name": vendor.company_name,
            "vendor_code": vendor.vendor_code,
            "total_purchase_orders": total_pos,
            "completed_purchase_orders": completed_pos,
            "total_deliveries": total_delivs,
            "on_time_deliveries": on_time_delivs,
            "delayed_deliveries": delayed_delivs,
            "returned_deliveries": returned_delivs,
            "on_time_delivery_rate": on_time_rate,
            "delivery_success_rate": success_rate,
            "return_rate": return_rate,
            "average_delivery_delay_days": round(avg_delay, 2),
            "average_quality_rating": avg_quality,
            "average_delivery_rating": avg_delivery,
            "average_communication_rating": avg_comm,
            "average_overall_rating": avg_overall,
            "total_issues_reported": total_issues,
            "open_issues_count": open_issues,
            "resolved_issues_count": resolved_issues,
            "average_issue_resolution_hours": avg_res_hrs,
        }

    async def get_vendor_rankings(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Executes SQL aggregation to rank all vendors based on composite overall performance scores.
        """
        vendors_stmt = select(Vendor).order_by(Vendor.company_name)
        vendors_res = await db.execute(vendors_stmt)
        vendors = list(vendors_res.scalars().all())

        rankings = []
        for vendor in vendors:
            summary = await self.get_vendor_performance_summary(db, vendor.vendor_id)
            if not summary:
                continue

            on_time_rate = summary["on_time_delivery_rate"]
            avg_rating = summary["average_overall_rating"]
            total_iss = summary["total_issues_reported"]
            resolved_iss = summary["resolved_issues_count"]

            resolved_rate = (resolved_iss / total_iss * 100.0) if total_iss > 0 else 100.0

            # Composite Score: 40% On-Time Delivery + 40% Average Rating + 20% Issue Resolution
            composite_score = round(
                (on_time_rate * 0.4) + ((avg_rating / 5.0 * 100.0) * 0.4) + (resolved_rate * 0.2),
                2,
            )

            rankings.append({
                "vendor_id": vendor.vendor_id,
                "vendor_name": vendor.company_name,
                "vendor_code": vendor.vendor_code,
                "overall_score": composite_score,
                "on_time_delivery_rate": on_time_rate,
                "average_overall_rating": avg_rating,
                "resolved_issues_rate": round(resolved_rate, 2),
            })

        # Sort by overall_score DESC
        rankings.sort(key=lambda x: x["overall_score"], reverse=True)

        # Apply ranking indices and pagination
        paginated_rankings = rankings[skip : skip + limit]
        for idx, item in enumerate(paginated_rankings, start=skip + 1):
            item["rank"] = idx

        return paginated_rankings


# Singleton instance
vendor_performance_repository = VendorPerformanceRepository()
