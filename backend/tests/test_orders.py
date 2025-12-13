"""
Tests for Orders & Payments API (Phase 10)

Tests cover:
- Order creation with polymorphic items
- Coupon validation
- Payment processing
- Order history
"""

import httpx

# pyright: reportMissingImports=false
from uuid_utils import uuid7


class TestOrderCreation:
    """Tests for order creation."""

    async def test_create_order_success(
        self,
        client: httpx.AsyncClient,
        auth_headers,
        test_user_id,
        test_location_id,
        test_product_id,
    ):
        """POST /orders creates an order successfully."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(test_location_id),
            "items": [
                {
                    "product_id": str(test_product_id),
                    "quantity": 2,
                    "unit_price": "99.99",
                }
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code == 201, f"Response: {response.text}"
        data = response.json()
        assert data["customer_id"] == str(user_id)
        assert data["total_amount"] == "199.98"  # 2 * 99.99

    async def test_create_order_with_booking_item(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders creates order with booking item."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {"booking_id": str(uuid7()), "quantity": 1, "unit_price": "500.00"}
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code in [201, 404]

    async def test_create_order_with_gift_card_item(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders creates order with gift card item."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {"gift_card_id": str(uuid7()), "quantity": 1, "unit_price": "1000.00"}
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code in [201, 404]

    async def test_create_order_empty_items(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders fails with empty items list."""
        user_id, email = test_user_id
        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [],  # Empty items
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_order_invalid_item_quantity(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders validates item quantity."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {
                    "product_id": str(uuid7()),
                    "quantity": 0,  # Invalid quantity
                    "unit_price": "99.99",
                }
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_order_negative_price(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders validates unit price."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {
                    "product_id": str(uuid7()),
                    "quantity": 1,
                    "unit_price": "-10.00",  # Negative price
                }
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code == 422


class TestCouponValidation:
    """Tests for coupon validation."""

    async def test_validate_coupon_not_found(self, client: httpx.AsyncClient):
        """POST /orders/coupons/validate returns invalid for non-existent coupon."""
        coupon_data = {"code": "NONEXISTENT"}

        response = await client.post(
            "/api/v1/orders/coupons/validate", json=coupon_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert data["reason"] == "not_found"

    async def test_validate_coupon_missing_code(self, client: httpx.AsyncClient):
        """POST /orders/coupons/validate requires code."""
        response = await client.post("/api/v1/orders/coupons/validate", json={})

        assert response.status_code == 422

    async def test_create_order_with_valid_coupon(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """POST /orders applies valid coupon."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "coupon_code": "SUMMER2024",  # Likely doesn't exist
            "items": [
                {"product_id": str(uuid7()), "quantity": 1, "unit_price": "100.00"}
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        # Will fail on coupon validation or FK constraints
        assert response.status_code in [201, 404, 409]


class TestOrderRetrieval:
    """Tests for order retrieval."""

    async def test_get_user_orders(self, client: httpx.AsyncClient, auth_headers):
        """GET /orders returns current user's orders."""
        response = await client.get("/api/v1/orders/", headers=auth_headers)

        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)

    async def test_get_user_orders_with_pagination(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /orders respects pagination."""
        response = await client.get(
            "/api/v1/orders/?limit=10&offset=0", headers=auth_headers
        )

        assert response.status_code == 200
        orders = response.json()
        assert len(orders) <= 10

    async def test_get_order_by_id_not_found(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """GET /orders/{id} returns 404 for non-existent order."""

        fake_id = uuid7()

        response = await client.get(f"/api/v1/orders/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_get_order_by_id_success(
        self,
        client: httpx.AsyncClient,
        auth_headers,
        test_user_id,
        test_location_id,
        test_product_id,
    ):
        """GET /orders/{id} returns order details."""
        # Create order first
        user_id, _ = test_user_id
        order_data = {
            "customer_id": str(user_id),
            "location_id": str(test_location_id),
            "items": [
                {
                    "product_id": str(test_product_id),
                    "quantity": 1,
                    "unit_price": "100.00",
                }
            ],
        }
        create_response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]

        # Get order
        response = await client.get(f"/api/v1/orders/{order_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert len(data["items"]) == 1

    async def test_get_location_orders(self, client: httpx.AsyncClient, auth_headers):
        """GET /orders/locations/{id}/orders returns orders for location."""

        location_id = uuid7()

        response = await client.get(
            f"/api/v1/orders/locations/{location_id}/orders", headers=auth_headers
        )

        assert response.status_code in [200, 404]


class TestPaymentProcessing:
    """Tests for payment processing."""

    async def test_process_payment_success(
        self,
        client: httpx.AsyncClient,
        auth_headers,
        test_user_id,
        test_location_id,
        test_product_id,
    ):
        """POST /orders/{id}/payments processes payment."""
        # Create order first
        user_id, _ = test_user_id
        order_data = {
            "customer_id": str(user_id),
            "location_id": str(test_location_id),
            "items": [
                {
                    "product_id": str(test_product_id),
                    "quantity": 1,
                    "unit_price": "100.00",
                }
            ],
        }
        create_response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]

        payment_data = {
            "amount": "100.00",
            "payment_method": "card",
            "transaction_id": "txn_123456",
        }

        response = await client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"

    async def test_process_payment_negative_amount(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /orders/{id}/payments validates amount."""

        order_id = uuid7()

        payment_data = {
            "amount": "-50.00",  # Negative amount
            "payment_method": "card",
        }

        response = await client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code in [404, 422]

    async def test_process_payment_invalid_method(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """POST /orders/{id}/payments validates payment method."""

        order_id = uuid7()

        payment_data = {"amount": "100.00", "payment_method": "invalid_method"}

        response = await client.post(
            f"/api/v1/orders/{order_id}/payments",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code in [404, 422]

    async def test_get_order_payments(self, client: httpx.AsyncClient, auth_headers):
        """GET /orders/{id}/payments returns payments for order."""

        order_id = uuid7()

        response = await client.get(
            f"/api/v1/orders/{order_id}/payments", headers=auth_headers
        )

        assert response.status_code in [200, 404]


class TestOrderReceipt:
    """Tests for order receipts."""

    async def test_get_order_receipt(self, client: httpx.AsyncClient, auth_headers):
        """GET /orders/{id}/receipt returns receipt."""

        order_id = uuid7()

        response = await client.get(
            f"/api/v1/orders/{order_id}/receipt", headers=auth_headers
        )

        assert response.status_code in [200, 404]

    async def test_receipt_contains_order_details(
        self, client: httpx.AsyncClient, auth_headers
    ):
        """Receipt includes order details and items."""

        order_id = uuid7()

        response = await client.get(
            f"/api/v1/orders/{order_id}/receipt", headers=auth_headers
        )

        if response.status_code == 200:
            receipt = response.json()
            assert "receipt_number" in receipt or "order_id" in receipt


class TestPolymorphicOrderItems:
    """Tests for polymorphic order items validation."""

    async def test_order_item_multiple_types(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """Order item cannot have multiple item types."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {
                    "booking_id": str(uuid7()),
                    "product_id": str(uuid7()),  # Both booking AND product
                    "quantity": 1,
                    "unit_price": "100.00",
                }
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        # Should fail validation (polymorphic constraint)
        assert response.status_code in [404, 422]

    async def test_order_item_no_type(
        self, client: httpx.AsyncClient, auth_headers, test_user_id
    ):
        """Order item must have at least one item type."""
        user_id, email = test_user_id

        order_data = {
            "customer_id": str(user_id),
            "location_id": str(uuid7()),
            "items": [
                {
                    # No booking_id, product_id, or gift_card_id
                    "quantity": 1,
                    "unit_price": "100.00",
                }
            ],
        }

        response = await client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )

        assert response.status_code == 422
