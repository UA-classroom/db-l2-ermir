from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

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
    # TODO :Consider using typing.overload decorators to satisfy type checkers

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

    def _apply_soft_delete_filter(self, base_condition: str = "1=1") -> str:
        """Apply soft delete filter to a SQL WHERE clause if enabled.

        where_clause: str = "1=1" :  Allows easy appending of AND conditions

        Args:
            base_condition: Existing SQL condition to append to
        Returns: SQL condition string with soft delete filter if enabled

        Note: SQL string concatenation in _apply_soft_delete_filter is acceptable here but document it
        """

        if self.enable_soft_delete:
            return f"{base_condition} AND deleted_at IS NULL"
        return base_condition
    

    async def _execute_one(
        self, query: str, params: tuple[Any, ...], row_factory: type[U]
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
            await cur.execute(query, params)  # type: ignore[arg-type]
            return await cur.fetchone()
        
    async def _execute_many(
        self, query: str, params: tuple[Any, ...], row_factory: type[U]
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
            await cur.execute(query, params)  # type: ignore[arg-type]
            return await cur.fetchall()
        

    async def _execute_scalar(self, query: str, params: tuple[Any, ...]) -> Any:
        """
        Execute a query and return a single scalar value.

        Template method for executing queries that return a single value.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single scalar value or None if not found
        """

        async with self.conn.cursor() as cur:
            await cur.execute(query, params) # type: ignore[arg-type]
            result = await cur.fetchone()
            return result[0] if result else None 
        

    async def _execute_command(self, query: str, params: tuple[Any, ...]) -> int:
        """
        Execute a command that does not return results.

        Template method for executing commands like INSERT, UPDATE, DELETE.

        Args:
            query: SQL command string
            params: Command parameters
        Returns:
            Number of affected rows
        """

        async with self.conn.cursor() as cur:
            result = await cur.execute(query, params)  # type: ignore[arg-type]
            return result.rowcount


    async def _find_by_id(self, table: str, id: UUID | int , row_factory: type[T]) -> Optional[T]:
        """
        Find a record by its ID.

        Args:
            table: Table name
            id: Record ID (UUID or int)
            row_factory: Pydantic model class for row mapping

        Returns:
            Record instance or None if not found
        """

        condition = self._apply_soft_delete_filter("id = %s")
        query = f"SELECT * FROM {table} WHERE {condition}"
        params = (id,)
        return await self._execute_one(query, params, row_factory)
    

    async def _find_all(
        self,
        table: str,
        row_factory: type[T],
        limit: int = 100,
        offset: int = 0,
    ) -> list[T]:
        """
        Find all records with optional pagination.

        Args:
            table: Table name
            row_factory: Pydantic model class for row mapping
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of record instances
        """

        condition = self._apply_soft_delete_filter()    
        query = f"SELECT * FROM {table} WHERE {condition} ORDER BY created_at DESC LIMIT %s OFFSET %s"
        return await self._execute_many(query, (limit, offset), row_factory)
    
    async def _create(
            self,
            table: str,
            data: dict[str, Any],
            row_factory: type[U],
    ) -> U:
        """
        Create a new record in the specified table.

        Args:
            table: Table name
            data: Dictionary of field names and values
            row_factory: Pydantic model class for row mapping

        Returns:
            New record instance
            
        Raises:
            Exception: If record creation fails
        """

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"

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
    ) -> U:
        """
        Update an existing record in the specified table.

        Args:
            table: Table name
            id: Record ID (UUID or int)
            data: Dictionary of field names and new values
            row_factory: Pydantic model class for row mapping       
        Returns:
            Updated record instance
        """

        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        condition = self._apply_soft_delete_filter("id = %s")
        query = f"UPDATE {table} SET {set_clause} WHERE {condition} RETURNING *"
        params = tuple(data.values()) + (id,)
        result = await self._execute_one(query, params, row_factory)
        if result is None:
            raise RuntimeError(f"Failed to update record with id {id} in {table}")
        return result
    

    async def _delete(self, table: str, id: UUID | int, soft: bool = True) -> bool:
        """
        Delete a record (soft or hard based on configuration).

        Args:
            table: Table name
            id: Record ID (UUID or int)
            soft: If True and soft delete is enabled, sets deleted_at. Otherwise hard deletes.

        Returns:
            True if successful, False otherwise
        """

        if soft and self.enable_soft_delete:
            # Soft delete by setting deleted_at timestamp
            condition = self._apply_soft_delete_filter("id = %s")
            query = f"UPDATE {table} SET deleted_at = NOW() WHERE {condition}"
            params = (id,)
            rowcount = await self._execute_command(query, params)
            return rowcount > 0
        else:
            # Hard delete
            condition = self._apply_soft_delete_filter("id = %s")
            query = f"DELETE FROM {table} WHERE {condition}"
            params = (id,)
            rowcount = await self._execute_command(query, params)
            return rowcount > 0  
        

    async def _exists(self, table: str, id: UUID) -> bool:
        """
        Check if a record exists by its ID.

        Args:
            table: Table name
            id: Record ID (UUID or int)

        Returns:
            True if record exists, False otherwise
        """

        condition = self._apply_soft_delete_filter("id = %s")
        query = f"SELECT 1 FROM {table} WHERE {condition}"
        params = (id,)
        result = await self._execute_scalar(query, params)
        return result is not None