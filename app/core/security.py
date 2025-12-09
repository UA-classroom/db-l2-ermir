"""
Security and Authentication Module

This module handles all security-related operations for the application:
- Password hashing using bcrypt
- JWT token creation and validation
- User authentication

Security Features:
    - Bcrypt password hashing (industry standard, slow by design to prevent brute force)
    - JWT tokens for stateless authentication
    - Token type validation (access vs refresh tokens)
    - Automatic token expiration

Usage:
    # Password hashing
    from app.core.security import get_password_hash, verify_password
    hashed = get_password_hash("user_password")
    is_valid = verify_password("user_password", hashed)

    # JWT tokens
    from app.core.security import create_access_token, decode_token
    token = create_access_token({"sub": user.email})
    payload = decode_token(token)

Security Notes:
    - Never log or display hashed passwords
    - SECRET_KEY must be kept secret and random in production
    - Tokens are signed but not encrypted (don't put sensitive data in them)
    - Always use HTTPS in production to protect tokens in transit
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def get_password_hash(password: str) -> str:
    """ 
    Hash a plaintext password using bcrypt. 
    
    Args:
        password (str): The plaintext password to hash.
    Returns:
        str: The hashed password.

    Security Note:
        - Same password will yield different hashes due to salting.
        - Hash is one-way; original password cannot be retrieved.
        - Use verify_password to check if password matches hash.
    """
    return pwd_context.hash(password)

# Alias for compatibility if needed, or just yse  get_password_hash directly
hash_password = get_password_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    This is used during user login to authenticate credentials.
    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to compare against.
    Returns:
        bool: True if the password matches the hash, False otherwise.

    Security Note:
        - Timing-safe comparison to prevent timing attacks.
        - Always return False if verification fails.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token for user authentication.

    Args:
        data (dict): The payload data to include in the token (e.g., user ID, email).
        expires_delta (Optional[timedelta]): Optional expiration time for the token.
    
    Returns:
        str: The encoded JWT access token.

    Token Structure:
        - Header: Algorithm and token type (JWT)
        - Payload: User data and expiration time and token type
        - Signature: HMAC SHA256 signature using SECRET_KEY
    Security Note:
        - Token is signed but not encrypted
        - Do not include sensitive data in the payload
        - Token automatically expires after specified time
        - "type" : "access" prevents misuse as refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT refresh token for obtaining new access tokens.

    Args:
        data (dict): The payload data to include in the token (e.g., user ID, email).
        expires_delta (Optional[timedelta]): Optional expiration time for the token.
    
    Returns:
        str: The encoded JWT refresh token.

    Token Lifecycle:
        - Acess tokens : Short ( 30 minutes) lifespan for regular API access
        - Refresh tokens : Longer ( 7 days) lifespan to obtain new access tokens without re-authenticating

    Security Note:
        - Refresh tokens live longer than access tokens
        - "type": "refresh" prevents access tokens from being used as refresh tokens
        - Should be stored in httpOnly cookie or secure storage
        - Revoke refresh token on logout or password change
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and verify a JWT token.

    Validates the token signature, expiration, and type before returning the payload.
    Used to authenticate users from their JWT tokens.

    Args:
        token: JWT token string to decode
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        dict: Decoded token payload containing user data

    Raises:
        HTTPException (401): If token is invalid, expired, or wrong type

    Validation Checks:
        1. Signature verification (token not tampered with)
        2. Expiration check (token not expired)
        3. Type check (access vs refresh token)

    Security Notes:
        - Returns 401 Unauthorized for any validation failure
        - Type check prevents using refresh tokens as access tokens
        - Expired tokens are automatically rejected
        - Invalid signatures (tampered tokens) are rejected
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


   