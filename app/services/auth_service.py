"""
Authentication Service Module

Handles the business logic for authentication and user registration.
Includes user signup, login, and token management.
"""

from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status
from psycopg import AsyncConnection

from app.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.auth import (
    CustomerRegisterRequest,
    LoginRequest,
    ProviderRegisterRequest,
    TokenResponse,
)
from app.models.user import UserDB
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for handling authentication logic."""

    def __init__(self, conn: AsyncConnection):
        self.user_repo = UserRepository(conn)

    async def register_customer(self, data: CustomerRegisterRequest) -> UserDB:
        """
        Register a new customer account.

        Args:
            data: Customer registration data

        Returns:
            Created user with customer role

        Raises:
            HTTPException: If email already exists
        """
        try:
            if await self.user_repo.email_exists(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

            hashed_password = get_password_hash(data.password)

            user_data = data.model_dump(exclude={"password"})
            user_data["password_hash"] = hashed_password
            user_data["role"] = "customer"  # Hardcoded customer role

            return await self.user_repo.create(user_data)
        except HTTPException:
            raise
        except Exception as e:
            if "users_email_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            raise

    async def register_provider(self, data: ProviderRegisterRequest) -> UserDB:
        """
        Register a new provider account.

        Args:
            data: Provider registration data

        Returns:
            Created user with provider role

        Raises:
            HTTPException: If email already exists
        """
        try:
            if await self.user_repo.email_exists(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

            hashed_password = get_password_hash(data.password)

            user_data = data.model_dump(exclude={"password"})
            user_data["password_hash"] = hashed_password
            user_data["role"] = "provider"  # Hardcoded provider role

            return await self.user_repo.create(user_data)
        except HTTPException:
            raise
        except Exception as e:
            if "users_email_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            raise

    async def authenticate_user(self, data: LoginRequest) -> UserDB:
        """
        Authenticate a user.

        Args:
            data: Login credentials

        Returns:
            Authenticated user

        Raises:
            UnauthorizedError: If credentials are invalid
        """
        user = await self.user_repo.find_by_email(data.email)

        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        return user

    async def create_tokens(self, user: UserDB) -> TokenResponse:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User instance

        Returns:
            Token response with access and refresh tokens
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert user.role is not None, "User must have a role"
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires,
        )

        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=refresh_token_expires,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Create a new access token using a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token response

        Raises:
            UnauthorizedError: If token is invalid
        """
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedError("Invalid refresh token")
        except Exception:
            raise UnauthorizedError("Invalid refresh token")

        user = await self.user_repo.find_by_id(UUID(user_id))
        if not user:
            raise UnauthorizedError("User not found")

        if not user.is_active:
            raise UnauthorizedError("User is inactive")

        return await self.create_tokens(user)
