"""
Business Repository Module

Handles all database operations for businesses, locations, contacts, and services.

This repository includes:
- Business CRUD operations with search filters (city, name, category, min_rating)
- Location management for businesses
- Contact management for locations
- Service retrieval for businesses
- Calculated fields (average_rating, review_count, primary_category) via JOIN queries
- Soft delete support for businesses and locations

Rating Calculation:
    Ratings are calculated via LEFT JOINs following this data flow:
    businesses → locations → bookings → reviews

    This maintains database normalization by not storing redundant data,
    while still providing aggregated rating information in responses.
"""

from typing import Optional
from uuid import UUID

from psycopg import sql

from app.core.exceptions import ConflictError
from app.models.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    LocationCreate,
    LocationImageResponse,
    LocationResponse,
    LocationSearchResult,
    LocationUpdate,
)
from app.models.service import ServiceResponse
from app.repositories.base import BaseRepository


class BusinessRepository(BaseRepository[BusinessResponse]):
    """Repository for business data access."""

    def __init__(self, conn):
        super().__init__(conn)
        self.table = "businesses"
        self.enable_soft_delete = True

    async def get_businesses(
        self,
        city: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        owner_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BusinessResponse]:
        """
        Get list of businesses with optional filters.

        Args:
            city: Filter by city (case-insensitive partial match)
            name: Filter by business name (case-insensitive partial match)
            category: Filter by category name
            min_rating: Minimum average rating (1-5)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of businesses with ratings and category
        """
        # Build query with JOINs to get ratings and category
        query = """
            SELECT 
                b.*,
                COALESCE(AVG(r.rating), 0) as average_rating,
                COUNT(DISTINCT r.id) as review_count,
                (
                    SELECT c.name 
                    FROM services s 
                    LEFT JOIN categories c ON s.category_id = c.id 
                    WHERE s.business_id = b.id 
                    LIMIT 1
                ) as primary_category
            FROM businesses b
            LEFT JOIN locations l ON b.id = l.business_id AND l.deleted_at IS NULL
            LEFT JOIN bookings bk ON l.id = bk.location_id AND bk.deleted_at IS NULL
            LEFT JOIN reviews r ON bk.id = r.booking_id
            WHERE b.deleted_at IS NULL
        """
        params = []

        if name:
            query += " AND b.name ILIKE %s"
            params.append(f"%{name}%")

        if city:
            query += " AND l.city ILIKE %s"
            params.append(f"%{city}%")

        if owner_id:
            query += " AND b.owner_id = %s"
            params.append(owner_id)

        query += " GROUP BY b.id"

        # Apply HAVING filters after GROUP BY
        if min_rating is not None:
            query += " HAVING AVG(r.rating) >= %s"
            params.append(min_rating)

        # Filter by category in outer query if needed
        if category:
            query = f"""
                SELECT * FROM ({query}) as businesses_with_ratings
                WHERE primary_category ILIKE %s
            """
            params.append(f"%{category}%")

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        return await self._execute_many(query, tuple(params), BusinessResponse)

    async def get_business_by_id(self, business_id: UUID) -> Optional[BusinessResponse]:
        """
        Get a single business by ID with ratings and category.

        Args:
            business_id: Business UUID

        Returns:
            Business with ratings and category, or None if not found
        """
        query = """
                SELECT 
                    b.*,
                    COALESCE(AVG(r.rating), 0) as average_rating,
                    COUNT(DISTINCT r.id) as review_count,
                    (
                        SELECT c.name 
                        FROM services s 
                        LEFT JOIN categories c ON s.category_id = c.id 
                        WHERE s.business_id = b.id 
                        LIMIT 1
                    ) as primary_category
                FROM businesses b
                LEFT JOIN locations l ON b.id = l.business_id AND l.deleted_at IS NULL
                LEFT JOIN bookings bk ON l.id = bk.location_id AND bk.deleted_at IS NULL
                LEFT JOIN reviews r ON bk.id = r.booking_id
                WHERE b.id = %s AND b.deleted_at IS NULL
                GROUP BY b.id
            """
        return await self._execute_one(query, (business_id,), BusinessResponse)

    async def get_business_locations(self, business_id: UUID) -> list[LocationResponse]:
        """
        Get all locations for a business.

        Args:
            business_id: Business UUID

        Returns:
            List of locations
        """
        query = "SELECT * FROM locations WHERE business_id = %s ORDER BY name"
        return await self._execute_many(query, (business_id,), LocationResponse)

    async def get_business_services(self, business_id: UUID) -> list[ServiceResponse]:
        """
        Get all services for a business.

        Args:
            business_id: Business UUID

        Returns:
            List of services
        """
        query = """
            SELECT id, business_id, category_id, name, description, is_active
            FROM services
            WHERE business_id = %s AND is_active = TRUE
            ORDER BY name
        """
        return await self._execute_many(query, (business_id,), ServiceResponse)

    async def get_location_contacts(self, location_id: UUID) -> list[ContactResponse]:
        """
        Get all contacts for a location.

        Args:
            location_id: Location UUID

        Returns:
            List of contacts
        """
        query = "SELECT * FROM location_contacts WHERE location_id = %s ORDER BY contact_type"
        return await self._execute_many(query, (location_id,), ContactResponse)

    async def get_location_images(
        self, location_id: UUID
    ) -> list[LocationImageResponse]:
        """
        Get all images for a location.

        Args:
            location_id: Location UUID

        Returns:
            List of location images ordered by primary flag and display order
        """
        query = """
            SELECT id, location_id, url, alt_text, display_order, is_primary
            FROM location_images
            WHERE location_id = %s
            ORDER BY is_primary DESC, display_order ASC
        """
        return await self._execute_many(query, (location_id,), LocationImageResponse)

    async def get_location_by_id(self, location_id: UUID) -> Optional[LocationResponse]:
        """
        Get a single location by ID.

        Args:
            location_id: Location UUID

        Returns:
            Location or None if not found
        """
        query = "SELECT * FROM locations WHERE id = %s AND deleted_at IS NULL"
        return await self._execute_one(query, (location_id,), LocationResponse)

    async def get_contact_by_id(self, contact_id: int) -> Optional[ContactResponse]:
        """
        Get a single contact by ID.

        Args:
            contact_id: Contact ID (SERIAL, not UUID)

        Returns:
            Contact or None if not found
        """
        query = "SELECT * FROM location_contacts WHERE id = %s"
        return await self._execute_one(query, (contact_id,), ContactResponse)

    async def create_business(self, business_data: BusinessCreate) -> BusinessResponse:
        """
        Create a new business.

        Args:
            business_data: Business creation data

        Returns:
            Created business

        Raises:
            ConflictError: If business with slug or org_number already exists
        """
        try:
            data = {
                "owner_id": business_data.owner_id,
                "name": business_data.name,
                "org_number": business_data.org_number,
                "slug": business_data.slug,
            }
            return await self._create("businesses", data, BusinessResponse)
        except Exception as e:
            # PostgreSQL unique constraint violation
            error_msg = str(e).lower()
            if "unique constraint" in error_msg or "duplicate key" in error_msg:
                if "slug" in error_msg:
                    raise ConflictError(
                        f"Business with slug '{business_data.slug}' already exists"
                    )
                elif "org_number" in error_msg:
                    raise ConflictError(
                        f"Business with org_number '{business_data.org_number}' already exists"
                    )
                else:
                    raise ConflictError(
                        "Business with this slug or org_number already exists"
                    )
            raise

    async def update_business(
        self, business_id: UUID, business_data: BusinessUpdate
    ) -> Optional[BusinessResponse]:
        """
        Update a business.

        Args:
            business_id: Business UUID
            business_data: Business update data

        Returns:
            Updated business or None if not found
        """
        # Only include fields that are not None
        data = {}
        if business_data.name is not None:
            data["name"] = business_data.name
        if business_data.org_number is not None:
            data["org_number"] = business_data.org_number
        if business_data.slug is not None:
            data["slug"] = business_data.slug

        if not data:
            # No fields to update, return existing business
            return await self.get_business_by_id(business_id)

        return await self._update("businesses", business_id, data, BusinessResponse)

    async def get_locations(
        self,
        city: Optional[str] = None,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LocationSearchResult]:
        """
        Get locations across all businesses with optional filters.

        Args:
            city: Filter by city
            query: Search query (business name or location name)
            category: Filter by category
            limit: Max results
            offset: Pagination offset

        Returns:
            List of locations with business details
        """
        # TODO: legacy code - using b.created_at...Need created_at column at location table

        sql_query = """
            SELECT 
                l.*,
                b.created_at,
                b.name as business_name,
                COALESCE(AVG(r.rating), 0) as average_rating,
                COUNT(DISTINCT r.id) as review_count,
                (
                    SELECT c.name 
                    FROM services s 
                    LEFT JOIN categories c ON s.category_id = c.id 
                    WHERE s.business_id = b.id 
                    LIMIT 1
                ) as primary_category,
                (
                    SELECT li.url 
                    FROM location_images li 
                    WHERE li.location_id = l.id 
                    ORDER BY li.is_primary DESC, li.display_order ASC 
                    LIMIT 1
                ) as primary_image
            FROM locations l
            JOIN businesses b ON l.business_id = b.id
            LEFT JOIN bookings bk ON l.id = bk.location_id AND bk.deleted_at IS NULL
            LEFT JOIN reviews r ON bk.id = r.booking_id
            WHERE l.deleted_at IS NULL AND b.deleted_at IS NULL
        """
        params = []

        if city:
            sql_query += " AND l.city ILIKE %s"
            params.append(f"%{city}%")

        if query:
            sql_query += " AND (b.name ILIKE %s OR l.name ILIKE %s)"
            params.append(f"%{query}%")
            params.append(f"%{query}%")

        # Category filter needs to check services
        if category:
            sql_query += """
                AND EXISTS (
                    SELECT 1 FROM services s
                    JOIN categories c ON s.category_id = c.id
                    WHERE s.business_id = b.id AND c.slug ILIKE %s
                )
            """
            params.append(f"%{category}%")

        sql_query += " GROUP BY l.id, b.id, b.name, b.created_at"
        sql_query += (
            " ORDER BY average_rating DESC, b.created_at DESC LIMIT %s OFFSET %s"
        )
        params.extend([limit, offset])

        return await self._execute_many(sql_query, tuple(params), LocationSearchResult)

    async def create_location(self, location_data: LocationCreate) -> LocationResponse:
        """
        Create a new location for a business.

        Args:
            location_data: Location creation data

        Returns:
            Created location
        """
        data = {
            "business_id": location_data.business_id,
            "name": location_data.name,
            "address": location_data.address,
            "city": location_data.city,
            "postal_code": location_data.postal_code,
            "latitude": location_data.latitude,
            "longitude": location_data.longitude,
        }
        return await self._create("locations", data, LocationResponse)

    async def update_location(
        self, location_id: UUID, location_data: LocationUpdate
    ) -> Optional[LocationResponse]:
        """
        Update a location.

        Args:
            location_id: Location UUID
            location_data: Location update data

        Returns:
            Updated location or None if not found
        """
        # Only include fields that are not None
        data = {}
        if location_data.name is not None:
            data["name"] = location_data.name
        if location_data.address is not None:
            data["address"] = location_data.address
        if location_data.city is not None:
            data["city"] = location_data.city
        if location_data.postal_code is not None:
            data["postal_code"] = location_data.postal_code
        if location_data.latitude is not None:
            data["latitude"] = location_data.latitude
        if location_data.longitude is not None:
            data["longitude"] = location_data.longitude

        if not data:
            # No fields to update, return existing location
            query = "SELECT * FROM locations WHERE id = %s"
            return await self._execute_one(query, (location_id,), LocationResponse)

        return await self._update("locations", location_id, data, LocationResponse)

    async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """
        Create a new contact for a location.

        Args:
            contact_data: Contact creation data

        Returns:
            Created contact
        """
        data = {
            "location_id": contact_data.location_id,
            "contact_type": contact_data.contact_type,
            "phone_number": contact_data.phone_number,
        }
        return await self._create("location_contacts", data, ContactResponse)

    async def update_contact(
        self, contact_id: int, contact_data: ContactUpdate
    ) -> Optional[ContactResponse]:
        """
        Update a contact.

        Args:
            contact_id: Contact ID (SERIAL, not UUID)
            contact_data: Contact update data

        Returns:
            Updated contact or None if not found
        """
        # Only include fields that are not None
        data = {}
        if contact_data.contact_type is not None:
            data["contact_type"] = contact_data.contact_type
        if contact_data.phone_number is not None:
            data["phone_number"] = contact_data.phone_number

        if not data:
            # No fields to update, return existing contact
            query = "SELECT * FROM location_contacts WHERE id = %s"
            return await self._execute_one(query, (contact_id,), ContactResponse)

        # location_contacts doesn't have soft delete, use direct UPDATE with sql.SQL
        set_parts = [
            sql.SQL("{} = %s").format(sql.Identifier(key)) for key in data.keys()
        ]
        set_clause = sql.SQL(", ").join(set_parts)
        query = sql.SQL(
            "UPDATE location_contacts SET {set_clause} WHERE id = %s RETURNING *"
        ).format(set_clause=set_clause)
        return await self._execute_one(
            query, (*data.values(), contact_id), ContactResponse
        )

    async def delete_contact(self, contact_id: int) -> bool:
        """
        Delete a contact.

        Args:
            contact_id: Contact ID (SERIAL, not UUID)

        Returns:
            True if contact was deleted, False if not found
        """
        query = "DELETE FROM location_contacts WHERE id = %s"
        rowcount = await self._execute_command(query, (contact_id,))
        return rowcount > 0
