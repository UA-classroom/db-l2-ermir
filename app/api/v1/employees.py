from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg import AsyncConnection

from app.api.deps import (
    get_current_provider,
    get_db_conn,
    verify_employee_ownership,
    verify_location_ownership,
)
from app.core.exceptions import NotFoundError
from app.models.employee import (
    AvailabilityResponse,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeSkillCreate,
    EmployeeUpdate,
    InternalEventCreate,
    InternalEventResponse,
    WorkingHoursCreate,
    WorkingHoursResponse,
)
from app.models.user import UserDB
from app.repositories.employee_repository import EmployeeRepository
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/", response_model=list[EmployeeResponse])
async def get_employees(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    location_id: Optional[UUID] = Query(None, description="Filter by location ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get list of employees with optional filters.

    - **location_id**: Filter by location UUID
    - **is_active**: Filter by active status (true/false)
    - **skip**: Number of results to skip (pagination)
    - **limit**: Maximum number of results (max 100)
    """
    repo = EmployeeRepository(conn)
    return await repo.get_employees(
        location_id=location_id,
        is_active=is_active,
        limit=limit,
        offset=skip,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get a single employee by ID.

    - **employee_id**: UUID of the employee
    """
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    return employee


@router.get("/{employee_id}/schedule", response_model=dict)
async def get_employee_schedule(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    start_date: Optional[datetime] = Query(
        None, description="Start date for internal events filter"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for internal events filter"
    ),
):
    """
    Get complete employee schedule including working hours and internal events.

    - **employee_id**: UUID of the employee
    - **start_date**: Optional start date for filtering internal events
    - **end_date**: Optional end date for filtering internal events
    """
    repo = EmployeeRepository(conn)

    # Verify employee exists
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")

    schedule_service = ScheduleService(repo)
    return await schedule_service.get_employee_schedule(
        employee_id, start_date, end_date
    )


@router.post(
    "/{employee_id}/working-hours",
    response_model=WorkingHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_working_hours(
    employee_id: UUID,
    working_hours_data: WorkingHoursCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """
    Add working hours for an employee (Provider only).

    Supports split shifts (multiple entries for same day).

    - **employee_id**: UUID of the employee (must match employee_id in request body)
    - **day_of_week**: Day of week (1=Monday, 7=Sunday)
    - **start_time**: Start time (HH:MM:SS format)
    - **end_time**: End time (HH:MM:SS format)
    """
    # Verify employee ownership
    await verify_employee_ownership(employee_id, current_user, conn)

    # Ensure the employee_id in the path matches the one in the body
    if working_hours_data.employee_id != employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee ID mismatch between path and body"
        )

    repo = EmployeeRepository(conn)
    return await repo.add_working_hours(working_hours_data)


@router.post(
    "/{employee_id}/internal-events",
    response_model=InternalEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_internal_event(
    employee_id: UUID,
    event_data: InternalEventCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """
    Add an internal event for an employee (Provider only).

    Events include vacation, sick leave, meetings, etc.

    - **employee_id**: UUID of the employee (must match employee_id in request body)
    - **type**: Type of event (e.g., 'vacation', 'sick', 'meeting')
    - **start_time**: Start time
    - **end_time**: End time
    - **description**: Optional description
    """
    # Verify employee ownership
    await verify_employee_ownership(employee_id, current_user, conn)

    # Ensure the employee_id in the path matches the one in the body
    if event_data.employee_id != employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee ID mismatch between path and body"
        )

    repo = EmployeeRepository(conn)
    return await repo.add_internal_event(event_data)


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """Create a new employee (Provider only)."""
    # Verify location ownership - provider must own the location
    await verify_location_ownership(employee_data.location_id, current_user, conn)

    repo = EmployeeRepository(conn)
    return await repo.create_employee(employee_data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """Update an existing employee (Provider only)."""
    # Verify employee ownership
    await verify_employee_ownership(employee_id, current_user, conn)

    repo = EmployeeRepository(conn)
    employee = await repo.update_employee(employee_id, employee_data)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """Delete an employee (Provider only)."""
    # Verify employee ownership
    await verify_employee_ownership(employee_id, current_user, conn)

    repo = EmployeeRepository(conn)
    deleted = await repo.delete(employee_id)
    if not deleted:
        raise NotFoundError(f"Employee {employee_id} not found")


@router.get("/{employee_id}/working-hours", response_model=list[WorkingHoursResponse])
async def get_employee_working_hours(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Get all working hours for an employee."""
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    return await repo.get_employee_working_hours(employee_id)


@router.get("/{employee_id}/skills", response_model=list[dict])
async def get_employee_skills(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Get all skills (service variants) for an employee with custom pricing."""
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    return await repo.get_employee_skills(employee_id)


@router.post("/{employee_id}/skills", status_code=status.HTTP_201_CREATED)
async def add_employee_skill(
    employee_id: UUID,
    skill_data: EmployeeSkillCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
):
    """Add a skill to an employee with optional custom pricing (Provider only)."""
    # Verify employee ownership
    await verify_employee_ownership(employee_id, current_user, conn)

    repo = EmployeeRepository(conn)
    success = await repo.add_employee_skill(
        employee_id,
        skill_data.service_variant_id,
        skill_data.custom_price,
        skill_data.custom_duration,
    )
    if not success:
        raise NotFoundError("Skill already exists or service variant not found")
    return {"message": "Skill added successfully"}


@router.get("/{employee_id}/availability", response_model=AvailabilityResponse)
async def check_employee_availability(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    start_time: datetime = Query(..., description="Booking start time"),
    end_time: datetime = Query(..., description="Booking end time"),
):
    """Check if an employee is available for a booking at a specific time."""
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    schedule_service = ScheduleService(repo)
    return await schedule_service.check_availability(employee_id, start_time, end_time)


@router.get(
    "/{employee_id}/internal-events", response_model=list[InternalEventResponse]
)
async def get_employee_internal_events(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
):
    """Get internal events for an employee (vacation, sick leave, meetings)."""
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    return await repo.get_employee_internal_events(employee_id, start_date, end_date)

@router.get("/{employee_id}/available-slots", response_model=list[dict])
async def get_available_slots(
    employee_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    date: datetime = Query(..., description="Date to check for available slots"),
    duration_minutes: int = Query(
        ..., ge=15, le=480, description="Duration needed (15-480 minutes)"
    ),
    slot_interval_minutes: int = Query(
        30, ge=15, le=120, description="Interval between slots (15-120 minutes)"
    ),
):
    """Get available time slots for an employee on a specific date."""
    repo = EmployeeRepository(conn)
    employee = await repo.get_employee_by_id(employee_id)
    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")
    schedule_service = ScheduleService(repo)
    return await schedule_service.get_available_slots(
        employee_id, date, duration_minutes, slot_interval_minutes
    )