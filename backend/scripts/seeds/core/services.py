"""Seed categories, services, and service variants tables with test data."""
import asyncio
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_services(conn: AsyncConnection) -> None:
    """Insert test categories, services, and service variants."""

    # First, seed categories
    categories = [
        {"name": "Hair Care", "slug": "hair-care", "parent_id": None},
        {"name": "Hair Cutting", "slug": "hair-cutting", "parent_id": 1},
        {"name": "Hair Coloring", "slug": "hair-coloring", "parent_id": 1},
        {"name": "Hair Treatment", "slug": "hair-treatment", "parent_id": 1},
        {"name": "Restaurant", "slug": "restaurant", "parent_id": None},
        {"name": "Italian Cuisine", "slug": "italian-cuisine", "parent_id": 5},
        {"name": "Fitness", "slug": "fitness", "parent_id": None},
        {"name": "Personal Training", "slug": "personal-training", "parent_id": 7},
        {"name": "Group Classes", "slug": "group-classes", "parent_id": 7},
        {"name": "Spa & Wellness", "slug": "spa-wellness", "parent_id": None},
        {"name": "Massage", "slug": "massage", "parent_id": 10},
        {"name": "Facial Treatments", "slug": "facial-treatments", "parent_id": 10},
        {"name": "Medical", "slug": "medical", "parent_id": None},
        {"name": "General Practice", "slug": "general-practice", "parent_id": 13},
        {"name": "Specialist Care", "slug": "specialist-care", "parent_id": 13},
        {"name": "Automotive", "slug": "automotive", "parent_id": None},
        {"name": "Car Service", "slug": "car-service", "parent_id": 16},
        {"name": "Car Repair", "slug": "car-repair", "parent_id": 16},
        {"name": "Veterinary", "slug": "veterinary", "parent_id": None},
        {"name": "Pet Health", "slug": "pet-health", "parent_id": 19},
        {"name": "Pet Surgery", "slug": "pet-surgery", "parent_id": 19},
        {"name": "Home Services", "slug": "home-services", "parent_id": None},
        {"name": "Cleaning", "slug": "cleaning", "parent_id": 22},
        {"name": "Repairs", "slug": "repairs", "parent_id": 22}
    ]

    category_count = 0
    async with conn.cursor() as cur:
        for cat in categories:
            await cur.execute(
                """
                INSERT INTO categories (name, slug, parent_id)
                VALUES (%(name)s, %(slug)s, %(parent_id)s)
                ON CONFLICT (slug) DO NOTHING
                RETURNING id
                """,
                cat
            )
            result = await cur.fetchone()
            if result:
                category_count += 1

    # Get business IDs by slug
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT id, slug FROM businesses
            WHERE slug IN (
                'nikita-hair-salon',
                'marios-italian-restaurant',
                'fitzone-gym',
                'bergstrom-spa-wellness',
                'johansson-medical-clinic',
                'lindstrom-auto-service',
                'petcare-veterinary-clinic',
                'gustafsson-home-services'
            )
        """)
        business_rows = await cur.fetchall()
        businesses = {slug: biz_id for biz_id, slug in business_rows}

    # Get category IDs by slug
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, slug FROM categories")
        category_rows = await cur.fetchall()
        category_ids = {slug: cat_id for cat_id, slug in category_rows}

    # Define services with their variants
    services_data = [
        # ===== NIKITA HAIR SALON =====
        {
            "service": {
                "business_id": businesses.get("nikita-hair-salon"),
                "category_id": category_ids.get("hair-cutting"),
                "name": "Women's Haircut",
                "description": "Professional haircut with wash and blow-dry included",
                "is_active": True
            },
            "variants": [
                {"name": "Short Hair", "price": Decimal("650.00"), "duration_minutes": 45},
                {"name": "Medium Hair", "price": Decimal("750.00"), "duration_minutes": 60},
                {"name": "Long Hair", "price": Decimal("850.00"), "duration_minutes": 75}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("nikita-hair-salon"),
                "category_id": category_ids.get("hair-cutting"),
                "name": "Men's Haircut",
                "description": "Classic or modern men's cut with styling",
                "is_active": True
            },
            "variants": [
                {"name": "Standard Cut", "price": Decimal("450.00"), "duration_minutes": 30},
                {"name": "Premium Cut & Beard Trim", "price": Decimal("550.00"), "duration_minutes": 45}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("nikita-hair-salon"),
                "category_id": category_ids.get("hair-coloring"),
                "name": "Full Hair Coloring",
                "description": "Complete hair coloring service with premium products",
                "is_active": True
            },
            "variants": [
                {"name": "Single Color - Short", "price": Decimal("1200.00"), "duration_minutes": 120},
                {"name": "Single Color - Medium", "price": Decimal("1500.00"), "duration_minutes": 150},
                {"name": "Single Color - Long", "price": Decimal("1800.00"), "duration_minutes": 180}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("nikita-hair-salon"),
                "category_id": category_ids.get("hair-coloring"),
                "name": "Highlights",
                "description": "Partial or full highlights for dimension and depth",
                "is_active": True
            },
            "variants": [
                {"name": "Partial Highlights", "price": Decimal("1400.00"), "duration_minutes": 150},
                {"name": "Full Highlights", "price": Decimal("1900.00"), "duration_minutes": 180},
                {"name": "Balayage", "price": Decimal("2200.00"), "duration_minutes": 210}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("nikita-hair-salon"),
                "category_id": category_ids.get("hair-treatment"),
                "name": "Hair Treatment",
                "description": "Deep conditioning and repair treatments",
                "is_active": True
            },
            "variants": [
                {"name": "Basic Treatment", "price": Decimal("450.00"), "duration_minutes": 30},
                {"name": "Keratin Treatment", "price": Decimal("2500.00"), "duration_minutes": 180},
                {"name": "Olaplex Repair", "price": Decimal("800.00"), "duration_minutes": 45}
            ]
        },

        # ===== MARIO'S ITALIAN RESTAURANT =====
        {
            "service": {
                "business_id": businesses.get("marios-italian-restaurant"),
                "category_id": category_ids.get("italian-cuisine"),
                "name": "Dinner Reservation",
                "description": "Table reservation for fine Italian dining",
                "is_active": True
            },
            "variants": [
                {"name": "2 Person Table", "price": Decimal("0.00"), "duration_minutes": 120},
                {"name": "4 Person Table", "price": Decimal("0.00"), "duration_minutes": 120},
                {"name": "6+ Person Table", "price": Decimal("0.00"), "duration_minutes": 150}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("marios-italian-restaurant"),
                "category_id": category_ids.get("italian-cuisine"),
                "name": "Private Event",
                "description": "Private dining room for special occasions",
                "is_active": True
            },
            "variants": [
                {"name": "10-15 Guests", "price": Decimal("5000.00"), "duration_minutes": 180},
                {"name": "16-25 Guests", "price": Decimal("8000.00"), "duration_minutes": 240},
                {"name": "26-40 Guests", "price": Decimal("12000.00"), "duration_minutes": 300}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("marios-italian-restaurant"),
                "category_id": category_ids.get("italian-cuisine"),
                "name": "Cooking Class",
                "description": "Learn authentic Italian cooking with our chef",
                "is_active": True
            },
            "variants": [
                {"name": "Pasta Making Class", "price": Decimal("950.00"), "duration_minutes": 120},
                {"name": "Pizza Master Class", "price": Decimal("850.00"), "duration_minutes": 90},
                {"name": "Full Italian Dinner Course", "price": Decimal("1500.00"), "duration_minutes": 180}
            ]
        },

        # ===== FITZONE GYM =====
        {
            "service": {
                "business_id": businesses.get("fitzone-gym"),
                "category_id": category_ids.get("personal-training"),
                "name": "Personal Training Session",
                "description": "One-on-one training with certified personal trainer",
                "is_active": True
            },
            "variants": [
                {"name": "Single Session", "price": Decimal("650.00"), "duration_minutes": 60},
                {"name": "5 Session Package", "price": Decimal("3000.00"), "duration_minutes": 60},
                {"name": "10 Session Package", "price": Decimal("5500.00"), "duration_minutes": 60}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("fitzone-gym"),
                "category_id": category_ids.get("group-classes"),
                "name": "Yoga Class",
                "description": "All levels yoga class for flexibility and mindfulness",
                "is_active": True
            },
            "variants": [
                {"name": "Drop-in Class", "price": Decimal("180.00"), "duration_minutes": 60},
                {"name": "10 Class Package", "price": Decimal("1500.00"), "duration_minutes": 60},
                {"name": "Monthly Unlimited", "price": Decimal("2500.00"), "duration_minutes": 60}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("fitzone-gym"),
                "category_id": category_ids.get("group-classes"),
                "name": "HIIT Training",
                "description": "High-intensity interval training for maximum results",
                "is_active": True
            },
            "variants": [
                {"name": "Drop-in Class", "price": Decimal("200.00"), "duration_minutes": 45},
                {"name": "10 Class Package", "price": Decimal("1700.00"), "duration_minutes": 45}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("fitzone-gym"),
                "category_id": category_ids.get("group-classes"),
                "name": "Spinning Class",
                "description": "Indoor cycling workout with energizing music",
                "is_active": True
            },
            "variants": [
                {"name": "Drop-in Class", "price": Decimal("190.00"), "duration_minutes": 50},
                {"name": "10 Class Package", "price": Decimal("1600.00"), "duration_minutes": 50}
            ]
        },

        # ===== BERGSTRÖM SPA & WELLNESS =====
        {
            "service": {
                "business_id": businesses.get("bergstrom-spa-wellness"),
                "category_id": category_ids.get("massage"),
                "name": "Swedish Massage",
                "description": "Classic Swedish massage for deep relaxation",
                "is_active": True
            },
            "variants": [
                {"name": "30 Minutes", "price": Decimal("550.00"), "duration_minutes": 30},
                {"name": "60 Minutes", "price": Decimal("950.00"), "duration_minutes": 60},
                {"name": "90 Minutes", "price": Decimal("1350.00"), "duration_minutes": 90}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("bergstrom-spa-wellness"),
                "category_id": category_ids.get("massage"),
                "name": "Deep Tissue Massage",
                "description": "Intense massage for muscle tension and pain relief",
                "is_active": True
            },
            "variants": [
                {"name": "60 Minutes", "price": Decimal("1100.00"), "duration_minutes": 60},
                {"name": "90 Minutes", "price": Decimal("1550.00"), "duration_minutes": 90}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("bergstrom-spa-wellness"),
                "category_id": category_ids.get("massage"),
                "name": "Hot Stone Massage",
                "description": "Therapeutic massage with heated stones",
                "is_active": True
            },
            "variants": [
                {"name": "75 Minutes", "price": Decimal("1450.00"), "duration_minutes": 75},
                {"name": "90 Minutes", "price": Decimal("1650.00"), "duration_minutes": 90}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("bergstrom-spa-wellness"),
                "category_id": category_ids.get("facial-treatments"),
                "name": "Classic Facial",
                "description": "Deep cleansing facial for all skin types",
                "is_active": True
            },
            "variants": [
                {"name": "60 Minutes", "price": Decimal("850.00"), "duration_minutes": 60},
                {"name": "90 Minutes Deluxe", "price": Decimal("1250.00"), "duration_minutes": 90}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("bergstrom-spa-wellness"),
                "category_id": category_ids.get("facial-treatments"),
                "name": "Anti-Aging Treatment",
                "description": "Premium facial with collagen boost and LED therapy",
                "is_active": True
            },
            "variants": [
                {"name": "Single Treatment", "price": Decimal("1850.00"), "duration_minutes": 90},
                {"name": "3 Treatment Package", "price": Decimal("5000.00"), "duration_minutes": 90}
            ]
        },

        # ===== JOHANSSON MEDICAL CLINIC =====
        {
            "service": {
                "business_id": businesses.get("johansson-medical-clinic"),
                "category_id": category_ids.get("general-practice"),
                "name": "General Consultation",
                "description": "Standard medical consultation with doctor",
                "is_active": True
            },
            "variants": [
                {"name": "15 Minutes", "price": Decimal("500.00"), "duration_minutes": 15},
                {"name": "30 Minutes", "price": Decimal("800.00"), "duration_minutes": 30},
                {"name": "45 Minutes", "price": Decimal("1100.00"), "duration_minutes": 45}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("johansson-medical-clinic"),
                "category_id": category_ids.get("general-practice"),
                "name": "Health Check-up",
                "description": "Comprehensive health screening with lab tests",
                "is_active": True
            },
            "variants": [
                {"name": "Basic Check-up", "price": Decimal("2500.00"), "duration_minutes": 60},
                {"name": "Complete Check-up", "price": Decimal("4500.00"), "duration_minutes": 90},
                {"name": "Premium Executive Check-up", "price": Decimal("7500.00"), "duration_minutes": 120}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("johansson-medical-clinic"),
                "category_id": category_ids.get("specialist-care"),
                "name": "Specialist Consultation",
                "description": "Consultation with medical specialist",
                "is_active": True
            },
            "variants": [
                {"name": "Cardiology", "price": Decimal("1500.00"), "duration_minutes": 45},
                {"name": "Dermatology", "price": Decimal("1300.00"), "duration_minutes": 30},
                {"name": "Orthopedics", "price": Decimal("1400.00"), "duration_minutes": 45}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("johansson-medical-clinic"),
                "category_id": category_ids.get("general-practice"),
                "name": "Vaccination",
                "description": "Various vaccination services",
                "is_active": True
            },
            "variants": [
                {"name": "Flu Shot", "price": Decimal("350.00"), "duration_minutes": 15},
                {"name": "Travel Vaccines (per dose)", "price": Decimal("550.00"), "duration_minutes": 20},
                {"name": "Vaccination Package", "price": Decimal("2000.00"), "duration_minutes": 30}
            ]
        },

        # ===== LINDSTRÖM AUTO SERVICE =====
        {
            "service": {
                "business_id": businesses.get("lindstrom-auto-service"),
                "category_id": category_ids.get("car-service"),
                "name": "Oil Change & Service",
                "description": "Complete oil change with filter and inspection",
                "is_active": True
            },
            "variants": [
                {"name": "Standard Oil Change", "price": Decimal("850.00"), "duration_minutes": 45},
                {"name": "Synthetic Oil Change", "price": Decimal("1200.00"), "duration_minutes": 45},
                {"name": "Premium Service Package", "price": Decimal("2500.00"), "duration_minutes": 90}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("lindstrom-auto-service"),
                "category_id": category_ids.get("car-service"),
                "name": "Tire Service",
                "description": "Tire change, balancing, and storage",
                "is_active": True
            },
            "variants": [
                {"name": "Tire Change (4 wheels)", "price": Decimal("600.00"), "duration_minutes": 60},
                {"name": "Tire Change + Balancing", "price": Decimal("900.00"), "duration_minutes": 75},
                {"name": "New Tires + Installation", "price": Decimal("5000.00"), "duration_minutes": 120}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("lindstrom-auto-service"),
                "category_id": category_ids.get("car-repair"),
                "name": "Brake Service",
                "description": "Brake inspection and repair",
                "is_active": True
            },
            "variants": [
                {"name": "Brake Inspection", "price": Decimal("500.00"), "duration_minutes": 30},
                {"name": "Front Brake Pads Replacement", "price": Decimal("2500.00"), "duration_minutes": 120},
                {"name": "Complete Brake System Service", "price": Decimal("4500.00"), "duration_minutes": 180}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("lindstrom-auto-service"),
                "category_id": category_ids.get("car-repair"),
                "name": "Engine Diagnostics",
                "description": "Computer diagnostics and problem identification",
                "is_active": True
            },
            "variants": [
                {"name": "Basic Diagnostic Scan", "price": Decimal("750.00"), "duration_minutes": 45},
                {"name": "Full System Diagnostics", "price": Decimal("1500.00"), "duration_minutes": 90}
            ]
        },

        # ===== PETCARE VETERINARY CLINIC =====
        {
            "service": {
                "business_id": businesses.get("petcare-veterinary-clinic"),
                "category_id": category_ids.get("pet-health"),
                "name": "Veterinary Consultation",
                "description": "General health check and consultation",
                "is_active": True
            },
            "variants": [
                {"name": "Cat/Small Pet", "price": Decimal("550.00"), "duration_minutes": 30},
                {"name": "Dog (Small/Medium)", "price": Decimal("600.00"), "duration_minutes": 30},
                {"name": "Dog (Large)", "price": Decimal("650.00"), "duration_minutes": 30}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("petcare-veterinary-clinic"),
                "category_id": category_ids.get("pet-health"),
                "name": "Vaccination",
                "description": "Standard pet vaccinations",
                "is_active": True
            },
            "variants": [
                {"name": "Cat Vaccination Package", "price": Decimal("800.00"), "duration_minutes": 20},
                {"name": "Dog Vaccination Package", "price": Decimal("950.00"), "duration_minutes": 20},
                {"name": "Rabies Vaccine", "price": Decimal("450.00"), "duration_minutes": 15}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("petcare-veterinary-clinic"),
                "category_id": category_ids.get("pet-health"),
                "name": "Dental Cleaning",
                "description": "Professional pet dental cleaning under sedation",
                "is_active": True
            },
            "variants": [
                {"name": "Cat Dental", "price": Decimal("2500.00"), "duration_minutes": 120},
                {"name": "Small Dog", "price": Decimal("2800.00"), "duration_minutes": 120},
                {"name": "Large Dog", "price": Decimal("3500.00"), "duration_minutes": 150}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("petcare-veterinary-clinic"),
                "category_id": category_ids.get("pet-surgery"),
                "name": "Spay/Neuter Surgery",
                "description": "Sterilization surgery with post-op care",
                "is_active": True
            },
            "variants": [
                {"name": "Cat Spay/Neuter", "price": Decimal("3500.00"), "duration_minutes": 90},
                {"name": "Small Dog Spay/Neuter", "price": Decimal("4500.00"), "duration_minutes": 120},
                {"name": "Large Dog Spay/Neuter", "price": Decimal("5500.00"), "duration_minutes": 150}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("petcare-veterinary-clinic"),
                "category_id": category_ids.get("pet-health"),
                "name": "Emergency Visit",
                "description": "Urgent care for pet emergencies",
                "is_active": True
            },
            "variants": [
                {"name": "Emergency Consultation", "price": Decimal("1500.00"), "duration_minutes": 45},
                {"name": "Critical Care Package", "price": Decimal("5000.00"), "duration_minutes": 180}
            ]
        },

        # ===== GUSTAFSSON HOME SERVICES =====
        {
            "service": {
                "business_id": businesses.get("gustafsson-home-services"),
                "category_id": category_ids.get("cleaning"),
                "name": "Home Cleaning",
                "description": "Professional home cleaning service",
                "is_active": True
            },
            "variants": [
                {"name": "Basic Clean (< 50 sqm)", "price": Decimal("900.00"), "duration_minutes": 120},
                {"name": "Standard Clean (50-100 sqm)", "price": Decimal("1400.00"), "duration_minutes": 180},
                {"name": "Deep Clean (50-100 sqm)", "price": Decimal("2200.00"), "duration_minutes": 240},
                {"name": "Large Home (> 100 sqm)", "price": Decimal("2800.00"), "duration_minutes": 300}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("gustafsson-home-services"),
                "category_id": category_ids.get("cleaning"),
                "name": "Window Cleaning",
                "description": "Interior and exterior window cleaning",
                "is_active": True
            },
            "variants": [
                {"name": "Small Apartment", "price": Decimal("800.00"), "duration_minutes": 90},
                {"name": "Standard House", "price": Decimal("1500.00"), "duration_minutes": 150},
                {"name": "Large House with High Windows", "price": Decimal("2500.00"), "duration_minutes": 240}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("gustafsson-home-services"),
                "category_id": category_ids.get("repairs"),
                "name": "Plumbing Service",
                "description": "General plumbing repairs and installations",
                "is_active": True
            },
            "variants": [
                {"name": "Minor Repair (1 hour)", "price": Decimal("950.00"), "duration_minutes": 60},
                {"name": "Standard Service (2 hours)", "price": Decimal("1800.00"), "duration_minutes": 120},
                {"name": "Major Installation (4+ hours)", "price": Decimal("4000.00"), "duration_minutes": 240}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("gustafsson-home-services"),
                "category_id": category_ids.get("repairs"),
                "name": "Electrical Work",
                "description": "Licensed electrician for home electrical work",
                "is_active": True
            },
            "variants": [
                {"name": "Minor Electrical Fix", "price": Decimal("1100.00"), "duration_minutes": 60},
                {"name": "Outlet/Switch Installation", "price": Decimal("1500.00"), "duration_minutes": 90},
                {"name": "Major Electrical Work", "price": Decimal("4500.00"), "duration_minutes": 300}
            ]
        },
        {
            "service": {
                "business_id": businesses.get("gustafsson-home-services"),
                "category_id": category_ids.get("repairs"),
                "name": "Handyman Service",
                "description": "General home repairs and maintenance",
                "is_active": True
            },
            "variants": [
                {"name": "2 Hours", "price": Decimal("1400.00"), "duration_minutes": 120},
                {"name": "4 Hours", "price": Decimal("2600.00"), "duration_minutes": 240},
                {"name": "Full Day (8 hours)", "price": Decimal("4800.00"), "duration_minutes": 480}
            ]
        }
    ]

    service_count = 0
    variant_count = 0

    async with conn.cursor() as cur:
        for svc_data in services_data:
            # Skip if business_id is None (business wasn't seeded)
            if svc_data["service"]["business_id"] is None:
                continue

            # Insert service
            await cur.execute(
                """
                INSERT INTO services (business_id, category_id, name, description, is_active)
                VALUES (%(business_id)s, %(category_id)s, %(name)s, %(description)s, %(is_active)s)
                RETURNING id
                """,
                svc_data["service"]
            )
            result = await cur.fetchone()

            if result:
                service_id = result[0]
                service_count += 1

                # Insert variants for this service
                for variant in svc_data["variants"]:
                    await cur.execute(
                        """
                        INSERT INTO service_variants (service_id, name, price, duration_minutes)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (service_id, variant["name"], variant["price"], variant["duration_minutes"])
                    )
                    variant_count += 1

    await conn.commit()
    print(f"✓ Seeded {category_count} categories, {service_count} services, {variant_count} service variants")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_services(conn)
        await db.disconnect()

    asyncio.run(main())
