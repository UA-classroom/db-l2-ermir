from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    """Base employee fields."""
    job_title: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")  # e.g., #FF5733
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    """Employee creation request."""
    user_id: UUID
    location_id: UUID


class EmployeeUpdate(BaseModel):
    """Employee update request (all fields optional)."""
    job_title: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None
    location_id: Optional[UUID] = None


class EmployeeResponse(EmployeeBase):
    """Employee response."""
    id: UUID
    user_id: UUID
    location_id: UUID

    model_config = ConfigDict(from_attributes=True)


class WorkingHoursBase(BaseModel):
    """Base working hours fields."""
    day_of_week: int = Field(ge=1, le=7, description="1=Monday, 7=Sunday")
    start_time: time
    end_time: time


class WorkingHoursCreate(WorkingHoursBase):
    """Working hours creation request."""
    employee_id: UUID


class WorkingHoursUpdate(BaseModel):
    """Working hours update request."""
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class WorkingHoursResponse(WorkingHoursBase):
    """Working hours response."""
    id: UUID
    employee_id: UUID

    model_config = ConfigDict(from_attributes=True)


class InternalEventBase(BaseModel):
    """Base internal event fields."""
    type: str = Field(max_length=50, description="e.g., 'vacation', 'sick', 'meeting'")
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None


class InternalEventCreate(InternalEventBase):
    """Internal event creation request."""
    employee_id: UUID


class InternalEventUpdate(BaseModel):
    """Internal event update request."""
    type: Optional[str] = Field(None, max_length=50)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None


class InternalEventResponse(InternalEventBase):
    """Internal event response."""
    id: UUID
    employee_id: UUID

    model_config = ConfigDict(from_attributes=True)


class AvailabilityResponse(BaseModel):
    """Employee availability response."""
    is_available: bool
    reason: Optional[str] = None  # Reason if not available (e.g., "Not working on this day", "Has internal event")


class EmployeeScheduleResponse(BaseModel):
    """Complete employee schedule including working hours and internal events."""
    employee: EmployeeResponse
    working_hours: list[WorkingHoursResponse]
    internal_events: list[InternalEventResponse]


class EmployeeDetail(EmployeeResponse):
    """Employee with nested relationships."""
    working_hours: list[WorkingHoursResponse] = []
    internal_events: list[InternalEventResponse] = []


class EmployeeSkillCreate(BaseModel):
    """Employee skill creation request."""
    service_variant_id: UUID
    custom_price: Optional[float] = Field(None, description="Custom price override")
    custom_duration: Optional[int] = Field(None, description="Custom duration override (minutes)")
