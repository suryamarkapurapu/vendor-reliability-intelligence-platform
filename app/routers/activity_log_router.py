from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.activity_log_service import activity_log_service

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)


@router.get("/recent")
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    activities = await activity_log_service.get_recent_activity(
        db,
        limit=limit,
    )

    return [
        {
            "log_id": activity.log_id,
            "user_id": activity.user_id,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "action": activity.action,
            "description": activity.description,
            "ip_address": str(activity.ip_address)
            if activity.ip_address
            else None,
            "created_at": activity.created_at,
        }
        for activity in activities
    ]