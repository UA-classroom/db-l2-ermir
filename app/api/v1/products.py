from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.api.deps import (
    get_current_provider,
    get_db_conn,
    verify_location_ownership,
    verify_product_ownership,
)
from app.core.exceptions import NotFoundError
from app.models.product import (
    InventoryAdjustment,
    InventoryLogResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.models.user import UserDB
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
) -> ProductService:
    """Dependency to get ProductService instance."""
    product_repo = ProductRepository(conn)
    return ProductService(product_repo)


@router.get("/", response_model=list[ProductResponse])
async def get_products(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    location_id: Optional[UUID] = Query(None, description="Filter by location"),
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List products with optional location filter."""
    repo = ProductRepository(conn)
    return await repo.get_products(location_id=location_id, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Get product details."""
    repo = ProductRepository(conn)
    product = await repo.get_product_by_id(product_id)
    if not product:
        raise NotFoundError("Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],  # Changed
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Create new product (provider only)."""
    # Verify location ownership
    await verify_location_ownership(product_data.location_id, current_user, conn)

    return await product_service.create_product(product_data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],  # Changed
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """Update product details (provider only)."""
    await verify_product_ownership(product_id, current_user, conn)

    return await product_service.update_product(product_id, product_data)


@router.post("/{product_id}/inventory", response_model=ProductResponse)
async def adjust_inventory(
    product_id: UUID,
    adjustment: InventoryAdjustment,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Adjust product inventory (provider only).

    Atomically updates stock and logs the change.
    Prevents negative stock.
    """

    await verify_product_ownership(product_id, current_user, conn)
    return await product_service.adjust_inventory(
        product_id, adjustment.change_amount, adjustment.reason
    )


@router.get("/{product_id}/inventory/logs", response_model=list[InventoryLogResponse])
async def get_inventory_logs(
    product_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get inventory change history for a product (provider only)."""

    await verify_product_ownership(product_id, current_user, conn)
    
    repo = ProductRepository(conn)
    return await repo.get_inventory_logs(product_id, limit, offset)
