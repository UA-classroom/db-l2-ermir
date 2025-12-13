"""Seed users table with test users."""
import asyncio
from psycopg import AsyncConnection

from app.core.security import get_password_hash


async def seed_users(conn: AsyncConnection) -> None:
    """Insert test users into users and user_roles tables."""

    # Password: Password123
    password_hash = get_password_hash("Password123")

    users = [
        # 1 Admin
        {
            "email": "admin@test.com",
            "password_hash": password_hash,
            "first_name": "Admin",
            "last_name": "User",
            "mobile_number": "+46701111111",
            "role": "admin"
        },
        # 8 Providers (one per business)
        {
            "email": "nikita@hairsalon.se",
            "password_hash": password_hash,
            "first_name": "Nikita",
            "last_name": "Andersson",
            "mobile_number": "+46702000001",
            "role": "provider"
        },
        {
            "email": "mario@restaurant.se",
            "password_hash": password_hash,
            "first_name": "Mario",
            "last_name": "Rossi",
            "mobile_number": "+46702000002",
            "role": "provider"
        },
        {
            "email": "erik@gym.se",
            "password_hash": password_hash,
            "first_name": "Erik",
            "last_name": "Karlsson",
            "mobile_number": "+46702000003",
            "role": "provider"
        },
        {
            "email": "sofia@spa.se",
            "password_hash": password_hash,
            "first_name": "Sofia",
            "last_name": "Bergström",
            "mobile_number": "+46702000004",
            "role": "provider"
        },
        {
            "email": "lars@clinic.se",
            "password_hash": password_hash,
            "first_name": "Lars",
            "last_name": "Johansson",
            "mobile_number": "+46702000005",
            "role": "provider"
        },
        {
            "email": "anna@autoservice.se",
            "password_hash": password_hash,
            "first_name": "Anna",
            "last_name": "Lindström",
            "mobile_number": "+46702000006",
            "role": "provider"
        },
        {
            "email": "peter@petcare.se",
            "password_hash": password_hash,
            "first_name": "Peter",
            "last_name": "Nilsson",
            "mobile_number": "+46702000007",
            "role": "provider"
        },
        {
            "email": "maria@homeservice.se",
            "password_hash": password_hash,
            "first_name": "Maria",
            "last_name": "Gustafsson",
            "mobile_number": "+46702000008",
            "role": "provider"
        },
        # 20 Customers
        {
            "email": "emma.svensson@email.se",
            "password_hash": password_hash,
            "first_name": "Emma",
            "last_name": "Svensson",
            "mobile_number": "+46703000001",
            "role": "customer"
        },
        {
            "email": "oskar.larsson@email.se",
            "password_hash": password_hash,
            "first_name": "Oskar",
            "last_name": "Larsson",
            "mobile_number": "+46703000002",
            "role": "customer"
        },
        {
            "email": "linnea.olsson@email.se",
            "password_hash": password_hash,
            "first_name": "Linnea",
            "last_name": "Olsson",
            "mobile_number": "+46703000003",
            "role": "customer"
        },
        {
            "email": "alexander.persson@email.se",
            "password_hash": password_hash,
            "first_name": "Alexander",
            "last_name": "Persson",
            "mobile_number": "+46703000004",
            "role": "customer"
        },
        {
            "email": "maja.eriksson@email.se",
            "password_hash": password_hash,
            "first_name": "Maja",
            "last_name": "Eriksson",
            "mobile_number": "+46703000005",
            "role": "customer"
        },
        {
            "email": "william.gustafsson@email.se",
            "password_hash": password_hash,
            "first_name": "William",
            "last_name": "Gustafsson",
            "mobile_number": "+46703000006",
            "role": "customer"
        },
        {
            "email": "alice.pettersson@email.se",
            "password_hash": password_hash,
            "first_name": "Alice",
            "last_name": "Pettersson",
            "mobile_number": "+46703000007",
            "role": "customer"
        },
        {
            "email": "lucas.jonsson@email.se",
            "password_hash": password_hash,
            "first_name": "Lucas",
            "last_name": "Jonsson",
            "mobile_number": "+46703000008",
            "role": "customer"
        },
        {
            "email": "ella.samuelsson@email.se",
            "password_hash": password_hash,
            "first_name": "Ella",
            "last_name": "Samuelsson",
            "mobile_number": "+46703000009",
            "role": "customer"
        },
        {
            "email": "hugo.jakobsson@email.se",
            "password_hash": password_hash,
            "first_name": "Hugo",
            "last_name": "Jakobsson",
            "mobile_number": "+46703000010",
            "role": "customer"
        },
        {
            "email": "ebba.carlsson@email.se",
            "password_hash": password_hash,
            "first_name": "Ebba",
            "last_name": "Carlsson",
            "mobile_number": "+46703000011",
            "role": "customer"
        },
        {
            "email": "elias.berg@email.se",
            "password_hash": password_hash,
            "first_name": "Elias",
            "last_name": "Berg",
            "mobile_number": "+46703000012",
            "role": "customer"
        },
        {
            "email": "wilma.sandberg@email.se",
            "password_hash": password_hash,
            "first_name": "Wilma",
            "last_name": "Sandberg",
            "mobile_number": "+46703000013",
            "role": "customer"
        },
        {
            "email": "liam.lundgren@email.se",
            "password_hash": password_hash,
            "first_name": "Liam",
            "last_name": "Lundgren",
            "mobile_number": "+46703000014",
            "role": "customer"
        },
        {
            "email": "astrid.forsberg@email.se",
            "password_hash": password_hash,
            "first_name": "Astrid",
            "last_name": "Forsberg",
            "mobile_number": "+46703000015",
            "role": "customer"
        },
        {
            "email": "noah.hedlund@email.se",
            "password_hash": password_hash,
            "first_name": "Noah",
            "last_name": "Hedlund",
            "mobile_number": "+46703000016",
            "role": "customer"
        },
        {
            "email": "vera.lundqvist@email.se",
            "password_hash": password_hash,
            "first_name": "Vera",
            "last_name": "Lundqvist",
            "mobile_number": "+46703000017",
            "role": "customer"
        },
        {
            "email": "oliver.wallin@email.se",
            "password_hash": password_hash,
            "first_name": "Oliver",
            "last_name": "Wallin",
            "mobile_number": "+46703000018",
            "role": "customer"
        },
        {
            "email": "saga.holmberg@email.se",
            "password_hash": password_hash,
            "first_name": "Saga",
            "last_name": "Holmberg",
            "mobile_number": "+46703000019",
            "role": "customer"
        },
        {
            "email": "adam.bjork@email.se",
            "password_hash": password_hash,
            "first_name": "Adam",
            "last_name": "Björk",
            "mobile_number": "+46703000020",
            "role": "customer"
        }
    ]

    async with conn.cursor() as cur:
        for user in users:
            role_name = user.pop("role")

            # Insert user
            await cur.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, mobile_number)
                VALUES (%(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(mobile_number)s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
                """,
                user
            )
            result = await cur.fetchone()

            if result:
                user_id = result[0]

                # Get role_id
                await cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role_row = await cur.fetchone()

                if role_row:
                    role_id = role_row[0]

                    # Assign role
                    await cur.execute(
                        """
                        INSERT INTO user_roles (user_id, role_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (user_id, role_id)
                    )

    await conn.commit()
    print(f"✓ Seeded {len(users)} users")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_users(conn)
        await db.disconnect()

    asyncio.run(main())
