from typing import List, Optional
from uuid import UUID

from psycopg import AsyncConnection

from app.models.order import (
    CouponResponse,
    OrderDetail,
    OrderItemResponse,
    OrderResponse,
    PaymentResponse,
)
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[OrderResponse]):
    """Repository for order-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "orders"

    async def create_order(self, data: dict) -> OrderResponse:
        """Insert new order."""
        return await self._create(self.table, data, OrderResponse)

    async def create_order_item(self, data: dict) -> OrderItemResponse:
        """
        Insert polymorphic order item.

        Must have exactly ONE of: booking_id, product_id, or gift_card_id.
        Database constraint enforces this.
        """
        item_data = {
            "order_id": data["order_id"],
            "booking_id": data.get("booking_id"),
            "product_id": data.get("product_id"),
            "gift_card_id": data.get("gift_card_id"),
            "quantity": data["quantity"],
            "unit_price": data["unit_price"],
        }
        return await self._create("order_items", item_data, OrderItemResponse)

    async def get_order_by_id(self, order_id: UUID) -> Optional[OrderDetail]:
        """Get order with all items."""
        # Get order
        order_query = """
            SELECT id, customer_id, location_id, coupon_id, total_amount, 
                   currency, status, receipt_number, receipt_url, created_at
            FROM orders
            WHERE id = %s
        """
        order = await self._execute_one(order_query, (order_id,), OrderResponse)

        if not order:
            return None

        # Get order items
        items_query = """
            SELECT id, order_id, booking_id, product_id, gift_card_id, quantity, unit_price
            FROM order_items
            WHERE order_id = %s
        """
        items = await self._execute_many(items_query, (order_id,), OrderItemResponse)

        # Combine into OrderDetail
        return OrderDetail(**order.model_dump(), items=items)

    async def create_payment(self, data: dict) -> PaymentResponse:
        """Insert payment record."""
        payment_data = {
            "order_id": data["order_id"],
            "amount": data["amount"],
            "currency": data.get("currency", "SEK"),
            "payment_method": data["payment_method"],
            "status": data.get("status", "completed"),
            "transaction_id": data.get("transaction_id"),
            "gift_card_id": data.get("gift_card_id"),
            "clipping_card_id": data.get("clipping_card_id"),
        }
        return await self._create("payments", payment_data, PaymentResponse)

    async def get_order_payments(self, order_id: UUID) -> List[PaymentResponse]:
        """Get all payments for an order."""
        query = """
            SELECT id, order_id, amount, currency, payment_method, status,
                   transaction_id, gift_card_id, clipping_card_id, created_at
            FROM payments
            WHERE order_id = %s
            ORDER BY created_at DESC
        """
        return await self._execute_many(query, (order_id,), PaymentResponse)

    async def get_coupon_by_code(self, code: str) -> Optional[CouponResponse]:
        """Get coupon by code."""
        query = """
            SELECT id, code, discount_type, discount_value, usage_limit, 
                   used_count, valid_until
            FROM coupons
            WHERE code = %s
        """
        return await self._execute_one(query, (code,), CouponResponse)

    async def increment_coupon_usage(self, coupon_id: UUID) -> None:
        """Increment coupon usage count."""
        query = """
            UPDATE coupons
            SET used_count = used_count + 1
            WHERE id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (coupon_id,))

    async def get_user_orders(
        self, customer_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[OrderResponse]:
        """Get all orders for a customer."""
        query = """
            SELECT id, customer_id, location_id, coupon_id, total_amount,
                   currency, status, receipt_number, receipt_url, created_at
            FROM orders
            WHERE customer_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return await self._execute_many(
            query, (customer_id, limit, offset), OrderResponse
        )

    async def get_location_orders(
        self, location_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[OrderResponse]:
        """Get all orders for a location (for providers)."""
        query = """
            SELECT id, customer_id, location_id, coupon_id, total_amount,
                   currency, status, receipt_number, receipt_url, created_at
            FROM orders
            WHERE location_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return await self._execute_many(
            query, (location_id, limit, offset), OrderResponse
        )
