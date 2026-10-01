from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_logs import ActivityLog


class ActivityLogRepository:

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID | None,
        entity_type: str,
        entity_id: UUID | None,
        action: str,
        description: str | None = None,
        ip_address: str | None = None,
    ) -> ActivityLog:

        activity = ActivityLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            ip_address=ip_address,
        )

        db.add(activity)
        await db.flush()

        return activity

    async def get_recent(
        self,
        db: AsyncSession,
        limit: int = 10,
    ) -> list[ActivityLog]:

        result = await db.execute(
            select(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )

        return list(result.scalars().all())