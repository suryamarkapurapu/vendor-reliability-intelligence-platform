"""
Repository layer for PasswordResetToken database operations using SQLAlchemy 2.0 Async.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset import PasswordResetToken


class PasswordResetRepository:
    """
    Repository executing CRUD operations on the PasswordResetToken model.
    """

    async def create_token(
        self,
        db: AsyncSession,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        """
        Creates a new hashed password reset token record.
        """
        try:
            db_token = PasswordResetToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            db.add(db_token)
            await db.commit()
            await db.refresh(db_token)
            return db_token
        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_valid_token(
        self,
        db: AsyncSession,
        token_hash: str,
    ) -> PasswordResetToken | None:
        """
        Retrieves a token by its SHA-256 hash if it has not been used and is not expired.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def invalidate_token(
        self,
        db: AsyncSession,
        db_token: PasswordResetToken,
    ) -> PasswordResetToken:
        """
        Marks a reset token as used (one-time use invalidation).
        """
        try:
            db_token.used_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(db_token)
            return db_token
        except SQLAlchemyError:
            await db.rollback()
            raise


password_reset_repository = PasswordResetRepository()
