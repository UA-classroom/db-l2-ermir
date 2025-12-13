from datetime import time as Time
from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


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
    start_time: Time
    end_time: Time


class WorkingHoursCreate(WorkingHoursBase):
    """Working hours creation request."""
    employee_id: UUID

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class WorkingHoursUpdate(BaseModel):
    """Working hours update request."""
    start_time: Optional[Time] = None
    end_time: Optional[Time] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class WorkingHoursResponse(WorkingHoursBase):
    """Working hours response."""
    id: UUID
    employee_id: UUID

    model_config = ConfigDict(from_attributes=True)


class InternalEventBase(BaseModel):
    """Base internal event fields."""
    type: str = Field(max_length=50, description="e.g., 'vacation', 'sick', 'meeting'")
    start_time: AwareDatetime
    end_time: AwareDatetime
    description: Optional[str] = None


class InternalEventCreate(InternalEventBase):
    """Internal event creation request."""
    employee_id: UUID

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class InternalEventUpdate(BaseModel):
    """Internal event update request."""
    type: Optional[str] = Field(None, max_length=50)
    start_time: Optional[AwareDatetime] = None
    end_time: Optional[AwareDatetime] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class InternalEventResponse(InternalEventBase):
    """Internal event response."""
    id: UUID
    employee_id: UUID

    model_config = ConfigDict(from_attributes=True)


class AvailabilityResponse(BaseModel):
    """Employee availability response."""
    is_available: bool
    reason: Optional[str] = Field(None, description="Reason if not available")


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
