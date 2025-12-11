"""
Business Models Module

Pydantic models for business-related data validation and serialization.

This module includes models for:
- Businesses: Core business entities with owner information
- Locations: Physical locations/branches for businesses
- Contacts: Contact information for locations (phone, type)

Key Features:
- BusinessResponse includes calculated fields (average_rating, review_count, primary_category)
  that are populated via repository JOIN queries, not stored in the database
- All update models use optional fields for partial updates
- Maintains separation between create, update, and response models
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class BusinessBase(BaseModel):
    """Base business fields."""

    name: str = Field(min_length=1, max_length=100)
    org_number: Optional[str] = Field(None, max_length=20)
    slug: str = Field(min_length=1, max_length=100)


class BusinessCreate(BusinessBase):
    """Business creation request."""

    owner_id: UUID


class BusinessUpdate(BaseModel):
    """Business update request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    org_number: Optional[str] = Field(None, max_length=20)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)


class BusinessResponse(BusinessBase):
    """Business response with calculated rating and category fields."""

    id: UUID
    owner_id: UUID
    created_at: AwareDatetime

    # Calculated fields from JOIN queries (not stored in businesses table)
    average_rating: Optional[float] = None  # Average rating from reviews
    review_count: int = 0  # Total number of reviews
    primary_category: Optional[str] = None  # Primary category from services

    model_config = ConfigDict(from_attributes=True)


class LocationBase(BaseModel):
    """Base location fields."""

    name: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=6)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=6)


class LocationCreate(LocationBase):
    """Location creation request."""

    business_id: UUID


class LocationUpdate(BaseModel):
    """Location update request."""

    name: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=6)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=6)


class LocationResponse(LocationBase):
    """Location response."""

    id: UUID
    business_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ContactBase(BaseModel):
    """Base contact fields."""

    contact_type: str = Field(max_length=50)
    phone_number: str = Field(max_length=20)


class ContactCreate(ContactBase):
    """Contact creation request."""

    location_id: UUID


class ContactUpdate(BaseModel):
    """Contact update request."""

    contact_type: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)


class ContactResponse(ContactBase):
    """Contact response."""

    id: UUID
    location_id: UUID

    model_config = ConfigDict(from_attributes=True)


class BusinessDetail(BusinessResponse):
    """Business with nested locations."""

    locations: list[LocationResponse] = []