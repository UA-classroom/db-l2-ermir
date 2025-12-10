"""
Admin API Endpoints

Admin-only operations including user management and platform administration.
Requires admin role for all endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from psycopg import AsyncConnection

from app.api.deps import get_current_admin, get_db_conn
from app.core.enums import RoleEnum
from app.core.security import get_password_hash
from app.models.user import UserDB, UserResponse
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    mobile_number: str,
    role: RoleEnum,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_admin: Annotated[UserDB, Depends(get_current_admin)],
):
    """
    Create a new user with any role (admin-only).

    Only existing admins can create new users with admin role.
    This is the ONLY way to create admin accounts.
    """
    user_repo = UserRepository(conn)

    # Check if email already exists
    if await user_repo.email_exists(email):
        from app.core.exceptions import ConflictError

        raise ConflictError(f"Email {email} is already registered")

    # Hash password
    hashed_password = get_password_hash(password)

    # Create user data
    user_data = {
        "email": email,
        "password_hash": hashed_password,
        "first_name": first_name,
        "last_name": last_name,
        "mobile_number": mobile_number,
        "role": role.value,
        "is_active": True,
    }

    # Create user
    user = await user_repo.create(user_data)
    return UserResponse.model_validate(user)