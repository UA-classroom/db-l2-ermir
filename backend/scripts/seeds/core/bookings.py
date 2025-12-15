"""Seed bookings table with test data."""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from psycopg import AsyncConnection


async def seed_bookings(conn: AsyncConnection) -> None:
    """Insert test bookings with various statuses."""

    # Get user IDs (customers)
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT id, email FROM users
            WHERE email LIKE '%@email.se'
            ORDER BY email
        """)
        customer_rows = await cur.fetchall()
        customers = {email: user_id for user_id, email in customer_rows}

    # Get employee IDs with their locations
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT e.id, u.email, l.id as location_id, b.slug as business_slug
            FROM employees e
            JOIN users u ON e.user_id = u.id
            JOIN locations l ON e.location_id = l.id
            JOIN businesses b ON l.business_id = b.id
            ORDER BY u.email
        """)
        employee_rows = await cur.fetchall()
        employees = {}
        for emp_id, email, loc_id, biz_slug in employee_rows:
            employees[email] = {
                "id": emp_id,
                "location_id": loc_id,
                "business_slug": biz_slug,
            }

    # Get service variant IDs with prices
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT sv.id, s.name as service_name, sv.name as variant_name,
                   sv.price, sv.duration_minutes, b.slug as business_slug
            FROM service_variants sv
            JOIN services s ON sv.service_id = s.id
            JOIN businesses b ON s.business_id = b.id
        """)
        variant_rows = await cur.fetchall()
        service_variants = {}
        for var_id, svc_name, var_name, price, duration, biz_slug in variant_rows:
            key = f"{biz_slug}:{svc_name}:{var_name}"
            service_variants[key] = {"id": var_id, "price": price, "duration": duration}

    # Get booking status IDs
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, name FROM booking_statuses")
        status_rows = await cur.fetchall()
        statuses = {name: status_id for status_id, name in status_rows}

    # Helper function to create booking time
    def booking_time(days_offset, hour, minute=0):
        """Create booking datetime relative to today."""
        base = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        return base + timedelta(days=days_offset)

    # Define bookings (mix of past completed, upcoming, and cancelled)
    bookings_data = [
        # ===== NIKITA HAIR SALON - COMPLETED BOOKINGS (Past) =====
        {
            "customer": "emma.svensson@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Women's Haircut",
            "variant": "Medium Hair",
            "start_offset_days": -30,
            "start_hour": 10,
            "status": "completed",
        },
        {
            "customer": "linnea.olsson@email.se",
            "employee": "emma.svensson@email.se",
            "service": "Women's Haircut",
            "variant": "Long Hair",
            "start_offset_days": -28,
            "start_hour": 14,
            "status": "completed",
        },
        {
            "customer": "maja.eriksson@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Highlights",
            "variant": "Balayage",
            "start_offset_days": -25,
            "start_hour": 10,
            "status": "completed",
        },
        {
            "customer": "alice.pettersson@email.se",
            "employee": "emma.svensson@email.se",
            "service": "Hair Treatment",
            "variant": "Basic Treatment",
            "start_offset_days": -22,
            "start_hour": 16,
            "status": "completed",
        },
        {
            "customer": "ella.samuelsson@email.se",
            "employee": "linnea.olsson@email.se",
            "service": "Men's Haircut",
            "variant": "Standard Cut",
            "start_offset_days": -20,
            "start_hour": 11,
            "status": "completed",
        },
        {
            "customer": "wilma.sandberg@email.se",
            "employee": "maja.eriksson@email.se",
            "service": "Women's Haircut",
            "variant": "Short Hair",
            "start_offset_days": -18,
            "start_hour": 13,
            "status": "completed",
        },
        {
            "customer": "ebba.carlsson@email.se",
            "employee": "alice.pettersson@email.se",
            "service": "Full Hair Coloring",
            "variant": "Single Color - Long",
            "start_offset_days": -15,
            "start_hour": 9,
            "status": "completed",
        },
        {
            "customer": "astrid.forsberg@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Highlights",
            "variant": "Full Highlights",
            "start_offset_days": -12,
            "start_hour": 10,
            "status": "completed",
        },
        {
            "customer": "vera.lundqvist@email.se",
            "employee": "ella.samuelsson@email.se",
            "service": "Women's Haircut",
            "variant": "Medium Hair",
            "start_offset_days": -10,
            "start_hour": 14,
            "status": "completed",
        },
        {
            "customer": "saga.holmberg@email.se",
            "employee": "wilma.sandberg@email.se",
            "service": "Hair Treatment",
            "variant": "Olaplex Repair",
            "start_offset_days": -8,
            "start_hour": 11,
            "status": "completed",
        },
        {
            "customer": "emma.svensson@email.se",
            "employee": "maja.eriksson@email.se",
            "service": "Highlights",
            "variant": "Partial Highlights",
            "start_offset_days": -7,
            "start_hour": 10,
            "status": "completed",
        },
        {
            "customer": "linnea.olsson@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Full Hair Coloring",
            "variant": "Single Color - Medium",
            "start_offset_days": -5,
            "start_hour": 9,
            "status": "completed",
        },
        # ===== NIKITA HAIR SALON - CONFIRMED BOOKINGS (Upcoming) =====
        {
            "customer": "maja.eriksson@email.se",
            "employee": "emma.svensson@email.se",
            "service": "Women's Haircut",
            "variant": "Short Hair",
            "start_offset_days": 2,
            "start_hour": 10,
            "status": "confirmed",
        },
        {
            "customer": "alice.pettersson@email.se",
            "employee": "linnea.olsson@email.se",
            "service": "Men's Haircut",
            "variant": "Standard Cut",
            "start_offset_days": 3,
            "start_hour": 11,
            "status": "confirmed",
        },
        {
            "customer": "ella.samuelsson@email.se",
            "employee": "maja.eriksson@email.se",
            "service": "Women's Haircut",
            "variant": "Long Hair",
            "start_offset_days": 4,
            "start_hour": 14,
            "status": "confirmed",
        },
        {
            "customer": "wilma.sandberg@email.se",
            "employee": "alice.pettersson@email.se",
            "service": "Highlights",
            "variant": "Balayage",
            "start_offset_days": 5,
            "start_hour": 10,
            "status": "confirmed",
        },
        {
            "customer": "ebba.carlsson@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Hair Treatment",
            "variant": "Keratin Treatment",
            "start_offset_days": 6,
            "start_hour": 9,
            "status": "confirmed",
        },
        {
            "customer": "astrid.forsberg@email.se",
            "employee": "ella.samuelsson@email.se",
            "service": "Women's Haircut",
            "variant": "Medium Hair",
            "start_offset_days": 7,
            "start_hour": 13,
            "status": "confirmed",
        },
        # ===== NIKITA HAIR SALON - PENDING/CANCELLED =====
        {
            "customer": "vera.lundqvist@email.se",
            "employee": "wilma.sandberg@email.se",
            "service": "Women's Haircut",
            "variant": "Short Hair",
            "start_offset_days": 8,
            "start_hour": 10,
            "status": "pending",
        },
        {
            "customer": "saga.holmberg@email.se",
            "employee": "maja.eriksson@email.se",
            "service": "Men's Haircut",
            "variant": "Premium Cut & Beard Trim",
            "start_offset_days": -3,
            "start_hour": 15,
            "status": "cancelled",
        },
        {
            "customer": "emma.svensson@email.se",
            "employee": "nikita@hairsalon.se",
            "service": "Full Hair Coloring",
            "variant": "Single Color - Long",
            "start_offset_days": -2,
            "start_hour": 10,
            "status": "no_show",
        },
        # ===== MARIO'S ITALIAN RESTAURANT - COMPLETED =====
        {
            "customer": "oskar.larsson@email.se",
            "employee": "mario@restaurant.se",
            "service": "Dinner Reservation",
            "variant": "2 Person Table",
            "start_offset_days": -14,
            "start_hour": 19,
            "status": "completed",
        },
        {
            "customer": "alexander.persson@email.se",
            "employee": "oskar.larsson@email.se",
            "service": "Dinner Reservation",
            "variant": "4 Person Table",
            "start_offset_days": -10,
            "start_hour": 18,
            "status": "completed",
        },
        {
            "customer": "william.gustafsson@email.se",
            "employee": "alexander.persson@email.se",
            "service": "Dinner Reservation",
            "variant": "2 Person Table",
            "start_offset_days": -7,
            "start_hour": 20,
            "status": "completed",
        },
        {
            "customer": "lucas.jonsson@email.se",
            "employee": "mario@restaurant.se",
            "service": "Cooking Class",
            "variant": "Pasta Making Class",
            "start_offset_days": -6,
            "start_hour": 15,
            "status": "completed",
        },
        {
            "customer": "hugo.jakobsson@email.se",
            "employee": "oskar.larsson@email.se",
            "service": "Private Event",
            "variant": "10-15 Guests",
            "start_offset_days": -4,
            "start_hour": 18,
            "status": "completed",
        },
        # ===== MARIO'S ITALIAN RESTAURANT - CONFIRMED =====
        {
            "customer": "elias.berg@email.se",
            "employee": "alexander.persson@email.se",
            "service": "Dinner Reservation",
            "variant": "6+ Person Table",
            "start_offset_days": 3,
            "start_hour": 19,
            "status": "confirmed",
        },
        {
            "customer": "liam.lundgren@email.se",
            "employee": "mario@restaurant.se",
            "service": "Cooking Class",
            "variant": "Pizza Master Class",
            "start_offset_days": 5,
            "start_hour": 16,
            "status": "confirmed",
        },
        {
            "customer": "noah.hedlund@email.se",
            "employee": "oskar.larsson@email.se",
            "service": "Dinner Reservation",
            "variant": "4 Person Table",
            "start_offset_days": 7,
            "start_hour": 18,
            "status": "confirmed",
        },
        {
            "customer": "oliver.wallin@email.se",
            "employee": "alexander.persson@email.se",
            "service": "Private Event",
            "variant": "16-25 Guests",
            "start_offset_days": 14,
            "start_hour": 17,
            "status": "confirmed",
        },
        # ===== MARIO'S ITALIAN RESTAURANT - CANCELLED =====
        {
            "customer": "adam.bjork@email.se",
            "employee": "mario@restaurant.se",
            "service": "Dinner Reservation",
            "variant": "2 Person Table",
            "start_offset_days": -1,
            "start_hour": 19,
            "status": "cancelled",
        },
        # ===== FITZONE GYM - COMPLETED =====
        {
            "customer": "oskar.larsson@email.se",
            "employee": "erik@gym.se",
            "service": "Personal Training Session",
            "variant": "Single Session",
            "start_offset_days": -20,
            "start_hour": 7,
            "status": "completed",
        },
        {
            "customer": "alexander.persson@email.se",
            "employee": "william.gustafsson@email.se",
            "service": "Yoga Class",
            "variant": "Drop-in Class",
            "start_offset_days": -18,
            "start_hour": 18,
            "status": "completed",
        },
        {
            "customer": "william.gustafsson@email.se",
            "employee": "lucas.jonsson@email.se",
            "service": "HIIT Training",
            "variant": "Drop-in Class",
            "start_offset_days": -16,
            "start_hour": 17,
            "status": "completed",
        },
        {
            "customer": "lucas.jonsson@email.se",
            "employee": "erik@gym.se",
            "service": "Personal Training Session",
            "variant": "5 Session Package",
            "start_offset_days": -15,
            "start_hour": 8,
            "status": "completed",
        },
        {
            "customer": "hugo.jakobsson@email.se",
            "employee": "lucas.jonsson@email.se",
            "service": "Spinning Class",
            "variant": "Drop-in Class",
            "start_offset_days": -13,
            "start_hour": 18,
            "status": "completed",
        },
        {
            "customer": "elias.berg@email.se",
            "employee": "william.gustafsson@email.se",
            "service": "Yoga Class",
            "variant": "10 Class Package",
            "start_offset_days": -11,
            "start_hour": 19,
            "status": "completed",
        },
        {
            "customer": "liam.lundgren@email.se",
            "employee": "erik@gym.se",
            "service": "Personal Training Session",
            "variant": "Single Session",
            "start_offset_days": -9,
            "start_hour": 9,
            "status": "completed",
        },
        {
            "customer": "noah.hedlund@email.se",
            "employee": "lucas.jonsson@email.se",
            "service": "HIIT Training",
            "variant": "10 Class Package",
            "start_offset_days": -8,
            "start_hour": 17,
            "status": "completed",
        },
        # ===== FITZONE GYM - CONFIRMED =====
        {
            "customer": "oliver.wallin@email.se",
            "employee": "erik@gym.se",
            "service": "Personal Training Session",
            "variant": "10 Session Package",
            "start_offset_days": 1,
            "start_hour": 7,
            "status": "confirmed",
        },
        {
            "customer": "adam.bjork@email.se",
            "employee": "william.gustafsson@email.se",
            "service": "Yoga Class",
            "variant": "Monthly Unlimited",
            "start_offset_days": 2,
            "start_hour": 18,
            "status": "confirmed",
        },
        {
            "customer": "oskar.larsson@email.se",
            "employee": "lucas.jonsson@email.se",
            "service": "Spinning Class",
            "variant": "10 Class Package",
            "start_offset_days": 3,
            "start_hour": 19,
            "status": "confirmed",
        },
        {
            "customer": "alexander.persson@email.se",
            "employee": "erik@gym.se",
            "service": "Personal Training Session",
            "variant": "Single Session",
            "start_offset_days": 4,
            "start_hour": 10,
            "status": "confirmed",
        },
        {
            "customer": "william.gustafsson@email.se",
            "employee": "lucas.jonsson@email.se",
            "service": "HIIT Training",
            "variant": "Drop-in Class",
            "start_offset_days": 5,
            "start_hour": 18,
            "status": "confirmed",
        },
        # ===== BERGSTRÖM SPA & WELLNESS - COMPLETED =====
        {
            "customer": "emma.svensson@email.se",
            "employee": "sofia@spa.se",
            "service": "Swedish Massage",
            "variant": "60 Minutes",
            "start_offset_days": -21,
            "start_hour": 11,
            "status": "completed",
        },
        {
            "customer": "linnea.olsson@email.se",
            "employee": "ebba.carlsson@email.se",
            "service": "Swedish Massage",
            "variant": "90 Minutes",
            "start_offset_days": -17,
            "start_hour": 14,
            "status": "completed",
        },
        {
            "customer": "maja.eriksson@email.se",
            "employee": "sofia@spa.se",
            "service": "Deep Tissue Massage",
            "variant": "60 Minutes",
            "start_offset_days": -14,
            "start_hour": 10,
            "status": "completed",
        },
        {
            "customer": "alice.pettersson@email.se",
            "employee": "ebba.carlsson@email.se",
            "service": "Swedish Massage",
            "variant": "30 Minutes",
            "start_offset_days": -11,
            "start_hour": 16,
            "status": "completed",
        },
        {
            "customer": "ella.samuelsson@email.se",
            "employee": "sofia@spa.se",
            "service": "Deep Tissue Massage",
            "variant": "90 Minutes",
            "start_offset_days": -9,
            "start_hour": 12,
            "status": "completed",
        },
        {
            "customer": "wilma.sandberg@email.se",
            "employee": "ebba.carlsson@email.se",
            "service": "Swedish Massage",
            "variant": "60 Minutes",
            "start_offset_days": -6,
            "start_hour": 15,
            "status": "completed",
        },
        # ===== BERGSTRÖM SPA & WELLNESS - CONFIRMED =====
        {
            "customer": "ebba.carlsson@email.se",
            "employee": "sofia@spa.se",
            "service": "Swedish Massage",
            "variant": "90 Minutes",
            "start_offset_days": 2,
            "start_hour": 11,
            "status": "confirmed",
        },
        {
            "customer": "astrid.forsberg@email.se",
            "employee": "ebba.carlsson@email.se",
            "service": "Swedish Massage",
            "variant": "60 Minutes",
            "start_offset_days": 4,
            "start_hour": 14,
            "status": "confirmed",
        },
        {
            "customer": "vera.lundqvist@email.se",
            "employee": "sofia@spa.se",
            "service": "Deep Tissue Massage",
            "variant": "60 Minutes",
            "start_offset_days": 6,
            "start_hour": 10,
            "status": "confirmed",
        },
        {
            "customer": "saga.holmberg@email.se",
            "employee": "ebba.carlsson@email.se",
            "service": "Swedish Massage",
            "variant": "30 Minutes",
            "start_offset_days": 8,
            "start_hour": 16,
            "status": "confirmed",
        },
        # ===== BERGSTRÖM SPA & WELLNESS - NO SHOW =====
        {
            "customer": "emma.svensson@email.se",
            "employee": "sofia@spa.se",
            "service": "Swedish Massage",
            "variant": "60 Minutes",
            "start_offset_days": -3,
            "start_hour": 11,
            "status": "no_show",
        },
        # ===== MANUALLY ADDED FOR REVIEW TESTING =====
        {
            "customer": "emma.svensson@email.se",
            "employee": "sofia@spa.se",
            "service": "Swedish Massage",
            "variant": "60 Minutes",
            "start_offset_days": -2,
            "start_hour": 14,
            "status": "completed",
        },
    ]

    booking_count = 0
    async with conn.cursor() as cur:
        for booking_data in bookings_data:
            # Get employee info
            emp_info = employees.get(booking_data["employee"])
            if not emp_info:
                continue

            # Get service variant info
            variant_key = f"{emp_info['business_slug']}:{booking_data['service']}:{booking_data['variant']}"
            variant_info = service_variants.get(variant_key)
            if not variant_info:
                continue

            # Calculate booking times
            start_time = booking_time(
                booking_data["start_offset_days"], booking_data["start_hour"]
            )
            end_time = start_time + timedelta(minutes=variant_info["duration"])

            # Insert booking
            await cur.execute(
                """
                INSERT INTO bookings (
                    customer_id, location_id, employee_id, service_variant_id,
                    status_id, start_time, end_time, total_price, customer_note
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    customers[booking_data["customer"]],
                    emp_info["location_id"],
                    emp_info["id"],
                    variant_info["id"],
                    statuses[booking_data["status"]],
                    start_time,
                    end_time,
                    variant_info["price"],
                    None,
                ),
            )
            booking_count += 1

    await conn.commit()
    print(f"✓ Seeded {booking_count} bookings")


if __name__ == "__main__":
    from app.core.database import db

    async def main():
        await db.connect()
        async with db.get_connection() as conn:
            await seed_bookings(conn)
        await db.disconnect()

    asyncio.run(main())
