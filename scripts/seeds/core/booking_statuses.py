"""Seed booking_statuses table with predefined statuses."""
import asyncio
from psycopg import AsyncConnection


async def seed_booking_statuses(conn: AsyncConnection) -> None:
    """Insert booking statuses."""

    statuses = [
        {
            "name": "pending",
            "color_code": "#FFA500",  # Orange
            "is_cancellable": True
        },
        {
            "name": "confirmed",
            "color_code": "#4CAF50",  # Green
            "is_cancellable": True
        },
        {
            "name": "completed",
            "color_code": "#2196F3",  # Blue
            "is_cancellable": False
        },
        {
            "name": "cancelled",
            "color_code": "#F44336",  # Red
            "is_cancellable": False
        },
        {
            "name": "no_show",
            "color_code": "#9E9E9E",  # Grey
            "is_cancellable": False
        }
    ]

    async with conn.cursor() as cur:
        for status in statuses:
            await cur.execute(
                """
                INSERT INTO booking_statuses (name, color_code, is_cancellable)
                VALUES (%(name)s, %(color_code)s, %(is_cancellable)s)
                ON CONFLICT (name) DO NOTHING
                """,
                status
            )

    await conn.commit()
    print(f"✓ Seeded {len(statuses)} booking statuses")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_booking_statuses(conn)
        await db.disconnect()

    asyncio.run(main())