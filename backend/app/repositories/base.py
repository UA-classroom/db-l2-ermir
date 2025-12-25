from typing import Any, Generic, LiteralString, Optional, TypeVar
from uuid import UUID

from psycopg import AsyncConnection, sql
from psycopg.rows import class_row
from psycopg.sql import Composed

T = TypeVar("T")
U = TypeVar("U")


class BaseRepository(Generic[T]):
    """
    Base repository providing common database operations.

    All domain repositories should inherit from this class.

    This class implements the Template Method pattern, providing reusable
    query execution logic while allowing subclasses to define specific queries.

    Design Pattern:
    ---------------
    Subclasses create "convenience wrapper" methods that simplify the base class API:
    - Base: find_by_id(table, id, row_factory) - Generic, requires all params
    - Subclass: find_by_id(user_id) - Domain-specific, delegates to base

    This is intentional and provides a clean API for service layer while maintaining
    DRY principles. Type checkers may warn about incompatible overrides, but this
    is a deliberate design choice for better ergonomics.

    Soft Delete Configuration:
    -------------------------
    Subclasses can configure soft delete behavior by setting:
    - self.table: Table name for generic CRUD operations
    - self.enable_soft_delete: Whether to filter deleted_at IS NULL (default: False)
    """


    def __init__(self, conn: AsyncConnection):
        """Initialize the repository with a database connection.
        Args:
            conn: Database connection
            table: Table name for generic CRUD operations
            enable_soft_delete: Whether to filter deleted_at IS NULL (default: False)

        Returns: None
        """
        self.conn = conn
        self.table: str = ""
        self.enable_soft_delete: bool = False

    def _apply_soft_delete_filter(
        self, base_condition: sql.SQL | Composed | None = None
    ) -> Composed:
        """
        Apply soft delete filter to a WHERE clause.

        Args:
            base_condition: Existing WHERE condition as sql.SQL or sql.Composed (e.g., sql.SQL("id = %s"))
                           If None, defaults to sql.SQL("1=1")

        Returns:
            Composed condition with soft delete filter appended if enabled
        """
        if base_condition is None:
            base_condition = sql.SQL("1=1")

        # Ensure base_condition is Composed
        if isinstance(base_condition, sql.SQL):
            base_condition = sql.Composed([base_condition])

        if self.enable_soft_delete:
            return sql.Composed([base_condition, sql.SQL(" AND deleted_at IS NULL")])
        return base_condition

    async def _execute_one(
        self,
        query: LiteralString | Composed,
        params: tuple[Any, ...],
        row_factory: type[U],
    ) -> Optional[U]:
        """
        Execute a query and return a single result.

        Template method for executing queries that return at most one row.

        Args:
            query: SQL query string
            params: Query parameters
            row_factory: Pydantic model class for row mapping

        Returns:
            Single record instance or None if not found
        """
        async with self.conn.cursor(row_factory=class_row(row_factory)) as cur:
            await cur.execute(query, params)
            return await cur.fetchone()

    async def _execute_many(
        self,
        query: LiteralString | Composed,
        params: tuple[Any, ...],
        row_factory: type[U],
    ) -> list[U]:
        """
        Execute a query and return multiple results.

        Template method for executing queries that return multiple rows.

        Args:
            query: SQL query string
            params: Query parameters
            row_factory: Pydantic model class for row mapping

        Returns:
            List of record instances
        """
        async with self.conn.cursor(row_factory=class_row(row_factory)) as cur:
            await cur.execute(query, params)
            return await cur.fetchall()

    async def _execute_scalar(
        self, query: LiteralString | Composed, params: tuple[Any, ...]
    ) -> Any:
        """
        Execute a query and return a scalar value.

        Template method for executing queries that return a single value
        (e.g., COUNT, EXISTS, or single column).

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single scalar value or None
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, params)  # type: ignore[arg-type]
            result = await cur.fetchone()
            return result[0] if result else None

    

    async def _execute_command(
        self, query: LiteralString | Composed, params: tuple[Any, ...]
    ) -> int:
        """
        Execute a command (INSERT/UPDATE/DELETE) without returning data.

        Template method for executing commands that modify data but don't
        need to return the modified rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, params)  # type: ignore[arg-type]
            return cur.rowcount

    async def _find_by_id(
        self, table: str, id: UUID | int, row_factory: type[T]
    ) -> Optional[T]:
        """
        Find a record by its ID.

        Args:
            table: Table name
            id: Record UUID
            row_factory: Pydantic model class for row mapping

        Returns:
            Record instance or None if not found
        """
        condition = self._apply_soft_delete_filter(sql.SQL("id = %s"))
        query = sql.Composed(
            [
                sql.SQL("SELECT * FROM "),
                sql.Identifier(table),
                sql.SQL(" WHERE "),
                condition,
            ]
        )
        return await self._execute_one(query, (id,), row_factory)


    async def _find_all(
        self,
        table: str,
        row_factory: type[T],
        limit: int = 100,
        offset: int = 0,
    ) -> list[T]:
        """
        Find all records with pagination.

        Args:
            table: Table name
            row_factory: Pydantic model class for row mapping
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of record instances
        """
        condition = self._apply_soft_delete_filter()
        query = sql.Composed(
            [
                sql.SQL("SELECT * FROM "),
                sql.Identifier(table),
                sql.SQL(" WHERE "),
                condition,
                sql.SQL(" ORDER BY created_at DESC LIMIT %s OFFSET %s"),
            ]
        )
        return await self._execute_many(query, (limit, offset), row_factory)

    async def _create(
        self, table: str, data: dict[str, Any], row_factory: type[U]
    ) -> U:
        """
        Create a new record.

        Args:
            table: Table name
            data: Dictionary of column names and values
            row_factory: Pydantic model class for row mapping

        Returns:
            Created record instance
        """
        columns = sql.SQL(", ").join([sql.Identifier(k) for k in data.keys()])
        placeholders = sql.SQL(", ").join([sql.SQL("%s")] * len(data))

        query = sql.Composed(
            [
                sql.SQL("INSERT INTO "),
                sql.Identifier(table),
                sql.SQL(" ("),
                columns,
                sql.SQL(") VALUES ("),
                placeholders,
                sql.SQL(") RETURNING *"),
            ]
        )

        result = await self._execute_one(query, tuple(data.values()), row_factory)
        if result is None:
            raise RuntimeError(f"Failed to create record in {table}")
        return result

    async def _update(
        self,
        table: str,
        id: UUID | int,
        data: dict[str, Any],
        row_factory: type[U],
    ) -> Optional[U]:
        """
        Update an existing record.

        Args:
            table: Table name
            id: Record UUID
            data: Dictionary of column names and values to update
            row_factory: Pydantic model class for row mapping

        Returns:
            Updated record instance or None if not found
        """
        set_parts = [
            sql.SQL("{} = %s").format(sql.Identifier(key)) for key in data.keys()
        ]
        set_clause = sql.SQL(", ").join(set_parts)
        condition = self._apply_soft_delete_filter(sql.SQL("id = %s"))

        query = sql.Composed(
            [
                sql.SQL("UPDATE "),
                sql.Identifier(table),
                sql.SQL(" SET "),
                set_clause,
                sql.SQL(" WHERE "),
                condition,
                sql.SQL(" RETURNING *"),
            ]
        )
        return await self._execute_one(query, (*data.values(), id), row_factory)

    async def _delete(self, table: str, id: UUID | int, soft: bool = True) -> bool:
        """
        Delete a record (soft or hard delete based on configuration).

        Args:
            table: Table name
            id: Record UUID or int
            soft: If True and soft delete is enabled, sets deleted_at. Otherwise hard delete.

        Returns:
            True if record was deleted, False if not found
        """
        if soft and self.enable_soft_delete:
            # Soft delete: set deleted_at timestamp
            condition = self._apply_soft_delete_filter(sql.SQL("id = %s"))
            query = sql.Composed(
                [
                    sql.SQL("UPDATE "),
                    sql.Identifier(table),
                    sql.SQL(" SET deleted_at = NOW() WHERE "),
                    condition,
                ]
            )
            rowcount = await self._execute_command(query, (id,))
            return rowcount > 0
        else:
            # Hard delete: permanently remove
            query = sql.Composed(
                [
                    sql.SQL("DELETE FROM "),
                    sql.Identifier(table),
                    sql.SQL(" WHERE id = %s"),
                ]
            )
            rowcount = await self._execute_command(query, (id,))
            return rowcount > 0

    async def _exists(self, table: str, id: UUID) -> bool:
        """
        Check if a record exists.

        Args:
            table: Table name
            id: Record UUID

        Returns:
            True if record exists and not soft-deleted
        """
        condition = self._apply_soft_delete_filter(sql.SQL("id = %s"))
        query = sql.Composed(
            [
                sql.SQL("SELECT EXISTS(SELECT 1 FROM "),
                sql.Identifier(table),
                sql.SQL(" WHERE "),
                condition,
                sql.SQL(")"),
            ]
        )
        result = await self._execute_scalar(query, (id,))
        return result if result is not None else False
