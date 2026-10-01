"""
Pydantic v2 Schemas for Authentication and Token Management.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    user_id: UUID | None = None

    email: EmailStr | None = None

    role: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role_id: int = Field(default=2, description="Role ID (1=Admin, 2=Procurement, 3=Vendor, etc.)")

    model_config = ConfigDict(extra="ignore")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(extra="ignore")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="ignore")

