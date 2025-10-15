"""
Unit tests for CategoryService.

Tests business logic in isolation using mocked database.
Focus on edge cases and error handling to boost coverage.

Phase: 4 - Categories CRUD
Session: 3 - Validation & Testing
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.category import CategoryService
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryFilterParams, CategorySortParams
from src.db.models.category import Category


@pytest.mark.asyncio
class TestCategoryServiceCreate:
    """Test CategoryService.create() method."""
    
    async def test_create_category_success(self):
        """Test creating a category successfully."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        data = CategoryCreate(name="Electronics", description="Electronic items")
        
        # Act
        with patch.object(service, 'get', return_value=None):
            category = await service.create(data, tenant_id)
        
        # Assert
        assert category.name == "Electronics"
        assert category.description == "Electronic items"
        assert category.tenant_id == tenant_id
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
    
    async def test_create_subcategory_with_valid_parent(self):
        """Test creating a subcategory with existing parent."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        parent_id = uuid4()
        parent_category = Category(
            id=parent_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        data = CategoryCreate(name="Smartphones", parent_id=parent_id)
        
        # Mock get to return parent
        with patch.object(service, 'get', return_value=parent_category):
            # Act
            category = await service.create(data, tenant_id)
        
        # Assert
        assert category.parent_id == parent_id
        db.commit.assert_awaited_once()
    
    async def test_create_subcategory_with_invalid_parent_fails(self):
        """Test creating subcategory with non-existent parent raises error."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        parent_id = uuid4()
        data = CategoryCreate(name="Smartphones", parent_id=parent_id)
        
        # Mock get to return None (parent not found)
        with patch.object(service, 'get', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="Parent category .* not found"):
                await service.create(data, tenant_id)
    
    async def test_create_duplicate_name_raises_integrity_error(self):
        """Test creating category with duplicate name raises ValueError."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        data = CategoryCreate(name="Electronics")
        
        # Mock commit to raise IntegrityError with tenant_name constraint
        db.commit.side_effect = IntegrityError(
            "statement", "params", 
            orig=Exception("duplicate key value violates unique constraint \"ix_categories_tenant_name\"")
        )
        
        with patch.object(service, 'get', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="already exists"):
                await service.create(data, tenant_id)
            
            db.rollback.assert_awaited_once()


@pytest.mark.asyncio
class TestCategoryServiceUpdate:
    """Test CategoryService.update() method."""
    
    async def test_update_category_not_found_returns_none(self):
        """Test updating non-existent category returns None."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        data = CategoryUpdate(name="New Name")
        
        # Mock get to return None
        with patch.object(service, 'get', return_value=None):
            # Act
            result = await service.update(category_id, tenant_id, data)
        
        # Assert
        assert result is None
        db.commit.assert_not_awaited()
    
    async def test_update_with_valid_parent(self):
        """Test updating category with new valid parent."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        parent_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Smartphones",
            status="active"
        )
        parent = Category(
            id=parent_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        data = CategoryUpdate(parent_id=parent_id)
        
        # Mock get calls
        get_calls = [category, parent]
        with patch.object(service, 'get', side_effect=get_calls):
            # Act
            result = await service.update(category_id, tenant_id, data)
        
        # Assert
        assert result.parent_id == parent_id
        db.commit.assert_awaited_once()
    
    async def test_update_with_invalid_parent_raises_error(self):
        """Test updating category with non-existent parent raises ValueError."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        parent_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Smartphones",
            status="active"
        )
        data = CategoryUpdate(parent_id=parent_id)
        
        # Mock get: first call returns category, second returns None (parent not found)
        with patch.object(service, 'get', side_effect=[category, None]):
            # Act & Assert
            with pytest.raises(ValueError, match="Parent category .* not found"):
                await service.update(category_id, tenant_id, data)
    
    async def test_update_circular_parent_reference_raises_error(self):
        """Test updating category to be its own parent raises ValueError."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        # Try to set parent to itself
        data = CategoryUpdate(parent_id=category_id)
        
        with patch.object(service, 'get', return_value=category):
            # Act & Assert
            with pytest.raises(ValueError, match="cannot be its own parent"):
                await service.update(category_id, tenant_id, data)
    
    async def test_update_duplicate_name_raises_error(self):
        """Test updating to duplicate name raises ValueError."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        data = CategoryUpdate(name="Existing Name")
        
        # Mock commit to raise IntegrityError
        db.commit.side_effect = IntegrityError(
            "statement", "params",
            orig=Exception("duplicate key value violates unique constraint \"ix_categories_tenant_name\"")
        )
        
        with patch.object(service, 'get', return_value=category):
            # Act & Assert
            with pytest.raises(ValueError, match="already exists"):
                await service.update(category_id, tenant_id, data)
            
            db.rollback.assert_awaited_once()


@pytest.mark.asyncio
class TestCategoryServiceDelete:
    """Test CategoryService.delete() method."""
    
    async def test_delete_category_not_found_returns_false(self):
        """Test deleting non-existent category returns False."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        
        # Mock get to return None
        with patch.object(service, 'get', return_value=None):
            # Act
            result = await service.delete(category_id, tenant_id)
        
        # Assert
        assert result is False
        db.delete.assert_not_called()
    
    async def test_delete_category_with_products_raises_error(self):
        """Test deleting category with products raises ValueError."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        
        # Mock product count query to return 5 products
        product_count_result = AsyncMock()
        product_count_result.scalar = MagicMock(return_value=5)  # Use MagicMock for sync call
        db.execute = AsyncMock(return_value=product_count_result)
        
        with patch.object(service, 'get', return_value=category):
            # Act & Assert
            with pytest.raises(ValueError, match="Cannot delete category.*has.*product"):
                await service.delete(category_id, tenant_id)
    
    async def test_delete_category_updates_children_to_root(self):
        """Test deleting category sets children's parent_id to None."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        category_id = uuid4()
        
        category = Category(
            id=category_id,
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        
        # Create child categories
        child1 = Category(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Smartphones",
            parent_id=category_id,
            status="active"
        )
        child2 = Category(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Laptops",
            parent_id=category_id,
            status="active"
        )
        
        # Mock product count (no products)
        product_count_result = AsyncMock()
        product_count_result.scalar = MagicMock(return_value=0)  # Use MagicMock for sync
        
        # Mock children query
        children_result = AsyncMock()
        children_scalars = MagicMock()
        children_scalars.all = MagicMock(return_value=[child1, child2])
        children_result.scalars = MagicMock(return_value=children_scalars)
        
        # Setup execute to return different results on each call
        db.execute = AsyncMock(side_effect=[product_count_result, children_result])
        
        with patch.object(service, 'get', return_value=category):
            # Act
            result = await service.delete(category_id, tenant_id)
        
        # Assert
        assert result is True
        assert child1.parent_id is None
        assert child2.parent_id is None
        db.delete.assert_called_once_with(category)
        db.commit.assert_awaited_once()


@pytest.mark.asyncio
class TestCategoryServiceList:
    """Test CategoryService.list() method."""
    
    async def test_list_categories_with_name_filter(self):
        """Test listing categories with name filter."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        
        filters = CategoryFilterParams(name="Elec")
        
        # Mock query results
        count_result = AsyncMock()
        count_result.scalar = MagicMock(return_value=1)
        
        categories_result = AsyncMock()
        category = Category(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Electronics",
            status="active"
        )
        categories_scalars = MagicMock()
        categories_scalars.all = MagicMock(return_value=[category])
        categories_result.scalars = MagicMock(return_value=categories_scalars)
        
        db.execute = AsyncMock(side_effect=[count_result, categories_result])
        
        # Act
        categories, total = await service.list(
            tenant_id=tenant_id,
            filters=filters,
            page=1,
            page_size=50
        )
        
        # Assert
        assert len(categories) == 1
        assert total == 1
        assert categories[0].name == "Electronics"
    
    async def test_list_root_categories_only(self):
        """Test listing only root categories (no parent)."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        
        filters = CategoryFilterParams(root_only=True)
        
        # Mock query results
        count_result = AsyncMock()
        count_result.scalar = MagicMock(return_value=2)
        
        categories_result = AsyncMock()
        root1 = Category(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Electronics",
            parent_id=None,
            status="active"
        )
        root2 = Category(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Clothing",
            parent_id=None,
            status="active"
        )
        categories_scalars = MagicMock()
        categories_scalars.all = MagicMock(return_value=[root1, root2])
        categories_result.scalars = MagicMock(return_value=categories_scalars)
        
        db.execute = AsyncMock(side_effect=[count_result, categories_result])
        
        # Act
        categories, total = await service.list(
            tenant_id=tenant_id,
            filters=filters,
            page=1,
            page_size=50
        )
        
        # Assert
        assert len(categories) == 2
        assert total == 2
        assert all(cat.parent_id is None for cat in categories)


@pytest.mark.asyncio
class TestCategoryServiceGetCategoryTree:
    """Test CategoryService.get_category_tree() method."""
    
    async def test_get_category_tree_root_level(self):
        """Test getting root level categories."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        
        # Mock query result
        result = AsyncMock()
        root_categories = [
            Category(
                id=uuid4(),
                tenant_id=tenant_id,
                name="Electronics",
                parent_id=None,
                status="active"
            ),
            Category(
                id=uuid4(),
                tenant_id=tenant_id,
                name="Clothing",
                parent_id=None,
                status="active"
            )
        ]
        result_scalars = MagicMock()
        result_scalars.all = MagicMock(return_value=root_categories)
        result.scalars = MagicMock(return_value=result_scalars)
        db.execute = AsyncMock(return_value=result)
        
        # Act
        categories = await service.get_category_tree(tenant_id, parent_id=None)
        
        # Assert
        assert len(categories) == 2
        assert all(cat.parent_id is None for cat in categories)
        assert categories[0].name == "Electronics"
    
    async def test_get_category_tree_children_of_parent(self):
        """Test getting children of specific parent."""
        # Arrange
        db = AsyncMock(spec=AsyncSession)
        service = CategoryService(db)
        tenant_id = uuid4()
        parent_id = uuid4()
        
        # Mock query result
        result = AsyncMock()
        children = [
            Category(
                id=uuid4(),
                tenant_id=tenant_id,
                name="Smartphones",
                parent_id=parent_id,
                status="active"
            ),
            Category(
                id=uuid4(),
                tenant_id=tenant_id,
                name="Laptops",
                parent_id=parent_id,
                status="active"
            )
        ]
        result_scalars = MagicMock()
        result_scalars.all = MagicMock(return_value=children)
        result.scalars = MagicMock(return_value=result_scalars)
        db.execute = AsyncMock(return_value=result)
        
        # Act
        categories = await service.get_category_tree(tenant_id, parent_id=parent_id)
        
        # Assert
        assert len(categories) == 2
        assert all(cat.parent_id == parent_id for cat in categories)
