"""
Enums Module

Application-wide enumeration types for consistent value validation.
These enums map to database lookup tables and ensure type safety.
"""
from enum import Enum


class RoleEnum(str, Enum):
    """Enumeration of user roles in the system."""

    ADMIN = "admin"
    CUSTOMER = "customer"
    PROVIDER = "provider"
    

class BookingStatusEnum(str, Enum):
    """Booking status values."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

    # TODO: Remove hardcoded mapping - can get out of sync with database
    # Replace with database lookup: SELECT id FROM booking_statuses WHERE name = %s
    # This is currently hardcoded for performance but risks desync if database changes
    def to_status_id(self) -> int:
        """Get database status_id for this enum value."""
        status_map = {
            "pending": 1,
            "confirmed": 2,
            "completed": 3,
            "cancelled": 4,
            "no_show": 5,
        }
        return status_map[self.value]
    

class PaymentStatusEnum(str, Enum):
    """Payment status values."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethodEnum(str, Enum):
    """Payment method values."""

    CARD = "card"
    KLARNA = "klarna"
    SWISH = "swish"
    GIFT_CARD = "gift_card"
    CLIPPING_CARD = "clipping_card"


class DiscountTypeEnum(str, Enum):
    """Discount type for coupons."""

    PERCENT = "percent"
    FIXED = "fixed"
    