"""
Repository layer for UserSettings database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import UserSettings


class SettingsRepository:
    """
    Repository executing CRUD operations on the UserSettings model.
    """

    async def get_settings_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> UserSettings | None:
        """
        Retrieves settings record for a specific user.
        """
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_settings(
        self,
        db: AsyncSession,
        user_id: UUID,
        settings_data: dict[str, Any] | None = None,
    ) -> UserSettings:
        """
        Creates a default UserSettings record for a user.
        """
        try:
            data = settings_data or {}
            data["user_id"] = user_id
            db_settings = UserSettings(**data)
            db.add(db_settings)
            await db.commit()
            await db.refresh(db_settings)
            return db_settings
        except SQLAlchemyError:
            await db.rollback()
            raise

    async def update_settings(
        self,
        db: AsyncSession,
        db_settings: UserSettings,
        update_data: dict[str, Any],
    ) -> UserSettings:
        """
        Updates an existing UserSettings record.
        """
        try:
            for field, value in update_data.items():
                if hasattr(db_settings, field) and value is not None:
                    setattr(db_settings, field, value)

            await db.commit()
            await db.refresh(db_settings)
            return db_settings
        except SQLAlchemyError:
            await db.rollback()
            raise


settings_repository = SettingsRepository()
