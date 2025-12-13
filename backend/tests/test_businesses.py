"""
Tests for Business & Location API (Phase 4)

Tests cover:
- Business search with filters
- Business details
- Locations listing
- Contacts management
"""
# pyright: reportMissingImports=false
import httpx
from uuid_utils import uuid7


class TestBusinessSearch:
    """Tests for business search functionality."""

    async def test_get_businesses_empty(self, client: httpx.AsyncClient):
        """GET /businesses returns empty list when no businesses exist."""
        response = await client.get("/api/v1/businesses/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_businesses_with_pagination(self, client: httpx.AsyncClient):
        """GET /businesses respects pagination parameters."""
        response = await client.get("/api/v1/businesses/?skip=0&limit=10")

        assert response.status_code == 200
        businesses = response.json()
        assert len(businesses) <= 10

    async def test_search_businesses_by_name(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /businesses filters by name."""
        response = await client.get("/api/v1/businesses/?name=Test")

        assert response.status_code == 200
        businesses = response.json()
        # Should include test business
        assert any("Test" in b["name"] for b in businesses) or len(businesses) == 0

    async def test_search_businesses_by_city(self, client: httpx.AsyncClient):
        """GET /businesses filters by city."""
        response = await client.get("/api/v1/businesses/?city=Stockholm")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestBusinessDetails:
    """Tests for business details endpoints."""

    async def test_get_business_by_id(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /businesses/{id} returns business details."""
        response = await client.get(f"/api/v1/businesses/{test_business_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_business_id)
        assert data["name"] == "Test Business"
        assert "owner_id" in data

    async def test_get_business_not_found(self, client: httpx.AsyncClient):
        """GET /businesses/{id} returns 404 for non-existent business."""

        fake_id = uuid7()

        response = await client.get(f"/api/v1/businesses/{fake_id}")

        assert response.status_code == 404

    async def test_get_business_invalid_uuid(self, client: httpx.AsyncClient):
        """GET /businesses/{id} validates UUID format."""
        response = await client.get("/api/v1/businesses/not-a-uuid")

        assert response.status_code == 422


class TestBusinessLocations:
    """Tests for business locations."""

    async def test_get_business_locations(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /businesses/{id}/locations returns locations for business."""
        response = await client.get(f"/api/v1/businesses/{test_business_id}/locations")

        assert response.status_code == 200
        locations = response.json()
        assert isinstance(locations, list)

    async def test_get_locations_for_nonexistent_business(
        self, client: httpx.AsyncClient
    ):
        """GET /businesses/{id}/locations returns 404 for non-existent business."""

        fake_id = uuid7()

        response = await client.get(f"/api/v1/businesses/{fake_id}/locations")

        assert response.status_code == 404


class TestBusinessServices:
    """Tests for business services."""

    async def test_get_business_services(
        self, client: httpx.AsyncClient, test_business_id
    ):
        """GET /businesses/{id}/services returns services for business."""
        response = await client.get(f"/api/v1/businesses/{test_business_id}/services")

        assert response.status_code == 200
        services = response.json()
        assert isinstance(services, list)

    async def test_get_services_for_nonexistent_business(
        self, client: httpx.AsyncClient
    ):
        """GET /businesses/{id}/services returns 404 for non-existent business."""

        fake_id = uuid7()

        response = await client.get(f"/api/v1/businesses/{fake_id}/services")

        assert response.status_code == 404


class TestLocationContacts:
    """Tests for location contacts."""

    async def test_get_location_contacts_empty(self, client: httpx.AsyncClient):
        """GET /locations/{id}/contacts returns empty list when no contacts exist."""

        fake_location_id = uuid7()

        response = await client.get(
            f"/api/v1/businesses/locations/{fake_location_id}/contacts"
        )

        # Should return 404 if location doesn't exist, or empty list if it does
        assert response.status_code in [200, 404]


class TestBusinessCreation:
    """Tests for business creation (provider endpoints)."""

    async def test_create_business_success(
        self, client: httpx.AsyncClient, auth_headers, test_user_id, request
    ):
        """POST /businesses creates a new business."""
        user_id, email = test_user_id
        test_id = request.node.name
        business_data = {
            "owner_id": str(user_id),
            "name": f"New Business {test_id}",
            "org_number": "123456-7890",
            "slug": f"new-business-{test_id}",
        }

        response = await client.post(
            "/api/v1/businesses/", json=business_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == business_data["name"]
        assert data["slug"] == business_data["slug"]
        assert "id" in data

    async def test_create_business_duplicate_slug(
        self, client: httpx.AsyncClient, auth_headers, test_user_id, test_business_id
    ):
        """POST /businesses fails with duplicate slug."""
        user_id, email = test_user_id
        business_data = {
            "owner_id": str(user_id),
            "name": "Another Business",
            "org_number": "987654-3210",
            "slug": "test-business",  # Already exists from fixture
        }

        response = await client.post(
            "/api/v1/businesses/", json=business_data, headers=auth_headers
        )

        assert response.status_code == 409

    async def test_create_business_duplicate_org_number(
        self, client: httpx.AsyncClient, auth_headers, test_user_id, test_business_id
    ):
        """POST /businesses fails with duplicate org_number."""
        user_id, email = test_user_id
        business_data = {
            "owner_id": str(user_id),
            "name": "Another Business",
            "org_number": "123456-7890",  # Already exists from fixture
            "slug": "different-slug",
        }

        response = await client.post(
            "/api/v1/businesses/", json=business_data, headers=auth_headers
        )

        assert response.status_code == 409

    async def test_create_business_missing_required_fields(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /businesses fails when required fields are missing."""
        business_data = {
            "name": "Incomplete Business"
            # Missing owner_id, org_number, slug
        }

        response = await client.post(
            "/api/v1/businesses/", json=business_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_update_business_success(
        self, client: httpx.AsyncClient, auth_headers, test_business_id
    ):
        """PUT /businesses/{id} updates business details."""
        update_data = {"name": "Updated Business Name"}

        response = await client.put(
            f"/api/v1/businesses/{test_business_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Business Name"

    async def test_update_business_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /businesses/{id} returns 404 for non-existent business."""

        fake_id = uuid7()
        update_data = {"name": "Updated"}

        response = await client.put(
            f"/api/v1/businesses/{fake_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404


class TestLocationCRUD:
    """Tests for location CRUD."""

    async def test_create_location_success(
        self, client: httpx.AsyncClient, auth_headers, test_business_id, request
    ):
        """POST /businesses/{id}/locations creates a new location."""
        test_id = request.node.name
        location_data = {
            "business_id": str(test_business_id),
            "name": f"New Location {test_id}",
            "address": "New Address 123",
            "city": "Stockholm",
            "postal_code": "10000",
        }

        response = await client.post(
            f"/api/v1/businesses/{test_business_id}/locations",
            json=location_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == location_data["name"]
        assert "id" in data

    async def test_update_location_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """PUT /businesses/locations/{id} updates location."""
        update_data = {"name": "Updated Location Name", "city": "Gothenburg"}

        response = await client.put(
            f"/api/v1/businesses/locations/{test_location_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Location Name"
        assert data["city"] == "Gothenburg"

    async def test_update_location_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /businesses/locations/{id} returns 404 for non-existent location."""

        fake_id = uuid7()
        update_data = {"name": "Updated"}

        response = await client.put(
            f"/api/v1/businesses/locations/{fake_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestContactCRUD:
    """Tests for contact CRUD."""

    async def test_create_contact_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """POST /businesses/locations/{id}/contacts creates a new contact."""
        contact_data = {
            "location_id": str(test_location_id),
            "contact_type": "Reception",
            "phone_number": "+46701234567",
        }

        response = await client.post(
            f"/api/v1/businesses/locations/{test_location_id}/contacts",
            json=contact_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["contact_type"] == "Reception"
        assert data["phone_number"] == "+46701234567"
        assert "id" in data

    async def test_update_contact_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """PUT /businesses/location-contacts/{id} updates contact."""
        # Create contact first
        contact_data = {
            "location_id": str(test_location_id),
            "contact_type": "Manager",
            "phone_number": "+46700000000",
        }
        create_resp = await client.post(
            f"/api/v1/businesses/locations/{test_location_id}/contacts",
            json=contact_data,
            headers=auth_headers,
        )
        contact_id = create_resp.json()["id"]

        # Update
        update_data = {"phone_number": "+46799999999"}
        response = await client.put(
            f"/api/v1/businesses/location-contacts/{contact_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone_number"] == "+46799999999"

    async def test_delete_contact_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """DELETE /businesses/location-contacts/{id} deletes contact."""
        # Create contact
        contact_data = {
            "location_id": str(test_location_id),
            "contact_type": "Temp",
            "phone_number": "123",
        }
        create_resp = await client.post(
            f"/api/v1/businesses/locations/{test_location_id}/contacts",
            json=contact_data,
            headers=auth_headers,
        )
        contact_id = create_resp.json()["id"]

        # Delete
        response = await client.delete(
            f"/api/v1/businesses/location-contacts/{contact_id}", headers=auth_headers
        )

        assert response.status_code == 204

    async def test_delete_contact_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """DELETE /businesses/location-contacts/{id} returns 404 for non-existent contact."""
        fake_id = 99999
        response = await client.delete(
            f"/api/v1/businesses/location-contacts/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404

class TestLocationSearch:
    """Tests for top-level location search."""

    async def test_get_locations_success(self, client: httpx.AsyncClient):
        """GET /businesses/locations returns locations."""
        response = await client.get("/api/v1/businesses/locations")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_locations_filters(
        self, client: httpx.AsyncClient, test_location_id
    ):
        """GET /businesses/locations filters by query and city."""
        response = await client.get("/api/v1/businesses/locations?city=Stockholm")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify city filter if data returned
        if data:
            assert all("stockholm" in (loc.get("city") or "").lower() for loc in data)

        response = await client.get("/api/v1/businesses/locations?query=Test")
        assert response.status_code == 200
