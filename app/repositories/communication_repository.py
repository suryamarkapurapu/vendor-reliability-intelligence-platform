"""
Repository implementation for Messages / Communication data access.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication import Message
from app.schemas.communication import MessageCreate


class CommunicationRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        message_id: UUID,
    ) -> Message | None:
        stmt = select(Message).where(
            Message.message_id == message_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Message]:

        stmt = (
            select(Message)
            .offset(skip)
            .limit(limit)
            .order_by(Message.sent_at.desc())
        )

        result = await db.execute(stmt)

        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        sender_id: UUID,
        obj_in: MessageCreate,
    ) -> Message:

        db_obj = Message(
            sender_id=sender_id,
            **obj_in.model_dump(),
        )

        db.add(db_obj)

        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def mark_as_read(
        self,
        db: AsyncSession,
        message: Message,
    ) -> Message:

        message.is_read = True

        await db.commit()
        await db.refresh(message)

        return message


communication_repository = CommunicationRepository()