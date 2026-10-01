"""
FastAPI Router for Notification endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.users import User
from app.schemas.notifications import (
    NotificationResponse,
    UnreadNotificationCount,
)
from app.services.notification_service import notification_service


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user's notifications",
)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[NotificationResponse]:

    return list(
        await notification_service.get_user_notifications(
            db,
            current_user.user_id,
            skip=skip,
            limit=limit,
        )
    )


@router.get(
    "/unread-count",
    response_model=UnreadNotificationCount,
    status_code=status.HTTP_200_OK,
    summary="Get unread notification count",
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnreadNotificationCount:

    count = await notification_service.get_unread_count(
        db,
        current_user.user_id,
    )

    return UnreadNotificationCount(count=count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:

    return await notification_service.mark_as_read(
        db,
        current_user.user_id,
        notification_id,
    )