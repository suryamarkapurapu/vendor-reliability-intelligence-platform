"""
Repositories package initialization.
"""

from app.repositories.analytics_repository import (
    AnalyticsRepository,
    analytics_repository,
)
from app.repositories.delivery_repository import (
    DeliveryRepository,
    delivery_repository,
)
from app.repositories.invoice_repository import (
    InvoiceRepository,
    invoice_repository,
)
from app.repositories.procurement_repository import (
    ProcurementRepository,
    procurement_repository,
)
from app.repositories.report_repository import (
    ReportRepository,
    report_repository,
)
from app.repositories.user_repository import UserRepository, user_repository
from app.repositories.vendor_performance_repository import (
    VendorPerformanceRepository,
    vendor_performance_repository,
)
from app.repositories.vendor_repository import VendorRepository, vendor_repository

__all__ = [
    "UserRepository",
    "user_repository",
    "VendorRepository",
    "vendor_repository",
    "ProcurementRepository",
    "procurement_repository",
    "InvoiceRepository",
    "invoice_repository",
    "DeliveryRepository",
    "delivery_repository",
    "VendorPerformanceRepository",
    "vendor_performance_repository",
    "AnalyticsRepository",
    "analytics_repository",
    "ReportRepository",
    "report_repository",
]
