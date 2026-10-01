"""
Pydantic v2 Schemas for the Vendor module.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.vendors import VendorStatusEnum


class VendorBase(BaseModel):
    """
    Base client input fields for a Vendor. Shared across create schemas.
    Excludes server-managed and database-managed fields.
    """

    model_config = ConfigDict(extra="forbid")

    vendor_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique identifier code for the vendor (max 20 characters).",
        examples=["VEND-001"],
    )
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Official legal name of the vendor (max 150 characters).",
        examples=["Acme Industrial Supplies"],
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="Foreign key referencing vendor_categories table.",
        examples=[1],
    )
    linked_user_id: Optional[UUID] = Field(
        None,
        description="Optional associated portal user ID.",
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Tax identifier or VAT registration number.",
    )
    website: Optional[str] = Field(
        None,
        max_length=200,
        description="Official website URL.",
    )
    address_line: Optional[str] = Field(
        None,
        max_length=200,
        description="Street address.",
    )
    city: Optional[str] = Field(
        None,
        max_length=80,
        description="City location.",
    )
    state: Optional[str] = Field(
        None,
        max_length=80,
        description="State or region.",
    )
    country: Optional[str] = Field(
        None,
        max_length=80,
        description="Country location.",
    )
    postal_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Postal or ZIP code.",
    )


class VendorCreate(VendorBase):
    """
    Schema for creating a new Vendor (Client Input only).

    Fields strictly managed by backend/database are EXCLUDED:
    - status (Server-managed: defaults to 'pending')
    - approved_by (Server-managed: null until approved via approval workflow)
    - approved_at (Server-managed: null until approved via approval workflow)
    - registration_date (Database-managed: defaults to CURRENT_DATE)
    """

    pass


class VendorUpdate(BaseModel):
    """
    Schema for updating an existing Vendor (Client Input only).
    All fields are optional.

    Fields strictly managed by backend/database are EXCLUDED:
    - status
    - approved_by
    - approved_at
    - registration_date
    """

    model_config = ConfigDict(extra="forbid")

    vendor_code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Unique identifier code for the vendor.",
    )
    company_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150,
        description="Official legal name of the vendor.",
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="Foreign key referencing vendor_categories table.",
    )
    linked_user_id: Optional[UUID] = Field(
        None,
        description="Optional associated portal user ID.",
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
    )
    website: Optional[str] = Field(
        None,
        max_length=200,
    )
    address_line: Optional[str] = Field(
        None,
        max_length=200,
    )
    city: Optional[str] = Field(
        None,
        max_length=80,
    )
    state: Optional[str] = Field(
        None,
        max_length=80,
    )
    country: Optional[str] = Field(
        None,
        max_length=80,
    )
    postal_code: Optional[str] = Field(
        None,
        max_length=20,
    )


class VendorResponse(BaseModel):
    """
    Response schema representing complete Vendor entity returned to clients.
    Exposes client input, server-managed, database-managed, and audit fields.

    Inherits from BaseModel (not VendorBase) to avoid leaking input-only
    validations (min_length, gt) into response serialization.
    """

    vendor_id: UUID
    vendor_code: str
    company_name: str
    category_id: int
    category_name: str | None = None
    linked_user_id: Optional[UUID] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    status: VendorStatusEnum
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    registration_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_category_name(cls, data: Any) -> Any:
        """
        Extract category_name from the nested VendorCategory ORM
        relationship object when deserializing from an ORM model instance.
        """
        # Handle ORM model objects (from_attributes=True path)
        if hasattr(data, "vendor_id") and hasattr(data, "category_id"):
            # Determine category_name from relationship if loaded
            category_name = None
            if hasattr(data, "category") and data.category is not None:
                if hasattr(data.category, "category_name"):
                    category_name = data.category.category_name

            # Always build explicit dict to prevent implicit lazy-load
            result = {
                "vendor_id": data.vendor_id,
                "vendor_code": data.vendor_code,
                "company_name": data.company_name,
                "category_id": data.category_id,
                "category_name": category_name,
                "linked_user_id": data.linked_user_id,
                "tax_id": data.tax_id,
                "website": data.website,
                "address_line": data.address_line,
                "city": data.city,
                "state": data.state,
                "country": data.country,
                "postal_code": data.postal_code,
                "status": data.status,
                "approved_by": data.approved_by,
                "approved_at": data.approved_at,
                "registration_date": data.registration_date,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
            return result
        return data
