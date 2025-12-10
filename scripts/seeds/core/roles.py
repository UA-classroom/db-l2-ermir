"""Seed roles table with default roles."""
import asyncio
from psycopg import AsyncConnection


async def seed_roles(conn: AsyncConnection) -> None:
    """Insert default roles into the roles table."""

    roles = ["admin", "customer", "provider"]

    async with conn.cursor() as cur:
        for role_name in roles:
            await cur.execute(
                "INSERT INTO roles (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                (role_name,)
            )

    await conn.commit()
    print(f"✓ Seeded {len(roles)} roles")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_roles(conn)
        await db.disconnect()

    asyncio.run(main())
