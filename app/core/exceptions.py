"""
Domain Exception Definitions for Vendor, User, Procurement, Invoice, Delivery Tracking, and Vendor Performance Modules.
"""


class DomainError(Exception):
    """Base exception class for domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Entity '{identifier}' was not found.")



# ----------------------------------------------------------------------
# Vendor Domain Exceptions
# ----------------------------------------------------------------------

class VendorDomainError(DomainError):
    """Base exception class for Vendor domain errors."""

    pass


class VendorNotFoundError(VendorDomainError):
    """Raised when a requested vendor is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Vendor with ID or code '{identifier}' was not found.")


class VendorAlreadyExistsError(VendorDomainError):
    """Raised when attempting to create/update a vendor with a code that already exists."""

    def __init__(self, vendor_code: str) -> None:
        super().__init__(f"Vendor code '{vendor_code}' already exists.")


class VendorCategoryNotFoundError(VendorDomainError):
    """Raised when the specified category_id does not exist."""

    def __init__(self, category_id: int) -> None:
        super().__init__(f"Vendor category with ID '{category_id}' was not found.")


class InvalidVendorDataError(VendorDomainError):
    """Raised when vendor update or create payload is invalid."""

    pass


# ----------------------------------------------------------------------
# User Domain Exceptions
# ----------------------------------------------------------------------

class UserDomainError(DomainError):
    """Base exception class for User domain errors."""

    pass


class UserNotFoundError(UserDomainError):
    """Raised when a requested user is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"User '{identifier}' was not found.")


class UserAlreadyExistsError(UserDomainError):
    """Raised when attempting to create/update a user with an existing username or email."""

    def __init__(self, field_or_value: str) -> None:
        super().__init__(f"User with username or email '{field_or_value}' already exists.")


class InvalidUserDataError(UserDomainError):
    """Raised when user data validation fails in business logic."""

    pass


# ----------------------------------------------------------------------
# Role Domain Exceptions
# ----------------------------------------------------------------------

class RoleNotFoundError(DomainError):
    """Raised when a requested role_id does not exist in the roles table."""

    def __init__(self, role_id: int) -> None:
        super().__init__(f"Role with ID '{role_id}' was not found.")


# ----------------------------------------------------------------------
# Procurement Domain Exceptions
# ----------------------------------------------------------------------

class ProcurementDomainError(DomainError):
    """Base exception class for Procurement domain errors."""

    pass


class ProcurementRequestNotFoundError(ProcurementDomainError):
    """Raised when a requested procurement request is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Procurement request '{identifier}' was not found.")


class PurchaseOrderNotFoundError(ProcurementDomainError):
    """Raised when a requested purchase order is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Purchase order '{identifier}' was not found.")


class InvalidProcurementDataError(ProcurementDomainError):
    """Raised when procurement business rules or data validation fails."""

    pass


# ----------------------------------------------------------------------
# Invoice Domain Exceptions
# ----------------------------------------------------------------------

class InvoiceDomainError(DomainError):
    """Base exception class for Invoice domain errors."""

    pass


class InvoiceNotFoundError(InvoiceDomainError):
    """Raised when a requested invoice is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Invoice '{identifier}' was not found.")


class InvalidInvoiceDataError(InvoiceDomainError):
    """Raised when invoice business rules or data validation fails."""

    pass


# ----------------------------------------------------------------------
# Delivery Tracking Domain Exceptions
# ----------------------------------------------------------------------

class DeliveryDomainError(DomainError):
    """Base exception class for Delivery Tracking domain errors."""

    pass


class DeliveryNotFoundError(DeliveryDomainError):
    """Raised when a requested delivery tracking record is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Delivery tracking record '{identifier}' was not found.")


class InvalidDeliveryDataError(DeliveryDomainError):
    """Raised when delivery business rules or data validation fails."""

    pass


# ----------------------------------------------------------------------
# Vendor Performance Domain Exceptions
# ----------------------------------------------------------------------

class VendorPerformanceDomainError(DomainError):
    """Base exception class for Vendor Performance domain errors."""

    pass


class VendorRatingNotFoundError(VendorPerformanceDomainError):
    """Raised when a requested vendor rating is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Vendor rating '{identifier}' was not found.")


class VendorIssueNotFoundError(VendorPerformanceDomainError):
    """Raised when a requested vendor issue is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Vendor issue '{identifier}' was not found.")


class InvalidVendorPerformanceDataError(VendorPerformanceDomainError):
    """Raised when vendor performance business rules or data validation fails."""

    pass
