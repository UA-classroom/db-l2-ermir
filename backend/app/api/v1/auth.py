"""
Authentication API Endpoints

Handles user authentication operations including registration, login,
token refresh, and logout. Uses AuthService for business logic.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import AsyncConnection

from app.api.deps import get_current_user, get_db_conn
from app.models.auth import (
    CustomerRegisterRequest,
    LoginRequest,
    ProviderRegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.models.user import UserDB, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/customer",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_customer(
    data: CustomerRegisterRequest,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Register a new customer account."""
    service = AuthService(conn)
    return await service.register_customer(data)


@router.post(
    "/register/provider",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_provider(
    data: ProviderRegisterRequest,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Register a new provider account."""
    service = AuthService(conn)
    return await service.register_provider(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Authenticate user and return tokens."""
    service = AuthService(conn)
    # Convert form data to LoginRequest
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    user = await service.authenticate_user(login_data)
    return await service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Get new access token using refresh token."""
    service = AuthService(conn)
    return await service.refresh_access_token(request.refresh_token)


@router.post("/logout")
async def logout(
    current_user: Annotated[UserDB, Depends(get_current_user)],
):
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}