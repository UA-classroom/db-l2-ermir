from typing import List
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.models.review import FavoriteResponse, ReviewResponse
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[ReviewResponse]):
    """Repository for review and favorite-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "reviews"

    async def create_review(self, data: dict) -> ReviewResponse:
        """
        Create a review for a booking.

        Note: booking_id has UNIQUE constraint, so one review per booking.
        """
        query = """
            WITH inserted_review AS (
                INSERT INTO reviews (booking_id, rating, comment)
                VALUES (%s, %s, %s)
                RETURNING id, booking_id, rating, comment, created_at
            )
            SELECT 
                r.id, r.booking_id, r.rating, r.comment, r.created_at,
                u.id as user_id,
                u.first_name || ' ' || u.last_name as user_name,
                u.email as user_email
            FROM inserted_review r
            JOIN bookings b ON r.booking_id = b.id
            JOIN users u ON b.customer_id = u.id
        """

        async with self.conn.cursor(row_factory=class_row(ReviewResponse)) as cur:
            await cur.execute(
                query, (data["booking_id"], data["rating"], data.get("comment"))
            )
            result = await cur.fetchone()
            if not result:
                raise RuntimeError("Failed to create review")
            return result

    async def get_business_reviews(
        self, location_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[ReviewResponse]:
        """Get all reviews for a location (passed as location_id)."""
        query = """
            SELECT 
                r.id, r.booking_id, r.rating, r.comment, r.created_at,
                u.id as user_id,
                u.first_name || ' ' || u.last_name as user_name,
                u.email as user_email
            FROM reviews r
            JOIN bookings b ON r.booking_id = b.id
            JOIN users u ON b.customer_id = u.id
            WHERE b.location_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """

        async with self.conn.cursor(row_factory=class_row(ReviewResponse)) as cur:
            await cur.execute(query, (location_id, limit, offset))
            return await cur.fetchall()

    async def add_favorite(self, user_id: UUID, location_id: UUID) -> FavoriteResponse:
        """Add location to user's favorites."""
        query = """
            WITH inserted_favorite AS (
                INSERT INTO favorites (user_id, location_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, location_id) DO UPDATE SET user_id = EXCLUDED.user_id
                RETURNING user_id, location_id, created_at
            )
            SELECT 
                f.user_id, f.location_id, f.created_at,
                l.name as location_name,
                l.business_id,
                b.name as business_name
            FROM inserted_favorite f
            JOIN locations l ON f.location_id = l.id
            JOIN businesses b ON l.business_id = b.id
        """

        async with self.conn.cursor(row_factory=class_row(FavoriteResponse)) as cur:
            await cur.execute(query, (user_id, location_id))
            result = await cur.fetchone()
            if not result:
                raise RuntimeError("Failed to add favorite")
            return result

    async def remove_favorite(self, user_id: UUID, location_id: UUID) -> bool:
        """Remove location from user's favorites."""
        query = """
            DELETE FROM favorites
            WHERE user_id = %s AND location_id = %s
        """

        async with self.conn.cursor() as cur:
            await cur.execute(query, (user_id, location_id))
            return cur.rowcount > 0

    async def get_user_favorites(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[FavoriteResponse]:
        """Get user's favorite locations."""
        query = """
            SELECT 
                f.user_id, f.location_id, f.created_at,
                l.name as location_name,
                l.business_id,
                b.name as business_name
            FROM favorites f
            JOIN locations l ON f.location_id = l.id
            JOIN businesses b ON l.business_id = b.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
            LIMIT %s OFFSET %s
        """

        async with self.conn.cursor(row_factory=class_row(FavoriteResponse)) as cur:
            await cur.execute(query, (user_id, limit, offset))
            return await cur.fetchall()
