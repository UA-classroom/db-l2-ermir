"""Seed products table with test data."""

import asyncio
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_products(conn: AsyncConnection) -> None:
    """Insert test products for locations."""

    # 1. Get Locations for specific businesses to assign relevant products
    # We want to find location IDs for:
    # - Nikita Hair Salon (Hair products)
    # - Fitzone Gym (Gym supplements/gear)
    # - Bergström Spa (Spa products)

    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT l.id, b.slug 
            FROM locations l
            JOIN businesses b ON l.business_id = b.id
            WHERE b.slug IN ('nikita-hair-salon', 'fitzone-gym', 'bergstrom-spa-wellness')
        """)
        rows = await cur.fetchall()

        # Map slug -> list of location_ids (in case multiple locations)
        locations_map = {}
        for loc_id, slug in rows:
            if slug not in locations_map:
                locations_map[slug] = []
            locations_map[slug].append(loc_id)

    # 2. Define Products
    products_data = []

    # Helper to add products to all locations of a business
    def add_products(slug, items):
        loc_ids = locations_map.get(slug, [])
        for loc_id in loc_ids:
            for item in items:
                products_data.append({"location_id": loc_id, **item})

    # Hair Salon Products
    add_products(
        "nikita-hair-salon",
        [
            {
                "name": "Premium Shampoo",
                "sku": "HAIR-SHAM-001",
                "price": Decimal("250.00"),
                "stock_quantity": 50,
            },
            {
                "name": "Conditioner",
                "sku": "HAIR-COND-001",
                "price": Decimal("250.00"),
                "stock_quantity": 45,
            },
            {
                "name": "Hair Wax",
                "sku": "HAIR-WAX-001",
                "price": Decimal("180.00"),
                "stock_quantity": 30,
            },
            {
                "name": "Hair Spray",
                "sku": "HAIR-SPR-001",
                "price": Decimal("150.00"),
                "stock_quantity": 40,
            },
            {
                "name": "Beard Oil",
                "sku": "HAIR-OIL-001",
                "price": Decimal("220.00"),
                "stock_quantity": 20,
            },
        ],
    )

    # Gym Products
    add_products(
        "fitzone-gym",
        [
            {
                "name": "Whey Protein (1kg)",
                "sku": "GYM-WHEY-001",
                "price": Decimal("350.00"),
                "stock_quantity": 100,
            },
            {
                "name": "BCAA Powder",
                "sku": "GYM-BCAA-001",
                "price": Decimal("250.00"),
                "stock_quantity": 60,
            },
            {
                "name": "Yoga Mat",
                "sku": "GYM-MAT-001",
                "price": Decimal("400.00"),
                "stock_quantity": 25,
            },
            {
                "name": "Shaker Bottle",
                "sku": "GYM-SHAK-001",
                "price": Decimal("80.00"),
                "stock_quantity": 150,
            },
            {
                "name": "Resistance Bands",
                "sku": "GYM-BAND-001",
                "price": Decimal("150.00"),
                "stock_quantity": 50,
            },
        ],
    )

    # Spa Products
    add_products(
        "bergstrom-spa-wellness",
        [
            {
                "name": "Facial Cream",
                "sku": "SPA-CRM-001",
                "price": Decimal("450.00"),
                "stock_quantity": 30,
            },
            {
                "name": "Body Scrub",
                "sku": "SPA-SCR-001",
                "price": Decimal("350.00"),
                "stock_quantity": 40,
            },
            {
                "name": "Essential Oil Lavender",
                "sku": "SPA-OIL-LAV",
                "price": Decimal("180.00"),
                "stock_quantity": 80,
            },
            {
                "name": "Scented Candle",
                "sku": "SPA-CNDL-001",
                "price": Decimal("220.00"),
                "stock_quantity": 60,
            },
            {
                "name": "Bath Robe",
                "sku": "SPA-ROBE-001",
                "price": Decimal("800.00"),
                "stock_quantity": 15,
            },
        ],
    )

    # 3. Insert into Database
    product_count = 0
    async with conn.cursor() as cur:
        for p in products_data:
            await cur.execute(
                """
                INSERT INTO products (location_id, name, sku, price, stock_quantity)
                VALUES (%(location_id)s, %(name)s, %(sku)s, %(price)s, %(stock_quantity)s)
            """,
                p,
            )
            product_count += 1

    await conn.commit()
    print(f"✓ Seeded {product_count} products")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_products(conn)
        await db.disconnect()

    asyncio.run(main())
