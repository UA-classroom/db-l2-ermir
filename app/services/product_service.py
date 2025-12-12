from typing import Optional
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import ProductCreate, ProductResponse, ProductUpdate
from app.repositories.product_repository import ProductRepository


class ProductService:
    """Service for product-related business logic."""

    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def adjust_inventory(
        self, product_id: UUID, change_amount: int, reason: Optional[str] = None
    ) -> ProductResponse:
        """
        Adjust product inventory with validation.

        Validates stock levels and prevents negative inventory.

        Args:
            product_id: Product UUID
            change_amount: Amount to add (positive) or subtract (negative)
            reason: Optional reason for the adjustment

        Returns:
            Updated product

        Raises:
            NotFoundError: If product doesn't exist
            ConflictError: If adjustment would result in negative stock
        """
        # Get current product
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")

        # Validate stock levels (business logic)
        new_stock = product.stock_quantity + change_amount
        if new_stock < 0:
            raise ConflictError(
                f"Insufficient stock. Current: {product.stock_quantity}, "
                f"Requested change: {change_amount}"
            )

        # Delegate to repository for data access
        return await self.product_repo.adjust_inventory_raw(
            product_id, change_amount, reason
        )


    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create new product with validation."""
        # Could add business logic here (e.g., check location exists)
        return await self.product_repo.create_product(product_data.model_dump())

    async def update_product(
        self, product_id: UUID, update_data: ProductUpdate
    ) -> ProductResponse:
        """Update product with validation."""
        # Get existing product
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")

        # Update
        updated = await self.product_repo.update_product(
            product_id, update_data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise NotFoundError(f"Product {product_id} not found")

        return updated