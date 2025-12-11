"""
Services API Endpoints

FastAPI router for service-related operations including CRUD for services,
service variants, and categories.

Key Features:
- Service search with filters (business_id, category_id, is_active)
- Service variant management (different prices/durations for same service)
- Category management for service classification
- Provider-only endpoints for creating/updating services
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection

from app.api.deps import (
    get_current_admin,
    get_current_provider,
    get_db_conn,
    verify_business_ownership,
    verify_service_ownership,
)
from app.core.exceptions import NotFoundError
from app.models.service import (
    CategoryCreate,
    CategoryResponse,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    ServiceVariantCreate,
    ServiceVariantResponse,
    ServiceVariantUpdate,
)
from app.models.user import UserDB
from app.repositories.service_repository import ServiceRepository

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=list[ServiceResponse])
async def get_services(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    business_id: Optional[UUID] = Query(None, description="Filter by business ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get list of services with optional filters.

    - **business_id**: Filter by business UUID
    - **category_id**: Filter by category ID
    - **is_active**: Filter by active status (true/false)
    - **skip**: Number of results to skip (pagination)
    - **limit**: Maximum number of results (max 100)
    """
    repo = ServiceRepository(conn)
    return await repo.get_services(
        business_id=business_id,
        category_id=category_id,
        is_active=is_active,
        limit=limit,
        offset=skip,
    )


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all service categories.

    - **skip**: Number of results to skip (pagination)
    - **limit**: Maximum number of results (max 100)
    """
    repo = ServiceRepository(conn)
    return await repo.get_categories(limit=limit, offset=skip)


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get a single service by ID.

    - **service_id**: UUID of the service
    """
    repo = ServiceRepository(conn)
    service = await repo.get_service_by_id(service_id)
    if not service:
        raise NotFoundError(f"Service {service_id} not found")
    return service


@router.get("/{service_id}/variants", response_model=list[ServiceVariantResponse])
async def get_service_variants(
    service_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Get all variants for a service.

    - **service_id**: UUID of the service
    """
    repo = ServiceRepository(conn)
    # Verify service exists first
    service = await repo.get_service_by_id(service_id)
    if not service:
        raise NotFoundError(f"Service {service_id} not found")

    return await repo.get_service_variants(service_id)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_data: CategoryCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_admin)],
):
    """
    Create a new category (Admin only).

    - **name**: Category name
    - **slug**: URL-friendly slug (optional)
    - **parent_id**: Parent category ID for hierarchical structure (optional)
    """
    repo = ServiceRepository(conn)
    return await repo.create_category(category_data)


@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    service_data: ServiceCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Create a new service (Provider only).

    - **business_id**: Business UUID that owns this service
    - **category_id**: Category ID (optional)
    - **name**: Service name
    - **description**: Service description (optional)
    - **is_active**: Whether service is active (default: true)
    """
    # Verify business ownership
    await verify_business_ownership(service_data.business_id, current_user, conn)
    
    repo = ServiceRepository(conn)
    return await repo.create_service(service_data)


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Update a service (Provider only).

    - **service_id**: UUID of the service to update
    - **name**: New service name (optional)
    - **description**: New description (optional)
    - **category_id**: New category ID (optional)
    - **is_active**: New active status (optional)
    """
    # Verify service ownership
    await verify_service_ownership(service_id, current_user, conn)

    repo = ServiceRepository(conn)
    return await repo.update_service(service_id, service_data)
    




@router.post(
    "/service-variants", response_model=ServiceVariantResponse, status_code=201
)
async def create_service_variant(
    variant_data: ServiceVariantCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Create a new service variant (Provider only).

    - **service_id**: UUID of the parent service
    - **name**: Variant name (e.g., 'Long Hair', 'Student')
    - **price**: Price for this variant
    - **duration_minutes**: Duration in minutes
    """
    # Verify service ownership
    await verify_service_ownership(variant_data.service_id, current_user, conn)
    repo = ServiceRepository(conn)
    return await repo.create_variant(variant_data)


@router.put("/service-variants/{variant_id}", response_model=ServiceVariantResponse)
async def update_service_variant(
    variant_id: UUID,
    variant_data: ServiceVariantUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Update a service variant (Provider only).

    - **variant_id**: UUID of the variant to update
    - **name**: New variant name (optional)
    - **price**: New price (optional)
    - **duration_minutes**: New duration (optional)
    """
    repo = ServiceRepository(conn)
    variant = await repo.get_service_variant_by_id(variant_id)
    if not variant:
        raise NotFoundError(f"Service variant {variant_id} not found")
    
    # Verify service ownership
    await verify_service_ownership(variant.service_id, current_user, conn)

    return await repo.update_variant(variant_id, variant_data)


@router.delete("/service-variants/{variant_id}", status_code=204)
async def delete_service_variant(
    variant_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated["UserDB", Depends(get_current_provider)],
):
    """
    Delete a service variant (Provider only).

    - **variant_id**: UUID of the variant to delete
    """
    repo = ServiceRepository(conn)
    variant = await repo.get_service_variant_by_id(variant_id)
    if not variant:
        raise NotFoundError(f"Service variant {variant_id} not found")

    # Verify service ownership
    await verify_service_ownership(variant.service_id, current_user, conn)

    await repo.delete_variant(variant_id)