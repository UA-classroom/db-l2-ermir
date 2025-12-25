"""
Application Configuration Module

This module handles all application settings and configuration using environment variables.
Settings are loaded from the .env file and validated using Pydantic.

Environment Variables Required:
    - DB_HOST: Database host address (e.g., localhost)
    - DB_PORT: Database port number (e.g., 5432)
    - DB_USER: Database username (e.g., postgres)
    - DB_PASSWORD: Database password
    - DB_NAME: Database name (e.g., mydatabase)
    - SECRET_KEY: Secret key for JWT token signing (must be random in production)
    - ACCESS_TOKEN_EXPIRE_MINUTES: JWT access token expiration time in minutes (default: 30)
    -REFRESH_TOKEN_EXPIRE_MINUTES: JWT refresh token expiration time in days
    - PROJECT_NAME: Name of the project (default: MyApp)
    - API_V1_STR: API version string (default: /api/v1)
    - BACKEND_CORS_ORIGINS: Allowed CORS origins as JSON array

Usage:
    from app.config import settings

    # Access configuration values
    db_url = settings.DATABASE_URL
    secret_key = settings.SECRET_KEY
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        """Construct the database URL from individual components."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # JWT Configuration
    SECRET_KEY: str  # In production, use a random and secure key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # Application Configuration
    PROJECT_NAME: str = "MyApp"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=True)
    
# Global settings instance
settings = Settings() # type: ignore
