"""
Tests for Authentication API (Phase 3)

Tests cover:
- User registration
- Login with credentials
- Token refresh
- Invalid credentials
- Duplicate email handling
"""

import httpx


class TestRegistration:
    """Tests for user registration."""

    async def test_register_customer_success(self, client: httpx.AsyncClient, request):
        """POST /auth/register/customer creates a new customer successfully."""
        test_id = request.node.name
        register_data = {
            "email": f"customer_{test_id}@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "Customer",
            "mobile_number": "+46701234567",
        }

        response = await client.post(
            "/api/v1/auth/register/customer", json=register_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["first_name"] == "New"
        assert data["last_name"] == "Customer"
        assert data["role"] == "customer"
        assert "id" in data
        assert "password" not in data

    async def test_register_provider_success(self, client: httpx.AsyncClient, request):
        """POST /auth/register/provider creates a new provider successfully."""
        test_id = request.node.name
        register_data = {
            "email": f"provider_{test_id}@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "Provider",
            "mobile_number": "+46709876543",
        }

        response = await client.post(
            "/api/v1/auth/register/provider", json=register_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["first_name"] == "New"
        assert data["last_name"] == "Provider"
        assert data["role"] == "provider"
        assert "id" in data

    async def test_register_duplicate_email(
        self, client: httpx.AsyncClient, test_user_id
    ):
        """POST /auth/register/customer fails with duplicate email."""
        user_id, email = test_user_id
        register_data = {
            "email": email,  # Already exists
            "password": "AnotherPass123!",
            "first_name": "Duplicate",
            "last_name": "User",
            "mobile_number": "+46700000000",
        }

        response = await client.post(
            "/api/v1/auth/register/customer", json=register_data
        )

        assert response.status_code in [409, 422]  # Conflict or validation error

    async def test_register_invalid_email(self, client: httpx.AsyncClient):
        """POST /auth/register/customer fails with invalid email format."""
        register_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "mobile_number": "+46701234567",
        }

        response = await client.post(
            "/api/v1/auth/register/customer", json=register_data
        )

        assert response.status_code == 422

    async def test_register_weak_password(self, client: httpx.AsyncClient, request):
        """POST /auth/register/customer fails with weak password."""
        test_id = request.node.name
        register_data = {
            "email": f"user_{test_id}@example.com",
            "password": "123",  # Too short
            "first_name": "Test",
            "last_name": "User",
            "mobile_number": "+46701234567",
        }

        response = await client.post(
            "/api/v1/auth/register/customer", json=register_data
        )

        assert response.status_code == 422

    async def test_register_missing_required_fields(self, client: httpx.AsyncClient):
        """POST /auth/register/customer fails when required fields are missing."""
        register_data = {
            "email": "incomplete@example.com"
            # Missing password, first_name, last_name
        }

        response = await client.post(
            "/api/v1/auth/register/customer", json=register_data
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    async def test_login_success(self, client: httpx.AsyncClient, test_user_id):
        """POST /auth/login returns tokens with valid credentials."""
        user_id, email = test_user_id
        login_data = {
            "username": email,  # OAuth2PasswordRequestForm expects 'username'
            "password": "password123",
        }

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(
        self, client: httpx.AsyncClient, test_user_id
    ):
        """POST /auth/login fails with incorrect password."""
        user_id, email = test_user_id
        login_data = {"username": email, "password": "WrongPassword123!"}

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: httpx.AsyncClient):
        """POST /auth/login fails with non-existent email."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401

    async def test_login_missing_credentials(self, client: httpx.AsyncClient):
        """POST /auth/login fails when credentials are missing."""
        response = await client.post("/api/v1/auth/login", data={})

        assert response.status_code == 422


class TestTokenRefresh:
    """Tests for token refresh."""

    async def test_refresh_token_success(self, client: httpx.AsyncClient, test_user_id):
        """POST /auth/refresh returns new access token."""
        # First login to get refresh token
        user_id, email = test_user_id
        login_response = await client.post(
            "/api/v1/auth/login", data={"username": email, "password": "password123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        refresh_response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_invalid_token(self, client: httpx.AsyncClient):
        """POST /auth/refresh fails with invalid token."""
        refresh_response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"}
        )

        assert refresh_response.status_code == 401


class TestAuthorizationHeaders:
    """Tests for authorization header validation."""

    async def test_protected_endpoint_without_token(self, client: httpx.AsyncClient):
        """Protected endpoints reject requests without auth token."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401

    async def test_protected_endpoint_with_invalid_token(
        self, client: httpx.AsyncClient
    ):
        """Protected endpoints reject requests with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401

    async def test_protected_endpoint_with_valid_token(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """Protected endpoints accept requests with valid token."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
