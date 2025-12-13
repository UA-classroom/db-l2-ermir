"""Seed coupons table with test data."""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_coupons(conn: AsyncConnection) -> None:
    """Insert test coupons (active, expired, and usage-limited)."""

    # Calculate dates
    today = datetime.now()
    past_date = today - timedelta(days=30)
    future_near = today + timedelta(days=30)
    future_far = today + timedelta(days=90)

    coupons = [
        # ===== ACTIVE COUPONS =====
        {
            "code": "WELCOME10",
            "discount_type": "percent",
            "discount_value": Decimal("10.00"),
            "usage_limit": 100,
            "used_count": 15,
            "valid_until": future_far
        },
        {
            "code": "FIRST50",
            "discount_type": "fixed",
            "discount_value": Decimal("50.00"),
            "usage_limit": 50,
            "used_count": 8,
            "valid_until": future_far
        },
        {
            "code": "NEWYEAR2025",
            "discount_type": "percent",
            "discount_value": Decimal("20.00"),
            "usage_limit": 200,
            "used_count": 45,
            "valid_until": future_near
        },
        {
            "code": "STUDENT15",
            "discount_type": "percent",
            "discount_value": Decimal("15.00"),
            "usage_limit": None,  # Unlimited
            "used_count": 120,
            "valid_until": None  # No expiration
        },
        {
            "code": "HAIR100",
            "discount_type": "fixed",
            "discount_value": Decimal("100.00"),
            "usage_limit": 30,
            "used_count": 5,
            "valid_until": future_near
        },
        {
            "code": "SPA20",
            "discount_type": "percent",
            "discount_value": Decimal("20.00"),
            "usage_limit": 50,
            "used_count": 12,
            "valid_until": future_far
        },
        {
            "code": "GYM25",
            "discount_type": "percent",
            "discount_value": Decimal("25.00"),
            "usage_limit": 40,
            "used_count": 7,
            "valid_until": future_near
        },
        {
            "code": "DINNER200",
            "discount_type": "fixed",
            "discount_value": Decimal("200.00"),
            "usage_limit": 20,
            "used_count": 3,
            "valid_until": future_far
        },
        {
            "code": "LOYALTY30",
            "discount_type": "percent",
            "discount_value": Decimal("30.00"),
            "usage_limit": 10,
            "used_count": 2,
            "valid_until": future_far
        },
        {
            "code": "REFERRAL150",
            "discount_type": "fixed",
            "discount_value": Decimal("150.00"),
            "usage_limit": 100,
            "used_count": 18,
            "valid_until": None  # No expiration
        },

        # ===== EXPIRED COUPONS =====
        {
            "code": "SUMMER2024",
            "discount_type": "percent",
            "discount_value": Decimal("25.00"),
            "usage_limit": 150,
            "used_count": 89,
            "valid_until": past_date
        },
        {
            "code": "XMAS2024",
            "discount_type": "fixed",
            "discount_value": Decimal("300.00"),
            "usage_limit": 50,
            "used_count": 42,
            "valid_until": past_date
        },

        # ===== USAGE LIMIT REACHED =====
        {
            "code": "FLASH50",
            "discount_type": "percent",
            "discount_value": Decimal("50.00"),
            "usage_limit": 10,
            "used_count": 10,  # Fully used
            "valid_until": future_near
        },
        {
            "code": "SPECIAL100",
            "discount_type": "fixed",
            "discount_value": Decimal("100.00"),
            "usage_limit": 5,
            "used_count": 5,  # Fully used
            "valid_until": future_far
        },

        # ===== NEARLY EXPIRED (Within 7 days) =====
        {
            "code": "LASTCHANCE",
            "discount_type": "percent",
            "discount_value": Decimal("35.00"),
            "usage_limit": 30,
            "used_count": 8,
            "valid_until": today + timedelta(days=7)
        },

        # ===== VIP COUPONS (High value) =====
        {
            "code": "VIP500",
            "discount_type": "fixed",
            "discount_value": Decimal("500.00"),
            "usage_limit": 5,
            "used_count": 1,
            "valid_until": future_far
        },
        {
            "code": "PLATINUM40",
            "discount_type": "percent",
            "discount_value": Decimal("40.00"),
            "usage_limit": 15,
            "used_count": 3,
            "valid_until": future_far
        }
    ]

    async with conn.cursor() as cur:
        for coupon in coupons:
            await cur.execute(
                """
                INSERT INTO coupons (code, discount_type, discount_value, usage_limit, used_count, valid_until)
                VALUES (%(code)s, %(discount_type)s, %(discount_value)s, %(usage_limit)s, %(used_count)s, %(valid_until)s)
                ON CONFLICT (code) DO NOTHING
                """,
                coupon
            )

    await conn.commit()
    print(f"✓ Seeded {len(coupons)} coupons")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_coupons(conn)
        await db.disconnect()

    asyncio.run(main())