"""Seed orders, order_items, and payments tables with test data."""
import asyncio
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_orders(conn: AsyncConnection) -> None:
    """Insert test orders with items and payments."""

    # Get completed bookings (these will become order items)
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT b.id, b.customer_id, b.location_id, b.total_price, b.created_at
            FROM bookings b
            JOIN booking_statuses bs ON b.status_id = bs.id
            WHERE bs.name = 'completed'
            ORDER BY b.created_at DESC
            LIMIT 40
        """)
        booking_rows = await cur.fetchall()
        bookings = [
            {
                "id": booking_id,
                "customer_id": customer_id,
                "location_id": location_id,
                "total_price": total_price,
                "created_at": created_at
            }
            for booking_id, customer_id, location_id, total_price, created_at in booking_rows
        ]

    # Get some coupon IDs
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT id, code, discount_type, discount_value
            FROM coupons
            WHERE (valid_until IS NULL OR valid_until > NOW())
              AND (usage_limit IS NULL OR used_count < usage_limit)
            ORDER BY code
            LIMIT 10
        """)
        coupon_rows = await cur.fetchall()
        coupons = [
            {
                "id": coupon_id,
                "code": code,
                "discount_type": discount_type,
                "discount_value": discount_value
            }
            for coupon_id, code, discount_type, discount_value in coupon_rows
        ]

    # Helper function to apply coupon discount
    def apply_discount(total, discount_type, discount_value):
        """Calculate discounted total."""
        if discount_type == "percent":
            discount_amount = total * (discount_value / Decimal("100"))
            return max(Decimal("0"), total - discount_amount)
        elif discount_type == "fixed":
            return max(Decimal("0"), total - discount_value)
        return total

    # Create orders from bookings
    orders_data = []
    coupon_index = 0

    for i, booking in enumerate(bookings):
        # Use coupon for ~30% of orders
        use_coupon = (i % 3 == 0) and coupon_index < len(coupons)
        coupon = coupons[coupon_index] if use_coupon else None

        # Calculate total
        items_total = booking["total_price"]
        if coupon:
            total_amount = apply_discount(items_total, coupon["discount_type"], coupon["discount_value"])
            coupon_id = coupon["id"]
            coupon_index += 1
        else:
            total_amount = items_total
            coupon_id = None

        # Determine payment status and method
        # 80% paid, 20% pending
        is_paid = (i % 5 != 0)
        status = "paid" if is_paid else "pending"

        # Payment methods distribution
        payment_methods = ["card", "klarna", "swish"]
        payment_method = payment_methods[i % len(payment_methods)]

        orders_data.append({
            "customer_id": booking["customer_id"],
            "location_id": booking["location_id"],
            "coupon_id": coupon_id,
            "total_amount": total_amount,
            "currency": "SEK",
            "status": status,
            "receipt_number": f"REC-{booking['created_at'].strftime('%Y%m%d')}-{i+1:04d}",
            "receipt_url": None,
            "booking_id": booking["id"],
            "booking_price": booking["total_price"],
            "payment_method": payment_method if is_paid else None,
            "is_paid": is_paid
        })

    order_count = 0
    order_items_count = 0
    payments_count = 0

    async with conn.cursor() as cur:
        for order_data in orders_data:
            # Insert order
            await cur.execute(
                """
                INSERT INTO orders (
                    customer_id, location_id, coupon_id, total_amount,
                    currency, status, receipt_number, receipt_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    order_data["customer_id"],
                    order_data["location_id"],
                    order_data["coupon_id"],
                    order_data["total_amount"],
                    order_data["currency"],
                    order_data["status"],
                    order_data["receipt_number"],
                    order_data["receipt_url"]
                )
            )
            result = await cur.fetchone()
            if not result:
                continue

            order_id = result[0]
            order_count += 1

            # Insert order item (booking)
            await cur.execute(
                """
                INSERT INTO order_items (
                    order_id, booking_id, product_id, gift_card_id,
                    quantity, unit_price
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    order_data["booking_id"],
                    None,  # Not a product
                    None,  # Not a gift card
                    1,
                    order_data["booking_price"]
                )
            )
            order_items_count += 1

            # Insert payment if order is paid
            if order_data["is_paid"]:
                await cur.execute(
                    """
                    INSERT INTO payments (
                        order_id, amount, currency, payment_method,
                        status, transaction_id, gift_card_id, clipping_card_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        order_data["total_amount"],
                        order_data["currency"],
                        order_data["payment_method"],
                        "completed",
                        f"TXN-{order_id}",
                        None,
                        None
                    )
                )
                payments_count += 1

            # Update coupon usage count if used
            if order_data["coupon_id"]:
                await cur.execute(
                    """
                    UPDATE coupons
                    SET used_count = used_count + 1
                    WHERE id = %s
                    """,
                    (order_data["coupon_id"],)
                )

    await conn.commit()
    print(f"✓ Seeded {order_count} orders")
    print(f"✓ Seeded {order_items_count} order items")
    print(f"✓ Seeded {payments_count} payments")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_orders(conn)
        await db.disconnect()

    asyncio.run(main())