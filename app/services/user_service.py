"""User Service Module

Handles user management operations including profile updates,
account activation/deactivation, and GDPR-compliant user deletion.

Note: Authentication logic (register, login) is in auth_service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash
from app.models.user import UserResponse, UserUpdate
from app.repositories.user_repository import UserRepository


class UserService:
    """
    Service for user-related business logic.

    This service implements the business rules for user management,
    including registration, authentication, and account operations.
    It uses UserRepository for data access and delegates all database
    operations to that layer.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """
        Get user by ID.

        Args:
            user_id: User's UUID

        Returns:
            UserResponse with user data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)
    

    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Get user by email.

        Args:
            email: User's email address

        Returns:
            UserResponse with user data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.find_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)


    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> UserResponse:
        """
        Update user information.

        Business rules:
        - Email must be unique if changed
        - Password must be hashed if provided
        - Cannot update role through this method (security)

        Args:
            user_id: User's UUID
            user_data: Updated user data

        Returns:
            UserResponse with updated user data

        Raises:
            NotFoundError: If user not found
            ConflictError: If new email already exists
        """
        # Check if user exists
        existing_user = await self.user_repo.find_by_id(user_id)
        if not existing_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Prepare update data (only include provided fields)
        update_data = {}

        if user_data.email is not None and user_data.email != existing_user.email:
            # Check for email uniqueness
            if await self.user_repo.email_exists(user_data.email, exclude_user_id=user_id):
                raise ConflictError(f"Email {user_data.email} is already in use")
            update_data["email"] = user_data.email

        if user_data.first_name is not None:
            update_data["first_name"] = user_data.first_name

        if user_data.last_name is not None:
            update_data["last_name"] = user_data.last_name

        if user_data.password is not None:
            # Hash the new password
            update_data["password_hash"] = get_password_hash(user_data.password)

        if user_data.mobile_number is not None:
            update_data["mobile_number"] = user_data.mobile_number

        # TODO: Add updated_at column to users table in schema.sql
        # Then uncomment: update_data["updated_at"] = datetime.now(timezone.utc)
        # Best practice: Track when records are modified for audit trails

        # Update in database
        updated_user = await self.user_repo.update(user_id, update_data)
        if not updated_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(updated_user)
        


    async def deactivate_user(self, user_id: UUID) -> UserResponse:
        """
        Deactivate user account.

        Args:
            user_id: User's UUID

        Returns:
            UserResponse with updated user data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.deactivate(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)


    async def activate_user(self, user_id: UUID) -> UserResponse:
        """
        Activate user account.

        Args:
            user_id: User's UUID

        Returns:
            UserResponse with updated user data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.activate(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)


    async def delete_user(self, user_id: UUID) -> bool:
        """
        GDPR-compliant user deletion via anonymization.

        This method anonymizes all personal data while maintaining referential
        integrity in the database. The user record remains but all PII is removed.

        Business rules:
        - Personal data is replaced with anonymized values
        - Account is deactivated (is_active = False)
        - Deletion timestamp is recorded (deleted_at)
        - User ID remains for foreign key integrity

        Args:
            user_id: User's UUID

        Returns:
            True if user was anonymized

        Raises:
            NotFoundError: If user not found
        """
        
        # Check if user exists
        existing_user = await self.user_repo.find_by_id(user_id)
        if not existing_user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # Anonymization data
        anonymized_data = {
            "first_name": "Anonymized",
            "last_name": "User",
            "email": f"deleted-{user_id}@anonymized.example.com",  # RFC 2606 reserved domain
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc),
            "password_hash": "DELETED",
        }

        # Update in database
        updated_user = await self.user_repo.update(user_id, anonymized_data)
        if not updated_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return True