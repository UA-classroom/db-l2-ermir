from datetime import datetime, time, timedelta
from typing import Optional
from uuid import UUID

from app.models.employee import (
    AvailabilityResponse,
    InternalEventResponse,
    WorkingHoursResponse,
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.employee_repository import EmployeeRepository


class ScheduleService:
    """
    Service for employee schedule and availability logic.

    This service is critical for the booking system as it determines
    when employees are available to take bookings.
    """

    def __init__(
        self, employee_repo: EmployeeRepository, booking_repo: BookingRepository
    ):
        self.employee_repo = employee_repo
        self.booking_repo = booking_repo

    async def check_availability(
        self,
        employee_id: UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> AvailabilityResponse:
        """
        Check if an employee is available for a booking at a specific time.

        This is the core availability algorithm that checks:
        1. Employee working hours for that day
        2. Internal events (vacation, sick leave, meetings) that overlap

        Args:
            employee_id: Employee UUID
            start_time: Booking start time
            end_time: Booking end time

        Returns:
            AvailabilityResponse with is_available and reason if not available
        """
        # Step 1: Check if employee is working on this day
        day_of_week = start_time.isoweekday()  # 1=Monday, 7=Sunday
        working_hours = await self.employee_repo.get_working_hours_for_day(
            employee_id, day_of_week
        )

        if not working_hours:
            return AvailabilityResponse(
                is_available=False,
                reason=f"Employee not working on this day (day {day_of_week})"
            )

        # Step 2: Check if the booking time falls within working hours
        booking_start_time = start_time.time()
        booking_end_time = end_time.time()

        is_within_working_hours = False
        for shift in working_hours:
            # Handle time comparisons
            if shift.start_time <= booking_start_time and booking_end_time <= shift.end_time:
                is_within_working_hours = True
                break

        if not is_within_working_hours:
            return AvailabilityResponse(
                is_available=False,
                reason=f"Requested time outside working hours. Working hours: {', '.join([f'{wh.start_time}-{wh.end_time}' for wh in working_hours])}"
            )

        # Step 3: Check for internal events (vacation, sick, meetings)
        internal_events = await self.employee_repo.get_employee_internal_events(
            employee_id,
            start_date=start_time,
            end_date=end_time
        )

        if internal_events:
            # Check if any event overlaps with the requested time
            for event in internal_events:
                if self._times_overlap(start_time, end_time, event.start_time, event.end_time):
                    return AvailabilityResponse(
                        is_available=False,
                        reason=f"Employee has internal event: {event.type} ({event.start_time} - {event.end_time})"
                    )

        # All checks passed - employee is available
        return AvailabilityResponse(is_available=True, reason=None)

    async def get_employee_schedule(
        self,
        employee_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Get complete employee schedule including working hours and internal events.

        Args:
            employee_id: Employee UUID
            start_date: Optional start date for internal events filter
            end_date: Optional end date for internal events filter

        Returns:
            Dictionary with working_hours and internal_events
        """
        working_hours = await self.employee_repo.get_employee_working_hours(employee_id)
        internal_events = await self.employee_repo.get_employee_internal_events(
            employee_id, start_date, end_date
        )

        return {
            "employee_id": str(employee_id),
            "working_hours": working_hours,
            "internal_events": internal_events,
        }

    def is_employee_working(
        self,
        working_hours: list[WorkingHoursResponse],
        day_of_week: int,
        check_time: time
    ) -> bool:
        """
        Check if employee is working at a specific day and time.

        Args:
            working_hours: List of employee's working hours
            day_of_week: Day of week (1=Monday, 7=Sunday)
            check_time: Time to check

        Returns:
            True if employee is working at that time
        """
        for shift in working_hours:
            if shift.day_of_week == day_of_week:
                if shift.start_time <= check_time <= shift.end_time:
                    return True
        return False

    def has_internal_event(
        self,
        internal_events: list[InternalEventResponse],
        start_time: datetime,
        end_time: datetime
    ) -> Optional[InternalEventResponse]:
        """
        Check if there's an internal event that overlaps with the given time range.

        Args:
            internal_events: List of employee's internal events
            start_time: Start time to check
            end_time: End time to check

        Returns:
            Conflicting internal event or None if no conflict
        """
        for event in internal_events:
            if self._times_overlap(start_time, end_time, event.start_time, event.end_time):
                return event
        return None

    @staticmethod
    def _times_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """
        Check if two time ranges overlap.

        Two ranges overlap if:
        - start1 < end2 AND start2 < end1

        Args:
            start1: First range start
            end1: First range end
            start2: Second range start
            end2: Second range end

        Returns:
            True if ranges overlap
        """
        return start1 < end2 and start2 < end1

    async def get_available_slots(
        self,
        employee_id: UUID,
        date: datetime,
        duration_minutes: int,
        slot_interval_minutes: int = 30,
    ) -> list[dict]:
        """
        Get available time slots for an employee on a specific date.

        This is useful for showing customers available booking times.

        Args:
            employee_id: Employee UUID
            date: Date to check (time component ignored)
            duration_minutes: Duration needed for the booking
            slot_interval_minutes: Interval between slots (default 30 minutes)

        Returns:
            List of available time slots with start and end times
        """
        # Get working hours for this day
        day_of_week = date.isoweekday()
        working_hours = await self.employee_repo.get_working_hours_for_day(
            employee_id, day_of_week
        )

        if not working_hours:
            return []

        # Define day range for fetching events and bookings
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get internal events
        internal_events = await self.employee_repo.get_employee_internal_events(
            employee_id, day_start, day_end
        )

        # Get existing bookings
        bookings = await self.booking_repo.get_employee_bookings_in_range(
            employee_id, day_start, day_end
        )

        available_slots = []

        # For each working shift, generate possible time slots
        for shift in working_hours:
            # Convert shift times to datetime for this specific date
            shift_start = datetime.combine(date.date(), shift.start_time)
            shift_end = datetime.combine(date.date(), shift.end_time)

            # Generate slots with the specified interval
            current_slot_start = shift_start

            while current_slot_start + timedelta(minutes=duration_minutes) <= shift_end:
                slot_end = current_slot_start + timedelta(minutes=duration_minutes)

                # Check if this slot conflicts with any internal event
                has_conflict = False
                for event in internal_events:
                    if self._times_overlap(
                        current_slot_start, slot_end, event.start_time, event.end_time
                    ):
                        has_conflict = True
                        break

                # Check conflicts with existing bookings
                if not has_conflict:
                    for booking in bookings:
                        # booking.start_time is offset-aware usually, ensure comparison compatibility
                        # Assuming repos return compatible types or using replacement below
                        b_start = (
                            booking.start_time.replace(tzinfo=None)
                            if booking.start_time.tzinfo
                            else booking.start_time
                        )
                        b_end = (
                            booking.end_time.replace(tzinfo=None)
                            if booking.end_time.tzinfo
                            else booking.end_time
                        )

                        if self._times_overlap(
                            current_slot_start, slot_end, b_start, b_end
                        ):
                            has_conflict = True
                            break

                if not has_conflict:
                    available_slots.append(
                        {
                            "start_time": current_slot_start.isoformat(),
                            "end_time": slot_end.isoformat(),
                        }
                    )

                # Move to next slot
                current_slot_start += timedelta(minutes=slot_interval_minutes)

        return available_slots
