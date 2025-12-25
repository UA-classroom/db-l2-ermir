"""
Tests for User Management API (Phase 3)

Tests cover:
- Get current user profile
- Update user profile
- Change password
- Address management (CRUD)
"""

import httpx

# pyright: reportMissingImports=false
from uuid_utils import uuid7


class TestUserProfile:
    """Tests for user profile endpoints."""

    async def test_get_current_user(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """GET /users/me returns current user's profile."""
        user_id, email = test_user_id
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert "id" in data
        assert "password" not in data

    async def test_update_profile_success(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /users/me updates user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "mobile_number": "+46709876543",
        }

        response = await client.put(
            "/api/v1/users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["mobile_number"] == "+46709876543"

    async def test_update_profile_partial(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /users/me allows partial updates."""
        update_data = {"first_name": "OnlyFirst"}

        response = await client.put(
            "/api/v1/users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "OnlyFirst"

    async def test_update_profile_invalid_phone(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /users/me validates phone number format."""
        update_data = {"mobile_number": "invalid-phone"}

        response = await client.put(
            "/api/v1/users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422


class TestPasswordChange:
    """Tests for password change."""

    async def test_change_password_success(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PATCH /users/me/password changes password successfully."""
        password_data = {
            "current_password": "password123",
            "new_password": "NewSecurePass456!",
        }

        response = await client.patch(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 200

    async def test_change_password_wrong_current(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PATCH /users/me/password fails with wrong current password."""
        password_data = {
            "current_password": "WrongPassword",
            "new_password": "NewSecurePass456!",
        }

        response = await client.patch(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 401

    async def test_change_password_weak_new(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PATCH /users/me/password validates new password strength."""
        password_data = {
            "current_password": "password123",
            "new_password": "123",  # Too weak
        }

        response = await client.patch(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 422


class TestAddresses:
    """Tests for address management."""

    async def test_create_address_success(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /users/me/addresses creates a new address."""
        address_data = {
            "street_address": "Kungsgatan 1",
            "city": "Stockholm",
            "postal_code": "11143",
            "country": "Sweden",
        }

        response = await client.post(
            "/api/v1/users/me/addresses", json=address_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["street_address"] == "Kungsgatan 1"
        assert data["city"] == "Stockholm"
        assert data["postal_code"] == "11143"
        assert "id" in data

    async def test_get_addresses(self, client: httpx.AsyncClient, auth_headers):
        """GET /users/me/addresses returns user's addresses."""
        # First create an address
        address_data = {
            "street_address": "Drottninggatan 2",
            "city": "Göteborg",
            "postal_code": "41103",
        }
        await client.post(
            "/api/v1/users/me/addresses", json=address_data, headers=auth_headers
        )

        # Get addresses
        response = await client.get("/api/v1/users/me/addresses", headers=auth_headers)

        assert response.status_code == 200
        addresses = response.json()
        assert isinstance(addresses, list)
        assert len(addresses) >= 1

    async def test_delete_address(self, client: httpx.AsyncClient, auth_headers):
        """DELETE /users/me/addresses/{id} removes an address."""
        # Create address
        address_data = {
            "street_address": "Storgatan 3",
            "city": "Malmö",
            "postal_code": "21122",
        }
        create_response = await client.post(
            "/api/v1/users/me/addresses", json=address_data, headers=auth_headers
        )
        address_id = create_response.json()["id"]

        # Delete address
        delete_response = await client.delete(
            f"/api/v1/users/me/addresses/{address_id}", headers=auth_headers
        )

        assert delete_response.status_code == 204

    async def test_delete_nonexistent_address(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """DELETE /users/me/addresses/{id} returns 404 for non-existent address."""


        fake_id = uuid7()

        response = await client.delete(
            f"/api/v1/users/me/addresses/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_create_address_missing_required_fields(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /users/me/addresses fails when required fields are missing."""
        address_data = {
            "city": "Stockholm"
            # Missing street_address, postal_code
        }

        response = await client.post(
            "/api/v1/users/me/addresses", json=address_data, headers=auth_headers
        )

        assert response.status_code == 422


class TestAddressUpdate:
    """Tests for updating addresses."""

    async def test_update_address_success(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /users/me/addresses/{id} updates address."""
        # Create address
        address_data = {
            "street_address": "Original St 1",
            "city": "City",
            "postal_code": "10000",
        }
        create_resp = await client.post(
            "/api/v1/users/me/addresses", json=address_data, headers=auth_headers
        )
        address_id = create_resp.json()["id"]

        # Update
        update_data = {"street_address": "Updated St 2", "city": "New City"}
        response = await client.put(
            f"/api/v1/users/me/addresses/{address_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["street_address"] == "Updated St 2"
        assert data["city"] == "New City"
        assert data["postal_code"] == "10000"  # Unchanged

    async def test_update_address_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """PUT /users/me/addresses/{id} returns 404 for non-existent address."""        

        fake_id = uuid7()

        update_data = {"city": "New City"}
        response = await client.put(
            f"/api/v1/users/me/addresses/{fake_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestAdminUserList:
    """Tests for admin user listing."""

    async def test_admin_list_users(self, client: httpx.AsyncClient, admin_headers):
        """GET /users/ lists all users (Admin only)."""
        response = await client.get("/api/v1/users/", headers=admin_headers)

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1  # Should at least contain the admin itself

    async def test_list_users_forbidden(self, client: httpx.AsyncClient, auth_headers):
        """GET /users/ is forbidden for non-admins."""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 403


class TestAccountDeletion:
    """Tests for account deletion."""

    async def test_delete_account_success(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """DELETE /users/me deletes (deactivates) account."""
        response = await client.delete("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200

        # Verify login fails or accessing secured endpoint fails
        # Note: Depending on implementation, token might still be valid until expiry,
        # but user check in DB should fail or return inactive.

        # Check profile access
        profile_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        # Assuming get_current_active_user checks is_active
        assert profile_resp.status_code in [400, 401, 404]
