from datetime import datetime
from typing import Optional
from uuid import UUID

from psycopg import AsyncConnection, sql

from app.core.exceptions import NotFoundError
from app.models.booking import BookingDetail, BookingResponse
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[BookingResponse]):
    """Repository for booking-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "bookings"

    async def create_booking(self, data: dict) -> BookingResponse:
        """Insert booking with default status and return with status name."""

        # Set default status if not provided
        if "status_id" not in data:
            data["status_id"] = 1  # Default: pending

        # Build INSERT query safely
        columns_sql = sql.SQL(", ").join([sql.Identifier(k) for k in data.keys()])
        placeholders = sql.SQL(", ").join([sql.SQL("%s")] * len(data))

        query = sql.Composed(
            [
                sql.SQL("INSERT INTO bookings ("),
                columns_sql,
                sql.SQL(") VALUES ("),
                placeholders,
                sql.SQL(""") RETURNING
                id, customer_id, location_id, employee_id, service_variant_id,
                start_time, end_time, total_price, customer_note, created_at,
                (SELECT name FROM booking_statuses WHERE id = bookings.status_id) as status
            """),
            ]
        )

        result = await self._execute_one(query, tuple(data.values()), BookingResponse)
        if result is None:
            raise NotFoundError("Failed to create booking")
        return result
        

    async def get_booking_by_id(self, booking_id: UUID) -> Optional[BookingDetail]:
        """Single booking with joins."""
        query = """
            SELECT
                b.id, b.customer_id, b.location_id, b.employee_id, b.service_variant_id,
                b.start_time, b.end_time, b.total_price, b.customer_note, b.created_at,
                bs.name as status,
                jsonb_build_object(
                    'id', u.id,
                    'email', u.email,
                    'first_name', u.first_name,
                    'last_name', u.last_name,
                    'mobile_number', u.mobile_number,
                    'role', r.name,
                    'is_active', u.is_active,
                    'created_at', u.created_at
                ) as customer,
                row_to_json(e.*) as employee,
                row_to_json(sv.*) as service
            FROM bookings b
            JOIN booking_statuses bs ON b.status_id = bs.id
            JOIN users u ON b.customer_id = u.id
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            JOIN employees e ON b.employee_id = e.id
            JOIN service_variants sv ON b.service_variant_id = sv.id
            WHERE b.id = %s
            LIMIT 1
        """
        return await self._execute_one(query, (booking_id,), BookingDetail)

    async def get_user_bookings(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BookingResponse]:
        """User's bookings with filters."""
        if status:
            query = """
                SELECT b.*, bs.name as status
                FROM bookings b
                JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.customer_id = %s AND bs.name = %s
                ORDER BY b.start_time DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, status, limit, offset)
        else:
            query = """
                SELECT b.*, bs.name as status
                FROM bookings b
                JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.customer_id = %s
                ORDER BY b.start_time DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, limit, offset)

        return await self._execute_many(query, params, BookingResponse)

    async def get_location_bookings(
        self, location_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[BookingResponse]:
        """Location's bookings (for providers)."""
        query = """
            SELECT b.*, bs.name as status
            FROM bookings b
            JOIN booking_statuses bs ON b.status_id = bs.id
            WHERE b.location_id = %s
            ORDER BY b.start_time DESC
            LIMIT %s OFFSET %s
        """
        return await self._execute_many(
            query, (location_id, limit, offset), BookingResponse
        )

    async def update_booking(
        self, booking_id: UUID, data: dict
    ) -> Optional[BookingResponse]:
        """Reschedule."""

        set_parts = [
            sql.SQL("{} = %s").format(sql.Identifier(key)) for key in data.keys()
        ]
        set_clause = sql.SQL(", ").join(set_parts)

        query = sql.Composed(
            [
                sql.SQL("UPDATE bookings SET "),
                set_clause,
                sql.SQL(""" WHERE id = %s RETURNING 
                id, customer_id, location_id, employee_id, service_variant_id,
                start_time, end_time, total_price, customer_note, created_at,
                (SELECT name FROM booking_statuses WHERE id = bookings.status_id) as status
            """),
            ]
        )

        return await self._execute_one(
            query, (*data.values(), booking_id), BookingResponse
        )

    async def update_booking_status(
        self, booking_id: UUID, status: str
    ) -> Optional[BookingResponse]:
        """Status change."""
        query = """
            UPDATE bookings
            SET status_id = (SELECT id FROM booking_statuses WHERE name = %s)
            WHERE id = %s
            RETURNING 
                id, customer_id, location_id, employee_id, service_variant_id,
                start_time, end_time, total_price, customer_note, created_at,
                (SELECT name FROM booking_statuses WHERE id = status_id) as status
        """
        return await self._execute_one(query, (status, booking_id), BookingResponse)

    async def delete_booking(self, booking_id: UUID) -> bool:
        """Cancel/delete."""
        return await self._delete(self.table, booking_id, soft=False)

    async def get_employee_bookings_in_range(
        self, employee_id: UUID, start_time: datetime, end_time: datetime
    ) -> list[BookingResponse]:
        """Conflict checking."""
        query = """
            SELECT b.*, bs.name as status
            FROM bookings b
            JOIN booking_statuses bs ON b.status_id = bs.id
            WHERE b.employee_id = %s
              AND bs.name NOT IN ('cancelled', 'no_show')
              AND (
                (b.start_time < %s AND b.end_time > %s) OR
                (b.start_time >= %s AND b.start_time < %s)
              )
            ORDER BY b.start_time ASC
        """
        return await self._execute_many(
            query,
            (employee_id, end_time, start_time, start_time, end_time),
            BookingResponse,
        )
