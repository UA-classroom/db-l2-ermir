"""
User Repository Module

Handles all database operations for users, including CRUD operations,
role management, and user address management.

This repository uses the BaseRepository pattern and includes:
- User creation with automatic role assignment
- User lookup by ID, email, or role
- User activation/deactivation
- Address management for users
- Soft delete support
"""
from typing import Any, Optional
from uuid import UUID

from psycopg import AsyncConnection

from app.core.enums import RoleEnum
from app.models.user import AddressResponse, UserDB
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserDB]):
    """Repository for user-related database operations."""

    def __init__(self, conn: AsyncConnection):
        """Initialize the UserRepository with a database connection."""
        super().__init__(conn)
        self.table = "users"
        self.enable_soft_delete = True


    async def find_by_id(self, user_id: UUID) -> Optional[UserDB]:
        """Find a user by their unique ID."""

        query = """
            SELECT u.*, r.name as role
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.id = %s AND u.deleted_at IS NULL
        """
        params = (user_id,)
        return await self._execute_one(query, params, UserDB)
    

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[UserDB]:
        """Find all users with optional pagination."""
        query = """
            SELECT u.*, r.name as role
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.deleted_at IS NULL
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """
        params = (limit, offset)
        return await self._execute_many(query, params, UserDB)
    

    async def find_by_email(self, email: str) -> Optional[UserDB]:
        """Find a user by their email address."""

        query = """
            SELECT u.*, r.name as role
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.email = %s AND u.deleted_at IS NULL
        """
        params = (email,)
        return await self._execute_one(query, params, UserDB)
    
    
    async def find_by_role(
        self, role: RoleEnum, limit: int = 100, offset: int = 0
    ) -> list[UserDB]:
        """Find all users with a specific role."""

        query = """
            SELECT u.*, r.name as role
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE r.name = %s AND u.deleted_at IS NULL
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """
        params = (role.value, limit, offset)
        return await self._execute_many(query, params, UserDB)
    

    async def create(self, data: dict) -> UserDB:
        """Create a new user and assign role."""

        # Extract role to handle separately
        role_name = data.pop("role", RoleEnum.CUSTOMER.value)
        if isinstance(role_name, RoleEnum):
            role_name = role_name.value

        async with self.conn.transaction():
            # 1. Insert user
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO users ({columns}) VALUES ({placeholders}) RETURNING *"

            async with self.conn.cursor() as cur:
                await cur.execute(query, tuple(data.values()))  # type: ignore[arg-type]
                user_row = await cur.fetchone()
                if not user_row:
                    raise RuntimeError(f"Failed to create user: {data}")

                # 2. Get Role ID
                await cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role_row = await cur.fetchone()
                if not role_row:
                    # Create role if not exists (fallback)
                    await cur.execute(
                        "INSERT INTO roles (name) VALUES (%s) RETURNING id",
                        (role_name,),
                    )
                    role_row = await cur.fetchone()
                    if not role_row:
                        raise RuntimeError(f"Failed to create role: {role_name}")
                role_id = role_row[0]

                # 3. Assign Role
                await cur.execute(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                    (user_row[0], role_id),
                )

        return await self.find_by_id(user_row[0])  # type: ignore


    async def update(self, user_id: UUID, data: dict) -> Optional[UserDB]:
        """Update user."""
        
        return await self._update(self.table, user_id, data, UserDB)            


    async def email_exists(
        self, email: str, exclude_user_id: Optional[UUID] = None
    ) -> bool:
        """Check if email exists."""

        if exclude_user_id:
            query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s AND id != %s AND deleted_at IS NULL)"
            result = await self._execute_scalar(query, (email, exclude_user_id))
        else:
            query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s AND deleted_at IS NULL)"
            result = await self._execute_scalar(query, (email,))
        return result if result is not None else False


    async def deactivate(self, user_id: UUID) -> Optional[UserDB]:
        """Deactivate user."""

        query = "UPDATE users SET is_active = FALSE WHERE id = %s RETURNING id"
        res = await self._execute_scalar(query, (user_id,))
        if res:
            return await self.find_by_id(user_id)
        return None


    async def activate(self, user_id: UUID) -> Optional[UserDB]:
        """Activate user."""

        query = "UPDATE users SET is_active = TRUE WHERE id = %s RETURNING id"
        res = await self._execute_scalar(query, (user_id,))
        if res:
            return await self.find_by_id(user_id)
        return None


    async def create_address(self, user_id: UUID, data: dict) -> Any:
        """Create a new address for user."""

        data["user_id"] = user_id
        return await self._create("user_addresses", data, AddressResponse)


    async def get_user_addresses(self, user_id: UUID) -> list[Any]:
        """Get all addresses for a user."""
        

        query = "SELECT * FROM user_addresses WHERE user_id = %s"
        return await self._execute_many(query, (user_id,), AddressResponse)


    async def update_address(
        self, address_id: UUID, user_id: UUID, data: dict
    ) -> Optional[Any]:
        """Update an address (only if it belongs to the user)."""

        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE user_addresses SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *"
        params = tuple(data.values()) + (address_id, user_id)
        return await self._execute_one(query, params, AddressResponse)


    async def delete_address(self, address_id: UUID, user_id: UUID) -> bool:
        """Delete an address."""

        query = "DELETE FROM user_addresses WHERE id = %s AND user_id = %s"
        rowcount = await self._execute_command(query, (address_id, user_id))
        return rowcount > 0