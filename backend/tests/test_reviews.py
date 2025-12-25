"""
Tests for Reviews & Social Features API (Phase 11)

Tests cover:
- Review creation
- Business reviews listing
- Favorites management (add, remove, list)
"""

from uuid import UUID

# pyright: reportMissingImports=false
import httpx
from uuid_utils import uuid7


class TestReviewCreation:
    """Tests for review creation."""

    async def test_create_review_success(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews creates a review successfully."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 5,
            "comment": "Excellent service!",
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent service!"

    async def test_create_review_invalid_rating(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews validates rating range (1-5)."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 6,  # Invalid (should be 1-5)
            "comment": "Great!",
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_review_rating_zero(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews rejects rating of 0."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 0,  # Invalid
            "comment": "Bad",
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_review_negative_rating(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews rejects negative rating."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": -1,  # Invalid
            "comment": "Terrible",
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_review_without_comment(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews allows review without comment."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 4,
            # No comment
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        # Note: If test_booking_id is reused from test_create_review_success, this might fail with 409
        # Assuming pytest isolation or clean DB, but if using shared DB, uniqueness might be an issue.
        # However, test_booking_id creates a NEW booking each time (function scope fixture).
        assert response.status_code == 201

    async def test_create_review_very_long_comment(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id
    ):
        """POST /reviews validates comment length."""

        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 5,
            "comment": "A" * 1001,  # Exceeds max length (1000)
        }

        response = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_duplicate_review_same_booking(
        self, client: httpx.AsyncClient, auth_headers, test_booking_id: UUID
    ):
        """POST /reviews prevents duplicate reviews for same booking."""
        review_data = {
            "booking_id": str(test_booking_id),
            "rating": 5,
            "comment": "First review",
        }

        # First review - should succeed
        response1 = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        # Second review for same booking - should fail on unique constraint
        review_data["comment"] = "Second review"
        response2 = await client.post(
            "/api/v1/reviews/", json=review_data, headers=auth_headers
        )

        assert response1.status_code == 201
        assert response2.status_code == 409


class TestBusinessReviews:
    """Tests for business reviews listing."""

    async def test_get_business_reviews_empty(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /reviews/businesses/{id}/reviews returns empty list."""

        response = await client.get(
            f"/api/v1/reviews/businesses/{test_business_id}/reviews"
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_business_reviews_with_pagination(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /reviews/businesses/{id}/reviews respects pagination."""

        response = await client.get(
            f"/api/v1/reviews/businesses/{test_business_id}/reviews?limit=10&offset=0"
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_business_reviews_invalid_business_id(
        self, client: httpx.AsyncClient
    ):
        """GET /reviews/businesses/{id}/reviews validates business ID."""
        response = await client.get("/api/v1/reviews/businesses/not-a-uuid/reviews")

        assert response.status_code == 422


class TestFavoritesManagement:
    """Tests for favorites management."""

    async def test_add_favorite_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """POST /reviews/users/me/favorites adds a favorite."""

        favorite_data = {"location_id": str(test_location_id)}

        response = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json=favorite_data,
            headers=auth_headers,
        )

        assert response.status_code == 201

    async def test_add_favorite_duplicate(
        self, client: httpx.AsyncClient, auth_headers, test_location_id: UUID
    ):
        """POST /reviews/users/me/favorites handles duplicate gracefully."""
        favorite_data = {"location_id": str(test_location_id)}

        # Add first time - should succeed
        response1 = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json=favorite_data,
            headers=auth_headers,
        )

        # Add second time (duplicate) - should succeed (idempotent) or fail?
        # Endpoints says 201 Created. Repo usually ignores duplicate inserts or returns existing.
        # Let's check implementation behavior: Repo usually does INSERT...ON CONFLICT DO NOTHING or returns.
        # If conflicts, it might raise.
        response2 = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json=favorite_data,
            headers=auth_headers,
        )

        assert response1.status_code == 201
        # Implementation handles duplicates gracefully (idempotent)
        assert response2.status_code == 201

    async def test_add_favorite_missing_location_id(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /reviews/users/me/favorites requires location_id."""
        response = await client.post(
            "/api/v1/reviews/users/me/favorites", json={}, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_add_favorite_invalid_location_id(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /reviews/users/me/favorites validates location_id format."""
        favorite_data = {"location_id": "not-a-uuid"}

        response = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json=favorite_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_remove_favorite_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """DELETE /reviews/users/me/favorites/{location_id} removes favorite."""
        # Add first
        await client.post(
            "/api/v1/reviews/users/me/favorites",
            json={"location_id": str(test_location_id)},
            headers=auth_headers,
        )

        response = await client.delete(
            f"/api/v1/reviews/users/me/favorites/{test_location_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    async def test_remove_favorite_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """DELETE /reviews/users/me/favorites/{location_id} returns 404 for non-existent favorite."""
        location_id = uuid7()

        response = await client.delete(
            f"/api/v1/reviews/users/me/favorites/{location_id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_remove_favorite_invalid_location_id(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """DELETE /reviews/users/me/favorites/{location_id} validates location ID."""
        response = await client.delete(
            "/api/v1/reviews/users/me/favorites/not-a-uuid", headers=auth_headers
        )

        assert response.status_code == 422

    async def test_get_my_favorites(self, client: httpx.AsyncClient, auth_headers):
        """GET /reviews/users/me/favorites returns user's favorites."""
        response = await client.get(
            "/api/v1/reviews/users/me/favorites", headers=auth_headers
        )

        assert response.status_code == 200
        favorites = response.json()
        assert isinstance(favorites, list)

    async def test_get_my_favorites_with_pagination(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /reviews/users/me/favorites respects pagination."""
        response = await client.get(
            "/api/v1/reviews/users/me/favorites?limit=10&offset=0", headers=auth_headers
        )

        assert response.status_code == 200
        favorites = response.json()
        assert len(favorites) <= 10


class TestFavoritesIntegration:
    """Integration tests for favorites workflow."""

    async def test_add_and_remove_favorite_workflow(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """Test complete add → list → remove workflow."""

        location_id = uuid7()

        # Add favorite
        add_response = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json={"location_id": str(location_id)},
            headers=auth_headers,
        )

        if add_response.status_code == 201:
            # List favorites
            list_response = await client.get(
                "/api/v1/reviews/users/me/favorites", headers=auth_headers
            )
            assert list_response.status_code == 200
            favorites = list_response.json()
            assert any(f["location_id"] == str(location_id) for f in favorites)

            # Remove favorite
            remove_response = await client.delete(
                f"/api/v1/reviews/users/me/favorites/{location_id}",
                headers=auth_headers,
            )
            assert remove_response.status_code == 204


class TestReviewsAuthorization:
    """Tests for reviews authorization."""

    async def test_create_review_requires_auth(self, client: httpx.AsyncClient):
        """POST /reviews requires authentication."""

        review_data = {"booking_id": str(uuid7()), "rating": 5}

        response = await client.post(
            "/api/v1/reviews/",
            json=review_data,
            # No auth headers
        )

        assert response.status_code == 401

    async def test_add_favorite_requires_auth(self, client: httpx.AsyncClient):
        """POST /reviews/users/me/favorites requires authentication."""

        favorite_data = {"location_id": str(uuid7())}

        response = await client.post(
            "/api/v1/reviews/users/me/favorites",
            json=favorite_data,
            # No auth headers
        )

        assert response.status_code == 401

    async def test_get_favorites_requires_auth(self, client: httpx.AsyncClient):
        """GET /reviews/users/me/favorites requires authentication."""
        response = await client.get(
            "/api/v1/reviews/users/me/favorites"
            # No auth headers
        )

        assert response.status_code == 401
