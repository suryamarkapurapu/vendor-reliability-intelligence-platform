"""
Pydantic v2 Schemas for Delivery Tracking module.
Covers DeliveryTrackingBase, DeliveryTrackingCreate, DeliveryTrackingUpdate, and DeliveryTrackingResponse.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.delivery import DeliveryStatusEnum


class DeliveryTrackingBase(BaseModel):
    """
    Base client input fields for a DeliveryTracking record.
    Shared across create schemas. Excludes server-managed fields.
    """

    model_config = ConfigDict(extra="forbid")

    po_id: UUID = Field(
        ...,
        description="Foreign key referencing purchase_orders table.",
    )
    tracking_number: Optional[str] = Field(
        None,
        max_length=80,
        description="Logistics or carrier tracking number.",
        examples=["TRK123456789"],
    )
    carrier: Optional[str] = Field(
        None,
        max_length=100,
        description="Logistics carrier or shipping vendor name.",
        examples=["DHL Express"],
    )
    expected_date: Optional[date] = Field(
        None,
        description="Expected delivery date.",
    )
    remarks: Optional[str] = Field(
        None,
        max_length=300,
        description="Additional shipment notes or delivery instructions.",
    )


class DeliveryTrackingCreate(DeliveryTrackingBase):
    """
    Schema for creating a new DeliveryTracking record (Client Input only).

    Server-managed fields EXCLUDED:
    - delivery_id (Database-generated UUID PK)
    - delivery_status (Server-managed: defaults to 'not_dispatched')
    - dispatch_date (Server-managed: set upon dispatch workflow action)
    - delivered_date (Server-managed: set upon delivery workflow action)
    - created_at (Database-managed timestamp)
    """

    pass


class DeliveryTrackingUpdate(BaseModel):
    """
    Schema for updating an existing DeliveryTracking record (Client Input only).
    All fields are optional.

    Status changes are EXCLUDED from this schema and enforced via dedicated workflow actions.
    """

    model_config = ConfigDict(extra="forbid")

    tracking_number: Optional[str] = Field(
        None,
        max_length=80,
        description="Updated tracking number.",
    )
    carrier: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated carrier name.",
    )
    expected_date: Optional[date] = Field(
        None,
        description="Updated expected delivery date.",
    )
    remarks: Optional[str] = Field(
        None,
        max_length=300,
        description="Updated remarks or delivery notes.",
    )


class DeliveryTrackingResponse(BaseModel):
    """
    Response schema representing complete DeliveryTracking entity.
    Exposes server-managed, DB-managed, derived, and relationship fields.

    Inherits from BaseModel (not DeliveryTrackingBase) to avoid leaking input-only
    validations into response serialization.
    """

    delivery_id: UUID
    po_id: UUID
    po_number: Optional[str] = None
    vendor_name: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    dispatch_date: Optional[date] = None
    expected_date: Optional[date] = None
    delivered_date: Optional[date] = None
    delivery_status: DeliveryStatusEnum
    remarks: Optional[str] = None
    created_at: datetime
    is_delivered: bool

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_relations_and_derived_fields(cls, data: Any) -> Any:
        """
        Safely extract po_number, vendor_name, and compute derived is_delivered flag
        when deserializing from an ORM DeliveryTracking model instance or dict.
        """
        if hasattr(data, "delivery_id") and hasattr(data, "po_id"):
            po_number = None
            vendor_name = None

            if hasattr(data, "purchase_order") and data.purchase_order is not None:
                if hasattr(data.purchase_order, "po_number"):
                    po_number = data.purchase_order.po_number

                if hasattr(data.purchase_order, "vendor") and data.purchase_order.vendor is not None:
                    if hasattr(data.purchase_order.vendor, "company_name"):
                        vendor_name = data.purchase_order.vendor.company_name

            status_val = getattr(data, "delivery_status", None)
            is_delivered = (status_val == DeliveryStatusEnum.DELIVERED or status_val == "delivered")

            result = {
                "delivery_id": data.delivery_id,
                "po_id": data.po_id,
                "po_number": po_number,
                "vendor_name": vendor_name,
                "tracking_number": data.tracking_number,
                "carrier": data.carrier,
                "dispatch_date": data.dispatch_date,
                "expected_date": data.expected_date,
                "delivered_date": data.delivered_date,
                "delivery_status": status_val,
                "remarks": data.remarks,
                "created_at": data.created_at,
                "is_delivered": is_delivered,
            }
            return result
        elif isinstance(data, dict):
            if "is_delivered" not in data:
                st = data.get("delivery_status")
                data["is_delivered"] = (st == DeliveryStatusEnum.DELIVERED or st == "delivered")
        return data
