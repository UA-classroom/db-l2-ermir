from datetime import datetime
from typing import Optional
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.models.employee import (
    EmployeeCreate,
    EmployeeDetail,
    EmployeeResponse,
    EmployeeUpdate,
    InternalEventCreate,
    InternalEventResponse,
    InternalEventUpdate,
    WorkingHoursCreate,
    WorkingHoursResponse,
    WorkingHoursUpdate,
)
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeResponse]):
    """Repository for employee-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "employees"

    async def get_employees(
        self,
        location_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EmployeeResponse]:
        """
        Get list of employees with optional filters.

        Args:
            location_id: Filter by location UUID
            is_active: Filter by active status
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of employees
        """
        from psycopg import sql

        conditions = []
        params = []

        if location_id is not None:
            conditions.append(sql.SQL("location_id = %s"))
            params.append(location_id)

        if is_active is not None:
            conditions.append(sql.SQL("is_active = %s"))
            params.append(is_active)

        # Build WHERE clause safely
        if conditions:
            where_clause = sql.SQL(" AND ").join(conditions)
        else:
            where_clause = sql.SQL("TRUE")

        query = sql.Composed(
            [
                sql.SQL(
                    "SELECT id, user_id, location_id, job_title, bio, color_code, is_active FROM employees WHERE "
                ),
                where_clause,
                sql.SQL(" ORDER BY job_title ASC LIMIT %s OFFSET %s"),
            ]
        )
        params.extend([limit, offset])

        async with self.conn.cursor(row_factory=class_row(EmployeeResponse)) as cur:
            await cur.execute(query, tuple(params))
            return await cur.fetchall()

    async def get_employee_by_id(self, employee_id: UUID) -> Optional[EmployeeResponse]:
        """
        Get a single employee by ID.

        Args:
            employee_id: Employee UUID

        Returns:
            Employee or None if not found
        """
        query = """
            SELECT id, user_id, location_id, job_title, bio, color_code, is_active
            FROM employees
            WHERE id = %s
        """
        async with self.conn.cursor(row_factory=class_row(EmployeeResponse)) as cur:
            await cur.execute(query, (employee_id,))
            return await cur.fetchone()

    async def get_employee_detail(self, employee_id: UUID) -> Optional[EmployeeDetail]:
        """
        Get employee with all related data (working hours and internal events).

        Args:
            employee_id: Employee UUID

        Returns:
            Employee detail or None if not found
        """
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return None

        working_hours = await self.get_employee_working_hours(employee_id)
        internal_events = await self.get_employee_internal_events(employee_id)

        return EmployeeDetail(
            **employee.model_dump(),
            working_hours=working_hours,
            internal_events=internal_events,
        )

    async def create_employee(self, employee_data: EmployeeCreate) -> EmployeeResponse:
        """
        Create a new employee.

        Args:
            employee_data: Employee creation data

        Returns:
            Created employee
        """
        query = """
            INSERT INTO employees (user_id, location_id, job_title, bio, color_code, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, location_id, job_title, bio, color_code, is_active
        """
        async with self.conn.cursor(row_factory=class_row(EmployeeResponse)) as cur:
            await cur.execute(
                query,
                (
                    employee_data.user_id,
                    employee_data.location_id,
                    employee_data.job_title,
                    employee_data.bio,
                    employee_data.color_code,
                    employee_data.is_active,
                ),
            )
            result = await cur.fetchone()
            if not result:
                raise RuntimeError("Failed to create employee")
            return result

    async def update_employee(
        self, employee_id: UUID, employee_data: EmployeeUpdate
    ) -> Optional[EmployeeResponse]:
        """
        Update an employee.

        Args:
            employee_id: Employee UUID
            employee_data: Employee update data

        Returns:
            Updated employee or None if not found
        """
        from psycopg import sql

        updates = []
        params = []

        if employee_data.job_title is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("job_title")))
            params.append(employee_data.job_title)
        if employee_data.bio is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("bio")))
            params.append(employee_data.bio)
        if employee_data.color_code is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("color_code")))
            params.append(employee_data.color_code)
        if employee_data.is_active is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("is_active")))
            params.append(employee_data.is_active)
        if employee_data.location_id is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("location_id")))
            params.append(employee_data.location_id)

        if not updates:
            return await self.get_employee_by_id(employee_id)

        set_clause = sql.SQL(", ").join(updates)
        params.append(employee_id)

        query = sql.Composed(
            [
                sql.SQL("UPDATE employees SET "),
                set_clause,
                sql.SQL(
                    " WHERE id = %s RETURNING id, user_id, location_id, job_title, bio, color_code, is_active"
                ),
            ]
        )

        async with self.conn.cursor(row_factory=class_row(EmployeeResponse)) as cur:
            await cur.execute(query, tuple(params))
            return await cur.fetchone()

    async def delete(self, employee_id: UUID) -> bool:
        """
        Soft delete an employee by setting deleted_at timestamp.

        Args:
            employee_id: Employee UUID

        Returns:
            True if deleted, False if not found
        """
        # Enable soft delete and use base class method
        self.enable_soft_delete = True
        return await self._delete(self.table, employee_id, soft=True)

    # === Working Hours Methods ===

    async def get_employee_working_hours(
        self, employee_id: UUID
    ) -> list[WorkingHoursResponse]:
        """
        Get all working hours for an employee.

        Args:
            employee_id: Employee UUID

        Returns:
            List of working hours
        """
        query = """
            SELECT id, employee_id, day_of_week, start_time, end_time
            FROM working_hours
            WHERE employee_id = %s
            ORDER BY day_of_week ASC, start_time ASC
        """
        async with self.conn.cursor(row_factory=class_row(WorkingHoursResponse)) as cur:
            await cur.execute(query, (employee_id,))
            return await cur.fetchall()

    async def get_working_hours_for_day(
        self, employee_id: UUID, day_of_week: int
    ) -> list[WorkingHoursResponse]:
        """
        Get working hours for a specific day.

        Args:
            employee_id: Employee UUID
            day_of_week: Day of week (1=Monday, 7=Sunday)

        Returns:
            List of working hours for that day (supports split shifts)
        """
        query = """
            SELECT id, employee_id, day_of_week, start_time, end_time
            FROM working_hours
            WHERE employee_id = %s AND day_of_week = %s
            ORDER BY start_time ASC
        """
        async with self.conn.cursor(row_factory=class_row(WorkingHoursResponse)) as cur:
            await cur.execute(query, (employee_id, day_of_week))
            return await cur.fetchall()

    async def add_working_hours(
        self, working_hours_data: WorkingHoursCreate
    ) -> WorkingHoursResponse:
        """
        Add working hours for an employee.

        Args:
            working_hours_data: Working hours creation data

        Returns:
            Created working hours
        """
        query = """
            INSERT INTO working_hours (employee_id, day_of_week, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            RETURNING id, employee_id, day_of_week, start_time, end_time
        """
        async with self.conn.cursor(row_factory=class_row(WorkingHoursResponse)) as cur:
            await cur.execute(
                query,
                (
                    working_hours_data.employee_id,
                    working_hours_data.day_of_week,
                    working_hours_data.start_time,
                    working_hours_data.end_time,
                ),
            )
            result = await cur.fetchone()
            if not result:
                raise RuntimeError("Failed to add working hours")
            return result

    async def update_working_hours(
        self, working_hours_id: UUID, working_hours_data: WorkingHoursUpdate
    ) -> Optional[WorkingHoursResponse]:
        """
        Update working hours.

        Args:
            working_hours_id: Working hours UUID
            working_hours_data: Working hours update data

        Returns:
            Updated working hours or None if not found
        """
        from psycopg import sql

        updates = []
        params = []

        if working_hours_data.start_time is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("start_time")))
            params.append(working_hours_data.start_time)
        if working_hours_data.end_time is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("end_time")))
            params.append(working_hours_data.end_time)

        if not updates:
            query = "SELECT id, employee_id, day_of_week, start_time, end_time FROM working_hours WHERE id = %s"
            async with self.conn.cursor(
                row_factory=class_row(WorkingHoursResponse)
            ) as cur:
                await cur.execute(query, (working_hours_id,))
                return await cur.fetchone()

        set_clause = sql.SQL(", ").join(updates)
        params.append(working_hours_id)

        query = sql.Composed(
            [
                sql.SQL("UPDATE working_hours SET "),
                set_clause,
                sql.SQL(
                    " WHERE id = %s RETURNING id, employee_id, day_of_week, start_time, end_time"
                ),
            ]
        )

        async with self.conn.cursor(row_factory=class_row(WorkingHoursResponse)) as cur:
            await cur.execute(query, tuple(params))
            return await cur.fetchone()

    async def delete_working_hours(self, working_hours_id: UUID) -> bool:
        """
        Delete working hours.

        Args:
            working_hours_id: Working hours UUID

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM working_hours WHERE id = %s"
        async with self.conn.cursor() as cur:
            await cur.execute(query, (working_hours_id,))
            return cur.rowcount > 0

    # === Internal Events Methods ===

    async def get_employee_internal_events(
        self,
        employee_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[InternalEventResponse]:
        """
        Get internal events for an employee with optional date range filter.

        Args:
            employee_id: Employee UUID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of internal events
        """
        from psycopg import sql

        conditions = [sql.SQL("employee_id = %s")]
        params: list = [employee_id]

        if start_date is not None:
            conditions.append(sql.SQL("end_time >= %s"))
            params.append(start_date)

        if end_date is not None:
            conditions.append(sql.SQL("start_time <= %s"))
            params.append(end_date)

        where_clause = sql.SQL(" AND ").join(conditions)

        query = sql.Composed(
            [
                sql.SQL(
                    "SELECT id, employee_id, type, start_time, end_time, description FROM internal_events WHERE "
                ),
                where_clause,
                sql.SQL(" ORDER BY start_time ASC"),
            ]
        )

        async with self.conn.cursor(
            row_factory=class_row(InternalEventResponse)
        ) as cur:
            await cur.execute(query, tuple(params))
            return await cur.fetchall()

    async def add_internal_event(
        self, event_data: InternalEventCreate
    ) -> InternalEventResponse:
        """
        Add an internal event for an employee.

        Args:
            event_data: Internal event creation data

        Returns:
            Created internal event
        """
        query = """
            INSERT INTO internal_events (employee_id, type, start_time, end_time, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, employee_id, type, start_time, end_time, description
        """
        async with self.conn.cursor(
            row_factory=class_row(InternalEventResponse)
        ) as cur:
            await cur.execute(
                query,
                (
                    event_data.employee_id,
                    event_data.type,
                    event_data.start_time,
                    event_data.end_time,
                    event_data.description,
                ),
            )
            result = await cur.fetchone()
            if not result:
                raise RuntimeError("Failed to add internal event")
            return result

    async def update_internal_event(
        self, event_id: UUID, event_data: InternalEventUpdate
    ) -> Optional[InternalEventResponse]:
        """
        Update an internal event.

        Args:
            event_id: Internal event UUID
            event_data: Internal event update data

        Returns:
            Updated internal event or None if not found
        """
        from psycopg import sql

        updates = []
        params = []

        if event_data.type is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("type")))
            params.append(event_data.type)
        if event_data.start_time is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("start_time")))
            params.append(event_data.start_time)
        if event_data.end_time is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("end_time")))
            params.append(event_data.end_time)
        if event_data.description is not None:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("description")))
            params.append(event_data.description)

        if not updates:
            query = "SELECT id, employee_id, type, start_time, end_time, description FROM internal_events WHERE id = %s"
            async with self.conn.cursor(
                row_factory=class_row(InternalEventResponse)
            ) as cur:
                await cur.execute(query, (event_id,))
                return await cur.fetchone()

        set_clause = sql.SQL(", ").join(updates)
        params.append(event_id)

        query = sql.Composed(
            [
                sql.SQL("UPDATE internal_events SET "),
                set_clause,
                sql.SQL(
                    " WHERE id = %s RETURNING id, employee_id, type, start_time, end_time, description"
                ),
            ]
        )

        async with self.conn.cursor(
            row_factory=class_row(InternalEventResponse)
        ) as cur:
            await cur.execute(query, tuple(params))
            return await cur.fetchone()

    async def delete_internal_event(self, event_id: UUID) -> bool:
        """
        Delete an internal event.

        Args:
            event_id: Internal event UUID

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM internal_events WHERE id = %s"
        async with self.conn.cursor() as cur:
            await cur.execute(query, (event_id,))
            return cur.rowcount > 0

    # === Employee Skills Methods ===

    async def get_employee_skills(self, employee_id: UUID) -> list[dict]:
        """
        Get all skills (service variants) for an employee with custom pricing.

        Args:
            employee_id: Employee UUID

        Returns:
            List of skills with service variant details
        """
        query = """
            SELECT
                es.employee_id,
                es.service_variant_id,
                es.custom_price,
                es.custom_duration,
                sv.name AS variant_name,
                sv.price AS base_price,
                sv.duration_minutes AS base_duration,
                s.name AS service_name
            FROM employee_skills es
            JOIN service_variants sv ON es.service_variant_id = sv.id
            JOIN services s ON sv.service_id = s.id
            WHERE es.employee_id = %s
            ORDER BY s.name, sv.name
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (employee_id,))
            rows = await cur.fetchall()

            return [
                {
                    "employee_id": str(row[0]),
                    "service_variant_id": str(row[1]),
                    "custom_price": row[2],
                    "custom_duration": row[3],
                    "variant_name": row[4],
                    "base_price": row[5],
                    "base_duration": row[6],
                    "service_name": row[7],
                }
                for row in rows
            ]

    async def add_employee_skill(
        self,
        employee_id: UUID,
        service_variant_id: UUID,
        custom_price: Optional[float] = None,
        custom_duration: Optional[int] = None,
    ) -> bool:
        """
        Add a skill to an employee with optional custom pricing.

        Args:
            employee_id: Employee UUID
            service_variant_id: Service variant UUID
            custom_price: Optional custom price override
            custom_duration: Optional custom duration override

        Returns:
            True if added successfully
        """
        query = """
            INSERT INTO employee_skills (employee_id, service_variant_id, custom_price, custom_duration)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (employee_id, service_variant_id) DO NOTHING
        """
        async with self.conn.cursor() as cur:
            await cur.execute(
                query, (employee_id, service_variant_id, custom_price, custom_duration)
            )
            return cur.rowcount > 0

    async def remove_employee_skill(
        self, employee_id: UUID, service_variant_id: UUID
    ) -> bool:
        """
        Remove a skill from an employee.

        Args:
            employee_id: Employee UUID
            service_variant_id: Service variant UUID

        Returns:
            True if removed, False if not found
        """
        query = "DELETE FROM employee_skills WHERE employee_id = %s AND service_variant_id = %s"
        async with self.conn.cursor() as cur:
            await cur.execute(query, (employee_id, service_variant_id))
            return cur.rowcount > 0
