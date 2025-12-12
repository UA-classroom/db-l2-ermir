from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    """Review creation request."""

    booking_id: UUID
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Review response with user info."""

    id: UUID
    booking_id: UUID
    rating: int
    comment: Optional[str]
    created_at: AwareDatetime
    # User info from join
    user_id: UUID
    user_name: str
    user_email: str

    model_config = ConfigDict(from_attributes=True)


class FavoriteCreate(BaseModel):
    """Favorite creation request."""

    location_id: UUID


class FavoriteResponse(BaseModel):
    """Favorite response with location info."""

    user_id: UUID
    location_id: UUID
    created_at: AwareDatetime
    # Location info from join
    location_name: str
    business_id: UUID
    business_name: str

    model_config = ConfigDict(from_attributes=True)
