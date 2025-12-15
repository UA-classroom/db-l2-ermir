from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.core.enums import BookingStatusEnum
from app.models.employee import EmployeeResponse
from app.models.service import ServiceVariantResponse
from app.models.user import UserResponse


class BookingBase(BaseModel):
    """Base booking fields."""

    customer_id: UUID
    location_id: UUID
    employee_id: UUID
    service_variant_id: UUID
    start_time: AwareDatetime
    end_time: AwareDatetime
    total_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    customer_note: Optional[str] = None


class BookingCreate(BookingBase):
    """Booking creation request with validation."""

    @field_validator("start_time")
    @classmethod
    def validate_future_time(cls, v: AwareDatetime) -> AwareDatetime:
        if v < datetime.now(timezone.utc):
            raise ValueError("Cannot book in the past")
        return v

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class BookingUpdate(BaseModel):
    """Booking update request (reschedule)."""

    start_time: Optional[AwareDatetime] = None
    end_time: Optional[AwareDatetime] = None
    customer_note: Optional[str] = None

    @field_validator("start_time")
    @classmethod
    def validate_future_time(
        cls, v: Optional[AwareDatetime]
    ) -> Optional[AwareDatetime]:
        if v is not None and v < datetime.now(timezone.utc):
            raise ValueError("Cannot book in the past")
        return v

    @model_validator(mode="after")
    def check_time_order(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class BookingResponse(BaseModel):
    """Basic booking response with optional joined names."""

    id: UUID
    customer_id: UUID
    location_id: UUID
    employee_id: UUID
    service_variant_id: UUID
    status: BookingStatusEnum
    start_time: AwareDatetime
    end_time: AwareDatetime
    total_price: Decimal
    customer_note: Optional[str] = None
    created_at: AwareDatetime

    # Optional joined fields for display
    service_name: Optional[str] = None
    location_name: Optional[str] = None
    business_name: Optional[str] = None
    employee_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookingDetail(BaseModel):
    """Booking with nested customer, employee, and service."""

    id: UUID
    customer: UserResponse
    location_id: UUID
    employee: EmployeeResponse
    service: ServiceVariantResponse
    status: BookingStatusEnum
    start_time: AwareDatetime
    end_time: AwareDatetime
    total_price: Decimal
    customer_note: Optional[str] = None
    created_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdateRequest(BaseModel):
    """Status change request."""

    status: BookingStatusEnum


class AvailabilityRequest(BaseModel):
    """Availability check request."""

    employee_id: UUID
    start_time: AwareDatetime
    end_time: AwareDatetime


# TODO: Delete it after tested works
# class AvailabilityResponse(BaseModel):
#   """Availability response."""

#   is_available: bool
#   reason: Optional[str] = Field(None, description="Reason if not available")
