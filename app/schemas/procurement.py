"""
Pydantic v2 Schemas for Procurement Management module.
Covers ProcurementRequest, PurchaseOrder, and PurchaseOrderItem schemas.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.procurement import (
    PriorityEnum,
    PurchaseOrderStatusEnum,
    RequestStatusEnum,
)


# ======================================================================
# 1. PROCUREMENT REQUEST SCHEMAS
# ======================================================================

class ProcurementRequestBase(BaseModel):
    """
    Base client input fields for a Procurement Request.
    Shared across create schemas. Excludes server-managed fields.
    """

    model_config = ConfigDict(extra="forbid")

    department: Optional[str] = Field(
        None,
        max_length=100,
        description="Department requesting the procurement.",
        examples=["Engineering"],
    )
    item_description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of the requested item or service.",
        examples=["Heavy duty industrial lathe machine"],
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Requested quantity (must be greater than 0).",
        examples=[2.0],
    )
    estimated_cost: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Estimated total cost for the request.",
        examples=[15000.00],
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="Request priority level.",
    )
    required_by_date: Optional[date] = Field(
        None,
        description="Date by which the items/services are required.",
    )


class ProcurementRequestCreate(ProcurementRequestBase):
    """
    Schema for creating a new Procurement Request (Client Input only).

    Server-managed fields EXCLUDED:
    - request_number (Server-managed: auto-generated format PR-YYYY-XXXX)
    - status (Server-managed: defaults to 'pending')
    - approved_by (Server-managed: null until approved)
    - approved_at (Server-managed: null until approved)
    - created_at, updated_at (Database-managed)
    """

    pass


class ProcurementRequestUpdate(BaseModel):
    """
    Schema for updating an existing Procurement Request (Client Input only).
    All fields are optional.
    """

    model_config = ConfigDict(extra="forbid")

    department: Optional[str] = Field(
        None,
        max_length=100,
    )
    item_description: Optional[str] = Field(
        None,
        min_length=1,
    )
    quantity: Optional[Decimal] = Field(
        None,
        gt=0,
    )
    estimated_cost: Optional[Decimal] = Field(
        None,
        ge=0,
    )
    priority: Optional[PriorityEnum] = None
    required_by_date: Optional[date] = None


class ProcurementRequestResponse(BaseModel):
    """
    Response schema representing complete ProcurementRequest entity.
    """

    request_id: UUID
    request_number: str
    requested_by: UUID
    department: Optional[str] = None
    item_description: str
    quantity: Decimal
    estimated_cost: Optional[Decimal] = None
    priority: PriorityEnum
    required_by_date: Optional[date] = None
    status: RequestStatusEnum
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ======================================================================
# 2. PURCHASE ORDER ITEM SCHEMAS
# ======================================================================

class PurchaseOrderItemBase(BaseModel):
    """
    Base client input fields for a Purchase Order Item.
    Excludes server/database-managed total_price.
    """

    model_config = ConfigDict(extra="forbid")

    item_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Name of the ordered item or line item.",
        examples=["Steel Rods 10mm"],
    )
    description: Optional[str] = Field(
        None,
        max_length=400,
        description="Line item description.",
    )
    uom: Optional[str] = Field(
        None,
        max_length=20,
        description="Unit of Measure (e.g., PCS, KG, MTRS).",
        examples=["PCS"],
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Ordered quantity.",
        examples=[100.0],
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Unit price per item.",
        examples=[25.50],
    )


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """
    Schema for creating a line item within a Purchase Order.

    Server-managed fields EXCLUDED:
    - total_price (Database-managed STORED GENERATED column)
    """

    pass


class PurchaseOrderItemUpdate(BaseModel):
    """
    Schema for updating a Purchase Order Item.
    """

    model_config = ConfigDict(extra="forbid")

    item_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150,
    )
    description: Optional[str] = Field(
        None,
        max_length=400,
    )
    uom: Optional[str] = Field(
        None,
        max_length=20,
    )
    quantity: Optional[Decimal] = Field(
        None,
        gt=0,
    )
    unit_price: Optional[Decimal] = Field(
        None,
        ge=0,
    )


class PurchaseOrderItemResponse(BaseModel):
    """
    Response schema representing complete PurchaseOrderItem entity.
    Exposes total_price calculated by database.
    """

    po_item_id: UUID
    po_id: UUID
    item_name: str
    description: Optional[str] = None
    uom: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


# ======================================================================
# 3. PURCHASE ORDER SCHEMAS
# ======================================================================

class PurchaseOrderBase(BaseModel):
    """
    Base client input fields for a Purchase Order.
    Excludes server-managed fields.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: Optional[UUID] = Field(
        None,
        description="Optional associated Procurement Request ID.",
    )
    vendor_id: UUID = Field(
        ...,
        description="Foreign key referencing vendors table.",
    )
    expected_delivery_date: Optional[date] = Field(
        None,
        description="Expected delivery date.",
    )
    payment_terms: Optional[str] = Field(
        None,
        max_length=100,
        description="Agreed payment terms (e.g. Net 30).",
        examples=["Net 30 Days"],
    )


class PurchaseOrderCreate(PurchaseOrderBase):
    """
    Schema for creating a new Purchase Order (Client Input only).

    Server-managed fields EXCLUDED:
    - po_number (Server-managed: auto-generated format PO-YYYY-XXXX)
    - status (Server-managed: defaults to 'pending')
    - total_amount (Server-managed: auto-calculated from line items)
    - created_at, updated_at (Database-managed)
    """

    items: list[PurchaseOrderItemCreate] = Field(
        ...,
        min_length=1,
        description="Line items included in the purchase order (at least 1 item required).",
    )


class PurchaseOrderUpdate(BaseModel):
    """
    Schema for updating an existing Purchase Order (Client Input only).
    """

    model_config = ConfigDict(extra="forbid")

    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = Field(
        None,
        max_length=100,
    )


class PurchaseOrderResponse(BaseModel):
    """
    Response schema representing complete PurchaseOrder entity.
    Exposes server-managed, DB-managed, line items, and vendor name.
    """

    po_id: UUID
    po_number: str
    request_id: Optional[UUID] = None
    vendor_id: UUID
    vendor_name: str | None = None
    created_by: UUID
    order_date: date
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    total_amount: Decimal
    status: PurchaseOrderStatusEnum
    items: list[PurchaseOrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations(cls, data: Any) -> Any:
        """
        Extract vendor_name and items list safely when deserializing
        from an ORM PurchaseOrder model instance.
        """
        if hasattr(data, "po_id") and hasattr(data, "vendor_id"):
            vendor_name = None
            if hasattr(data, "vendor") and data.vendor is not None:
                if hasattr(data.vendor, "company_name"):
                    vendor_name = data.vendor.company_name

            items = []
            if hasattr(data, "items") and data.items is not None:
                items = data.items

            result = {
                "po_id": data.po_id,
                "po_number": data.po_number,
                "request_id": data.request_id,
                "vendor_id": data.vendor_id,
                "vendor_name": vendor_name,
                "created_by": data.created_by,
                "order_date": data.order_date,
                "expected_delivery_date": data.expected_delivery_date,
                "actual_delivery_date": data.actual_delivery_date,
                "payment_terms": data.payment_terms,
                "total_amount": data.total_amount,
                "status": data.status,
                "items": items,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
            return result
        return data
