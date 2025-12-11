"""
Service Repository Module

Handles all database operations for services, service variants, and categories.

This repository includes:
- Service CRUD operations with filters (business_id, category_id, is_active)
- Service variant management (create, update, delete)
- Category management for service classification
- Optimized queries to fetch services with variants in one query (eliminates N+1)

Key Features:
- get_services_with_variants(): Fetches services WITH nested variants in a single query
  Uses LEFT JOIN to eliminate N+1 query problem when displaying service variants
- Dynamic filtering for services by business, category, and active status
- Full CRUD support for services, variants, and categories
"""

from typing import Optional
from uuid import UUID

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from app.models.service import (
    CategoryCreate,
    CategoryResponse,
    ServiceCreate,
    ServiceDetail,
    ServiceResponse,
    ServiceUpdate,
    ServiceVariantCreate,
    ServiceVariantResponse,
    ServiceVariantUpdate,
)
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[ServiceResponse]):
    """Repository for service-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "services"
        self.enable_soft_delete = False  # Services don't use soft delete

    async def get_services(
        self,
        business_id: Optional[UUID] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ServiceResponse]:
        """
        Get list of services with optional filters.

        Args:
            business_id: Filter by business UUID
            category_id: Filter by category ID
            is_active: Filter by active status
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of services
        """
        conditions = []
        params = []

        if business_id is not None:
            conditions.append(sql.SQL("business_id = %s"))
            params.append(business_id)

        if category_id is not None:
            conditions.append(sql.SQL("category_id = %s"))
            params.append(category_id)

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
                    "SELECT id, business_id, category_id, name, description, is_active FROM services WHERE "
                ),
                where_clause,
                sql.SQL(" ORDER BY name ASC LIMIT %s OFFSET %s"),
            ]
        )
        params.extend([limit, offset])

        return await self._execute_many(query, tuple(params), ServiceResponse)
    

    async def get_service_by_id(self, service_id: UUID) -> Optional[ServiceResponse]:
        """
        Get a single service by ID.

        Args:
            service_id: Service UUID

        Returns:
            Service or None if not found
        """
        return await self._find_by_id(self.table, service_id, ServiceResponse)

    async def get_service_variants(
        self, service_id: UUID
    ) -> list[ServiceVariantResponse]:
        """
        Get all variants for a service.

        Args:
            service_id: Service UUID

        Returns:
            List of service variants
        """
        query = """
            SELECT id, service_id, name, price, duration_minutes
            FROM service_variants
            WHERE service_id = %s
            ORDER BY price ASC
        """
        return await self._execute_many(query, (service_id,), ServiceVariantResponse)

    async def get_services_with_variants(
        self, business_id: UUID
    ) -> list[ServiceDetail]:
        """
        Get all services for a business WITH their variants in one query.

        This eliminates N+1 queries by using a JOIN to fetch all variants
        at once, then grouping them by service in Python.

        Args:
            business_id: Business UUID

        Returns:
            List of services with nested variants
        """
        query = """
            SELECT 
                s.id AS service_id,
                s.business_id,
                s.category_id,
                s.name AS service_name,
                s.description,
                s.is_active,
                sv.id AS variant_id,
                sv.service_id AS variant_service_id,
                sv.name AS variant_name,
                sv.price,
                sv.duration_minutes
            FROM services s
            LEFT JOIN service_variants sv ON s.id = sv.service_id
            WHERE s.business_id = %s AND s.is_active = TRUE
            ORDER BY s.name, sv.name
        """

        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, (business_id,))
            rows = await cur.fetchall()

        # Group variants by service
        services = {}
        for row in rows:
            service_id = row["service_id"]

            if service_id not in services:
                # Create service
                services[service_id] = ServiceDetail(
                    id=row["service_id"],
                    business_id=row["business_id"],
                    category_id=row["category_id"],
                    name=row["service_name"],
                    description=row["description"],
                    is_active=row["is_active"],
                    variants=[],
                )

            # Add variant if exists
            if row["variant_id"]:
                variant = ServiceVariantResponse(
                    id=row["variant_id"],
                    service_id=service_id,
                    name=row["variant_name"],
                    price=row["price"],
                    duration_minutes=row["duration_minutes"],
                )
                services[service_id].variants.append(variant)

        return list(services.values())

    async def get_service_variant_by_id(
        self, variant_id: UUID
    ) -> Optional[ServiceVariantResponse]:
        """Get single service variant by ID."""
        query = """
            SELECT id, service_id, name, price, duration_minutes
            FROM service_variants
            WHERE id = %s
        """
        return await self._execute_one(query, (variant_id,), ServiceVariantResponse)

    async def get_categories(
        self, limit: int = 100, offset: int = 0
    ) -> list[CategoryResponse]:
        """
        Get all categories.

        Args:
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of categories
        """
        query = """
            SELECT id, parent_id, name, slug
            FROM categories
            ORDER BY name ASC
            LIMIT %s OFFSET %s
        """
        return await self._execute_many(query, (limit, offset), CategoryResponse)

    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """
        Create a new category.

        Args:
            category_data: Category creation data

        Returns:
            Created category
        """
        data = category_data.model_dump()
        return await self._create("categories", data, CategoryResponse)

    async def create_service(self, service_data: ServiceCreate) -> ServiceResponse:
        """
        Create a new service.

        Args:
            service_data: Service creation data

        Returns:
            Created service
        """
        data = service_data.model_dump()
        return await self._create(self.table, data, ServiceResponse)

    async def update_service(
        self, service_id: UUID, service_data: ServiceUpdate
    ) -> Optional[ServiceResponse]:
        """
        Update a service.

        Args:
            service_id: Service UUID
            service_data: Service update data

        Returns:
            Updated service or None if not found
        """
        # Get only fields that were actually set (exclude None/unset fields)
        updates = service_data.model_dump(exclude_unset=True)

        if not updates:
            # No fields to update, return existing service
            return await self.get_service_by_id(service_id)

        return await self._update(self.table, service_id, updates, ServiceResponse)

    async def create_variant(
        self, variant_data: ServiceVariantCreate
    ) -> ServiceVariantResponse:
        """
        Create a new service variant.

        Args:
            variant_data: Service variant creation data

        Returns:
            Created service variant
        """
        data = variant_data.model_dump()
        return await self._create("service_variants", data, ServiceVariantResponse)

    async def update_variant(
        self, variant_id: UUID, variant_data: ServiceVariantUpdate
    ) -> Optional[ServiceVariantResponse]:
        """
        Update a service variant.

        Args:
            variant_id: Service variant UUID
            variant_data: Service variant update data

        Returns:
            Updated service variant or None if not found
        """
        # Get only fields that were actually set (exclude None/unset fields)
        updates = variant_data.model_dump(exclude_unset=True)

        if not updates:
            # No fields to update, fetch existing variant
            query = "SELECT * FROM service_variants WHERE id = %s"
            return await self._execute_one(query, (variant_id,), ServiceVariantResponse)

        return await self._update(
            "service_variants", variant_id, updates, ServiceVariantResponse
        )

    async def delete_variant(self, variant_id: UUID) -> bool:
        """
        Delete a service variant.

        Args:
            variant_id: Service variant UUID

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM service_variants WHERE id = %s"
        async with self.conn.cursor() as cur:
            await cur.execute(query, (variant_id,))
            return cur.rowcount > 0
