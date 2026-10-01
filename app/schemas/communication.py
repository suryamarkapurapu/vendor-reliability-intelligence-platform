"""
Pydantic v2 Schemas for Communication / Messages.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    receiver_id: UUID
    vendor_id: Optional[UUID] = None
    po_id: Optional[UUID] = None
    subject: Optional[str] = Field(None, max_length=200)
    message_body: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="ignore")


class MessageResponse(BaseModel):
    message_id: UUID
    sender_id: UUID
    receiver_id: UUID
    vendor_id: Optional[UUID] = None
    po_id: Optional[UUID] = None
    subject: Optional[str] = None
    message_body: str
    is_read: bool
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
