from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.booking import (
    AvailabilityResponse,
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.service_repository import ServiceRepository


class BookingService:
    """Service for booking-related business logic."""

    def __init__(
        self,
        booking_repo: BookingRepository,
        employee_repo: EmployeeRepository,
        service_repo: ServiceRepository
    ):
        self.booking_repo = booking_repo
        self.employee_repo = employee_repo
        self.service_repo = service_repo

    async def check_availability(
        self,
        employee_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> AvailabilityResponse:
        """
        Multi-step availability algorithm.

        Step 1: Check employee working hours
        Step 2: Check conflicting bookings
        Step 3: Check internal events
        Step 4: Return available or specific conflict reason
        """
        # Step 1: Check employee working hours
        day_of_week = start_time.isoweekday()  # 1=Monday, 7=Sunda
        working_hours = await self.employee_repo.get_employee_working_hours(employee_id)

        is_working = False
        for wh in working_hours:
            if wh.day_of_week == day_of_week:
                # Convert times to comparable format
                work_start = datetime.combine(start_time.date(), wh.start_time).replace(tzinfo=timezone.utc)
                work_end = datetime.combine(start_time.date(), wh.end_time).replace(tzinfo=timezone.utc)
                booking_start = start_time
                booking_end = end_time

                if booking_start >= work_start and booking_end <= work_end:
                    is_working = True
                    break

        if not is_working:
            return AvailabilityResponse(
                is_available=False,
                reason="Employee is not working during this time"
            )

        # Step 2: Check conflicting bookings
        conflicting_bookings = await self.booking_repo.get_employee_bookings_in_range(
            employee_id, start_time, end_time
        )

        if conflicting_bookings:
            return AvailabilityResponse(
                is_available=False,
                reason="Employee has conflicting booking"
            )

        # Step 3: Check internal events
        internal_events = await self.employee_repo.get_employee_internal_events(
            employee_id, start_time, end_time
        )

        if internal_events:
            return AvailabilityResponse(
                is_available=False,
                reason="Employee has internal event (vacation/sick)"
            )

        # Step 4: Return available
        return AvailabilityResponse(is_available=True, reason=None)

    async def calculate_booking_price(
        self,
        employee_id: UUID,
        service_variant_id: UUID
    ) -> Decimal:
        """
        Pricing logic.

        Step 1: Get base price from service_variant
        Step 2: Check employee_skills for custom_price override
        Step 3: Return final price
        """
        # Step 1: Get base price from service_variant
        service_variant = await self.service_repo.get_service_variant_by_id(service_variant_id)
        if not service_variant:
            raise NotFoundError(f"Service variant {service_variant_id} not found")

        base_price = service_variant.price

        # Step 2: Check employee_skills for custom_price override
        employee_skills = await self.employee_repo.get_employee_skills(employee_id)

        for skill in employee_skills:
            # Convert string UUID to UUID for comparison
            skill_variant_id = UUID(skill.get('service_variant_id'))
            if skill_variant_id == service_variant_id:
                if skill.get('custom_price') is not None:
                    return Decimal(str(skill['custom_price']))

        # Step 3: Return final price
        return base_price

    async def create_booking(self, booking_data: BookingCreate) -> BookingResponse:
        """
        Orchestrate booking creation.

        Step 1: Check availability (throw exception if not available)
        Step 2: Calculate price
        Step 3: Create booking record
        Step 4: Return detailed response
        """
        # Step 1: Check availability (throw exception if not available)
        availability = await self.check_availability(
            booking_data.employee_id,
            booking_data.start_time,
            booking_data.end_time
        )

        if not availability.is_available:
            raise ConflictError(f"Employee not available: {availability.reason}")

        # Step 2: Calculate price
        total_price = await self.calculate_booking_price(
            booking_data.employee_id,
            booking_data.service_variant_id
        )

        # Step 3: Create booking record
        booking_dict = booking_data.model_dump()
        booking_dict['total_price'] = total_price
        booking_dict['status_id'] = 1  # pending status

        created_booking = await self.booking_repo.create_booking(booking_dict)

        # Step 4: Return detailed response
        return created_booking

    async def reschedule_booking(
        self,
        booking_id: UUID,
        booking_data: BookingUpdate
    ) -> BookingResponse:
        """
        Update booking time.

        Step 1: Check new time availability
        Step 2: Update booking
        """
        # Get existing booking
        existing = await self.booking_repo.get_booking_by_id(booking_id)
        if not existing:
            raise NotFoundError(f"Booking {booking_id} not found")

        # Determine new times
        new_start = booking_data.start_time if booking_data.start_time else existing.start_time
        new_end = booking_data.end_time if booking_data.end_time else existing.end_time

        # Step 1: Check new time availability
        availability = await self.check_availability(
            existing.employee.id,
            new_start,
            new_end
        )

        if not availability.is_available:
            raise ConflictError(f"New time slot not available: {availability.reason}")

        # Step 2: Update booking
        update_dict = {}
        if booking_data.start_time:
            update_dict['start_time'] = booking_data.start_time
        if booking_data.end_time:
            update_dict['end_time'] = booking_data.end_time
        if booking_data.customer_note is not None:
            update_dict['customer_note'] = booking_data.customer_note

        updated_booking = await self.booking_repo.update_booking(booking_id, update_dict)
        if not updated_booking:
            raise NotFoundError(f"Booking {booking_id} not found")

        return updated_booking

    async def cancel_booking(self, booking_id: UUID) -> BookingResponse:
        """
        Cancel with validation.

        Step 1: Check if cancellable (status)
        Step 2: Update status
        """
        # Step 1: Check if cancellable (status)
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError(f"Booking {booking_id} not found")

        if booking.status in ['cancelled', 'completed']:
            raise ConflictError(f"Cannot cancel booking with status: {booking.status}")

        # Step 2: Update status
        cancelled_booking = await self.booking_repo.update_booking_status(booking_id, 'cancelled')
        if not cancelled_booking:
            raise NotFoundError(f"Booking {booking_id} not found")

        return cancelled_booking
