from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.api.deps import get_current_active_user, get_db_conn, verify_review_creation
from app.models.review import (
    FavoriteCreate,
    FavoriteResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.models.user import UserDB
from app.repositories.review_repository import ReviewRepository
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_review_service(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
) -> ReviewService:
    """Dependency to get ReviewService instance."""
    review_repo = ReviewRepository(conn)
    return ReviewService(review_repo)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Create a review for a booking.

    Note: Only one review per booking (UNIQUE constraint).
    """
    # Verify user owns the booking
    await verify_review_creation(review_data.booking_id, current_user, conn)

    return await review_service.create_review(review_data)


@router.get("/businesses/{location_id}/reviews", response_model=list[ReviewResponse])
async def get_business_reviews(
    location_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all reviews for a location."""
    repo = ReviewRepository(conn)
    return await repo.get_business_reviews(location_id, limit, offset)


@router.post(
    "/users/me/favorites",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite(
    favorite_data: FavoriteCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Add location to current user's favorites."""
    repo = ReviewRepository(conn)
    return await repo.add_favorite(current_user.id, favorite_data.location_id)


@router.delete(
    "/users/me/favorites/{location_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_favorite(
    location_id: UUID,
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Remove location from current user's favorites."""
    await review_service.remove_favorite(current_user.id, location_id)


@router.get("/users/me/favorites", response_model=list[FavoriteResponse])
async def get_my_favorites(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get current user's favorite locations."""
    repo = ReviewRepository(conn)
    return await repo.get_user_favorites(current_user.id, limit, offset)
