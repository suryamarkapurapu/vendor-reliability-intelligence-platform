"""
Service layer for User business logic operations.
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidUserDataError,
    RoleNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import hash_password
from app.models.users import User
from app.repositories.user_repository import (
    UserRepository,
    user_repository,
)
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Service layer responsible for user-related business logic.
    """

    def __init__(self, repo: UserRepository | None = None) -> None:
        self.repo = repo or user_repository

    async def create_user(
        self,
        db: AsyncSession,
        user_in: UserCreate,
    ) -> User:

        # Business Rule: role_id must reference an existing role
        role = await self.repo.get_role_by_id(db, user_in.role_id)

        if not role:
            raise RoleNotFoundError(user_in.role_id)

        existing_username = await self.repo.get_user_by_username(
            db,
            user_in.username,
        )

        if existing_username:
            raise UserAlreadyExistsError(
                f"Username '{user_in.username}' already exists."
            )

        existing_email = await self.repo.get_user_by_email(
            db,
            str(user_in.email),
        )

        if existing_email:
            raise UserAlreadyExistsError(
                f"Email '{user_in.email}' already exists."
            )

        user_data: dict[str, Any] = user_in.model_dump(
            exclude_unset=True
        )

        raw_password = user_data.pop("password")

        user_data["password_hash"] = hash_password(raw_password)

        return await self.repo.create_user(
            db,
            user_data,
        )

    async def get_user(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> User:

        user = await self.repo.get_user_by_id(
            db,
            user_id,
        )

        if not user:
            raise UserNotFoundError(
                f"User '{user_id}' not found."
            )

        return user

    async def get_all_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        if skip < 0:
            raise InvalidUserDataError(
                "Skip must be greater than or equal to 0."
            )

        if limit <= 0:
            raise InvalidUserDataError(
                "Limit must be greater than 0."
            )

        return await self.repo.get_all_users(
            db,
            skip,
            limit,
        )

    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_in: UserUpdate,
    ) -> User:

        db_user = await self.repo.get_user_by_id(
            db,
            user_id,
        )

        if not db_user:
            raise UserNotFoundError(
                f"User '{user_id}' not found."
            )

        update_data: dict[str, Any] = user_in.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise InvalidUserDataError(
                "No fields provided for update."
            )

        # Business Rule: if role_id is being changed, validate it exists
        if (
            "role_id" in update_data
            and update_data["role_id"] != db_user.role_id
        ):
            role = await self.repo.get_role_by_id(
                db,
                update_data["role_id"],
            )

            if not role:
                raise RoleNotFoundError(update_data["role_id"])

        if (
            "username" in update_data
            and update_data["username"] != db_user.username
        ):

            existing = await self.repo.get_user_by_username(
                db,
                update_data["username"],
            )

            if existing and existing.user_id != user_id:
                raise UserAlreadyExistsError(
                    f"Username '{update_data['username']}' already exists."
                )

        if (
            "email" in update_data
            and str(update_data["email"]) != db_user.email
        ):

            existing = await self.repo.get_user_by_email(
                db,
                str(update_data["email"]),
            )

            if existing and existing.user_id != user_id:
                raise UserAlreadyExistsError(
                    f"Email '{update_data['email']}' already exists."
                )

        if "password" in update_data:

            raw_password = update_data.pop("password")

            update_data["password_hash"] = hash_password(
                raw_password
            )

        return await self.repo.update_user(
            db,
            db_user,
            update_data,
        )

    async def delete_user(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> User:

        db_user = await self.repo.get_user_by_id(
            db,
            user_id,
        )

        if not db_user:
            raise UserNotFoundError(
                f"User '{user_id}' not found."
            )

        if not db_user.is_active:
            raise InvalidUserDataError(
                f"User '{user_id}' is already inactive."
            )

        return await self.repo.delete_user(
            db,
            db_user,
        )


user_service = UserService()