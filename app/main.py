
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg import errors as pg_errors

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.config import settings
from app.core.database import db
from app.core.exceptions import ApplicationException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Initialize database connection pool
    await db.connect()
    yield
    # Shutdown: Close database connection pool
    await db.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)


# Exception handler for custom exceptions
@app.exception_handler(ApplicationException)
async def easy_booking_exception_handler(request: Request, exc: ApplicationException):
    """Convert ApplicationException to HTTP response."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Exception handler for database foreign key violations
@app.exception_handler(pg_errors.ForeignKeyViolation)
async def foreign_key_violation_handler(
    request: Request, exc: pg_errors.ForeignKeyViolation
):
    """Convert ForeignKeyViolation to 404 Not Found."""
    return JSONResponse(
        status_code=404, content={"detail": "Referenced resource not found"}
    )


# Exception handler for database unique violations
@app.exception_handler(pg_errors.UniqueViolation)
async def unique_violation_handler(request: Request, exc: pg_errors.UniqueViolation):
    """Convert UniqueViolation to 409 Conflict."""
    return JSONResponse(status_code=409, content={"detail": "Resource already exists"})


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(admin_router, prefix=f"{settings.API_V1_STR}")
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}")
app.include_router(users_router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
async def root():
    return {"message": "Welcome to Easy Booking API"}