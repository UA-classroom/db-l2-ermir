"""Seed employees, working_hours, internal_events, and employee_skills tables with test data."""
import asyncio
from datetime import time
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_employees(conn: AsyncConnection) -> None:
    """Insert test employees with working hours, internal events, and skills."""

    # Get user IDs
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, email FROM users ORDER BY email")
        user_rows = await cur.fetchall()
        users = {email: user_id for user_id, email in user_rows}

    # Get location IDs by business slug
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT l.id, l.name, b.slug as business_slug
            FROM locations l
            JOIN businesses b ON l.business_id = b.id
            ORDER BY b.slug, l.name
        """)
        location_rows = await cur.fetchall()
        locations = {}
        for loc_id, loc_name, biz_slug in location_rows:
            key = f"{biz_slug}:{loc_name}"
            locations[key] = loc_id

    # Get service variant IDs
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT sv.id, s.name as service_name, sv.name as variant_name, b.slug as business_slug
            FROM service_variants sv
            JOIN services s ON sv.service_id = s.id
            JOIN businesses b ON s.business_id = b.id
            ORDER BY b.slug, s.name, sv.name
        """)
        variant_rows = await cur.fetchall()
        service_variants = {}
        for var_id, svc_name, var_name, biz_slug in variant_rows:
            key = f"{biz_slug}:{svc_name}:{var_name}"
            service_variants[key] = var_id

    # Define employees with their details
    employees_data = [
        # ===== NIKITA HAIR SALON - Stureplan Branch =====
        {
            "employee": {
                "user_id": users["nikita@hairsalon.se"],
                "location_id": locations["nikita-hair-salon:Stureplan Branch"],
                "job_title": "Owner & Senior Stylist",
                "bio": "Award-winning stylist with 15+ years experience. Specialized in color correction and balayage.",
                "color_code": "#E91E63",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(18, 0)},  # Tuesday
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(18, 0)},  # Wednesday
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(19, 0)},  # Thursday
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(19, 0)},  # Friday
                {"day_of_week": 6, "start_time": time(10, 0), "end_time": time(16, 0)}   # Saturday
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair"},
                {"service": "Women's Haircut", "variant": "Medium Hair"},
                {"service": "Women's Haircut", "variant": "Long Hair"},
                {"service": "Full Hair Coloring", "variant": "Single Color - Short", "custom_price": Decimal("1300.00")},
                {"service": "Full Hair Coloring", "variant": "Single Color - Medium", "custom_price": Decimal("1600.00")},
                {"service": "Full Hair Coloring", "variant": "Single Color - Long", "custom_price": Decimal("1900.00")},
                {"service": "Highlights", "variant": "Partial Highlights"},
                {"service": "Highlights", "variant": "Full Highlights"},
                {"service": "Highlights", "variant": "Balayage", "custom_price": Decimal("2400.00")},
                {"service": "Hair Treatment", "variant": "Keratin Treatment"},
                {"service": "Hair Treatment", "variant": "Olaplex Repair"}
            ],
            "internal_events": [
                {"type": "vacation", "start_time": "2025-01-15 00:00:00+01", "end_time": "2025-01-22 23:59:59+01", "description": "Winter vacation in Thailand"}
            ]
        },
        {
            "employee": {
                "user_id": users["emma.svensson@email.se"],
                "location_id": locations["nikita-hair-salon:Stureplan Branch"],
                "job_title": "Senior Stylist",
                "bio": "Passionate about modern cuts and natural coloring techniques.",
                "color_code": "#9C27B0",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 4, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 5, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(15, 0)}
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair"},
                {"service": "Women's Haircut", "variant": "Medium Hair"},
                {"service": "Women's Haircut", "variant": "Long Hair"},
                {"service": "Men's Haircut", "variant": "Standard Cut"},
                {"service": "Full Hair Coloring", "variant": "Single Color - Short"},
                {"service": "Full Hair Coloring", "variant": "Single Color - Medium"},
                {"service": "Highlights", "variant": "Partial Highlights"},
                {"service": "Hair Treatment", "variant": "Basic Treatment"}
            ],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["linnea.olsson@email.se"],
                "location_id": locations["nikita-hair-salon:Stureplan Branch"],
                "job_title": "Junior Stylist",
                "bio": "Recently graduated, eager to learn and create beautiful hairstyles.",
                "color_code": "#673AB7",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 6, "start_time": time(10, 0), "end_time": time(16, 0)}
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair", "custom_price": Decimal("550.00")},
                {"service": "Women's Haircut", "variant": "Medium Hair", "custom_price": Decimal("650.00")},
                {"service": "Men's Haircut", "variant": "Standard Cut", "custom_price": Decimal("400.00")},
                {"service": "Hair Treatment", "variant": "Basic Treatment"}
            ],
            "internal_events": [
                {"type": "meeting", "start_time": "2025-01-10 09:00:00+01", "end_time": "2025-01-10 11:00:00+01", "description": "Advanced coloring workshop"}
            ]
        },

        # ===== NIKITA HAIR SALON - Vasastan Branch =====
        {
            "employee": {
                "user_id": users["maja.eriksson@email.se"],
                "location_id": locations["nikita-hair-salon:Vasastan Branch"],
                "job_title": "Branch Manager & Stylist",
                "bio": "Expert in creative styling and special occasion hair.",
                "color_code": "#3F51B5",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(18, 0)}
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair"},
                {"service": "Women's Haircut", "variant": "Medium Hair"},
                {"service": "Women's Haircut", "variant": "Long Hair"},
                {"service": "Men's Haircut", "variant": "Standard Cut"},
                {"service": "Men's Haircut", "variant": "Premium Cut & Beard Trim"},
                {"service": "Highlights", "variant": "Partial Highlights"},
                {"service": "Highlights", "variant": "Full Highlights"},
                {"service": "Hair Treatment", "variant": "Basic Treatment"},
                {"service": "Hair Treatment", "variant": "Olaplex Repair"}
            ],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["alice.pettersson@email.se"],
                "location_id": locations["nikita-hair-salon:Vasastan Branch"],
                "job_title": "Color Specialist",
                "bio": "Specialized in vibrant colors and trendy techniques.",
                "color_code": "#2196F3",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 3, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 4, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 5, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(16, 0)}
            ],
            "skills": [
                {"service": "Full Hair Coloring", "variant": "Single Color - Short"},
                {"service": "Full Hair Coloring", "variant": "Single Color - Medium"},
                {"service": "Full Hair Coloring", "variant": "Single Color - Long"},
                {"service": "Highlights", "variant": "Partial Highlights"},
                {"service": "Highlights", "variant": "Full Highlights"},
                {"service": "Highlights", "variant": "Balayage"},
                {"service": "Hair Treatment", "variant": "Keratin Treatment"}
            ],
            "internal_events": [
                {"type": "sick", "start_time": "2024-12-18 00:00:00+01", "end_time": "2024-12-20 23:59:59+01", "description": "Flu"}
            ]
        },

        # ===== NIKITA HAIR SALON - Södermalm Branch =====
        {
            "employee": {
                "user_id": users["ella.samuelsson@email.se"],
                "location_id": locations["nikita-hair-salon:Södermalm Branch"],
                "job_title": "Senior Stylist",
                "bio": "Urban style expert with a passion for edgy cuts.",
                "color_code": "#00BCD4",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 3, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 5, "start_time": time(10, 0), "end_time": time(19, 0)},
                {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(15, 0)}
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair"},
                {"service": "Women's Haircut", "variant": "Medium Hair"},
                {"service": "Men's Haircut", "variant": "Standard Cut"},
                {"service": "Men's Haircut", "variant": "Premium Cut & Beard Trim"},
                {"service": "Highlights", "variant": "Partial Highlights"}
            ],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["wilma.sandberg@email.se"],
                "location_id": locations["nikita-hair-salon:Södermalm Branch"],
                "job_title": "Stylist",
                "bio": "Creative and detail-oriented stylist.",
                "color_code": "#009688",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 6, "start_time": time(10, 0), "end_time": time(16, 0)}
            ],
            "skills": [
                {"service": "Women's Haircut", "variant": "Short Hair"},
                {"service": "Women's Haircut", "variant": "Medium Hair"},
                {"service": "Women's Haircut", "variant": "Long Hair"},
                {"service": "Hair Treatment", "variant": "Basic Treatment"},
                {"service": "Hair Treatment", "variant": "Olaplex Repair"}
            ],
            "internal_events": []
        },

        # ===== MARIO'S ITALIAN RESTAURANT - Östermalm Location =====
        {
            "employee": {
                "user_id": users["mario@restaurant.se"],
                "location_id": locations["marios-italian-restaurant:Östermalm Location"],
                "job_title": "Owner & Head Chef",
                "bio": "Third-generation chef from Naples, bringing authentic Italian cuisine to Stockholm.",
                "color_code": "#4CAF50",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 2, "start_time": time(16, 0), "end_time": time(23, 0)},
                {"day_of_week": 3, "start_time": time(16, 0), "end_time": time(23, 0)},
                {"day_of_week": 4, "start_time": time(16, 0), "end_time": time(23, 0)},
                {"day_of_week": 5, "start_time": time(16, 0), "end_time": time(23, 59)},
                {"day_of_week": 6, "start_time": time(16, 0), "end_time": time(23, 59)}
            ],
            "skills": [
                {"service": "Dinner Reservation", "variant": "2 Person Table"},
                {"service": "Dinner Reservation", "variant": "4 Person Table"},
                {"service": "Private Event", "variant": "10-15 Guests"},
                {"service": "Private Event", "variant": "16-25 Guests"},
                {"service": "Cooking Class", "variant": "Pasta Making Class"},
                {"service": "Cooking Class", "variant": "Pizza Master Class"},
                {"service": "Cooking Class", "variant": "Full Italian Dinner Course"}
            ],
            "internal_events": [
                {"type": "vacation", "start_time": "2025-02-10 00:00:00+01", "end_time": "2025-02-24 23:59:59+01", "description": "Visiting family in Italy"}
            ]
        },
        {
            "employee": {
                "user_id": users["oskar.larsson@email.se"],
                "location_id": locations["marios-italian-restaurant:Östermalm Location"],
                "job_title": "Sous Chef & Event Coordinator",
                "bio": "Managing reservations and assisting with special events.",
                "color_code": "#8BC34A",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 2, "start_time": time(15, 0), "end_time": time(22, 0)},
                {"day_of_week": 3, "start_time": time(15, 0), "end_time": time(22, 0)},
                {"day_of_week": 4, "start_time": time(15, 0), "end_time": time(22, 0)},
                {"day_of_week": 5, "start_time": time(15, 0), "end_time": time(23, 0)},
                {"day_of_week": 6, "start_time": time(15, 0), "end_time": time(23, 0)},
                {"day_of_week": 7, "start_time": time(15, 0), "end_time": time(22, 0)}
            ],
            "skills": [
                {"service": "Dinner Reservation", "variant": "2 Person Table"},
                {"service": "Dinner Reservation", "variant": "4 Person Table"},
                {"service": "Dinner Reservation", "variant": "6+ Person Table"},
                {"service": "Private Event", "variant": "10-15 Guests"},
                {"service": "Cooking Class", "variant": "Pasta Making Class"}
            ],
            "internal_events": []
        },

        # ===== MARIO'S ITALIAN RESTAURANT - Gamla Stan Location =====
        {
            "employee": {
                "user_id": users["alexander.persson@email.se"],
                "location_id": locations["marios-italian-restaurant:Gamla Stan Location"],
                "job_title": "Restaurant Manager",
                "bio": "Expert in customer service and event planning.",
                "color_code": "#CDDC39",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 3, "start_time": time(16, 0), "end_time": time(23, 0)},
                {"day_of_week": 4, "start_time": time(16, 0), "end_time": time(23, 0)},
                {"day_of_week": 5, "start_time": time(16, 0), "end_time": time(23, 59)},
                {"day_of_week": 6, "start_time": time(16, 0), "end_time": time(23, 59)},
                {"day_of_week": 7, "start_time": time(16, 0), "end_time": time(22, 0)}
            ],
            "skills": [
                {"service": "Dinner Reservation", "variant": "2 Person Table"},
                {"service": "Dinner Reservation", "variant": "4 Person Table"},
                {"service": "Dinner Reservation", "variant": "6+ Person Table"},
                {"service": "Private Event", "variant": "10-15 Guests"},
                {"service": "Private Event", "variant": "16-25 Guests"}
            ],
            "internal_events": []
        },

        # ===== FITZONE GYM =====
        {
            "employee": {
                "user_id": users["erik@gym.se"],
                "location_id": locations["fitzone-gym:City Center Gym"],
                "job_title": "Owner & Head Personal Trainer",
                "bio": "Certified personal trainer with specialization in strength training and rehabilitation.",
                "color_code": "#FF9800",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(6, 0), "end_time": time(14, 0)},
                {"day_of_week": 2, "start_time": time(6, 0), "end_time": time(14, 0)},
                {"day_of_week": 3, "start_time": time(6, 0), "end_time": time(14, 0)},
                {"day_of_week": 4, "start_time": time(6, 0), "end_time": time(14, 0)},
                {"day_of_week": 5, "start_time": time(6, 0), "end_time": time(14, 0)}
            ],
            "skills": [
                {"service": "Personal Training Session", "variant": "Single Session"},
                {"service": "Personal Training Session", "variant": "5 Session Package"},
                {"service": "Personal Training Session", "variant": "10 Session Package"},
                {"service": "HIIT Training", "variant": "Drop-in Class"},
                {"service": "HIIT Training", "variant": "10 Class Package"}
            ],
            "internal_events": [
                {"type": "meeting", "start_time": "2025-01-08 08:00:00+01", "end_time": "2025-01-08 10:00:00+01", "description": "Staff training on new equipment"}
            ]
        },
        {
            "employee": {
                "user_id": users["william.gustafsson@email.se"],
                "location_id": locations["fitzone-gym:City Center Gym"],
                "job_title": "Personal Trainer & Yoga Instructor",
                "bio": "Combining strength training with mindfulness and flexibility.",
                "color_code": "#FF5722",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(14, 0), "end_time": time(21, 0)},
                {"day_of_week": 2, "start_time": time(14, 0), "end_time": time(21, 0)},
                {"day_of_week": 3, "start_time": time(14, 0), "end_time": time(21, 0)},
                {"day_of_week": 5, "start_time": time(14, 0), "end_time": time(21, 0)},
                {"day_of_week": 6, "start_time": time(8, 0), "end_time": time(12, 0)}
            ],
            "skills": [
                {"service": "Personal Training Session", "variant": "Single Session", "custom_price": Decimal("600.00")},
                {"service": "Personal Training Session", "variant": "5 Session Package", "custom_price": Decimal("2800.00")},
                {"service": "Yoga Class", "variant": "Drop-in Class"},
                {"service": "Yoga Class", "variant": "10 Class Package"},
                {"service": "Yoga Class", "variant": "Monthly Unlimited"}
            ],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["lucas.jonsson@email.se"],
                "location_id": locations["fitzone-gym:City Center Gym"],
                "job_title": "Group Fitness Instructor",
                "bio": "High-energy instructor specializing in HIIT and Spinning.",
                "color_code": "#795548",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(17, 0), "end_time": time(21, 0)},
                {"day_of_week": 2, "start_time": time(17, 0), "end_time": time(21, 0)},
                {"day_of_week": 3, "start_time": time(17, 0), "end_time": time(21, 0)},
                {"day_of_week": 4, "start_time": time(17, 0), "end_time": time(21, 0)},
                {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(13, 0)}
            ],
            "skills": [
                {"service": "HIIT Training", "variant": "Drop-in Class"},
                {"service": "HIIT Training", "variant": "10 Class Package"},
                {"service": "Spinning Class", "variant": "Drop-in Class"},
                {"service": "Spinning Class", "variant": "10 Class Package"}
            ],
            "internal_events": []
        },

        # ===== BERGSTRÖM SPA & WELLNESS =====
        {
            "employee": {
                "user_id": users["sofia@spa.se"],
                "location_id": locations["bergstrom-spa-wellness:Luxury Spa Downtown"],
                "job_title": "Owner & Senior Therapist",
                "bio": "Licensed massage therapist and spa manager with 20 years of experience.",
                "color_code": "#E91E63",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 3, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 4, "start_time": time(10, 0), "end_time": time(20, 0)},
                {"day_of_week": 5, "start_time": time(10, 0), "end_time": time(20, 0)}
            ],
            "skills": [
                {"service": "Swedish Massage", "variant": "30 Minutes"},
                {"service": "Swedish Massage", "variant": "60 Minutes"},
                {"service": "Swedish Massage", "variant": "90 Minutes"},
                {"service": "Deep Tissue Massage", "variant": "60 Minutes"},
                {"service": "Deep Tissue Massage", "variant": "90 Minutes"}
            ],
            "internal_events": [
                {"type": "vacation", "start_time": "2025-03-01 00:00:00+01", "end_time": "2025-03-14 23:59:59+01", "description": "Spa wellness retreat in Bali"}
            ]
        },
        {
            "employee": {
                "user_id": users["ebba.carlsson@email.se"],
                "location_id": locations["bergstrom-spa-wellness:Luxury Spa Downtown"],
                "job_title": "Massage Therapist",
                "bio": "Specializing in relaxation and aromatherapy massage.",
                "color_code": "#9C27B0",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(19, 0)},
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(19, 0)},
                {"day_of_week": 6, "start_time": time(10, 0), "end_time": time(16, 0)}
            ],
            "skills": [
                {"service": "Swedish Massage", "variant": "30 Minutes"},
                {"service": "Swedish Massage", "variant": "60 Minutes"},
                {"service": "Swedish Massage", "variant": "90 Minutes"}
            ],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["astrid.forsberg@email.se"],
                "location_id": locations["bergstrom-spa-wellness:Luxury Spa Downtown"],
                "job_title": "Facial Specialist",
                "bio": "Expert in anti-aging and skincare treatments.",
                "color_code": "#673AB7",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 3, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 4, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 5, "start_time": time(10, 0), "end_time": time(18, 0)},
                {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(15, 0)}
            ],
            "skills": [],  # Facial services will be added later if needed
            "internal_events": []
        },

        # ===== JOHANSSON MEDICAL CLINIC =====
        {
            "employee": {
                "user_id": users["lars@clinic.se"],
                "location_id": locations["johansson-medical-clinic:Central Clinic"],
                "job_title": "Owner & General Practitioner",
                "bio": "Board-certified family medicine physician with 25 years experience.",
                "color_code": "#2196F3",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 2, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 5, "start_time": time(8, 0), "end_time": time(16, 0)}
            ],
            "skills": [],  # Medical services will be added later
            "internal_events": [
                {"type": "meeting", "start_time": "2025-01-20 13:00:00+01", "end_time": "2025-01-20 15:00:00+01", "description": "Medical conference"}
            ]
        },
        {
            "employee": {
                "user_id": users["hugo.jakobsson@email.se"],
                "location_id": locations["johansson-medical-clinic:Central Clinic"],
                "job_title": "Nurse Practitioner",
                "bio": "Providing primary care and preventive health services.",
                "color_code": "#00BCD4",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 2, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 3, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 5, "start_time": time(8, 0), "end_time": time(16, 0)}
            ],
            "skills": [],
            "internal_events": []
        },

        # ===== LINDSTRÖM AUTO SERVICE =====
        {
            "employee": {
                "user_id": users["anna@autoservice.se"],
                "location_id": locations["lindstrom-auto-service:Main Service Center"],
                "job_title": "Owner & Master Mechanic",
                "bio": "Certified automotive technician specializing in European cars.",
                "color_code": "#607D8B",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(7, 0), "end_time": time(17, 0)},
                {"day_of_week": 2, "start_time": time(7, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(7, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(7, 0), "end_time": time(17, 0)},
                {"day_of_week": 5, "start_time": time(7, 0), "end_time": time(16, 0)}
            ],
            "skills": [],  # Auto services will be added later
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["elias.berg@email.se"],
                "location_id": locations["lindstrom-auto-service:Main Service Center"],
                "job_title": "Automotive Technician",
                "bio": "Experienced in diagnostics and repair.",
                "color_code": "#9E9E9E",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(7, 0), "end_time": time(16, 0)},
                {"day_of_week": 2, "start_time": time(7, 0), "end_time": time(16, 0)},
                {"day_of_week": 3, "start_time": time(7, 0), "end_time": time(16, 0)},
                {"day_of_week": 4, "start_time": time(7, 0), "end_time": time(16, 0)},
                {"day_of_week": 5, "start_time": time(7, 0), "end_time": time(16, 0)}
            ],
            "skills": [],
            "internal_events": [
                {"type": "sick", "start_time": "2024-12-16 00:00:00+01", "end_time": "2024-12-17 23:59:59+01", "description": "Back pain"}
            ]
        },

        # ===== PETCARE VETERINARY CLINIC =====
        {
            "employee": {
                "user_id": users["peter@petcare.se"],
                "location_id": locations["petcare-veterinary-clinic:Central Veterinary"],
                "job_title": "Owner & Veterinarian",
                "bio": "DVM with specialization in small animal surgery.",
                "color_code": "#4CAF50",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(18, 0)},
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(17, 0)}
            ],
            "skills": [],  # Vet services will be added later
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["vera.lundqvist@email.se"],
                "location_id": locations["petcare-veterinary-clinic:Central Veterinary"],
                "job_title": "Veterinary Nurse",
                "bio": "Caring for animals with compassion and expertise.",
                "color_code": "#8BC34A",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(17, 0)}
            ],
            "skills": [],
            "internal_events": []
        },

        # ===== GUSTAFSSON HOME SERVICES =====
        {
            "employee": {
                "user_id": users["maria@homeservice.se"],
                "location_id": locations["gustafsson-home-services:Stockholm North Office"],
                "job_title": "Owner & Service Manager",
                "bio": "Professional home services with 15 years experience.",
                "color_code": "#FF9800",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 2, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 3, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(17, 0)},
                {"day_of_week": 5, "start_time": time(8, 0), "end_time": time(17, 0)}
            ],
            "skills": [],  # Home services will be added later
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["liam.lundgren@email.se"],
                "location_id": locations["gustafsson-home-services:Stockholm North Office"],
                "job_title": "Cleaning Specialist",
                "bio": "Detail-oriented professional cleaner.",
                "color_code": "#FFC107",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 2, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 3, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 5, "start_time": time(8, 0), "end_time": time(16, 0)}
            ],
            "skills": [],
            "internal_events": []
        },
        {
            "employee": {
                "user_id": users["noah.hedlund@email.se"],
                "location_id": locations["gustafsson-home-services:Stockholm North Office"],
                "job_title": "Handyman",
                "bio": "Skilled in repairs and maintenance.",
                "color_code": "#FF5722",
                "is_active": True
            },
            "working_hours": [
                {"day_of_week": 1, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 2, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 3, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(16, 0)},
                {"day_of_week": 5, "start_time": time(8, 0), "end_time": time(16, 0)}
            ],
            "skills": [],
            "internal_events": []
        }
    ]

    employee_count = 0
    working_hours_count = 0
    internal_events_count = 0
    skills_count = 0

    async with conn.cursor() as cur:
        for emp_data in employees_data:
            # Insert employee
            emp = emp_data["employee"]
            await cur.execute(
                """
                INSERT INTO employees (user_id, location_id, job_title, bio, color_code, is_active)
                VALUES (%(user_id)s, %(location_id)s, %(job_title)s, %(bio)s, %(color_code)s, %(is_active)s)
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                emp
            )
            result = await cur.fetchone()

            if result:
                employee_id = result[0]
                employee_count += 1

                # Insert working hours
                for wh in emp_data["working_hours"]:
                    await cur.execute(
                        """
                        INSERT INTO working_hours (employee_id, day_of_week, start_time, end_time)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (employee_id, wh["day_of_week"], wh["start_time"], wh["end_time"])
                    )
                    working_hours_count += 1

                # Insert internal events
                for event in emp_data["internal_events"]:
                    await cur.execute(
                        """
                        INSERT INTO internal_events (employee_id, type, start_time, end_time, description)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (employee_id, event["type"], event["start_time"], event["end_time"], event["description"])
                    )
                    internal_events_count += 1

                # Insert employee skills
                for skill in emp_data["skills"]:
                    # Find business slug from location
                    business_slug = None
                    for key, loc_id in locations.items():
                        if loc_id == emp["location_id"]:
                            business_slug = key.split(":")[0]
                            break

                    if business_slug:
                        variant_key = f"{business_slug}:{skill['service']}:{skill['variant']}"
                        variant_id = service_variants.get(variant_key)

                        if variant_id:
                            custom_price = skill.get("custom_price")
                            custom_duration = skill.get("custom_duration")

                            await cur.execute(
                                """
                                INSERT INTO employee_skills (employee_id, service_variant_id, custom_price, custom_duration)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                                """,
                                (employee_id, variant_id, custom_price, custom_duration)
                            )
                            skills_count += 1

    await conn.commit()
    print(f"✓ Seeded {employee_count} employees")
    print(f"✓ Seeded {working_hours_count} working hours")
    print(f"✓ Seeded {internal_events_count} internal events")
    print(f"✓ Seeded {skills_count} employee skills")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_employees(conn)
        await db.disconnect()

    asyncio.run(main())