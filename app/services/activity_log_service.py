from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.activity_log_repository import ActivityLogRepository


class ActivityLogService:

    def __init__(self):
        self.repo = ActivityLogRepository()

    async def log_activity(
        self,
        db: AsyncSession,
        *,
        user_id: UUID | None,
        entity_type: str,
        entity_id: UUID | None,
        action: str,
        description: str | None = None,
        ip_address: str | None = None,
    ):
        return await self.repo.create(
            db,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            ip_address=ip_address,
        )

    async def get_recent_activity(
        self,
        db: AsyncSession,
        limit: int = 10,
    ):
        return await self.repo.get_recent(
            db,
            limit=limit,
        )


activity_log_service = ActivityLogService()