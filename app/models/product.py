from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product fields."""

    name: str = Field(min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    price: Decimal = Field(gt=0, decimal_places=2)


class ProductCreate(ProductBase):
    """Product creation request."""

    location_id: UUID
    stock_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    """Product update request (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class ProductResponse(ProductBase):
    """Product response."""

    id: UUID
    location_id: UUID
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)


class InventoryAdjustment(BaseModel):
    """Inventory adjustment request."""

    change_amount: int = Field(description="Positive for restock, negative for sale")
    reason: Optional[str] = Field(
        None,
        max_length=50,
        description="Reason for adjustment (e.g., 'sale', 'restock', 'damage')",
    )


class InventoryLogResponse(BaseModel):
    """Inventory log entry."""

    id: UUID
    product_id: UUID
    change_amount: int
    reason: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
