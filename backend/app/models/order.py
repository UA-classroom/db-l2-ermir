from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.core.enums import DiscountTypeEnum, PaymentMethodEnum


class OrderItemCreate(BaseModel):
    """Single cart item (polymorphic: booking OR product OR gift_card)."""

    booking_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    gift_card_id: Optional[UUID] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(gt=0, decimal_places=2)

    @model_validator(mode="after")
    def check_exactly_one_type(self):
        """Ensure exactly one of booking_id, product_id, or gift_card_id is set."""
        count = sum(
            [
                self.booking_id is not None,
                self.product_id is not None,
                self.gift_card_id is not None,
            ]
        )
        if count != 1:
            raise ValueError(
                "Exactly one of booking_id, product_id, or gift_card_id must be provided"
            )
        return self


class OrderCreate(BaseModel):
    """Order creation request."""

    customer_id: UUID
    location_id: UUID
    coupon_code: Optional[str] = None
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    """Order item response."""

    id: UUID
    order_id: UUID
    booking_id: Optional[UUID]
    product_id: Optional[UUID]
    gift_card_id: Optional[UUID]
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Basic order response."""

    id: UUID
    customer_id: UUID
    location_id: UUID
    coupon_id: Optional[UUID]
    total_amount: Decimal
    currency: str
    status: str
    receipt_number: Optional[str]
    receipt_url: Optional[str]
    created_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetail(OrderResponse):
    """Order with nested items."""

    items: List[OrderItemResponse]


class PaymentCreate(BaseModel):
    """Payment creation request."""

    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_method: PaymentMethodEnum
    transaction_id: Optional[str] = None
    gift_card_id: Optional[UUID] = None
    clipping_card_id: Optional[UUID] = None


class PaymentResponse(BaseModel):
    """Payment response."""

    id: UUID
    order_id: UUID
    amount: Decimal
    currency: str
    payment_method: str
    status: str
    transaction_id: Optional[str]
    gift_card_id: Optional[UUID]
    clipping_card_id: Optional[UUID]
    created_at: AwareDatetime


    model_config = ConfigDict(from_attributes=True)


class CouponValidationRequest(BaseModel):
    """Coupon validation request."""

    code: str = Field(min_length=1, max_length=50)


class CouponValidationResponse(BaseModel):
    """Coupon validation response."""

    is_valid: bool
    discount_type: Optional[DiscountTypeEnum] = None
    discount_value: Optional[Decimal] = None
    reason: Optional[str] = (
        None  # If invalid: "expired", "usage_limit_reached", "not_found"
    )


class CouponResponse(BaseModel):
    """Coupon response."""

    id: UUID
    code: str
    discount_type: str
    discount_value: Decimal
    usage_limit: Optional[int]
    used_count: int
    valid_until: Optional[AwareDatetime]

    model_config = ConfigDict(from_attributes=True)


class ReceiptItemResponse(BaseModel):
    """Receipt item with calculated total."""

    id: UUID
    booking_id: Optional[UUID]
    product_id: Optional[UUID]
    gift_card_id: Optional[UUID]
    quantity: int
    unit_price: Decimal
    total: Decimal


class ReceiptResponse(BaseModel):
    """Order receipt response."""

    receipt_number: str
    order_id: UUID
    created_at: AwareDatetime
    customer_id: UUID
    location_id: UUID
    items: List[ReceiptItemResponse]
    total_amount: Decimal
    currency: str
    status: str
