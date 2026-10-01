"""
Pydantic v2 Schemas for User Management.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    role_id: int = Field(
        ...,
        gt=0,
        description="Foreign key referencing the roles table.",
    )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    role_id: int | None = Field(
        default=None,
        gt=0,
        description="Foreign key referencing the roles table.",
    )

    is_active: bool | None = None


class UserResponse(BaseModel):
    user_id: UUID
    username: str
    full_name: str
    email: EmailStr
    role_id: int
    role_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_role_name(cls, data: Any) -> Any:
        """
        Extract role_name from the nested Role ORM relationship object
        when deserializing from an ORM model instance.
        """
        # Handle ORM model objects (from_attributes=True path)
        if hasattr(data, "role") and data.role is not None:
            if hasattr(data.role, "role_name"):
                # SQLAlchemy ORM object — inject role_name as attribute
                # We need to return a dict so we can add the extra field
                result = {
                    "user_id": data.user_id,
                    "username": data.username,
                    "full_name": data.full_name,
                    "email": data.email,
                    "role_id": data.role_id,
                    "role_name": data.role.role_name,
                    "is_active": data.is_active,
                    "created_at": data.created_at,
                    "updated_at": data.updated_at,
                }
                return result
        return data