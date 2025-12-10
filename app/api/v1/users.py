"""User API Endpoints

Handles user profile management, password changes, and address management.
Includes admin-only endpoint for listing all users.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection

from app.api.deps import get_current_active_user, get_current_admin, get_db_conn
from app.core.security import get_password_hash, verify_password
from app.models.auth import PasswordChangeRequest
from app.models.user import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    UserDB,
    UserResponse,
    UserUpdate,
)
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Get current user profile."""
    return current_user


@router.get("/", response_model=list[UserResponse])
async def read_users(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_admin: Annotated[UserDB, Depends(get_current_admin)],
    skip: int = 0,
    limit: int = 100,
):
    """Retrieve all users (admin-only)."""
    repo = UserRepository(conn)
    return await repo.find_all(limit=limit, offset=skip)


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    data: UserUpdate,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Update current user profile."""
    repo = UserRepository(conn)
    service = UserService(repo)
    return await service.update_user(current_user.id, data)


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChangeRequest,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Change current user password."""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    repo = UserRepository(conn)
    new_hash = get_password_hash(data.new_password)
    await repo.update(current_user.id, {"password_hash": new_hash})

    return {"message": "Password updated successfully"}


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_user_me(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Delete own account (GDPR-compliant anonymization)."""
    repo = UserRepository(conn)
    service = UserService(repo)
    await service.delete_user(current_user.id)

    return {"message": "Account deleted successfully"}


@router.post(
    "/me/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED
)
async def create_address(
    data: AddressCreate,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Create a new address for current user."""
    repo = UserRepository(conn)
    return await repo.create_address(current_user.id, data.model_dump())


@router.get("/me/addresses", response_model=list[AddressResponse])
async def get_addresses(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Get all addresses for current user."""
    repo = UserRepository(conn)
    return await repo.get_user_addresses(current_user.id)


@router.put("/me/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: UUID,
    data: AddressUpdate,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Update an address."""
    repo = UserRepository(conn)
    # Only update fields that are provided
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await repo.update_address(address_id, current_user.id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: UUID,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Delete an address."""
    repo = UserRepository(conn)
    deleted = await repo.delete_address(address_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")
