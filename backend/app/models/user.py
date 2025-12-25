"""
User Models Module

Pydantic models for user-related data validation and serialization.
"""
import re
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, EmailStr, Field, field_validator
from pydantic.config import ConfigDict

from app.core.enums import RoleEnum


class UserBase(BaseModel):
    """Base user fields shared across all user operations."""

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    mobile_number: str = Field(min_length=1, max_length=20)

class UserCreate(UserBase):
    """User registration request with password and role."""

    password: str = Field(min_length=8, max_length=100)
    role: RoleEnum = RoleEnum.CUSTOMER


class UserUpdate(BaseModel):
    """User profile update request (all fields optional for partial updates)."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    mobile_number: Optional[str] = Field(None, min_length=1, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @field_validator("mobile_number")
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (international format required)."""
        if v is None:
            return v
        #This rejects valid formats like: (555) 123-4567, 555-123-4567, etc.
        #May cause UX issues for users
        if not re.match(r"^\+\d{10,15}$", v): # TODO:Consider more flexible phone validation or make it configurable AND Add email validation in UserUpdate (currently missing)
            raise ValueError(
                "Phone number must be in international format: +XXXXXXXXXXX"
            )
        return v
    
    
class UserDB(UserBase):
    """User database model with all fields including password_hash (internal use only)."""

    id: UUID
    role: Optional[RoleEnum] = None
    password_hash: str
    is_active: bool
    created_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User response model for API responses (excludes sensitive fields)."""

    id: UUID
    role: Optional[RoleEnum] = None
    is_active: bool
    created_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Token data model for storing token-related information."""

    user_id: UUID 
    role: Optional[RoleEnum] = None     
    email: Optional[str] = None


class AddressCreate(BaseModel):
    """User address creation request."""

    street_address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    type: Optional[str] = Field(None, max_length=20)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class AddressUpdate(BaseModel):
    """User address update request (all fields optional)."""

    street_address: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    type: Optional[str] = Field(None, max_length=20)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class AddressResponse(AddressCreate):
    """User address response model."""

    id: UUID
    user_id: UUID  
