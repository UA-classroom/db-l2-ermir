"""Seed reviews table with test data for completed bookings."""

import asyncio
import random
from datetime import timedelta
from psycopg import AsyncConnection


async def seed_reviews(conn: AsyncConnection) -> None:
    """Insert test reviews for completed bookings with realistic dates."""

    # Sample review comments for different business types
    # Using customer first names to personalize
    review_templates = {
        "hair": [
            "Fantastiskt resultat! Mycket nöjd med min nya frisyr.",
            "Kommer definitivt tillbaka! Bästa salongen i stan.",
            "Salongen har en fin atmosfär och personalen är trevlig.",
            "Lite lång väntetid men resultatet var värt det.",
            "Perfect haircut! Exactly what I wanted.",
            "Bästa balayage jag någonsin fått. Otroligt professionellt!",
            "Mycket kunnig personal som lyssnar på vad man vill ha.",
            "Rekommenderar varmt! Bra pris för kvaliteten.",
            "Supersnygg klippning och trevlig service.",
            "Fantastisk upplevelse! Min nya favoritsalong.",
            None,  # Some reviews without comment
            None,
        ],
        "restaurant": [
            "Utsökt mat och fantastisk service. Verklig italiensk smak!",
            "Den bästa pastan i stan. 10/10!",
            "Perfekt för romantisk middag. Stämningen var magisk.",
            "Matlagningskursen var jätterolig! Lärde mig massor.",
            "Lite dyrt men kvaliteten är värd det.",
            "Amazing pasta! Will definitely come back.",
            "Great atmosphere and friendly staff.",
            "Private event went perfectly. Thank you!",
            None,
        ],
        "gym": [
            "Fantastisk personlig tränare! Ser redan resultat.",
            "Bra gym med modern utrustning och bra instruktörer.",
            "Yogaklassen var så avslappnande. Rekommenderas!",
            "Intensiv HIIT-träning, precis vad jag behövde.",
            "Spinning är alltid roligt och energigivande.",
            "Best gym in Stockholm! Worth every penny.",
            "Bra gruppklasser och trevlig personal.",
            None,
        ],
        "spa": [
            "Helt underbar massage! Känner mig som en ny människa.",
            "Fantastisk på svenska massage.",
            "Avslappnande miljö och professionell behandling.",
            "Perfekt sätt att stressa av efter en lång vecka.",
            "Best spa experience ever! Highly recommend.",
            "Den bästa massagen jag någonsin haft.",
            None,
        ],
    }

    # Helper to get a random rating (weighted toward good reviews)
    def random_rating():
        weights = [0.02, 0.08, 0.15, 0.35, 0.40]  # More 4s and 5s
        return random.choices([1, 2, 3, 4, 5], weights=weights)[0]

    # Get completed bookings with their business type, customer info, and end time
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT DISTINCT 
                b.id, 
                bus.slug,
                b.end_time,
                u.first_name,
                u.last_name
            FROM bookings b
            JOIN locations l ON b.location_id = l.id
            JOIN businesses bus ON l.business_id = bus.id
            JOIN booking_statuses bs ON b.status_id = bs.id
            JOIN users u ON b.customer_id = u.id
            WHERE bs.name = 'completed'
            AND NOT EXISTS (SELECT 1 FROM reviews r WHERE r.booking_id = b.id)
            ORDER BY b.end_time
        """)
        completed_bookings = await cur.fetchall()

    # Create reviews for completed bookings
    review_count = 0
    async with conn.cursor() as cur:
        for (
            booking_id,
            business_slug,
            end_time,
            first_name,
            last_name,
        ) in completed_bookings:
            # Determine business type for appropriate comments
            if "hair" in business_slug:
                comments = review_templates["hair"]
            elif "restaurant" in business_slug:
                comments = review_templates["restaurant"]
            elif "gym" in business_slug or "fit" in business_slug:
                comments = review_templates["gym"]
            elif "spa" in business_slug or "wellness" in business_slug:
                comments = review_templates["spa"]
            else:
                comments = ["Great service!", "Very satisfied.", None]

            rating = random_rating()
            comment = random.choice(comments)

            # Set created_at to 1-3 days after booking ended
            days_after = random.randint(1, 3)
            hours_offset = random.randint(8, 20)  # Review written during normal hours
            review_date = end_time + timedelta(days=days_after, hours=hours_offset)

            try:
                await cur.execute(
                    """
                    INSERT INTO reviews (booking_id, rating, comment, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (booking_id) DO NOTHING
                    """,
                    (booking_id, rating, comment, review_date),
                )
                review_count += 1
            except Exception as e:
                print(f"Failed to insert review for booking {booking_id}: {e}")

    await conn.commit()
    print(f"✓ Seeded {review_count} reviews")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_reviews(conn)
        await db.disconnect()

    asyncio.run(main())
