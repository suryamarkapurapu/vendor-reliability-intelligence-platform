"""
Service layer for Notification operations.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.notifications import Notification
from app.repositories.notification_repository import (
    NotificationRepository,
    notification_repository,
)


class NotificationService:

    def __init__(
        self,
        repo: NotificationRepository | None = None,
    ) -> None:
        self.repo = repo or notification_repository

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Notification]:

        return await self.repo.get_for_user(
            db,
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_unread_count(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> int:

        return await self.repo.get_unread_count(
            db,
            user_id,
        )

    async def mark_as_read(
        self,
        db: AsyncSession,
        user_id: UUID,
        notification_id: UUID,
    ) -> Notification:

        notification = await self.repo.get_by_id(
            db,
            notification_id,
        )

        if not notification:
            raise EntityNotFoundError(
                f"Notification with ID {notification_id} not found."
            )

        # Security check:
        # A user can only mark their own notification as read.
        if notification.user_id != user_id:
            raise EntityNotFoundError(
                f"Notification with ID {notification_id} not found."
            )

        return await self.repo.mark_as_read(
            db,
            notification,
        )


notification_service = NotificationService()