"""Seed orders, order_items, and payments tables with test data."""

import asyncio
import random
from decimal import Decimal
from datetime import datetime, timedelta
from psycopg import AsyncConnection


async def seed_orders(conn: AsyncConnection) -> None:
    """Insert test orders with items and payments."""

    # 1. Get completed bookings (for Service Orders)
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
                "created_at": created_at,
            }
            for booking_id, customer_id, location_id, total_price, created_at in booking_rows
        ]

    # 2. Get Products (for Product Orders)
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT p.id, p.location_id, p.price, p.name 
            FROM products p
            LIMIT 50
        """)
        product_rows = await cur.fetchall()
        products = [
            {"id": pid, "location_id": lid, "price": price, "name": name}
            for pid, lid, price, name in product_rows
        ]

    # 3. Get Coupons
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
                "discount_value": discount_value,
            }
            for coupon_id, code, discount_type, discount_value in coupon_rows
        ]

    # Helper function to apply coupon discount
    def apply_discount(total, discount_type, discount_value):
        if discount_type == "percent":
            discount_amount = total * (discount_value / Decimal("100"))
            return max(Decimal("0"), total - discount_amount)
        elif discount_type == "fixed":
            return max(Decimal("0"), total - discount_value)
        return total

    orders_data = []
    order_items_data = []  # Store items to insert later

    # --- Generate Booking Orders ---
    coupon_index = 0
    unique_customers = list(set(b["customer_id"] for b in bookings))

    for i, booking in enumerate(bookings):
        # ... (Same logic as before)
        use_coupon = (i % 3 == 0) and coupon_index < len(coupons)
        coupon = coupons[coupon_index] if use_coupon else None

        items_total = booking["total_price"]
        total_amount = (
            apply_discount(
                items_total, coupon["discount_type"], coupon["discount_value"]
            )
            if coupon
            else items_total
        )
        coupon_id = coupon["id"] if coupon else None
        if coupon:
            coupon_index += 1

        is_paid = i % 5 != 0
        status = "paid" if is_paid else "pending"
        payment_methods = ["card", "klarna", "swish"]
        payment_method = payment_methods[i % len(payment_methods)]

        order = {
            "customer_id": booking["customer_id"],
            "location_id": booking["location_id"],
            "coupon_id": coupon_id,
            "total_amount": total_amount,
            "currency": "SEK",
            "status": status,
            "receipt_number": f"REC-{booking['created_at'].strftime('%Y%m%d')}-{i + 1:04d}",
            "booking_id": booking["id"],  # For reference
            "payment_method": payment_method if is_paid else None,
            "is_paid": is_paid,
            "items": [
                {
                    "booking_id": booking["id"],
                    "product_id": None,
                    "quantity": 1,
                    "unit_price": booking["total_price"],
                }
            ],
        }
        orders_data.append(order)

    # --- Generate Product Orders (New) ---
    if products and unique_customers:
        # Create 10 product orders
        for j in range(10):
            # Pick a random customer
            customer_id = random.choice(unique_customers)

            # Pick a random product to define location (orders are per location)
            base_product = random.choice(products)
            location_id = base_product["location_id"]

            # Filter products available at this location
            loc_products = [p for p in products if p["location_id"] == location_id]

            # Pick 1-3 items
            num_items = random.randint(1, 3)
            selected_items = random.sample(
                loc_products, min(num_items, len(loc_products))
            )

            # Calculate total
            items_total = sum(p["price"] for p in selected_items)

            # No coupons for product orders in this simple seed
            total_amount = items_total

            created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            is_paid = True  # Assume product orders are paid at counter
            status = "paid"
            payment_method = "card"

            order = {
                "customer_id": customer_id,
                "location_id": location_id,
                "coupon_id": None,
                "total_amount": total_amount,
                "currency": "SEK",
                "status": status,
                "receipt_number": f"REC-PROD-{created_at.strftime('%Y%m%d')}-{j + 1:04d}",
                "booking_id": None,
                "payment_method": payment_method,
                "is_paid": True,
                "items": [
                    {
                        "booking_id": None,
                        "product_id": p["id"],
                        "quantity": 1,
                        "unit_price": p["price"],
                    }
                    for p in selected_items
                ],
            }
            orders_data.append(order)

    # --- Insert Orders ---
    order_count = 0
    order_items_count = 0
    payments_count = 0

    async with conn.cursor() as cur:
        for order in orders_data:
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
                    order["customer_id"],
                    order["location_id"],
                    order["coupon_id"],
                    order["total_amount"],
                    order["currency"],
                    order["status"],
                    order["receipt_number"],
                    None,
                ),
            )
            result = await cur.fetchone()
            if not result:
                continue

            order_id = result[0]
            order_count += 1

            # Insert Items
            for item in order["items"]:
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
                        item["booking_id"],
                        item["product_id"],
                        None,
                        item["quantity"],
                        item["unit_price"],
                    ),
                )
                order_items_count += 1

            # Insert Payment
            if order["is_paid"]:
                await cur.execute(
                    """
                    INSERT INTO payments (
                        order_id, amount, currency, payment_method,
                        status, transaction_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        order["total_amount"],
                        order["currency"],
                        order["payment_method"],
                        "completed",
                        f"TXN-{order_id}",
                    ),
                )
                payments_count += 1

            # Update Coupons (only for booking orders that used them)
            if order["coupon_id"]:
                await cur.execute(
                    "UPDATE coupons SET used_count = used_count + 1 WHERE id = %s",
                    (order["coupon_id"],),
                )

    await conn.commit()
    print(f"✓ Seeded {order_count} orders (Bookings & Products)")
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
