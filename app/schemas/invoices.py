"""
Pydantic v2 Schemas for Invoice Management module.
Covers InvoiceBase, InvoiceCreate, InvoiceUpdate, and InvoiceResponse schemas.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.invoices import InvoiceStatusEnum


class InvoiceBase(BaseModel):
    """
    Base client input fields for an Invoice.
    Shared across create schemas. Excludes server-managed fields.
    """

    model_config = ConfigDict(extra="forbid")

    po_id: UUID = Field(
        ...,
        description="Foreign key referencing purchase_orders table.",
    )
    vendor_id: UUID = Field(
        ...,
        description="Foreign key referencing vendors table.",
    )
    invoice_date: date = Field(
        ...,
        description="Date the invoice was issued.",
    )
    due_date: Optional[date] = Field(
        None,
        description="Date payment is due.",
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        description="Invoice net amount before tax (must be non-negative).",
        examples=[1000.00],
    )
    tax_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Tax or VAT amount (must be non-negative).",
        examples=[180.00],
    )


class InvoiceCreate(InvoiceBase):
    """
    Schema for creating a new Invoice (Client Input only).

    Server-managed fields EXCLUDED:
    - invoice_number (Server-managed: auto-generated format INV-YYYY-XXXX)
    - status (Server-managed: defaults to 'pending')
    - paid_date (Server-managed: null until payment processed)
    - created_at (Database-managed timestamp)
    """

    pass


class InvoiceUpdate(BaseModel):
    """
    Schema for updating an existing Invoice (Client Input only).
    All fields are optional.
    """

    model_config = ConfigDict(extra="forbid")

    due_date: Optional[date] = Field(
        None,
        description="Updated payment due date.",
    )
    amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Updated net amount.",
    )
    tax_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Updated tax amount.",
    )


class InvoiceResponse(BaseModel):
    """
    Response schema representing complete Invoice entity.
    Exposes server-managed, DB-managed, derived, and relationship fields.

    Inherits from BaseModel (not InvoiceBase) to avoid leaking input-only
    validations into response serialization.
    """

    invoice_id: UUID
    invoice_number: str
    po_id: UUID
    po_number: Optional[str] = None
    vendor_id: UUID
    vendor_name: Optional[str] = None
    invoice_date: date
    due_date: Optional[date] = None
    amount: Decimal
    tax_amount: Decimal
    total_with_tax: Decimal
    status: InvoiceStatusEnum
    paid_date: Optional[date] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations_and_derived_fields(cls, data: Any) -> Any:
        """
        Safely extract po_number, vendor_name, and compute derived total_with_tax
        when deserializing from an ORM Invoice model instance or dict.
        """
        if hasattr(data, "invoice_id") and hasattr(data, "po_id"):
            po_number = None
            if hasattr(data, "purchase_order") and data.purchase_order is not None:
                if hasattr(data.purchase_order, "po_number"):
                    po_number = data.purchase_order.po_number

            vendor_name = None
            if hasattr(data, "vendor") and data.vendor is not None:
                if hasattr(data.vendor, "company_name"):
                    vendor_name = data.vendor.company_name

            amount = getattr(data, "amount", Decimal("0"))
            tax_amount = getattr(data, "tax_amount", Decimal("0"))
            total_with_tax = (amount or Decimal("0")) + (tax_amount or Decimal("0"))

            result = {
                "invoice_id": data.invoice_id,
                "invoice_number": data.invoice_number,
                "po_id": data.po_id,
                "po_number": po_number,
                "vendor_id": data.vendor_id,
                "vendor_name": vendor_name,
                "invoice_date": data.invoice_date,
                "due_date": data.due_date,
                "amount": amount,
                "tax_amount": tax_amount,
                "total_with_tax": total_with_tax,
                "status": data.status,
                "paid_date": data.paid_date,
                "created_at": data.created_at,
            }
            return result
        elif isinstance(data, dict):
            if "total_with_tax" not in data:
                amt = data.get("amount", Decimal("0")) or Decimal("0")
                tax = data.get("tax_amount", Decimal("0")) or Decimal("0")
                data["total_with_tax"] = amt + tax
        return data
