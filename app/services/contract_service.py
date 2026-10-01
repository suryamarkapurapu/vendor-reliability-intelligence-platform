"""
Service layer for Contract business logic.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.contracts import Contract
from app.repositories.contract_repository import (
    ContractRepository,
    contract_repository,
)
from app.schemas.contracts import ContractCreate, ContractUpdate


class ContractService:
    def __init__(self, repo: ContractRepository | None = None) -> None:
        self.repo = repo or contract_repository

    async def get_contract(self, db: AsyncSession, contract_id: UUID) -> Contract:
        contract = await self.repo.get_by_id(db, contract_id)
        if not contract:
            raise EntityNotFoundError(f"Contract with ID {contract_id} not found.")
        return contract

    async def get_all_contracts(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Contract]:
        return await self.repo.get_all(db, skip=skip, limit=limit)

    async def create_contract(
        self,
        db: AsyncSession,
        obj_in: ContractCreate,
    ) -> Contract:
        return await self.repo.create(db, obj_in)

    async def update_contract(
        self,
        db: AsyncSession,
        contract_id: UUID,
        obj_in: ContractUpdate,
    ) -> Contract:
        contract = await self.get_contract(db, contract_id)
        return await self.repo.update(db, contract, obj_in)


contract_service = ContractService()
