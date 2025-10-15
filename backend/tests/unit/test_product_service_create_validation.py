"""
Additional unit tests for ProductService.create() validation logic.

Focuses on covering validation paths and error handling in create method.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from src.services.product import ProductService
from src.db.models.product import Product


@pytest.fixture
def mock_db():
    """Mock database session."""
    session = Mock()
    session.add = Mock()
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
async def test_create_validates_empty_name_raises_error(mock_db, tenant_id):
    """Test that create validates name is not empty."""
    service = ProductService(mock_db)
    
    with pytest.raises(ValueError) as exc:
        await service.create(
            tenant_id=tenant_id,
            name="",
            sku="TEST-001",
            quantity=10,
            price=100,
        )
    
    assert "name" in str(exc.value).lower()
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_create_validates_whitespace_name_raises_error(mock_db, tenant_id):
    """Test that create validates name is not whitespace only."""
    service = ProductService(mock_db)
    
    with pytest.raises(ValueError) as exc:
        await service.create(
            tenant_id=tenant_id,
            name="   ",
            sku="TEST-002",
            quantity=10,
            price=100,
        )
    
    assert "name" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_create_validates_negative_quantity_raises_error(mock_db, tenant_id):
    """Test that create validates quantity is non-negative."""
    service = ProductService(mock_db)
    
    with pytest.raises(ValueError) as exc:
        await service.create(
            tenant_id=tenant_id,
            name="Product",
            sku="TEST-003",
            quantity=-10,
            price=100,
        )
    
    assert "quantity" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_create_validates_negative_price_raises_error(mock_db, tenant_id):
    """Test that create validates price is non-negative."""
    service = ProductService(mock_db)
    
    with pytest.raises(ValueError) as exc:
        await service.create(
            tenant_id=tenant_id,
            name="Product",
            sku="TEST-004",
            quantity=10,
            price=-50,
        )
    
    assert "price" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_create_allows_zero_quantity(mock_db, tenant_id):
    """Test that create allows zero quantity (out of stock)."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-005",
        quantity=0,
        price=100,
    )
    
    assert product.quantity == 0
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_allows_zero_price(mock_db, tenant_id):
    """Test that create allows zero price (free item)."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Free Product",
        sku="FREE-001",
        quantity=10,
        price=0,
    )
    
    assert product.price == 0
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_trims_name_whitespace(mock_db, tenant_id):
    """Test that create trims whitespace from name."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="  Product Name  ",
        sku="TEST-006",
        quantity=10,
        price=100,
    )
    
    assert product.name == "Product Name"


@pytest.mark.asyncio
async def test_create_trims_description_whitespace(mock_db, tenant_id):
    """Test that create trims whitespace from description."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-007",
        description="  Description  ",
        quantity=10,
        price=100,
    )
    
    assert product.description == "Description"


@pytest.mark.asyncio
async def test_create_handles_none_description(mock_db, tenant_id):
    """Test that create handles None description."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-008",
        description=None,
        quantity=10,
        price=100,
    )
    
    assert product.description is None


@pytest.mark.asyncio
async def test_create_sets_default_status_active(mock_db, tenant_id):
    """Test that create sets default status to active."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-009",
        quantity=10,
        price=100,
    )
    
    assert product.status == "active"


@pytest.mark.asyncio
async def test_create_handles_integrity_error(mock_db, tenant_id):
    """Test that create handles database integrity errors."""
    service = ProductService(mock_db)
    
    # Mock SKU check to pass
    mock_check_result = Mock()
    mock_check_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_check_result
    
    # Mock commit to raise IntegrityError
    mock_db.commit.side_effect = IntegrityError("statement", {}, Exception("duplicate"))
    
    with pytest.raises(IntegrityError):
        await service.create(
            tenant_id=tenant_id,
            name="Product",
            sku="DUP-SKU",
            quantity=10,
            price=100,
        )
    
    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_with_optional_min_quantity(mock_db, tenant_id):
    """Test create with optional min_quantity parameter."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-010",
        quantity=50,
        min_quantity=10,
        price=100,
    )
    
    assert product.min_quantity == 10


@pytest.mark.asyncio
async def test_create_with_optional_max_quantity(mock_db, tenant_id):
    """Test create with optional max_quantity parameter."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-011",
        quantity=50,
        max_quantity=100,
        price=100,
    )
    
    assert product.max_quantity == 100


@pytest.mark.asyncio
async def test_create_with_optional_category_id(mock_db, tenant_id):
    """Test create with optional category_id parameter."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    category_id = uuid4()
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-012",
        quantity=10,
        price=100,
        category_id=category_id,
    )
    
    assert product.category_id == category_id


@pytest.mark.asyncio
async def test_create_with_optional_custom_fields(mock_db, tenant_id):
    """Test create with optional custom_fields parameter."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    custom_fields = {"brand": "ACME", "color": "blue"}
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-013",
        quantity=10,
        price=100,
        custom_fields=custom_fields,
    )
    
    assert product.custom_fields == custom_fields


@pytest.mark.asyncio
async def test_create_with_empty_custom_fields(mock_db, tenant_id):
    """Test create with empty custom_fields dict."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="TEST-014",
        quantity=10,
        price=100,
        custom_fields={},
    )
    
    assert product.custom_fields == {}


@pytest.mark.asyncio
async def test_create_normalizes_sku_uppercase(mock_db, tenant_id):
    """Test that create normalizes SKU to uppercase."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="lowercase-sku",
        quantity=10,
        price=100,
    )
    
    assert product.sku == "LOWERCASE-SKU"


@pytest.mark.asyncio
async def test_create_normalizes_sku_trim(mock_db, tenant_id):
    """Test that create trims whitespace from SKU."""
    service = ProductService(mock_db)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=tenant_id,
        name="Product",
        sku="  SKU-015  ",
        quantity=10,
        price=100,
    )
    
    assert product.sku == "SKU-015"
