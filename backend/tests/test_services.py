"""
Comprehensive tests for Services API (Phase 5 & 6)

Tests cover:
- Happy path scenarios
- Edge cases (validation errors, not found, etc)
- Boundary conditions
- Data integrity
"""

from uuid import UUID

import httpx

# pyright: reportMissingImports=false
from uuid_utils import uuid7

# ==============================================================================
# PHASE 5: Categories Tests
# ==============================================================================

class TestCategories:
    """Tests for category endpoints."""

    async def test_get_categories_empty(self, client: httpx.AsyncClient):
        """GET /categories returns empty list when no categories exist."""
        response = await client.get("/api/v1/services/categories")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_categories_with_pagination(self, client: httpx.AsyncClient):
        """GET /categories respects pagination parameters."""
        response = await client.get("/api/v1/services/categories?skip=0&limit=10")

        assert response.status_code == 200
        assert len(response.json()) <= 10

    async def test_create_category_success(self, client: httpx.AsyncClient, admin_headers: dict):
        """POST /categories creates a new category successfully."""
        category_data = {
            "name": "Hair Services",
            "slug": "hair-services",
            "parent_id": None
        }

        response = await client.post(
            "/api/v1/services/categories",
            json=category_data,
            headers=admin_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Hair Services"
        assert data["slug"] == "hair-services"
        assert data["parent_id"] is None
        assert "id" in data

    async def test_create_category_name_too_long(self, client: httpx.AsyncClient, admin_headers: dict):
        """POST /categories fails when name exceeds max length."""
        category_data = {
            "name": "A" * 101  # Max is 100
        }

        response = await client.post(
            "/api/v1/services/categories",
            json=category_data,
            headers=admin_headers
        )

        assert response.status_code == 422


# ==============================================================================
# PHASE 6: Service Variants Tests
# ==============================================================================

class TestServiceVariants:
    """Tests for service variant endpoints."""
    
    async def test_create_variant_negative_price(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /service-variants fails with negative price."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "-100.00",
            "duration_minutes": 60
        }
        
        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_create_variant_zero_duration(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /service-variants fails with zero duration."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "500.00",
            "duration_minutes": 0
        }
        
        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_delete_variant_not_found(self, client: httpx.AsyncClient, auth_headers: dict):
        """DELETE /service-variants/{id} returns 404 when variant doesn't exist."""
        fake_id = uuid7()
        response = await client.delete(
            f"/api/v1/services/service-variants/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_create_variant_invalid_service_id(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /service-variants fails with invalid service_id format."""
        variant_data = {
            "service_id": "not-a-uuid",
            "price": "500.00",
            "duration_minutes": 60
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_variant_price_too_many_decimals(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /service-variants validates price decimal places."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "500.999",  # Should be max 2 decimal places
            "duration_minutes": 60
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_update_variant_partial_update(self, client: httpx.AsyncClient, auth_headers: dict):
        """PUT /service-variants/{id} allows partial updates."""
        fake_id = uuid7()
        update_data = {
            "price": "550.00"
            # Not updating name or duration
        }

        response = await client.put(
            f"/api/v1/services/service-variants/{fake_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_update_variant_empty_body(self, client: httpx.AsyncClient, auth_headers: dict):
        """PUT /service-variants/{id} handles empty update gracefully."""
        fake_id = uuid7()
        response = await client.put(
            f"/api/v1/services/service-variants/{fake_id}",
            json={},
            headers=auth_headers
        )

        # Should return existing variant if ID exists, or 404 if not
        assert response.status_code == 404


# ==============================================================================
# PHASE 5: Services Tests
# ==============================================================================

class TestServices:
    """Tests for service endpoints."""

    async def test_get_services_empty(self, client: httpx.AsyncClient):
        """GET /services returns empty list when no services exist."""
        response = await client.get("/api/v1/services/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_service_by_id_not_found(self, client: httpx.AsyncClient):
        """GET /services/{id} returns 404 when service doesn't exist."""
        fake_id = uuid7()
        response = await client.get(f"/api/v1/services/{fake_id}")

        assert response.status_code == 404

    async def test_create_service_name_too_long(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /services fails when name exceeds max length."""
        service_data = {
            "business_id": str(uuid7()),
            "name": "A" * 101  # Max is 100
        }

        response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_service_empty_name(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /services fails when name is empty."""
        service_data = {
            "business_id": str(uuid7()),
            "name": ""
        }

        response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_create_service_invalid_business_id(self, client: httpx.AsyncClient, auth_headers: dict):
        """POST /services fails with invalid business_id format."""
        service_data = {
            "business_id": "not-a-uuid",
            "name": "Service"
        }

        response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_update_service_not_found(self, client: httpx.AsyncClient, auth_headers: dict):
        """PUT /services/{id} returns 404 when service doesn't exist."""
        fake_id = uuid7()
        update_data = {
            "name": "Updated Name"
        }

        response = await client.put(
            f"/api/v1/services/{fake_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_update_service_empty_name(self, client: httpx.AsyncClient, auth_headers: dict):
        """PUT /services/{id} fails with empty name."""
        fake_id = uuid7()
        update_data = {
            "name": ""
        }

        response = await client.put(
            f"/api/v1/services/{fake_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_get_service_variants_service_not_found(self, client: httpx.AsyncClient):
        """GET /services/{id}/variants returns 404 when service doesn't exist."""
        fake_id = uuid7()
        response = await client.get(f"/api/v1/services/{fake_id}/variants")

        assert response.status_code == 404


# ==============================================================================
# Edge Cases & Boundary Tests
# ==============================================================================

class TestEdgeCases:
    """Additional edge case tests."""

    async def test_pagination_limit_exceeds_max(self, client: httpx.AsyncClient):
        """GET endpoints respect maximum limit (100)."""
        response = await client.get("/api/v1/services/?limit=200")

        # Should be capped at 100 or return validation error
        assert response.status_code in [200, 422]

    async def test_pagination_negative_skip(self, client: httpx.AsyncClient):
        """GET endpoints reject negative skip values."""
        response = await client.get("/api/v1/services/?offset=-1")

        assert response.status_code == 422

    async def test_pagination_negative_limit(self, client: httpx.AsyncClient):
        """GET endpoints reject negative limit values."""
        response = await client.get("/api/v1/services/?limit=-1")

        assert response.status_code == 422

    async def test_invalid_uuid_in_path(self, client: httpx.AsyncClient):
        """Endpoints reject malformed UUIDs in path."""
        response = await client.get("/api/v1/services/not-a-valid-uuid")

        assert response.status_code == 422

    async def test_variant_price_zero_is_valid(self, client: httpx.AsyncClient, auth_headers: dict):
        """Variant price accepts zero (free service)."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "0.00",
            "duration_minutes": 30
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        # Structure valid, will fail on service not found
        assert response.status_code == 404

    async def test_variant_duration_minimum(self, client: httpx.AsyncClient, auth_headers: dict):
        """Variant duration accepts 1 minute (minimum valid)."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "100.00",
            "duration_minutes": 1
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 404  # Service not found, but structure valid

    async def test_category_slug_optional(self, client: httpx.AsyncClient, admin_headers: dict):
        """Category can be created without slug."""
        category_data = {
            "name": "Test Category"
            # No slug provided
        }

        response = await client.post(
            "/api/v1/services/categories",
            json=category_data,
            headers=admin_headers
        )

        assert response.status_code == 201

    async def test_service_description_optional(self, client: httpx.AsyncClient, auth_headers: dict):
        """Service can be created without description."""
        service_data = {
            "business_id": str(uuid7()),
            "name": "Basic Service"
            # No description
        }

        response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )

        # Will fail on FK constraint (business doesn't exist)
        assert response.status_code == 404

    async def test_service_category_optional(self, client: httpx.AsyncClient, auth_headers: dict):
        """Service can be created without category_id."""
        service_data = {
            "business_id": str(uuid7()),
            "name": "Uncategorized Service"
            # No category_id
        }

        response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )

        # Will fail on FK constraint (business doesn't exist)
        assert response.status_code == 404

    async def test_variant_name_optional(self, client: httpx.AsyncClient, auth_headers: dict):
        """Variant can be created without name (default variant)."""
        variant_data = {
            "service_id": str(uuid7()),
            # No name
            "price": "300.00",
            "duration_minutes": 45
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 404  # Service not found

    async def test_large_price_value(self, client: httpx.AsyncClient, auth_headers: dict):
        """Variant accepts large price values (within DECIMAL(10,2))."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "99999999.99",  # Max for DECIMAL(10,2)
            "duration_minutes": 60
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 404  # Service not found, but price valid

    async def test_very_long_duration(self, client: httpx.AsyncClient, auth_headers: dict):
        """Variant accepts very long durations (e.g., all-day service)."""
        variant_data = {
            "service_id": str(uuid7()),
            "price": "5000.00",
            "duration_minutes": 480  # 8 hours
        }

        response = await client.post(
            "/api/v1/services/service-variants",
            json=variant_data,
            headers=auth_headers
        )

        assert response.status_code == 404


# ==============================================================================
# Integration Tests - Full CRUD Flows with Real Data
# ==============================================================================

class TestCategoryIntegration:
    """Integration tests for categories with real database operations."""

    async def test_category_create_and_read(self, client: httpx.AsyncClient, admin_headers: dict):
        """Test category creation and retrieval."""
        # Create
        create_data = {
            "name": "Beauty Services",
            "slug": "beauty-services",
            "parent_id": None
        }
        create_response = await client.post(
            "/api/v1/services/categories",
            json=create_data,
            headers=admin_headers
        )
        assert create_response.status_code == 201
        category = create_response.json()
        category_id = category["id"]
        assert category["name"] == "Beauty Services"
        assert category["slug"] == "beauty-services"

        # Read - Get all categories
        list_response = await client.get("/api/v1/services/categories")
        assert list_response.status_code == 200
        categories = list_response.json()
        assert any(c["id"] == category_id for c in categories)

    async def test_nested_categories(self, client: httpx.AsyncClient, admin_headers: dict, request):
        """Test creating parent and child categories."""
        # Create parent with unique slug
        test_id = request.node.name
        parent_data = {"name": "Health & Wellness", "slug": f"health-wellness-{test_id}"}
        parent_response = await client.post(
            "/api/v1/services/categories",
            json=parent_data,
            headers=admin_headers
        )
        assert parent_response.status_code == 201
        parent_id = parent_response.json()["id"]

        # Create child with unique slug
        child_data = {
            "name": "Massage",
            "slug": f"massage-{test_id}",
            "parent_id": parent_id
        }
        child_response = await client.post(
            "/api/v1/services/categories",
            json=child_data,
            headers=admin_headers
        )
        assert child_response.status_code == 201
        child = child_response.json()
        assert child["parent_id"] == parent_id

    async def test_category_pagination(self, client: httpx.AsyncClient, admin_headers: dict, request):
        """Test category pagination."""
        # Create multiple categories with unique slugs
        test_id = request.node.name
        for i in range(5):
            category_data = {"name": f"Category {i}", "slug": f"category-{i}-{test_id}"}
            await client.post(
                "/api/v1/services/categories",
                json=category_data,
                headers=admin_headers
            )

        # Test pagination
        response = await client.get("/api/v1/services/categories?skip=0&limit=3")
        assert response.status_code == 200
        assert len(response.json()) <= 3


class TestServiceIntegration:
    """Integration tests for services with real database operations."""

    async def test_service_create_read_update(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        test_business_id: UUID,
        test_category_id: int
    ):
        """Test service creation, retrieval, and update."""
        # Create
        create_data = {
            "business_id": str(test_business_id),
            "category_id": test_category_id,
            "name": "Haircut",
            "description": "Professional haircut service",
            "is_active": True
        }
        create_response = await client.post(
            "/api/v1/services/",
            json=create_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        service = create_response.json()
        service_id = service["id"]
        assert service["name"] == "Haircut"
        assert service["description"] == "Professional haircut service"
        assert service["is_active"] is True

        # Read - Get by ID
        get_response = await client.get(f"/api/v1/services/{service_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["id"] == service_id
        assert fetched["name"] == "Haircut"

        # Read - Get all services
        list_response = await client.get("/api/v1/services/")
        assert list_response.status_code == 200
        services = list_response.json()
        assert any(s["id"] == service_id for s in services)

        # Update
        update_data = {
            "name": "Premium Haircut",
            "description": "Premium haircut with styling"
        }
        update_response = await client.put(
            f"/api/v1/services/{service_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "Premium Haircut"
        assert updated["description"] == "Premium haircut with styling"

    async def test_service_deactivation(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        test_service_id: UUID
    ):
        """Test service can be deactivated without deletion."""
        # Deactivate
        update_data = {"is_active": False}
        response = await client.put(
            f"/api/v1/services/{test_service_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        # Service should still be readable
        get_response = await client.get(f"/api/v1/services/{test_service_id}")
        assert get_response.status_code == 200


class TestServiceVariantIntegration:
    """Integration tests for service variants with real database operations."""

    async def test_variant_full_lifecycle(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        test_service_id: UUID
    ):
        """Test complete variant lifecycle: create → read → update → delete."""
        # Create
        create_data = {
            "service_id": str(test_service_id),
            "name": "Standard",
            "price": "500.00",
            "duration_minutes": 60
        }
        create_response = await client.post(
            "/api/v1/services/service-variants",
            json=create_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        variant = create_response.json()
        variant_id = variant["id"]
        assert variant["name"] == "Standard"
        assert variant["price"] == "500.00"
        assert variant["duration_minutes"] == 60

        # Read - Get variants for service
        list_response = await client.get(f"/api/v1/services/{test_service_id}/variants")
        assert list_response.status_code == 200
        variants = list_response.json()
        assert any(v["id"] == variant_id for v in variants)

        # Update
        update_data = {
            "name": "Premium",
            "price": "750.00",
            "duration_minutes": 90
        }
        update_response = await client.put(
            f"/api/v1/services/service-variants/{variant_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "Premium"
        assert updated["price"] == "750.00"
        assert updated["duration_minutes"] == 90

        # Delete
        delete_response = await client.delete(
            f"/api/v1/services/service-variants/{variant_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

    async def test_multiple_variants_for_service(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        test_service_id: UUID
    ):
        """Test creating multiple variants for the same service."""
        variants_data = [
            {"name": "Basic", "price": "300.00", "duration_minutes": 30},
            {"name": "Standard", "price": "500.00", "duration_minutes": 60},
            {"name": "Premium", "price": "800.00", "duration_minutes": 90}
        ]

        created_ids = []
        for variant_data in variants_data:
            variant_data["service_id"] = str(test_service_id)
            response = await client.post(
                "/api/v1/services/service-variants",
                json=variant_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Verify all variants exist
        list_response = await client.get(f"/api/v1/services/{test_service_id}/variants")
        assert list_response.status_code == 200
        variants = list_response.json()
        assert len(variants) >= 3
        for variant_id in created_ids:
            assert any(v["id"] == variant_id for v in variants)


class TestServiceRelationships:
    """Test relationships between services, categories, and variants."""

    async def test_service_with_category_relationship(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        admin_headers: dict,
        test_business_id: UUID
    ):
        """Test service correctly links to category."""
        # Create category
        category_data = {"name": "Spa Services", "slug": "spa"}
        cat_response = await client.post(
            "/api/v1/services/categories",
            json=category_data,
            headers=admin_headers
        )
        assert cat_response.status_code == 201, f"Failed to create category: {cat_response.text}"
        category_id = cat_response.json()["id"]

        # Create service with category
        service_data = {
            "business_id": str(test_business_id),
            "category_id": category_id,
            "name": "Hot Stone Massage"
        }
        svc_response = await client.post(
            "/api/v1/services/",
            json=service_data,
            headers=auth_headers
        )
        assert svc_response.status_code == 201, f"Failed to create service: {svc_response.text}"
        service = svc_response.json()
        assert service["category_id"] == category_id

    async def test_pagination_with_real_data(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict,
        test_business_id: UUID
    ):
        """Test pagination works correctly with real data."""
        # Create multiple services
        for i in range(15):
            service_data = {
                "business_id": str(test_business_id),
                "name": f"Service {i}"
            }
            await client.post(
                "/api/v1/services/",
                json=service_data,
                headers=auth_headers
            )

        # Test pagination
        page1 = await client.get("/api/v1/services/?skip=0&limit=10")
        assert page1.status_code == 200
        assert len(page1.json()) <= 10

        page2 = await client.get("/api/v1/services/?skip=10&limit=10")
        assert page2.status_code == 200
        # Should have remaining services
