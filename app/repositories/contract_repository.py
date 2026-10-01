"""
Repository pattern implementation for Contract data access.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contracts import Contract
from app.schemas.contracts import ContractCreate, ContractUpdate


class ContractRepository:
    async def get_by_id(self, db: AsyncSession, contract_id: UUID) -> Contract | None:
        stmt = select(Contract).where(Contract.contract_id == contract_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Contract]:
        stmt = select(Contract).offset(skip).limit(limit).order_by(Contract.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: ContractCreate) -> Contract:
        db_obj = Contract(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: Contract,
        obj_in: ContractUpdate,
    ) -> Contract:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


contract_repository = ContractRepository()
