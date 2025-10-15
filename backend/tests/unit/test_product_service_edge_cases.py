"""
Additional unit tests for ProductService edge cases.

Covers specific scenarios in list(), update(), and soft_delete() methods.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from pydantic import ValidationError

from src.services.product import ProductService
from src.schemas.product import ProductFilterParams, ProductSortParams, ProductUpdate
from src.db.models.product import Product


@pytest.fixture
def mock_db():
    """Mock database session."""
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def tenant_id():
    """Sample tenant ID."""
    return uuid4()


@pytest.mark.asyncio
async def test_list_with_no_filters(mock_db, tenant_id):
    """Test list without filters returns all products."""
    service = ProductService(mock_db)
    
    # Mock execute to return product list
    mock_result = Mock()
    mock_result.scalars().all.return_value = []
    
    # Mock count
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 0
    
    mock_db.execute.side_effect = [mock_count_result, mock_result]
    
    products, total = await service.list(tenant_id)
    
    assert products == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_with_all_filters(mock_db, tenant_id):
    """Test list with all possible filters applied."""
    service = ProductService(mock_db)
    
    category_id = uuid4()
    filters = ProductFilterParams(
        name="Test",
        sku="TST",
        category_id=category_id,
        status="active",
        min_quantity=10,
        max_quantity=100,
        min_price=50.00,
        max_price=500.00,
    )
    
    # Mock execute
    mock_result = Mock()
    mock_result.scalars().all.return_value = []
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 0
    
    mock_db.execute.side_effect = [mock_count_result, mock_result]
    
    products, total = await service.list(tenant_id, filters=filters)
    
    assert products == []
    assert total == 0
    assert mock_db.execute.call_count == 2


@pytest.mark.asyncio
async def test_list_with_sorting_asc(mock_db, tenant_id):
    """Test list with ascending sort order."""
    service = ProductService(mock_db)
    
    sort = ProductSortParams(sort_by="name", sort_order="asc")
    
    # Mock execute
    mock_result = Mock()
    mock_result.scalars().all.return_value = []
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 0
    
    mock_db.execute.side_effect = [mock_count_result, mock_result]
    
    products, total = await service.list(tenant_id, sort=sort)
    
    assert products == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_with_sorting_desc(mock_db, tenant_id):
    """Test list with descending sort order."""
    service = ProductService(mock_db)
    
    sort = ProductSortParams(sort_by="price", sort_order="desc")
    
    # Mock execute
    mock_result = Mock()
    mock_result.scalars().all.return_value = []
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 0
    
    mock_db.execute.side_effect = [mock_count_result, mock_result]
    
    products, total = await service.list(tenant_id, sort=sort)
    
    assert products == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_with_pagination(mock_db, tenant_id):
    """Test list with custom pagination."""
    service = ProductService(mock_db)
    
    # Mock execute
    mock_result = Mock()
    mock_result.scalars().all.return_value = []
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 100
    
    mock_db.execute.side_effect = [mock_count_result, mock_result]
    
    products, total = await service.list(tenant_id, page=2, page_size=20)
    
    assert products == []
    assert total == 100


@pytest.mark.asyncio
async def test_update_product_not_found(mock_db, tenant_id):
    """Test update returns None when product not found."""
    service = ProductService(mock_db)
    
    # Mock get to return None
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product_id = uuid4()
    data = ProductUpdate(name="New Name")
    
    result = await service.update(product_id, tenant_id, data)
    
    assert result is None


@pytest.mark.asyncio
async def test_update_with_sku_change(mock_db, tenant_id):
    """Test update with SKU change."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="OLD-SKU",
        name="Product",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get to return existing product
    mock_get_result = Mock()
    mock_get_result.scalar_one_or_none.return_value = existing_product
    
    # Mock SKU uniqueness check
    mock_sku_result = Mock()
    mock_sku_result.scalar_one_or_none.return_value = None
    
    mock_db.execute.side_effect = [mock_get_result, mock_sku_result]
    
    data = ProductUpdate(sku="new-sku")
    
    result = await service.update(product_id, tenant_id, data)
    
    assert result.sku == "NEW-SKU"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_with_name_trim(mock_db, tenant_id):
    """Test update trims whitespace from name."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Old Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    data = ProductUpdate(name="  New Name  ")
    
    result = await service.update(product_id, tenant_id, data)
    
    assert result.name == "New Name"


@pytest.mark.asyncio
async def test_update_with_empty_name_raises_error(mock_db, tenant_id):
    """Test update with empty name raises ValueError."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Old Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    # Pydantic validates on creation, so we expect ValidationError
    with pytest.raises(ValidationError) as exc:
        data = ProductUpdate(name="   ")
    
    assert "name" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_update_with_description_trim(mock_db, tenant_id):
    """Test update trims whitespace from description."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    data = ProductUpdate(description="  Description  ")
    
    result = await service.update(product_id, tenant_id, data)
    
    assert result.description == "Description"


@pytest.mark.asyncio
async def test_update_with_negative_quantity_raises_error(mock_db, tenant_id):
    """Test update with negative quantity raises ValueError."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    # Pydantic validates on creation, so we expect ValidationError
    with pytest.raises(ValidationError) as exc:
        data = ProductUpdate(quantity=-5)
    
    assert "quantity" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_update_with_negative_price_raises_error(mock_db, tenant_id):
    """Test update with negative price raises ValueError."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    # Pydantic validates on creation, so we expect ValidationError
    with pytest.raises(ValidationError) as exc:
        data = ProductUpdate(price=-50.00)
    
    assert "price" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_soft_delete_product_not_found(mock_db, tenant_id):
    """Test soft delete returns False when product not found."""
    service = ProductService(mock_db)
    
    # Mock get to return None
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product_id = uuid4()
    
    result = await service.soft_delete(product_id, tenant_id)
    
    assert result is False
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_soft_delete_product_success(mock_db, tenant_id):
    """Test successful soft delete."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    result = await service.soft_delete(product_id, tenant_id)
    
    assert result is True
    assert existing_product.status == "deleted"
    mock_db.commit.assert_called_once()
