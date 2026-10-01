"""
Repository implementation for Notifications data access.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import (
    Notification,
    NotificationChannelEnum,
    NotificationPriorityEnum,
)


class NotificationRepository:

    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        related_entity_type: str | None = None,
        related_entity_id: UUID | None = None,
        priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            channel=NotificationChannelEnum.IN_APP,
            notification_type=notification_type,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            priority=priority,
            is_read=False,
        )

        db.add(notification)

        await db.flush()
        await db.refresh(notification)

        return notification

    async def get_for_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Notification]:

        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return result.scalars().all()

    async def get_unread_count(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> int:

        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one()

    async def get_by_id(
        self,
        db: AsyncSession,
        notification_id: UUID,
    ) -> Notification | None:

        stmt = select(Notification).where(
            Notification.notification_id == notification_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification: Notification,
    ) -> Notification:

        notification.is_read = True

        await db.commit()
        await db.refresh(notification)

        return notification


notification_repository = NotificationRepository()