"""
Product service - Business logic for product management.

Handles product CRUD operations with multi-tenant isolation,
SKU validation, and business rule enforcement.

Tasks: T055-T059
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.models.product import Product
from src.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductFilterParams,
    ProductSortParams,
)
from src.utils.validators import validate_sku
from src.core.logging import get_logger

logger = get_logger(__name__)


class ProductService:
    """Service for product business logic."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize product service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def _get_existing_product_by_sku(
        self,
        sku: str,
        tenant_id: UUID,
    ) -> Optional[Product]:
        """Get existing product by SKU and tenant."""
        stmt = select(Product).where(
            and_(
                Product.sku == sku.upper(),
                Product.tenant_id == tenant_id,
                Product.status != "deleted",
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        tenant_id: UUID,
        name: str,
        sku: str,
        quantity: int,
        price: Decimal,
        description: Optional[str] = None,
        category_id: Optional[UUID] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Product:
        """
        Create a new product.
        
        Task: T055 - ProductService.create()
        
        Args:
            tenant_id: Tenant UUID
            name: Product name
            sku: Stock Keeping Unit
            quantity: Initial stock quantity
            price: Product price
            description: Optional description
            category_id: Optional category UUID
            custom_fields: Optional custom JSONB fields
            
        Returns:
            Created product
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint fails
        """
        # Validate business rules
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")
        
        if price < 0:
            raise ValueError("Price must be non-negative")
        
        # Validate and normalize SKU
        existing = await self._get_existing_product_by_sku(sku, tenant_id)
        normalized_sku = await validate_sku(
            sku,
            tenant_id,
            existing_product={"sku": existing.sku, "tenant_id": existing.tenant_id} if existing else None,
        )
        
        # Create product
        product = Product(
            tenant_id=tenant_id,
            name=name.strip(),
            sku=normalized_sku,
            description=description.strip() if description else None,
            quantity=quantity,
            price=price,
            category_id=category_id,
            custom_fields=custom_fields,
            status="active",
        )
        
        self.db.add(product)
        
        try:
            await self.db.commit()
            await self.db.refresh(product)
            
            logger.info(
                "Product created",
                extra={
                    "product_id": str(product.id),
                    "tenant_id": str(tenant_id),
                    "sku": normalized_sku,
                },
            )
            
            return product
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to create product: {e}")
            raise
    
    async def get(
        self,
        product_id: UUID,
        tenant_id: UUID,
    ) -> Optional[Product]:
        """
        Get product by ID.
        
        Task: T056 - ProductService.get()
        
        Args:
            product_id: Product UUID
            tenant_id: Tenant UUID
            
        Returns:
            Product if found and not deleted, None otherwise
        """
        stmt = select(Product).where(
            and_(
                Product.id == product_id,
                Product.tenant_id == tenant_id,
                Product.status != "deleted",
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        tenant_id: UUID,
        filters: Optional[ProductFilterParams] = None,
        sort: Optional[ProductSortParams] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Product], int]:
        """
        List products with filtering, sorting, and pagination.
        
        Task: T057 - ProductService.list()
        
        Args:
            tenant_id: Tenant UUID
            filters: Optional filter parameters
            sort: Optional sort parameters
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            Tuple of (products list, total count)
        """
        # Base query
        stmt = select(Product).where(
            and_(
                Product.tenant_id == tenant_id,
                Product.status != "deleted",
            )
        )
        
        # Apply filters
        if filters:
            if filters.name:
                stmt = stmt.where(Product.name.ilike(f"%{filters.name}%"))
            
            if filters.sku:
                stmt = stmt.where(Product.sku.ilike(f"%{filters.sku}%"))
            
            if filters.category_id:
                stmt = stmt.where(Product.category_id == filters.category_id)
            
            if filters.status:
                stmt = stmt.where(Product.status == filters.status)
            
            if filters.min_quantity is not None:
                stmt = stmt.where(Product.quantity >= filters.min_quantity)
            
            if filters.max_quantity is not None:
                stmt = stmt.where(Product.quantity <= filters.max_quantity)
            
            if filters.min_price is not None:
                stmt = stmt.where(Product.price >= filters.min_price)
            
            if filters.max_price is not None:
                stmt = stmt.where(Product.price <= filters.max_price)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.alias())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply sorting
        if sort:
            sort_field = getattr(Product, sort.sort_by, Product.created_at)
            if sort.sort_order == "desc":
                stmt = stmt.order_by(sort_field.desc())
            else:
                stmt = stmt.order_by(sort_field.asc())
        else:
            stmt = stmt.order_by(Product.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # Execute
        result = await self.db.execute(stmt)
        products = result.scalars().all()
        
        return list(products), total
    
    async def update(
        self,
        product_id: UUID,
        tenant_id: UUID,
        data: ProductUpdate,
    ) -> Optional[Product]:
        """
        Update product.
        
        Task: T058 - ProductService.update()
        
        Args:
            product_id: Product UUID
            tenant_id: Tenant UUID
            data: Update data
            
        Returns:
            Updated product if found, None otherwise
            
        Raises:
            ValueError: If validation fails
        """
        # Get existing product
        product = await self.get(product_id, tenant_id)
        if not product:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        
        # Validate SKU if being updated
        if "sku" in update_data:
            existing = await self._get_existing_product_by_sku(
                update_data["sku"],
                tenant_id,
            )
            normalized_sku = await validate_sku(
                update_data["sku"],
                tenant_id,
                existing_product={
                    "id": existing.id,
                    "sku": existing.sku,
                    "tenant_id": existing.tenant_id,
                } if existing else None,
                current_product_id=product_id,
            )
            update_data["sku"] = normalized_sku
        
        # Validate business rules
        if "name" in update_data:
            if not update_data["name"] or not update_data["name"].strip():
                raise ValueError("Product name cannot be empty")
            update_data["name"] = update_data["name"].strip()
        
        if "description" in update_data and update_data["description"]:
            update_data["description"] = update_data["description"].strip()
        
        if "quantity" in update_data and update_data["quantity"] < 0:
            raise ValueError("Quantity must be non-negative")
        
        if "price" in update_data and update_data["price"] < 0:
            raise ValueError("Price must be non-negative")
        
        # Apply updates
        for key, value in update_data.items():
            setattr(product, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(product)
            
            logger.info(
                "Product updated",
                extra={
                    "product_id": str(product_id),
                    "tenant_id": str(tenant_id),
                    "updated_fields": list(update_data.keys()),
                },
            )
            
            return product
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to update product: {e}")
            raise
    
    async def soft_delete(
        self,
        product_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """
        Soft delete product (set status to 'deleted').
        
        Task: T059 - ProductService.soft_delete()
        
        Args:
            product_id: Product UUID
            tenant_id: Tenant UUID
            
        Returns:
            True if deleted, False if not found
        """
        product = await self.get(product_id, tenant_id)
        if not product:
            return False
        
        product.status = "deleted"
        
        await self.db.commit()
        
        logger.info(
            "Product soft deleted",
            extra={
                "product_id": str(product_id),
                "tenant_id": str(tenant_id),
            },
        )
        
        return True
