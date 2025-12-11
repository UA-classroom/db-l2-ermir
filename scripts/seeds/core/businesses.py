"""Seed businesses, locations, and contacts tables with test data."""
import asyncio
from psycopg import AsyncConnection


async def seed_businesses(conn: AsyncConnection) -> None:
    """Insert test businesses, locations, and contacts."""

    # First, get provider user IDs by email
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT id, email FROM users
            WHERE email IN (
                'nikita@hairsalon.se',
                'mario@restaurant.se',
                'erik@gym.se',
                'sofia@spa.se',
                'lars@clinic.se',
                'anna@autoservice.se',
                'peter@petcare.se',
                'maria@homeservice.se'
            )
        """)
        provider_rows = await cur.fetchall()
        providers = {email: user_id for user_id, email in provider_rows}

    # Define businesses with their locations and contacts
    businesses_data = [
        {
            "business": {
                "owner_id": providers["nikita@hairsalon.se"],
                "name": "Nikita Hair Salon",
                "org_number": "556123-4567",
                "slug": "nikita-hair-salon"
            },
            "locations": [
                {
                    "name": "Stureplan Branch",
                    "address": "Sturegatan 12",
                    "city": "Stockholm",
                    "postal_code": "11436",
                    "latitude": 59.3349,
                    "longitude": 18.0728,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812345001"},
                        {"contact_type": "Manager", "phone_number": "+46812345002"}
                    ]
                },
                {
                    "name": "Vasastan Branch",
                    "address": "Odengatan 45",
                    "city": "Stockholm",
                    "postal_code": "11351",
                    "latitude": 59.3425,
                    "longitude": 18.0520,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812345003"}
                    ]
                },
                {
                    "name": "Södermalm Branch",
                    "address": "Götgatan 78",
                    "city": "Stockholm",
                    "postal_code": "11830",
                    "latitude": 59.3141,
                    "longitude": 18.0731,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812345004"},
                        {"contact_type": "Booking", "phone_number": "+46812345005"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["mario@restaurant.se"],
                "name": "Mario's Italian Restaurant",
                "org_number": "556234-5678",
                "slug": "marios-italian-restaurant"
            },
            "locations": [
                {
                    "name": "Östermalm Location",
                    "address": "Karlavägen 89",
                    "city": "Stockholm",
                    "postal_code": "11459",
                    "latitude": 59.3450,
                    "longitude": 18.0850,
                    "contacts": [
                        {"contact_type": "Reservations", "phone_number": "+46812346001"},
                        {"contact_type": "Chef", "phone_number": "+46812346002"}
                    ]
                },
                {
                    "name": "Gamla Stan Location",
                    "address": "Stora Nygatan 21",
                    "city": "Stockholm",
                    "postal_code": "11127",
                    "latitude": 59.3251,
                    "longitude": 18.0686,
                    "contacts": [
                        {"contact_type": "Reservations", "phone_number": "+46812346003"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["erik@gym.se"],
                "name": "FitZone Gym",
                "org_number": "556345-6789",
                "slug": "fitzone-gym"
            },
            "locations": [
                {
                    "name": "City Center Gym",
                    "address": "Drottninggatan 55",
                    "city": "Stockholm",
                    "postal_code": "11121",
                    "latitude": 59.3326,
                    "longitude": 18.0649,
                    "contacts": [
                        {"contact_type": "Front Desk", "phone_number": "+46812347001"},
                        {"contact_type": "Personal Training", "phone_number": "+46812347002"}
                    ]
                },
                {
                    "name": "Kungsholmen Gym",
                    "address": "Hantverkargatan 32",
                    "city": "Stockholm",
                    "postal_code": "11221",
                    "latitude": 59.3325,
                    "longitude": 18.0372,
                    "contacts": [
                        {"contact_type": "Front Desk", "phone_number": "+46812347003"}
                    ]
                },
                {
                    "name": "Solna Gym",
                    "address": "Frösundaviks allé 15",
                    "city": "Solna",
                    "postal_code": "16970",
                    "latitude": 59.3600,
                    "longitude": 18.0100,
                    "contacts": [
                        {"contact_type": "Front Desk", "phone_number": "+46812347004"},
                        {"contact_type": "Group Classes", "phone_number": "+46812347005"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["sofia@spa.se"],
                "name": "Bergström Spa & Wellness",
                "org_number": "556456-7890",
                "slug": "bergstrom-spa-wellness"
            },
            "locations": [
                {
                    "name": "Luxury Spa Downtown",
                    "address": "Birger Jarlsgatan 43",
                    "city": "Stockholm",
                    "postal_code": "11429",
                    "latitude": 59.3367,
                    "longitude": 18.0738,
                    "contacts": [
                        {"contact_type": "Spa Reception", "phone_number": "+46812348001"},
                        {"contact_type": "Massage Booking", "phone_number": "+46812348002"}
                    ]
                },
                {
                    "name": "Djursholm Wellness Center",
                    "address": "Djursholmsvägen 25",
                    "city": "Djursholm",
                    "postal_code": "18230",
                    "latitude": 59.3994,
                    "longitude": 18.0794,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812348003"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["lars@clinic.se"],
                "name": "Johansson Medical Clinic",
                "org_number": "556567-8901",
                "slug": "johansson-medical-clinic"
            },
            "locations": [
                {
                    "name": "Central Clinic",
                    "address": "Kungsgatan 44",
                    "city": "Stockholm",
                    "postal_code": "11135",
                    "latitude": 59.3329,
                    "longitude": 18.0658,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812349001"},
                        {"contact_type": "Emergency", "phone_number": "+46812349002"}
                    ]
                },
                {
                    "name": "Family Health Center",
                    "address": "Valhallavägen 117",
                    "city": "Stockholm",
                    "postal_code": "11531",
                    "latitude": 59.3433,
                    "longitude": 18.0950,
                    "contacts": [
                        {"contact_type": "Appointments", "phone_number": "+46812349003"},
                        {"contact_type": "Pediatrics", "phone_number": "+46812349004"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["anna@autoservice.se"],
                "name": "Lindström Auto Service",
                "org_number": "556678-9012",
                "slug": "lindstrom-auto-service"
            },
            "locations": [
                {
                    "name": "Main Service Center",
                    "address": "Torshamnsgatan 35",
                    "city": "Stockholm",
                    "postal_code": "16440",
                    "latitude": 59.3177,
                    "longitude": 18.0267,
                    "contacts": [
                        {"contact_type": "Service Desk", "phone_number": "+46812350001"},
                        {"contact_type": "Parts Department", "phone_number": "+46812350002"}
                    ]
                },
                {
                    "name": "Express Service Kista",
                    "address": "Kistagången 16",
                    "city": "Kista",
                    "postal_code": "16440",
                    "latitude": 59.4032,
                    "longitude": 17.9437,
                    "contacts": [
                        {"contact_type": "Quick Service", "phone_number": "+46812350003"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["peter@petcare.se"],
                "name": "PetCare Veterinary Clinic",
                "org_number": "556789-0123",
                "slug": "petcare-veterinary-clinic"
            },
            "locations": [
                {
                    "name": "Central Veterinary",
                    "address": "Rålambsvägen 17",
                    "city": "Stockholm",
                    "postal_code": "11259",
                    "latitude": 59.3275,
                    "longitude": 18.0290,
                    "contacts": [
                        {"contact_type": "Reception", "phone_number": "+46812351001"},
                        {"contact_type": "Emergency", "phone_number": "+46812351002"}
                    ]
                },
                {
                    "name": "Nacka Pet Clinic",
                    "address": "Nacka Forum 14",
                    "city": "Nacka",
                    "postal_code": "13150",
                    "latitude": 59.3099,
                    "longitude": 18.1638,
                    "contacts": [
                        {"contact_type": "Appointments", "phone_number": "+46812351003"}
                    ]
                },
                {
                    "name": "Täby Pet Hospital",
                    "address": "Täby Centrum 8",
                    "city": "Täby",
                    "postal_code": "18330",
                    "latitude": 59.4439,
                    "longitude": 18.0686,
                    "contacts": [
                        {"contact_type": "Hospital Reception", "phone_number": "+46812351004"},
                        {"contact_type": "Surgery", "phone_number": "+46812351005"}
                    ]
                }
            ]
        },
        {
            "business": {
                "owner_id": providers["maria@homeservice.se"],
                "name": "Gustafsson Home Services",
                "org_number": "556890-1234",
                "slug": "gustafsson-home-services"
            },
            "locations": [
                {
                    "name": "Stockholm North Office",
                    "address": "Sveavägen 128",
                    "city": "Stockholm",
                    "postal_code": "11350",
                    "latitude": 59.3489,
                    "longitude": 18.0560,
                    "contacts": [
                        {"contact_type": "Customer Service", "phone_number": "+46812352001"},
                        {"contact_type": "Dispatch", "phone_number": "+46812352002"}
                    ]
                },
                {
                    "name": "South Suburbs Office",
                    "address": "Huddingevägen 5",
                    "city": "Huddinge",
                    "postal_code": "14146",
                    "latitude": 59.2369,
                    "longitude": 17.9803,
                    "contacts": [
                        {"contact_type": "Booking", "phone_number": "+46812352003"}
                    ]
                }
            ]
        }
    ]

    business_count = 0
    location_count = 0
    contact_count = 0

    async with conn.cursor() as cur:
        for biz_data in businesses_data:
            # Insert business
            await cur.execute(
                """
                INSERT INTO businesses (owner_id, name, org_number, slug)
                VALUES (%(owner_id)s, %(name)s, %(org_number)s, %(slug)s)
                ON CONFLICT (slug) DO NOTHING
                RETURNING id
                """,
                biz_data["business"]
            )
            result = await cur.fetchone()

            if result:
                business_id = result[0]
                business_count += 1

                # Insert locations for this business
                for loc_data in biz_data["locations"]:
                    await cur.execute(
                        """
                        INSERT INTO locations (business_id, name, address, city, postal_code, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            business_id,
                            loc_data["name"],
                            loc_data["address"],
                            loc_data["city"],
                            loc_data["postal_code"],
                            loc_data["latitude"],
                            loc_data["longitude"]
                        )
                    )
                    location_result = await cur.fetchone()

                    if location_result:
                        location_id = location_result[0]
                        location_count += 1

                        # Insert contacts for this location
                        for contact in loc_data["contacts"]:
                            await cur.execute(
                                """
                                INSERT INTO location_contacts (location_id, contact_type, phone_number)
                                VALUES (%s, %s, %s)
                                """,
                                (location_id, contact["contact_type"], contact["phone_number"])
                            )
                            contact_count += 1

    await conn.commit()
    print(f"✓ Seeded {business_count} businesses, {location_count} locations, {contact_count} contacts")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_businesses(conn)
        await db.disconnect()

    asyncio.run(main())
