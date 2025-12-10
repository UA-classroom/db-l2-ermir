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
    