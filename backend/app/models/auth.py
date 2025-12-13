"""
Authentication Models Module

Pydantic models for authentication and authorization operations.
Includes login, registration, token management, and password changes.
"""
from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class LoginRequest(BaseModel):
    """User login request with email and password."""

    email: str
    password: str


class CustomerRegisterRequest(BaseModel):
    """Customer registration request (role is automatically set to customer)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    mobile_number: str = Field(min_length=1, max_length=20)


class ProviderRegisterRequest(BaseModel):
    """Provider registration request (role is automatically set to provider)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    mobile_number: str = Field(min_length=1, max_length=20)


class TokenResponse(BaseModel):
    """JWT token response - OAuth2 compliant."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int

    # Override to disable camelCase conversion for OAuth2 compliance
    model_config = ConfigDict(
        alias_generator=None, 
        populate_by_name=True,
        from_attributes=True,
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Change password request model."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=100)