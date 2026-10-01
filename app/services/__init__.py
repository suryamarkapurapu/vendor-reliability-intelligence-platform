"""
Services package initialization.
"""

from app.services.analytics_service import AnalyticsService, analytics_service
from app.services.auth_service import AuthService, auth_service
from app.services.delivery_service import DeliveryService, delivery_service
from app.services.invoice_service import InvoiceService, invoice_service
from app.services.procurement_service import (
    ProcurementService,
    procurement_service,
)
from app.services.user_service import UserService, user_service
from app.services.vendor_performance_service import (
    VendorPerformanceService,
    vendor_performance_service,
)
from app.services.report_service import ReportService, report_service
from app.services.vendor_service import VendorService, vendor_service

__all__ = [
    "UserService",
    "user_service",
    "AuthService",
    "auth_service",
    "VendorService",
    "vendor_service",
    "ProcurementService",
    "procurement_service",
    "InvoiceService",
    "invoice_service",
    "DeliveryService",
    "delivery_service",
    "VendorPerformanceService",
    "vendor_performance_service",
    "AnalyticsService",
    "analytics_service",
    "ReportService",
    "report_service",
]
