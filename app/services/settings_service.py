"""
Service layer for User Settings operations.
Connects UserSettings repository to FastAPI router endpoints with PostgreSQL persistence.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.repositories.settings_repository import SettingsRepository, settings_repository
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate


class SettingsService:
    """
    Service managing UserSettings logic and PostgreSQL persistence.
    """

    def __init__(self, repo: SettingsRepository | None = None) -> None:
        self.repo = repo or settings_repository

    async def get_settings(
        self,
        db: AsyncSession,
        user: User,
    ) -> UserSettingsResponse:
        """
        Retrieves user settings from PostgreSQL.
        If no settings record exists for the user, creates default settings.
        """
        db_settings = await self.repo.get_settings_by_user_id(db, user.user_id)
        if not db_settings:
            db_settings = await self.repo.create_settings(
                db,
                user_id=user.user_id,
                settings_data={
                    "company_name": "Enterprise Vendor Reliability Corp",
                    "company_email": user.email,
                },
            )

        return UserSettingsResponse.model_validate(db_settings)

    async def update_settings(
        self,
        db: AsyncSession,
        user: User,
        settings_in: UserSettingsUpdate,
    ) -> UserSettingsResponse:
        """
        Updates user settings in PostgreSQL.
        """
        db_settings = await self.repo.get_settings_by_user_id(db, user.user_id)
        if not db_settings:
            db_settings = await self.repo.create_settings(
                db,
                user_id=user.user_id,
            )

        update_data = settings_in.model_dump(exclude_unset=True)
        updated = await self.repo.update_settings(db, db_settings, update_data)
        return UserSettingsResponse.model_validate(updated)


settings_service = SettingsService()
