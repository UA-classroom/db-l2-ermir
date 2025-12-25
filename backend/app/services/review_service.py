from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.review import ReviewCreate, ReviewResponse
from app.repositories.review_repository import ReviewRepository


class ReviewService:
    """Service for review and favorite-related business logic."""

    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    async def create_review(self, review_data: ReviewCreate) -> ReviewResponse:
        """
        Create a review for a booking.

        Business logic:
        - Converts database unique constraint violation to ConflictError
        - One review per booking (enforced by database UNIQUE constraint)

        Args:
            review_data: Review creation data

        Returns:
            Created review with user info

        Raises:
            ConflictError: If review already exists for this booking
        """
        try:
            return await self.review_repo.create_review(review_data.model_dump())
        except Exception as e:
            # Check if it's a unique constraint violation (psycopg exception)
            if "unique constraint" in str(e).lower() or "already exists" in str(e).lower():
                raise ConflictError(
                    f"Review already exists for booking {review_data.booking_id}"
                )
            raise

    async def remove_favorite(self, user_id: UUID, location_id: UUID) -> bool:
        """
        Remove location from user's favorites.

        Business logic:
        - Converts False return to NotFoundError exception

        Returns:
            True if favorite was removed

        Raises:
            NotFoundError: If favorite doesn't exist
        """
        removed = await self.review_repo.remove_favorite(user_id, location_id)
        if not removed:
            raise NotFoundError(
                f"Favorite for location {location_id} not found for user {user_id}"
            )
        return removed