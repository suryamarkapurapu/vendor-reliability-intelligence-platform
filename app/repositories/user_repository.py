"""
Repository layer for User database operations using SQLAlchemy 2.0 Async.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.roles import Role
from app.models.users import User


class UserRepository:
    """
    Repository responsible only for database operations.
    """

    async def create_user(
        self,
        db: AsyncSession,
        user_data: dict[str, Any],
    ) -> User:
        try:
            db_user = User(**user_data)

            db.add(db_user)

            await db.commit()

            await db.refresh(db_user)

            await db.refresh(db_user, attribute_names=["role"])

            return db_user

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> User | None:

        stmt = (
            select(User)
            .options(selectinload(User.role))
            .where(User.user_id == user_id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_by_username(
        self,
        db: AsyncSession,
        username: str,
    ) -> User | None:

        stmt = (
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        stmt = (
            select(User)
            .options(selectinload(User.role))
            .order_by(
                User.created_at.desc(),
                User.user_id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def update_user(
        self,
        db: AsyncSession,
        db_user: User,
        update_data: dict[str, Any],
    ) -> User:

        try:
            for field, value in update_data.items():
                if hasattr(db_user, field):
                    setattr(db_user, field, value)

            await db.commit()

            await db.refresh(db_user)

            await db.refresh(db_user, attribute_names=["role"])

            return db_user

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def delete_user(
        self,
        db: AsyncSession,
        db_user: User,
    ) -> User:

        try:
            db_user.is_active = False

            await db.commit()

            await db.refresh(db_user)

            await db.refresh(db_user, attribute_names=["role"])

            return db_user

        except SQLAlchemyError:
            await db.rollback()
            raise

    async def get_role_by_id(
        self,
        db: AsyncSession,
        role_id: int,
    ) -> Role | None:
        """
        Retrieves a role by primary key to validate role_id existence.
        """
        stmt = select(Role).where(Role.role_id == role_id)

        result = await db.execute(stmt)

        return result.scalar_one_or_none()


user_repository = UserRepository()                    
