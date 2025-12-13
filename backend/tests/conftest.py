import asyncio
import sys
from datetime import time
from decimal import Decimal
from typing import AsyncGenerator
from uuid import UUID

import httpx
import pytest
from app.api.deps import get_db_conn
from app.core.database import db
from app.core.enums import RoleEnum
from app.core.security import hash_password
from app.main import app
from app.models.business import BusinessCreate, LocationCreate
from app.models.employee import EmployeeCreate, WorkingHoursCreate
from app.models.service import CategoryCreate, ServiceCreate, ServiceVariantCreate
from app.repositories.business_repository import BusinessRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from psycopg import AsyncConnection

# Windows Compatibility: Set event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Database & Event Loop Fixtures
@pytest.fixture(scope="session", autouse=True)
async def setup_db_pool():
    """
    Initializes the Database Pool ONCE for the entire test session.
    This ensures all tests share the same pool and event loop.
    """
    await db.connect()
    yield
    await db.disconnect()


@pytest.fixture(scope="function")
async def db_conn():
    """
    Provides a database connection for a single test.
    Wraps the test in a transaction and FORCES a rollback at the end.
    """
    if not db.pool:
        await db.connect()
    
    assert db.pool is not None, "Database pool failed to initialize"
    async with db.pool.connection() as conn:  # ✓ Pylance knows it's not None  
        # Override the dependency to use this specific connection
        async def get_test_conn():
            yield conn

        app.dependency_overrides[get_db_conn] = get_test_conn

        try:
            # Start a transaction
            async with conn.transaction():
                try:
                    # Yield the connection to the test
                    yield conn
                finally:
                    # CRITICAL: Force a rollback by raising an exception.
                    # Psycopg3 commits by default if the block exits normally.
                    # This ensures no test data persists.
                    raise RuntimeError("Force Rollback")
        except RuntimeError as e:
            # Catch the rollback exception to prevent it from propagating
            if "Force Rollback" not in str(e):
                raise
        finally:
            # Clean up the dependency override
            app.dependency_overrides.pop(get_db_conn, None)

# Client Fixture
@pytest.fixture
async def client(db_conn: AsyncConnection) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    HTTP client linked to the app.
    Depends on db_conn to ensure the dependency override is set up.
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user_id(db_conn: AsyncConnection, request) -> tuple[UUID, str]:
    """Create a test user with a unique email for each test."""
    repo = UserRepository(db_conn)
    # Use test node ID to create unique email
    test_id = request.node.name
    email = f"test_{test_id}@example.com"
    user_data = {
        "email": email,
        "password_hash": hash_password("password123"),
        "first_name": "Test",
        "last_name": "User",
        "mobile_number": "+1234567890",
        "role": RoleEnum.PROVIDER,
        "is_active": True,
    }
    user = await repo.create(user_data)
    return (user.id, email)


@pytest.fixture
async def auth_headers(
    client: httpx.AsyncClient, test_user_id: tuple[UUID, str]
) -> dict[str, str]:
    """Get authentication headers for the test user."""
    user_id, email = test_user_id
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": email,  # OAuth2PasswordRequestForm expects 'username'
            "password": "password123",
        },
    )

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_user_id(db_conn: AsyncConnection, request) -> tuple[UUID, str]:
    """Create a test admin user."""
    repo = UserRepository(db_conn)
    test_id = request.node.name
    email = f"admin_{test_id}@example.com"
    user_data = {
        "email": email,
        "password_hash": hash_password("adminpass123"),
        "first_name": "Admin",
        "last_name": "User",
        "mobile_number": "+1999999999",
        "role": RoleEnum.ADMIN,
        "is_active": True,
    }
    user = await repo.create(user_data)
    return (user.id, email)


@pytest.fixture
async def admin_headers(
    client: httpx.AsyncClient, admin_user_id: tuple[UUID, str]
) -> dict[str, str]:
    """Get authentication headers for the admin user."""
    user_id, email = admin_user_id
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "adminpass123",
        },
    )

    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_business_id(
    db_conn: AsyncConnection, test_user_id: tuple[UUID, str]
) -> UUID:
    """Create a test business."""
    user_id, _ = test_user_id
    repo = BusinessRepository(db_conn)
    business_data = BusinessCreate(
        owner_id=user_id,
        name="Test Business",
        org_number="123456-7890",
        slug="test-business",
    )
    business = await repo.create_business(business_data)
    return business.id


@pytest.fixture
async def test_category_id(db_conn: AsyncConnection) -> int:
    """Create a test category."""
    repo = ServiceRepository(db_conn)
    category_data = CategoryCreate(
        name="Test Category", slug="test-category", parent_id=None
    )
    category = await repo.create_category(category_data)
    return category.id


@pytest.fixture
async def test_location_id(db_conn: AsyncConnection, test_business_id: UUID) -> UUID:
    """Create a test location for a business."""   

    repo = BusinessRepository(db_conn)
    location_data = LocationCreate(
        business_id=test_business_id,
        name="Test Location",
        address="Test Street 123",
        city="Stockholm",
        postal_code="12345",
        latitude=Decimal("45.3293"),
        longitude=Decimal("18.0686"),
    
    )
    location = await repo.create_location(location_data)
    return location.id


@pytest.fixture
async def test_service_id(
    db_conn: AsyncConnection, test_business_id: UUID, test_category_id: int
) -> UUID:
    """Create a test service."""
    repo = ServiceRepository(db_conn)
    service_data = ServiceCreate(
        business_id=test_business_id,
        category_id=test_category_id,
        name="Test Service",
        description="Test service description",
        is_active=True,
    )
    service = await repo.create_service(service_data)
    return service.id


@pytest.fixture
async def test_service_variant_id(
    db_conn: AsyncConnection, test_service_id: UUID
) -> UUID:
    """Create a test service variant."""

    repo = ServiceRepository(db_conn)
    variant_data = ServiceVariantCreate(
        service_id=test_service_id,
        name="Standard",
        duration_minutes=60,
        price=Decimal("100.00"),
    )
    variant = await repo.create_variant(variant_data)
    return variant.id


@pytest.fixture
async def test_employee_id(
    db_conn: AsyncConnection, test_user_id: tuple[UUID, str], test_location_id: UUID
) -> UUID:
    """Create a test employee."""   

    user_id, _ = test_user_id
    repo = EmployeeRepository(db_conn)
    employee_data = EmployeeCreate(
        user_id=user_id,
        location_id=test_location_id,
        job_title="Test Stylist",
        bio="Test employee bio",
        color_code="#FF5733",
        is_active=True,
    )
    employee = await repo.create_employee(employee_data)

    # Add working hours for all days
    for day in range(1, 8):  # 1=Mon, 7=Sun
        hours_data = WorkingHoursCreate(
            employee_id=employee.id,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(18, 0),
        )
        await repo.add_working_hours(hours_data)

    return employee.id


@pytest.fixture
async def test_booking_id(
    db_conn: AsyncConnection,
    test_user_id: tuple[UUID, str],
    test_location_id: UUID,
    test_employee_id: UUID,
    test_service_variant_id: UUID,
) -> UUID:
    """Create a test booking for review tests."""
    from datetime import datetime, timedelta, timezone

    from app.models.booking import BookingCreate
    from app.repositories.booking_repository import BookingRepository

    user_id, _ = test_user_id
    repo = BookingRepository(db_conn)

    # Create booking for tomorrow
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = BookingCreate(
        customer_id=user_id,
        location_id=test_location_id,
        employee_id=test_employee_id,
        service_variant_id=test_service_variant_id,
        start_time=start_time,
        end_time=end_time,
        total_price=Decimal("100.00"),
        customer_note="Test booking for reviews",
    )

    booking = await repo.create_booking(booking_data.model_dump())
    return booking.id


@pytest.fixture
async def test_product_id(db_conn: AsyncConnection, test_location_id: UUID) -> UUID:
    """Create a test product."""
    from app.models.product import ProductCreate
    from app.repositories.product_repository import ProductRepository

    repo = ProductRepository(db_conn)
    product_data = ProductCreate(
        location_id=test_location_id,
        name="Test Product",
        sku="TEST-SKU",
        price=Decimal("99.99"),
        stock_quantity=10,
    )
    product = await repo.create_product(product_data.model_dump())
    return product.id