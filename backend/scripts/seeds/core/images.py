"""Seed location_images table with Unsplash images for each location."""

import asyncio
from psycopg import AsyncConnection


# Unsplash images by business type
UNSPLASH_IMAGES = {
    "hair-salon": [
        "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80",  # Salon interior
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80",  # Hair styling
        "https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800&q=80",  # Salon chairs
    ],
    "restaurant": [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",  # Restaurant interior
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",  # Fine dining
        "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=800&q=80",  # Italian food
    ],
    "gym": [
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80",  # Gym equipment
        "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800&q=80",  # Modern gym
        "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800&q=80",  # Workout area
    ],
    "spa": [
        "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800&q=80",  # Spa massage
        "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=800&q=80",  # Spa relaxation
        "https://images.unsplash.com/photo-1600334129128-685c5582fd35?w=800&q=80",  # Wellness center
    ],
    "clinic": [
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80",  # Medical clinic
        "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=800&q=80",  # Doctor office
        "https://images.unsplash.com/photo-1666214280557-f1b5022eb634?w=800&q=80",  # Healthcare
    ],
    "auto": [
        "https://images.unsplash.com/photo-1625047509248-ec889cbff17f?w=800&q=80",  # Auto service
        "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?w=800&q=80",  # Car repair
        "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&q=80",  # Mechanic shop
    ],
    "pet": [
        "https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=800&q=80",  # Vet clinic
        "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80",  # Pets
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800&q=80",  # Dog care
    ],
    "home-service": [
        "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80",  # Home cleaning
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",  # Home service
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",  # Maintenance
    ],
}

# Mapping business slug to image type
BUSINESS_IMAGE_MAP = {
    "nikita-hair-salon": "hair-salon",
    "marios-italian-restaurant": "restaurant",
    "fitzone-gym": "gym",
    "bergstrom-spa-wellness": "spa",
    "johansson-medical-clinic": "clinic",
    "lindstrom-auto-service": "auto",
    "petcare-veterinary-clinic": "pet",
    "gustafsson-home-services": "home-service",
}


async def seed_location_images(conn: AsyncConnection) -> None:
    """Insert images for each location based on business type."""

    image_count = 0

    async with conn.cursor() as cur:
        # Get all locations with their business slug
        await cur.execute("""
            SELECT l.id, l.name, b.slug 
            FROM locations l
            JOIN businesses b ON l.business_id = b.id
            WHERE l.deleted_at IS NULL
            ORDER BY b.slug, l.name
        """)
        locations = await cur.fetchall()

        for location_id, location_name, business_slug in locations:
            # Get image type for this business
            image_type = BUSINESS_IMAGE_MAP.get(business_slug)
            if not image_type:
                continue

            images = UNSPLASH_IMAGES.get(image_type, [])

            # Insert images for this location
            for i, url in enumerate(images):
                is_primary = i == 0
                alt_text = f"{location_name} - Image {i + 1}"

                await cur.execute(
                    """
                    INSERT INTO location_images (location_id, url, alt_text, display_order, is_primary)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """,
                    (location_id, url, alt_text, i, is_primary),
                )
                image_count += 1

    await conn.commit()
    print(f"✓ Seeded {image_count} location images")


if __name__ == "__main__":
    import sys
    import selectors
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_location_images(conn)
        await db.disconnect()

    # Windows fix for Psycopg async
    if sys.platform == "win32":
        asyncio.run(
            main(),
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    else:
        asyncio.run(main())
