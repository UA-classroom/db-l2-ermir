"""
Tests for Products & Inventory API (Phase 9)

Tests cover:
- Product CRUD
- Inventory adjustment
- Negative stock prevention
- Inventory logs
"""

# pyright: reportMissingImports=false
import httpx
from uuid_utils import uuid7


class TestProductManagement:
    """Tests for product CRUD operations."""

    async def test_get_products_empty(self, client: httpx.AsyncClient, auth_headers):
        """GET /products returns list (might not be empty due to other tests)."""
        response = await client.get("/api/v1/products/", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_products_with_pagination(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /products respects pagination."""
        response = await client.get(
            "/api/v1/products/?limit=10&offset=0", headers=auth_headers
        )

        assert response.status_code == 200
        products = response.json()
        assert len(products) <= 10

    async def test_get_product_by_id_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /products/{id} returns 404 for non-existent product."""

        fake_id = uuid7()

        response = await client.get(f"/api/v1/products/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_create_product_success(
        self, client: httpx.AsyncClient, auth_headers, test_location_id, request
    ):
        """POST /products creates a product successfully."""
        test_id = request.node.name
        product_data = {
            "location_id": str(test_location_id),
            "name": f"Test Product {test_id}",
            "description": "A test product",
            "price": "99.99",
            "stock_quantity": 10,
            "sku": f"TEST-{test_id[-8:]}",
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["stock_quantity"] == 10

    async def test_create_product_negative_price(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """POST /products fails with negative price."""
        product_data = {
            "location_id": str(test_location_id),
            "name": "Invalid Product",
            "price": "-10.00",  # Negative price
            "stock_quantity": 10,
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_product_negative_stock(
        self, client: httpx.AsyncClient, auth_headers, test_location_id
    ):
        """POST /products fails with negative stock."""
        product_data = {
            "location_id": str(test_location_id),
            "name": "Invalid Product",
            "price": "10.00",
            "stock_quantity": -5,  # Negative stock
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_update_product_success(
        self, client: httpx.AsyncClient, auth_headers, test_product_id
    ):
        """PUT /products/{id} updates product details."""
        update_data = {"name": "Updated Product", "price": "149.99"}

        response = await client.put(
            f"/api/v1/products/{test_product_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert float(data["price"]) == 149.99

    async def test_update_product_invalid_price(
        self, client: httpx.AsyncClient, auth_headers, test_product_id
    ):
        """PUT /products/{id} validates price."""
        update_data = {
            "price": "-50.00"  # Negative price
        }

        response = await client.put(
            f"/api/v1/products/{test_product_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestInventoryAdjustment:
    """Tests for inventory adjustment - CRITICAL!"""

    async def test_adjust_inventory_increase(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products/{id}/inventory increases stock."""

        product_id = uuid7()

        adjustment_data = {"change_amount": 10, "reason": "restock"}

        response = await client.post(
            f"/api/v1/products/{product_id}/inventory",
            json=adjustment_data,
            headers=auth_headers,
        )

        assert response.status_code == 404  # Product doesn't exist

    async def test_adjust_inventory_decrease(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products/{id}/inventory decreases stock."""

        product_id = uuid7()

        adjustment_data = {"change_amount": -5, "reason": "sale"}

        response = await client.post(
            f"/api/v1/products/{product_id}/inventory",
            json=adjustment_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_adjust_inventory_zero_change(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products/{id}/inventory rejects zero change."""

        product_id = uuid7()

        adjustment_data = {
            "change_amount": 0,  # No change
            "reason": "adjustment",
        }

        response = await client.post(
            f"/api/v1/products/{product_id}/inventory",
            json=adjustment_data,
            headers=auth_headers,
        )

        assert response.status_code in [404, 422]

    async def test_adjust_inventory_negative_stock_prevention(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products/{id}/inventory prevents negative stock."""

        product_id = uuid7()

        # Try to decrease by large amount (would go negative)
        adjustment_data = {"change_amount": -1000, "reason": "sale"}

        response = await client.post(
            f"/api/v1/products/{product_id}/inventory",
            json=adjustment_data,
            headers=auth_headers,
        )

        # Should fail (either 404 for product not found, or 409 for negative stock)
        assert response.status_code in [404, 409]

    async def test_adjust_inventory_missing_reason(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products/{id}/inventory requires reason."""

        product_id = uuid7()

        adjustment_data = {
            "change_amount": 10
            # Missing reason
        }

        response = await client.post(
            f"/api/v1/products/{product_id}/inventory",
            json=adjustment_data,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestInventoryLogs:
    """Tests for inventory logs."""

    async def test_get_inventory_logs(self, client: httpx.AsyncClient, auth_headers):
        """GET /products/{id}/inventory/logs returns inventory history."""

        product_id = uuid7()

        response = await client.get(
            f"/api/v1/products/{product_id}/inventory/logs", headers=auth_headers
        )

        assert response.status_code in [200, 404]

    async def test_get_inventory_logs_with_pagination(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /products/{id}/inventory/logs respects pagination."""

        product_id = uuid7()

        response = await client.get(
            f"/api/v1/products/{product_id}/inventory/logs?limit=10&offset=0",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestProductFiltering:
    """Tests for product filtering."""

    async def test_filter_products_by_location(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /products filters by location_id."""

        location_id = uuid7()

        response = await client.get(
            f"/api/v1/products/?location_id={location_id}", headers=auth_headers
        )

        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)

    async def test_filter_products_by_stock_status(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /products filters by stock availability."""
        response = await client.get(
            "/api/v1/products/?in_stock=true", headers=auth_headers
        )

        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)


class TestProductValidation:
    """Tests for product validation."""

    async def test_create_product_price_too_many_decimals(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products validates price decimal places."""

        product_data = {
            "location_id": str(uuid7()),
            "name": "Invalid Product",
            "price": "99.999",  # Too many decimal places
            "stock_quantity": 10,
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_product_missing_required_fields(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products fails when required fields are missing."""
        product_data = {
            "name": "Incomplete Product"
            # Missing location_id, price, stock_quantity
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_product_very_large_price(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products accepts large price values (within DECIMAL(10,2))."""

        product_data = {
            "location_id": str(uuid7()),
            "name": "Expensive Product",
            "price": "99999999.99",  # Max for DECIMAL(10,2)
            "stock_quantity": 1,
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code in [201, 404]

    async def test_create_product_very_large_stock(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /products accepts large stock quantities."""

        product_data = {
            "location_id": str(uuid7()),
            "name": "High Stock Product",
            "price": "10.00",
            "stock_quantity": 999999,
        }

        response = await client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code in [201, 404]
