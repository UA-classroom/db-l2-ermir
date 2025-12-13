from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.api.deps import (
    get_booking_service,
    get_current_active_user,
    get_current_provider,
    get_db_conn,
    validate_booking_creation,
    verify_booking_ownership,
    verify_location_ownership,
)
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.booking import (
    AvailabilityRequest,
    BookingCreate,
    BookingDetail,
    BookingResponse,
    BookingUpdate,
    StatusUpdateRequest,
)
from app.models.employee import AvailabilityResponse
from app.models.user import UserDB
from app.repositories.booking_repository import BookingRepository
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Create booking."""
    # Validate authorization
    await validate_booking_creation(booking_data, current_user, conn)

    return await booking_service.create_booking(booking_data)


# MOVED: /availability BEFORE /{booking_id} to fix route matching
@router.get("/availability", response_model=AvailabilityResponse)
async def check_availability(
    availability_request: Annotated[AvailabilityRequest, Depends()],
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    """Check availability."""
    # Validate time range
    if availability_request.end_time <= availability_request.start_time:
        raise BadRequestError("end_time must be after start_time")

    return await booking_service.check_availability(
        availability_request.employee_id,
        availability_request.start_time,
        availability_request.end_time,
    )


@router.get("/", response_model=list[BookingResponse])
async def get_user_bookings(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """User bookings."""
    booking_repo = BookingRepository(conn)
    return await booking_repo.get_user_bookings(current_user.id, status, limit, offset)

@router.get("/slots", response_model=list[dict])
async def get_booking_slots(
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
    date: datetime = Query(..., description="Date to check"),
    service_variant_id: UUID = Query(..., description="Service Variant ID"),
    location_id: UUID = Query(..., description="Location ID"),
    employee_id: Optional[UUID] = Query(None, description="Optional specific employee"),
):
    """
    Get available time slots for booking.

    Returns list of slots with start_time and list of available_employee_ids.
    """
    return await booking_service.get_available_slots_for_booking(
        date, service_variant_id, location_id, employee_id
    )


@router.get("/{booking_id}", response_model=BookingDetail)
async def get_booking(
    booking_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Booking details."""
    # Verify booking ownership
    await verify_booking_ownership(booking_id, current_user, conn)

    booking_repo = BookingRepository(conn)
    booking = await booking_repo.get_booking_by_id(booking_id)
    if not booking:
        raise NotFoundError(f"Booking {booking_id} not found")
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: UUID,
    booking_data: BookingUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Reschedule."""
    # Verify booking ownership
    await verify_booking_ownership(booking_id, current_user, conn)

    return await booking_service.reschedule_booking(booking_id, booking_data)


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: UUID,
    status_data: StatusUpdateRequest,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Update status."""
    # Verify booking ownership
    await verify_booking_ownership(booking_id, current_user, conn)

    booking_repo = BookingRepository(conn)
    updated = await booking_repo.update_booking_status(
        booking_id, status_data.status.value
    )
    if not updated:
        raise NotFoundError(f"Booking {booking_id} not found")
    return updated


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Delete."""
    # Verify booking ownership
    await verify_booking_ownership(booking_id, current_user, conn)

    booking_repo = BookingRepository(conn)
    await booking_repo.delete_booking(booking_id) 



@router.get("/locations/{location_id}", response_model=list[BookingResponse])
async def get_location_bookings(
    location_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Location bookings."""
    # Verify location ownership
    await verify_location_ownership(location_id, current_user, conn)

    booking_repo = BookingRepository(conn)
    return await booking_repo.get_location_bookings(location_id, limit, offset)
