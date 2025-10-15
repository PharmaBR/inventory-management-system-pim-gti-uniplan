"""
Category business logic service.

Handles CRUD operations for categories with:
- Hierarchical structure (parent-child relationships)
- Unique name validation per tenant
- Product constraint checking
- Cascade behavior for parent deletion

Phase: 4 - Categories CRUD
Session: 2 - Implementation
"""

from typing import Optional, List, Tuple
from uuid import UUID
import logging

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.models.category import Category
from src.db.models.product import Product
from src.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryFilterParams,
    CategorySortParams,
)

logger = logging.getLogger("inventory_system")


class CategoryService:
    """
    Service for category CRUD operations.
    
    Implements business logic for hierarchical category management.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
    
    async def create(
        self,
        data: CategoryCreate,
        tenant_id: UUID,
    ) -> Category:
        """
        Create a new category.
        
        Validates:
        - Name is unique per tenant
        - Parent exists if provided
        
        Args:
            data: Category creation data
            tenant_id: Tenant UUID
            
        Returns:
            Created category
            
        Raises:
            IntegrityError: If name already exists or parent not found
        """
        try:
            # Validate parent exists if provided
            if data.parent_id:
                parent = await self.get(data.parent_id, tenant_id)
                if not parent:
                    raise ValueError(f"Parent category {data.parent_id} not found")
            
            # Create category
            category = Category(
                tenant_id=tenant_id,
                name=data.name,
                description=data.description,
                parent_id=data.parent_id,
                status=data.status,
            )
            
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(category)
            
            logger.info(
                f"Created category: {category.id} ({category.name}) "
                f"for tenant {tenant_id}"
            )
            
            return category
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to create category: {e}")
            
            # Check if it's a duplicate name error
            if "ix_categories_tenant_name" in str(e):
                raise ValueError(
                    f"Category with name '{data.name}' already exists"
                )
            raise
    
    async def get(
        self,
        category_id: UUID,
        tenant_id: UUID,
    ) -> Optional[Category]:
        """
        Get category by ID.
        
        Enforces tenant isolation.
        
        Args:
            category_id: Category UUID
            tenant_id: Tenant UUID
            
        Returns:
            Category if found, None otherwise
        """
        stmt = select(Category).where(
            and_(
                Category.id == category_id,
                Category.tenant_id == tenant_id,
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        tenant_id: UUID,
        filters: Optional[CategoryFilterParams] = None,
        sort: Optional[CategorySortParams] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Category], int]:
        """
        List categories with filtering, sorting, and pagination.
        
        Args:
            tenant_id: Tenant UUID
            filters: Filter parameters
            sort: Sort parameters
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            Tuple of (categories, total_count)
        """
        # Base query with tenant filter
        stmt = select(Category).where(Category.tenant_id == tenant_id)
        
        # Apply filters
        if filters:
            if filters.name:
                # Case-insensitive partial match
                stmt = stmt.where(
                    Category.name.ilike(f"%{filters.name}%")
                )
            
            if filters.status:
                stmt = stmt.where(Category.status == filters.status)
            
            if filters.parent_id:
                stmt = stmt.where(Category.parent_id == filters.parent_id)
            
            if filters.root_only:
                stmt = stmt.where(Category.parent_id.is_(None))
        
        # Get total count before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Apply sorting
        if sort:
            sort_column = getattr(Category, sort.sort_by, Category.created_at)
            if sort.sort_order == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(Category.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # Execute query
        result = await self.db.execute(stmt)
        categories = result.scalars().all()
        
        return list(categories), total
    
    async def update(
        self,
        category_id: UUID,
        tenant_id: UUID,
        data: CategoryUpdate,
    ) -> Optional[Category]:
        """
        Update category.
        
        Supports partial updates.
        Validates unique name if changing.
        
        Args:
            category_id: Category UUID
            tenant_id: Tenant UUID
            data: Update data
            
        Returns:
            Updated category or None if not found
            
        Raises:
            IntegrityError: If name conflict
            ValueError: If parent not found
        """
        # Get existing category
        category = await self.get(category_id, tenant_id)
        if not category:
            return None
        
        try:
            # Validate parent if changing
            if data.parent_id is not None:
                # Check parent exists
                parent = await self.get(data.parent_id, tenant_id)
                if not parent:
                    raise ValueError(f"Parent category {data.parent_id} not found")
                
                # Prevent circular reference (can't be its own parent)
                if data.parent_id == category_id:
                    raise ValueError("Category cannot be its own parent")
            
            # Apply updates
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(category, key, value)
            
            await self.db.commit()
            await self.db.refresh(category)
            
            logger.info(
                f"Updated category: {category.id} ({category.name}) "
                f"for tenant {tenant_id}"
            )
            
            return category
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to update category: {e}")
            
            # Check if it's a duplicate name error
            if "ix_categories_tenant_name" in str(e):
                raise ValueError(
                    f"Category with name '{data.name}' already exists"
                )
            raise
    
    async def delete(
        self,
        category_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """
        Delete category.
        
        Validates:
        - Category has no products
        - Updates children to be root categories (parent_id = NULL)
        
        Args:
            category_id: Category UUID
            tenant_id: Tenant UUID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If category has products
        """
        # Get category
        category = await self.get(category_id, tenant_id)
        if not category:
            return False
        
        # Check if category has products
        product_count_stmt = select(func.count()).where(
            and_(
                Product.category_id == category_id,
                Product.tenant_id == tenant_id,
            )
        )
        product_count_result = await self.db.execute(product_count_stmt)
        product_count = product_count_result.scalar() or 0
        
        if product_count > 0:
            raise ValueError(
                f"Cannot delete category '{category.name}' because it has "
                f"{product_count} associated product(s). "
                "Please move or delete the products first."
            )
        
        # Update children to be root categories (SET NULL behavior)
        update_children_stmt = (
            select(Category)
            .where(
                and_(
                    Category.parent_id == category_id,
                    Category.tenant_id == tenant_id,
                )
            )
        )
        children_result = await self.db.execute(update_children_stmt)
        children = children_result.scalars().all()
        
        for child in children:
            child.parent_id = None
        
        # Delete category
        await self.db.delete(category)
        await self.db.commit()
        
        logger.info(
            f"Deleted category: {category_id} ({category.name}) "
            f"for tenant {tenant_id}. "
            f"Updated {len(children)} children to root categories."
        )
        
        return True
    
    async def get_category_tree(
        self,
        tenant_id: UUID,
        parent_id: Optional[UUID] = None,
    ) -> List[Category]:
        """
        Get category tree (hierarchical structure).
        
        Useful for building nested category displays.
        
        Args:
            tenant_id: Tenant UUID
            parent_id: Parent to start from (None for root)
            
        Returns:
            List of categories at this level
        """
        stmt = select(Category).where(
            and_(
                Category.tenant_id == tenant_id,
                Category.parent_id == parent_id if parent_id else Category.parent_id.is_(None),
            )
        ).order_by(Category.name.asc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
