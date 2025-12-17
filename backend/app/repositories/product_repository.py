from typing import Optional
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.core.exceptions import NotFoundError
from app.models.product import InventoryLogResponse, ProductResponse
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[ProductResponse]):
    """Repository for product-related database operations."""

    def __init__(self, conn: AsyncConnection):
        super().__init__(conn)
        self.table = "products"

    async def get_products(
        self,
        location_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProductResponse]:
        """List products with optional location filter."""
        if location_id:
            query = """
                SELECT id, location_id, name, sku, price, stock_quantity
                FROM products
                WHERE location_id = %s
                ORDER BY name ASC
                LIMIT %s OFFSET %s
            """
            params = (location_id, limit, offset)
        elif business_id:
            # Filter by business via join
            query = """
                SELECT p.id, p.location_id, p.name, p.sku, p.price, p.stock_quantity
                FROM products p
                JOIN locations l ON p.location_id = l.id
                WHERE l.business_id = %s
                ORDER BY p.name ASC
                LIMIT %s OFFSET %s
            """
            params = (business_id, limit, offset)
        else:
            query = """
                SELECT id, location_id, name, sku, price, stock_quantity
                FROM products
                ORDER BY name ASC
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)

        return await self._execute_many(query, params, ProductResponse)

    async def get_product_by_id(self, product_id: UUID) -> Optional[ProductResponse]:
        """Get single product by ID."""
        query = """
            SELECT id, location_id, name, sku, price, stock_quantity
            FROM products
            WHERE id = %s
        """
        return await self._execute_one(query, (product_id,), ProductResponse)

    async def create_product(self, data: dict) -> ProductResponse:
        """Insert new product."""
        return await self._create(self.table, data, ProductResponse)

    async def update_product(
        self, product_id: UUID, data: dict
    ) -> Optional[ProductResponse]:
        """Update product details."""
        return await self._update(self.table, product_id, data, ProductResponse)

    async def adjust_inventory_raw(
        self, product_id: UUID, change_amount: int, reason: Optional[str] = None
    ) -> ProductResponse:
        """
        Atomic inventory adjustment with logging.

        Pure data access - no validation.
        Validation should be done in ProductService.
        """
        async with self.conn.transaction():
            # Update stock
            query_update = """
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE id = %s
                RETURNING id, location_id, name, sku, price, stock_quantity
            """
            async with self.conn.cursor(row_factory=class_row(ProductResponse)) as cur:
                await cur.execute(query_update, (change_amount, product_id))
                updated_product = await cur.fetchone()

                if not updated_product:
                    raise NotFoundError(f"Product with ID {product_id} not found")

                # Log the change
                query_log = """
                    INSERT INTO inventory_logs (product_id, change_amount, reason)
                    VALUES (%s, %s, %s)
                """
                await cur.execute(query_log, (product_id, change_amount, reason))

        return updated_product

    async def get_inventory_logs(
        self, product_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[InventoryLogResponse]:
        """Get inventory change history for a product."""
        query = """
            SELECT id, product_id, change_amount, reason, created_at
            FROM inventory_logs
            WHERE product_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return await self._execute_many(
            query, (product_id, limit, offset), InventoryLogResponse
        )
