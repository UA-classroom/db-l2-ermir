"""
Database Connection Pool Module

This module manages PostgreSQL database connections using psycopg connection pooling.
Connection pooling improves performance by reusing database connections instead of
creating new ones for each request.

The pool is initialized at application startup and closed at shutdown.
Connections are automatically returned to the pool after use.

Usage:
    from app.core.database import db

    # In main.py startup
    await db.connect()

    # In endpoints (via dependency injection)
    async with db.get_connection() as conn:
        # Use connection
        pass

    # In main.py shutdown
    await db.disconnect()
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from app.config import settings


class Database:
    """
    Database connection pool manager.

    Manages a pool of PostgreSQL connections for efficient database access.
    Uses psycopg AsyncConnectionPool for async operations.

    Attributes:
        pool: AsyncConnectionPool instance (None until connect() is called)
        _conninfo: Database connection string from settings

    Pool Configuration:
        - min_size: 5 connections (always kept open)
        - max_size: 20 connections (maximum concurrent connections)
        - timeout: 30 seconds (wait time for available connection)
    """

    def __init__(self):
        self.pool: Optional[AsyncConnectionPool] = None
        self._conninfo: str = settings.DATABASE_URL

    async def connect(self) -> None:
        """
        Initialize the database connection pool.

        Creates an AsyncConnectionPool with configured min/max connections.
        Should be called once at application startup.

        Pool Settings:
            - min_size=5: Minimum connections kept alive
            - max_size=20: Maximum concurrent connections
            - timeout=30: Seconds to wait for available connection

        Raises:
            psycopg.OperationalError: If unable to connect to database

        Note:
            This method is idempotent - calling it multiple times won't
            create multiple pools.
        """
        if not self.pool:
            self.pool = AsyncConnectionPool(
                conninfo=self._conninfo, 
                min_size=5, 
                max_size=20, 
                timeout=30, 
                open=False
            )
            await self.pool.open()

    async def disconnect(self) -> None:
        """
        Close the database connection pool.

        Gracefully closes all connections in the pool.
        Should be called once at application shutdown.

        Args:
            timeout: Maximum 2 seconds to wait for connections to close

        Note:
            Sets pool to None after closing to prevent reuse.
            Safe to call even if pool is already closed.
        """
        if self.pool:
            await self.pool.close(timeout=2)
            self.pool = None

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """
        Get a database connection from the pool.

        This is an async context manager that provides a connection from the pool.
        The connection is automatically returned to the pool when the context exits.

        Yields:
            AsyncConnection: Database connection from the pool

        Raises:
            RuntimeError: If pool not initialized (connect() not called)
            TimeoutError: If no connection available within timeout period

        Usage:
            async with db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM users")
                    results = await cur.fetchall()

        Note:
            Connection is automatically returned to pool on context exit,
            even if an exception occurs.
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

        async with self.pool.connection() as conn:
            yield conn


# Global database instance
db = Database() #TODO: test after build main.py