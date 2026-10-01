"""
Service layer for Messages / Communication operations.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.communication import Message
from app.repositories.communication_repository import (
    CommunicationRepository,
    communication_repository,
)
from app.repositories.notification_repository import (
    notification_repository,
)
from app.schemas.communication import MessageCreate


class CommunicationService:

    def __init__(
        self,
        repo: CommunicationRepository | None = None,
    ) -> None:
        self.repo = repo or communication_repository

    async def get_message(
        self,
        db: AsyncSession,
        message_id: UUID,
    ) -> Message:

        msg = await self.repo.get_by_id(
            db,
            message_id,
        )

        if not msg:
            raise EntityNotFoundError(
                f"Message with ID {message_id} not found."
            )

        return msg

    async def get_all_messages(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Message]:

        return await self.repo.get_all(
            db,
            skip=skip,
            limit=limit,
        )

    async def send_message(
        self,
        db: AsyncSession,
        sender_id: UUID,
        obj_in: MessageCreate,
    ) -> Message:

        message = await self.repo.create(
            db,
            sender_id,
            obj_in,
        )

        await notification_repository.create(
            db=db,
            user_id=message.receiver_id,
            notification_type="new_message",
            title=message.subject or "New Message",
            message=message.message_body,
            related_entity_type="message",
            related_entity_id=message.message_id,
        )

        await db.commit()

        await db.refresh(message)

        return message

    async def mark_as_read(
        self,
        db: AsyncSession,
        user_id: UUID,
        message_id: UUID,
    ) -> Message:

        message = await self.repo.get_by_id(
            db,
            message_id,
        )

        if not message:
            raise EntityNotFoundError(
                f"Message with ID {message_id} not found."
            )

        # Only the receiver can mark the message as read.
        if message.receiver_id != user_id:
            raise EntityNotFoundError(
                f"Message with ID {message_id} not found."
            )

        if not message.is_read:
            return await self.repo.mark_as_read(
                db,
                message,
            )

        return message


communication_service = CommunicationService()