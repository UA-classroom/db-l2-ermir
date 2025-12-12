"""
API Dependencies Module

FastAPI dependency injection functions for authentication and database access.
Provides reusable dependencies for JWT token validation, user authentication,
and database connection management.
"""
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from psycopg import AsyncConnection
from pydantic import ValidationError

from app.config import settings
from app.core.database import db
from app.core.enums import RoleEnum
from app.core.exceptions import NotFoundError
from app.core.security import ALGORITHM
from app.models.order import OrderCreate
from app.models.user import TokenData, UserDB
from app.repositories.booking_repository import BookingRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db_conn() -> AsyncGenerator[AsyncConnection, None]:
    """
    Dependency to get a database connection from the pool.
    Yields the connection and ensures it's closed (returned to pool) after use.
    """
    async with db.get_connection() as conn:
        yield conn



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    conn: Annotated[AsyncConnection, Depends(get_db_conn)],
) -> UserDB:
    """
    Dependency to get the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Validate UUID format
        try:
            user_id_uuid = UUID(user_id)
        except (ValueError, AttributeError):
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id_uuid, email=payload.get("email"), role=payload.get("role")
        )
    except (JWTError, ValidationError):
        raise credentials_exception

    user_repo = UserRepository(conn)
    user = await user_repo.find_by_id(token_data.user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserDB, Depends(get_current_user)],
) -> UserDB:
    """
    Dependency to get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
    

async def get_current_provider(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
) -> UserDB:
    """
    Verify user has provider role.

    Use this dependency to protect provider-only endpoints like
    creating services, managing employees, or viewing bookings.

    Args:
        current_user: Authenticated active user

    Returns:
        User with provider role

    Raises:
        HTTPException: 403 if user is not a provider
    """
    if current_user.role != RoleEnum.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Provider access required"
        )
    return current_user


async def get_current_customer(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
) -> UserDB:
    """
    Verify user has customer role.

    Use this dependency to protect customer-only endpoints.

    Args:
        current_user: Authenticated active user

    Returns:
        User with customer role

    Raises:
        HTTPException: 403 if user is not a customer
    """
    if current_user.role != RoleEnum.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required"
        )
    return current_user


async def get_current_admin(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
) -> UserDB:
    """
    Verify user has admin role.

    Use this dependency to protect admin-only endpoints like
    creating new admin users or managing platform settings.

    Args:
        current_user: Authenticated active user

    Returns:
        User with admin role

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user

async def verify_business_ownership(
    business_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the business.

    Args:
        business_id: Business UUID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If business not found
        HTTPException: 403 if user doesn't own the business
    """
    

    business_repo = BusinessRepository(conn)
    business = await business_repo.get_business_by_id(business_id)

    if not business:
        raise NotFoundError(f"Business {business_id} not found")

    if business.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this business",
        )
    

async def verify_service_ownership(
    service_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the service (via business ownership).

    Args:
        service_id: Service UUID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If service not found
        HTTPException: 403 if user doesn't own the service's business
    """

    service_repo = ServiceRepository(conn)
    service = await service_repo.get_service_by_id(service_id)

    if not service:
        raise NotFoundError(f"Service {service_id} not found")

    # Verify business ownership
    await verify_business_ownership(service.business_id, current_user, conn)


async def verify_location_ownership(
    location_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the location (via business ownership).

    Args:
        location_id: Location UUID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If location not found
        HTTPException: 403 if user doesn't own the location's business
    """

    business_repo = BusinessRepository(conn)
    location = await business_repo.get_location_by_id(location_id)

    if not location:
        raise NotFoundError(f"Location {location_id} not found")

    # Verify business ownership
    await verify_business_ownership(location.business_id, current_user, conn)


async def verify_contact_ownership(
    contact_id: int, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the contact (via location → business ownership).

    Args:
        contact_id: Contact ID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If contact not found
        HTTPException: 403 if user doesn't own the contact's business
    """

    business_repo = BusinessRepository(conn)
    contact = await business_repo.get_contact_by_id(contact_id)

    if not contact:
        raise NotFoundError(f"Contact {contact_id} not found")

    # Verify location ownership (which verifies business ownership)
    await verify_location_ownership(contact.location_id, current_user, conn)


async def verify_booking_ownership(
    booking_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the booking.

    - Customer can access their own bookings
    - Provider can access bookings for their locations

    Args:
        booking_id: Booking UUID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If booking not found
        HTTPException: 403 if user doesn't have permission
    """

    booking_repo = BookingRepository(conn)
    booking = await booking_repo.get_booking_by_id(booking_id)

    if not booking:
        raise NotFoundError(f"Booking {booking_id} not found")

    # Customer can access their own bookings
    if booking.customer.id == current_user.id:
        return

    # Provider can access bookings for their locations
    if current_user.role == RoleEnum.PROVIDER:
        await verify_location_ownership(booking.location_id, current_user, conn)
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this booking",
    )


async def verify_order_ownership(
    order_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the order.

    - Customer can access their own orders
    - Provider can access orders for their locations

    Args:
        order_id: Order UUID to verify
        current_user: Current authenticated user
        conn: Database connection

    Raises:
        NotFoundError: If order not found
        HTTPException: 403 if user doesn't have permission
    """

    order_repo = OrderRepository(conn)
    order = await order_repo.get_order_by_id(order_id)

    if not order:
        raise NotFoundError(f"Order {order_id} not found")

    # Customer can access their own orders
    if order.customer_id == current_user.id:
        return

    # Provider can access orders for their locations
    if current_user.role == RoleEnum.PROVIDER:
        await verify_location_ownership(order.location_id, current_user, conn)
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this order",
    )


async def verify_employee_ownership(
    employee_id: UUID, current_user: UserDB, conn: AsyncConnection
):
    """
    Verify that current user owns the employee (via location ownership).

    - Provider can access employees for their locations

    Args:
        employee_id: Employee UUID to verify
        current_user: Current authenticated user (must be provider)
        conn: Database connection

    Raises:
        NotFoundError: If employee not found
        HTTPException: 403 if user doesn't own the employee's location
    """
    
    employee_repo = EmployeeRepository(conn)
    employee = await employee_repo.get_employee_by_id(employee_id)

    if not employee:
        raise NotFoundError(f"Employee {employee_id} not found")

    # Verify location ownership
    await verify_location_ownership(employee.location_id, current_user, conn)


async def validate_booking_creation(
    booking_data, current_user: UserDB, conn: AsyncConnection
):
    """
    Validate that current user can create this booking.

    Rules:
    - CUSTOMER: Can only book for themselves
    - PROVIDER: Can only book on their own locations
    - ADMIN: Can book for anyone (support/testing)
    """

    if current_user.role == RoleEnum.CUSTOMER:
        if booking_data.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers can only create bookings for themselves",
            )

    elif current_user.role == RoleEnum.PROVIDER:
        await verify_location_ownership(booking_data.location_id, current_user, conn)

    elif current_user.role == RoleEnum.ADMIN:
        # Admin can book for anyone
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for booking creation",
        )
    

async def validate_order_creation(
    order_data: "OrderCreate", current_user: UserDB, conn: AsyncConnection
):
    """
    Validate that user can create order.

    Rules:
    - CUSTOMER: Can only create orders for themselves
    - PROVIDER: Can create orders for their locations
    - ADMIN: Can create orders for anyone
    """
    if current_user.role == RoleEnum.CUSTOMER:
        if order_data.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers can only create orders for themselves",
            )

    elif current_user.role == RoleEnum.PROVIDER:
        await verify_location_ownership(order_data.location_id, current_user, conn)

    elif current_user.role == RoleEnum.ADMIN:
        # Admin can create orders for anyone
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for order creation",
        )