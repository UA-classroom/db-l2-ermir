from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.core.enums import DiscountTypeEnum
from app.core.exceptions import ConflictError, NotFoundError
from app.models.order import (
    CouponValidationResponse,
    OrderCreate,
    OrderDetail,
    PaymentCreate,
    PaymentResponse,
    ReceiptItemResponse,
    ReceiptResponse,
)
from app.repositories.order_repository import OrderRepository


class PaymentService:
    """Service for order and payment-related business logic."""

    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def validate_coupon(self, code: str) -> CouponValidationResponse:
        """
        Validate coupon code.

        Checks:
        1. Coupon exists
        2. Not expired
        3. Usage limit not reached
        """
        coupon = await self.order_repo.get_coupon_by_code(code)

        if not coupon:
            return CouponValidationResponse(is_valid=False, reason="not_found")

        # Check expiration
        if coupon.valid_until:
            if datetime.now(timezone.utc) > coupon.valid_until:
                return CouponValidationResponse(is_valid=False, reason="expired")

        # Check usage limit
        if coupon.usage_limit is not None:
            if coupon.used_count >= coupon.usage_limit:
                return CouponValidationResponse(
                    is_valid=False, reason="usage_limit_reached"
                )

        return CouponValidationResponse(
            is_valid=True,
            discount_type=DiscountTypeEnum(coupon.discount_type),
            discount_value=coupon.discount_value,
        )

    def calculate_order_total(
        self,
        items_total: Decimal,
        discount_type: Optional[DiscountTypeEnum],
        discount_value: Optional[Decimal],
    ) -> Decimal:
        """
        Calculate final order total with coupon discount.

        Args:
            items_total: Sum of all item prices
            discount_type: 'percent' or 'fixed'
            discount_value: Discount amount
        """
        if not discount_type or not discount_value:
            return items_total

        if discount_type == DiscountTypeEnum.PERCENT:
            discount_amount = items_total * (discount_value / Decimal("100"))
            return max(Decimal("0"), items_total - discount_amount)
        elif discount_type == DiscountTypeEnum.FIXED:
            return max(Decimal("0"), items_total - discount_value)

        return items_total

    async def create_order(self, order_data: OrderCreate) -> OrderDetail:
        """
        Orchestrate order creation with transaction.

        Steps:
        1. Validate coupon if provided
        2. Calculate items total
        3. Apply discount
        4. Create order + order_items atomically
        5. Increment coupon usage
        """
        coupon_id = None
        discount_type = None
        discount_value = None

        # Step 1: Validate coupon if provided
        if order_data.coupon_code:
            validation = await self.validate_coupon(order_data.coupon_code)
            if not validation.is_valid:
                raise ConflictError(f"Invalid coupon: {validation.reason}")

            coupon = await self.order_repo.get_coupon_by_code(order_data.coupon_code)
            if not coupon:
                raise ConflictError(f"Coupon {order_data.coupon_code} not found")
            coupon_id = coupon.id
            discount_type = validation.discount_type
            discount_value = validation.discount_value

        # Step 2: Calculate items total
        items_total = Decimal(
            sum(item.unit_price * item.quantity for item in order_data.items)
        )

        # Step 3: Apply discount
        total_amount = self.calculate_order_total(
            items_total, discount_type, discount_value
        )

        # Step 4: Create order + order_items in transaction
        async with self.order_repo.conn.transaction():
            # Create order
            order_dict = {
                "customer_id": order_data.customer_id,
                "location_id": order_data.location_id,
                "coupon_id": coupon_id,
                "total_amount": total_amount,
                "currency": "SEK",
                "status": "pending",
            }
            created_order = await self.order_repo.create_order(order_dict)

            # Create order items
            items = []
            for item_data in order_data.items:
                item_dict = {
                    "order_id": created_order.id,
                    "booking_id": item_data.booking_id,
                    "product_id": item_data.product_id,
                    "gift_card_id": item_data.gift_card_id,
                    "quantity": item_data.quantity,
                    "unit_price": item_data.unit_price,
                }
                created_item = await self.order_repo.create_order_item(item_dict)
                items.append(created_item)

            # Step 5: Increment coupon usage
            if coupon_id:
                await self.order_repo.increment_coupon_usage(coupon_id)

        # Return order with items
        return OrderDetail(
            id=created_order.id,
            customer_id=created_order.customer_id,
            location_id=created_order.location_id,
            coupon_id=created_order.coupon_id,
            total_amount=created_order.total_amount,
            currency=created_order.currency,
            status=created_order.status,
            receipt_number=created_order.receipt_number,
            receipt_url=created_order.receipt_url,
            created_at=created_order.created_at,
            items=items,
        )

    async def process_payment(
        self, order_id: UUID, payment_data: PaymentCreate
    ) -> PaymentResponse:
        """
        Process payment for an order.

        Steps:
        1. Validate order exists
        2. Create payment record
        3. Update order status to 'paid'
        """
        # Step 1: Validate order exists
        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order {order_id} not found")
        
        # Check if already paid
        if order.status == "paid":
            raise ConflictError(f"Order {order_id} is already paid")
        
        # Validate payment amount matches order total
        if payment_data.amount != order.total_amount:
            raise ConflictError(
                f"Payment amount {payment_data.amount} does not match order total {order.total_amount}"
            )

        # Step 2 & 3: Create payment and update order in transaction
        async with self.order_repo.conn.transaction():
            # Create payment
            payment_dict = {
                "order_id": order_id,
                "amount": payment_data.amount,
                "currency": "SEK",
                "payment_method": payment_data.payment_method.value,
                "status": "completed",
                "transaction_id": payment_data.transaction_id,
                "gift_card_id": payment_data.gift_card_id,
                "clipping_card_id": payment_data.clipping_card_id,
            }
            payment = await self.order_repo.create_payment(payment_dict)

            # Update order status
            async with self.order_repo.conn.cursor() as cur:
                await cur.execute(
                    "UPDATE orders SET status = 'paid' WHERE id = %s", (order_id,)
                )

        return payment

    async def get_order_receipt(self, order_id: UUID) -> ReceiptResponse:
        """
        Get order formatted as receipt.

        Handles receipt number generation and item total calculations.
        """
        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order {order_id} not found")

        # Format items with calculated totals
        receipt_items = [
            ReceiptItemResponse(
                id=item.id,
                booking_id=item.booking_id,
                product_id=item.product_id,
                gift_card_id=item.gift_card_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=item.unit_price * item.quantity,
            )
            for item in order.items
        ]

        # Generate receipt number if not exists
        receipt_number = order.receipt_number or f"ORD-{str(order.id)[:8].upper()}"

        return ReceiptResponse(
            receipt_number=receipt_number,
            order_id=order.id,
            created_at=order.created_at,
            customer_id=order.customer_id,
            location_id=order.location_id,
            items=receipt_items,
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status,
        )
