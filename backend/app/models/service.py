"""
Service Models Module

Pydantic models for service-related data validation and serialization.

This module includes models for:
- Categories: Service categories (e.g., "Hair", "Nails", "Spa")
- Services: Core services offered by businesses
- Service Variants: Different variations of a service (e.g., "Long Hair", "Short Hair")

Key Features:
- ServiceDetail includes nested variants to avoid N+1 queries
- Use this model when you need services WITH their variants in one query
- All update models use optional fields for partial updates
- Maintains separation between create, update, and response models
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base category fields."""

    name: str = Field(min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Category creation model for POST /categories."""

    pass


class CategoryResponse(CategoryBase):
    """Category response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceBase(BaseModel):
    """Base service fields."""

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    """Service creation model for POST /services."""

    business_id: UUID
    category_id: Optional[int] = None


class ServiceUpdate(BaseModel):
    """Service update model for PUT /services/{id}."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    """Service response."""

    id: UUID
    business_id: UUID
    category_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceVariantBase(BaseModel):
    """Base service variant fields."""

    name: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(ge=0, decimal_places=2)
    duration_minutes: int = Field(gt=0)


class ServiceVariantCreate(ServiceVariantBase):
    """Service variant creation model for POST /service-variants."""

    service_id: UUID


class ServiceVariantUpdate(BaseModel):
    """Service variant update model for PUT /service-variants/{id}."""

    name: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    duration_minutes: Optional[int] = Field(None, gt=0)


class ServiceVariantResponse(ServiceVariantBase):
    """Service variant response."""

    id: UUID
    service_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ServiceDetail(ServiceResponse):
    """Service with nested variants."""

    variants: list[ServiceVariantResponse] = []