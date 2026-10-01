"""
Pydantic v2 Schemas for User Settings.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserSettingsResponse(BaseModel):
    company_name: Optional[str] = "Enterprise Vendor Reliability Corp"
    company_email: Optional[str] = "admin@vendorplatform.com"
    company_phone: Optional[str] = "+91 9876543210"
    company_address: Optional[str] = "Hyderabad, Telangana"
    email_notifications: bool = True
    sms_notifications: bool = False
    vendor_alerts: bool = True
    contract_alerts: bool = True
    security_2fa: bool = False
    language: Optional[str] = "English"
    theme: Optional[str] = "light"
    timezone: Optional[str] = "Asia/Kolkata"
    preferred_currency: Optional[str] = "INR"

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class UserSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    vendor_alerts: Optional[bool] = None
    contract_alerts: Optional[bool] = None
    security_2fa: Optional[bool] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    preferred_currency: Optional[str] = None

    model_config = ConfigDict(extra="ignore")
