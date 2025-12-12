from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.api.deps import (
    get_current_active_user,
    get_current_provider,
    get_db_conn,
    validate_order_creation,
    verify_location_ownership,
    verify_order_ownership,
)
from app.models.order import (
    CouponValidationRequest,
    CouponValidationResponse,
    OrderCreate,
    OrderDetail,
    OrderResponse,
    PaymentCreate,
    PaymentResponse,
    ReceiptResponse,
)
from app.models.user import UserDB
from app.repositories.order_repository import OrderRepository
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_payment_service(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
) -> PaymentService:
    """Dependency to get PaymentService instance."""
    order_repo = OrderRepository(conn)
    return PaymentService(order_repo)


@router.post("/", response_model=OrderDetail, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
):
    """
    Create order (checkout).

    Atomically creates order with items and applies coupon if provided.
    """
    await validate_order_creation(order_data, current_user, conn)

    return await payment_service.create_order(order_data)


@router.get("/", response_model=list[OrderResponse])
async def get_user_orders(
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get current user's order history."""
    repo = OrderRepository(conn)
    return await repo.get_user_orders(current_user.id, limit, offset)


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Get order details with items."""
    # Verify order ownership
    await verify_order_ownership(order_id, current_user, conn)

    repo = OrderRepository(conn)
    order = await repo.get_order_by_id(order_id)
    return order


@router.post(
    "/{order_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_payment(
    order_id: UUID,
    payment_data: PaymentCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """
    Process payment for an order.

    Creates payment record and updates order status to 'paid'.
    """
    # Authorization: Verify order ownership
    await verify_order_ownership(order_id, current_user, conn)

    return await payment_service.process_payment(order_id, payment_data)


@router.get("/{order_id}/payments", response_model=list[PaymentResponse])
async def get_order_payments(
    order_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Get all payments for an order."""
    # Verify order ownership
    await verify_order_ownership(order_id, current_user, conn)

    repo = OrderRepository(conn)
    return await repo.get_order_payments(order_id)


@router.get("/{order_id}/receipt", response_model=ReceiptResponse)
async def get_receipt(
    order_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """
    Get order receipt.

    Returns order details formatted as a receipt.
    """
    # Verify order ownership
    await verify_order_ownership(order_id, current_user, conn)

    return await payment_service.get_order_receipt(order_id)


@router.post("/coupons/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    coupon_request: CouponValidationRequest,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
):
    """
    Validate coupon code.

    Checks expiration and usage limits.
    Public endpoint - no auth required for coupon validation.
    """
    return await payment_service.validate_coupon(coupon_request.code)


@router.get("/locations/{location_id}/orders", response_model=list[OrderResponse])
async def get_location_orders(
    location_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
    current_user: Annotated[UserDB, Depends(get_current_provider)],
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all orders for a location (provider only)."""
    # Authorization: Verify location ownership
    await verify_location_ownership(location_id, current_user, conn)

    repo = OrderRepository(conn)
    return await repo.get_location_orders(location_id, limit, offset)

