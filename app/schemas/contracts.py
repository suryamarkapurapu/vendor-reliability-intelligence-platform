"""
Pydantic v2 Schemas for Contracts.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContractCreate(BaseModel):
    contract_number: str = Field(..., min_length=1, max_length=30)
    vendor_id: UUID
    contract_type: Optional[str] = Field(None, max_length=80)
    start_date: date
    end_date: date
    contract_value: Optional[float] = Field(None, ge=0)
    status: str = Field(default="draft", max_length=30)
    document_path: Optional[str] = Field(None, max_length=400)

    model_config = ConfigDict(extra="ignore")


class ContractUpdate(BaseModel):
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_value: Optional[float] = None
    status: Optional[str] = None
    document_path: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ContractResponse(BaseModel):
    contract_id: UUID
    contract_number: str
    vendor_id: UUID
    contract_type: Optional[str] = None
    start_date: date
    end_date: date
    contract_value: Optional[float] = None
    status: str
    document_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
