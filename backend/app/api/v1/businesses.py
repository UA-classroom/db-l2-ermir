"""
Businesses API Endpoints

FastAPI router for business-related operations including CRUD for businesses,
locations, contacts, and services.

Key Features:
- Business search with filters (city, name, category, min_rating)
- Business responses include calculated fields (average_rating, review_count, primary_category)
- Service listing with optional variant inclusion (eliminates N+1 queries)
- Location and contact management for businesses
- Provider-only endpoints protected by role-based authorization
"""

from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection

from app.api.deps import (
    get_current_provider,
    get_db_conn,
    verify_business_ownership,
    verify_contact_ownership,
    verify_location_ownership,
)
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    LocationCreate,
    LocationResponse,
    LocationSearchResult,
    LocationUpdate,
)
from app.models.service import ServiceDetail, ServiceResponse
from app.models.user import UserDB
from app.repositories.business_repository import BusinessRepository
from app.repositories.service_repository import ServiceRepository

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.get("/locations", response_model=list[LocationSearchResult])
async def get_locations(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    query: Optional[str] = Query(None, description="Search by name or business"),
    city: Optional[str] = Query(None, description="Filter by city"),
    category: Optional[str] = Query(None, description="Filter by category"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get locations (shops) across all businesses.

    Returns specific locations with their address and parent business info.
    """
    repo = BusinessRepository(conn)
    return await repo.get_locations(
        query=query, city=city, category=category, offset=offset, limit=limit
    )


@router.get("/", response_model=list[BusinessResponse])
async def get_businesses(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    city: Optional[str] = Query(None, description="Filter by city"),
    name: Optional[str] = Query(None, description="Filter by business name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(
        None, ge=1, le=5, description="Minimum average rating (1-5)"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get list of businesses with optional filters.

    - **city**: Filter by city (case-insensitive partial match)
    - **name**: Filter by business name (case-insensitive partial match)
    - **category**: Filter by category (e.g., "Hair", "Nails", "Spa")
    - **min_rating**: Minimum average rating (1-5 stars)
    - **offset**: Number of results to skip (pagination)
    - **limit**: Maximum number of results (max 100)
    """
    repo = BusinessRepository(conn)
    return await repo.get_businesses(
        city=city,
        name=name,
        category=category,
        min_rating=min_rating,
        limit=limit,
        offset=offset,
    )


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get a single business by ID.

    - **business_id**: UUID of the business
    """
    repo = BusinessRepository(conn)
    business = await repo.get_business_by_id(business_id)
    if not business:
        raise NotFoundError(f"Business {business_id} not found")
    return business


@router.get("/{business_id}/locations", response_model=list[LocationResponse])
async def get_business_locations(
    business_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get all locations for a business.

    - **business_id**: UUID of the business
    """
    repo = BusinessRepository(conn)
    # Verify business exists first
    business = await repo.get_business_by_id(business_id)
    if not business:
        raise NotFoundError(f"Business {business_id} not found")

    return await repo.get_business_locations(business_id)


@router.get(
    "/{business_id}/services",
    response_model=Union[list[ServiceResponse], list[ServiceDetail]],
)
async def get_business_services(
    business_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    include_variants: bool = Query(
        False,
        description="Include service variants in response (eliminates N+1 queries)",
    ),
):
    """
    Get all services for a business.

    - **business_id**: UUID of the business
    - **include_variants**: If true, includes all variants in one query (recommended)

    Performance Note:
        Use include_variants=true to fetch services and variants in a single query
        instead of making N+1 separate requests for each service's variants.
    """
    # Verify business exists first
    business_repo = BusinessRepository(conn)
    business = await business_repo.get_business_by_id(business_id)
    if not business:
        raise NotFoundError(f"Business {business_id} not found")

    service_repo = ServiceRepository(conn)

    if include_variants:
        return await service_repo.get_services_with_variants(business_id)
    else:
        return await service_repo.get_services(business_id=business_id, is_active=True)


@router.get("/locations/{location_id}/contacts", response_model=list[ContactResponse])
async def get_location_contacts(
    location_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get all contacts for a location.

    - **location_id**: UUID of the location
    """
    repo = BusinessRepository(conn)
    return await repo.get_location_contacts(location_id)


@router.post("/", response_model=BusinessResponse, status_code=201)
async def create_business(
    business: BusinessCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Create a new business (Provider only).

    - **name**: Business name (required)
    - **owner_id**: UUID of the owner user (required)
    - **slug**: URL-friendly identifier (required)
    - **org_number**: Organization number (optional)
    """
    # Verify that user_id in request matches current user
    if business.owner_id != current_user.id:
        raise ForbiddenError("You can only create businesses for yourself")

    repo = BusinessRepository(conn)
    return await repo.create_business(business)


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: UUID,
    business_data: BusinessUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Update a business (Provider only).

    - **business_id**: UUID of the business to update
    - **name**: New business name (optional)
    - **slug**: New slug (optional)
    - **org_number**: New organization number (optional)
    """
    # Verify business ownership
    await verify_business_ownership(business_id, current_user, conn)

    repo = BusinessRepository(conn)
    return await repo.update_business(business_id, business_data)


@router.post(
    "/{business_id}/locations", response_model=LocationResponse, status_code=201
)
async def create_location(
    business_id: UUID,
    location_data: LocationCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Create a new location for a business (Provider only).

    - **business_id**: UUID of the business
    - **name**: Location name (optional)
    - **address**: Street address (optional)
    - **city**: City (optional)
    - **postal_code**: Postal code (optional)
    - **latitude**: Latitude coordinate (optional)
    - **longitude**: Longitude coordinate (optional)
    """
    # Verify business ownership
    await verify_business_ownership(business_id, current_user, conn)

    repo = BusinessRepository(conn)
    # Ensure business_id in request matches path parameter
    if location_data.business_id != business_id:
        raise BadRequestError(
            f"Business ID in body ({location_data.business_id}) does not match path parameter ({business_id})"
        )

    return await repo.create_location(location_data)


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    location_data: LocationUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Update a location (Provider only).

    - **location_id**: UUID of the location to update
    - **name**: New location name (optional)
    - **address**: New street address (optional)
    - **city**: New city (optional)
    - **postal_code**: New postal code (optional)
    - **latitude**: New latitude coordinate (optional)
    - **longitude**: New longitude coordinate (optional)
    """
    # Verify location ownership
    await verify_location_ownership(location_id, current_user, conn)

    repo = BusinessRepository(conn)
    return await repo.update_location(location_id, location_data)


@router.post(
    "/locations/{location_id}/contacts", response_model=ContactResponse, status_code=201
)
async def create_contact(
    location_id: UUID,
    contact_data: ContactCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Create a new contact for a location (Provider only).

    - **location_id**: UUID of the location
    - **contact_type**: Type of contact (e.g., 'Reception', 'Manager')
    - **phone_number**: Phone number
    """
    # Verify location ownership
    await verify_location_ownership(location_id, current_user, conn)

    repo = BusinessRepository(conn)
    # Ensure location_id in request matches path parameter
    if contact_data.location_id != location_id:
        raise BadRequestError(
            f"Location ID in body ({contact_data.location_id}) does not match path parameter ({location_id})"
        )

    return await repo.create_contact(contact_data)


@router.put("/location-contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Update a contact (Provider only).

    - **contact_id**: ID of the contact to update (SERIAL, not UUID)
    - **contact_type**: New contact type (optional)
    - **phone_number**: New phone number (optional)
    """
    # Verify contact ownership
    await verify_contact_ownership(contact_id, current_user, conn)

    repo = BusinessRepository(conn)
    return await repo.update_contact(contact_id, contact_data)


@router.delete("/location-contacts/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Delete a contact (Provider only).

    - **contact_id**: ID of the contact to delete (SERIAL, not UUID)
    """
    # Verify contact ownership
    await verify_contact_ownership(contact_id, current_user, conn)

    repo = BusinessRepository(conn)
    await repo.delete_contact(contact_id)
