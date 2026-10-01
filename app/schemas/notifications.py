"""
Pydantic v2 Schemas for Notifications.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    notification_id: UUID
    user_id: UUID
    channel: str
    notification_type: str
    title: str
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    priority: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnreadNotificationCount(BaseModel):
    count: int