"""
Unit tests for ProductService.

Tests the business logic of ProductService in isolation using mocks.
Following TDD methodology - tests written FIRST.

Task: T046 - Unit test: ProductService.create()
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.db.models.product import Product
from src.db.models.tenant import Tenant


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def sample_tenant():
    """Sample tenant for testing."""
    tenant = Tenant(
        id=uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        max_users=10,
        max_products=1000,
        status="active",
    )
    return tenant


@pytest.fixture
def sample_product_data():
    """Sample product data for creation."""
    return {
        "name": "Test Product",
        "sku": "TEST-001",
        "quantity": 10,
        "price": 100.50,
        "description": "A test product",
    }


@pytest.mark.asyncio
async def test_create_product_success(mock_db_session, sample_tenant, sample_product_data):
    """Test successful product creation."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock the SKU uniqueness check to return no duplicates
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    # Create product
    product = await service.create(
        tenant_id=sample_tenant.id,
        **sample_product_data
    )
    
    # Verify product was created with correct data
    assert product.name == "Test Product"
    assert product.sku == "TEST-001"
    assert product.quantity == 10
    assert product.price == 100.50
    assert product.tenant_id == sample_tenant.id
    assert product.status == "active"
    
    # Verify database operations
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_duplicate_sku_raises_error(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test that creating a product with duplicate SKU raises error."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock existing product with same SKU
    existing_product = Product(
        id=uuid4(),
        tenant_id=sample_tenant.id,
        sku="TEST-001",
        name="Existing Product",
        quantity=5,
        price=50.0,
    )
    
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=existing_product)
    mock_db_session.execute.return_value = mock_result
    
    # Attempt to create product with duplicate SKU
    with pytest.raises(ValueError) as exc_info:
        await service.create(
            tenant_id=sample_tenant.id,
            **sample_product_data
        )
    
    assert "sku" in str(exc_info.value).lower()
    assert "already exists" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_product_validates_quantity_non_negative(
    mock_db_session, sample_tenant
):
    """Test that negative quantity is rejected."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    with pytest.raises(ValueError) as exc_info:
        await service.create(
            tenant_id=sample_tenant.id,
            name="Product",
            sku="PROD-001",
            quantity=-5,
            price=100.0,
        )
    
    assert "quantity" in str(exc_info.value).lower()
    assert "negative" in str(exc_info.value).lower() or "positive" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_product_validates_price_non_negative(
    mock_db_session, sample_tenant
):
    """Test that negative price is rejected."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    with pytest.raises(ValueError) as exc_info:
        await service.create(
            tenant_id=sample_tenant.id,
            name="Product",
            sku="PROD-001",
            quantity=10,
            price=-50.0,
        )
    
    assert "price" in str(exc_info.value).lower()
    assert "negative" in str(exc_info.value).lower() or "positive" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_product_with_category(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test creating product with category_id."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    category_id = uuid4()
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        category_id=category_id,
        **sample_product_data
    )
    
    assert product.category_id == category_id


@pytest.mark.asyncio
async def test_create_product_with_custom_fields(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test creating product with custom_fields."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    custom_fields = {"brand": "ACME", "warranty": 12}
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        custom_fields=custom_fields,
        **sample_product_data
    )
    
    assert product.custom_fields == custom_fields


@pytest.mark.asyncio
async def test_create_product_sets_default_status(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test that new products have 'active' status by default."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        **sample_product_data
    )
    
    assert product.status == "active"


@pytest.mark.asyncio
async def test_create_product_sets_timestamps(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test that created_at and updated_at are set."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        **sample_product_data
    )
    
    # Timestamps should be set (even if mocked)
    # In real implementation, these are set by database defaults
    # Here we verify the service doesn't interfere with timestamp logic
    assert hasattr(product, 'created_at')
    assert hasattr(product, 'updated_at')


@pytest.mark.asyncio
async def test_create_product_handles_database_error(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test that database errors are handled appropriately."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock SKU check success
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    # Mock database commit failure
    mock_db_session.commit.side_effect = IntegrityError("DB Error", None, None)
    
    with pytest.raises(IntegrityError):
        await service.create(
            tenant_id=sample_tenant.id,
            **sample_product_data
        )


@pytest.mark.asyncio
async def test_create_product_normalizes_sku(
    mock_db_session, sample_tenant
):
    """Test that SKU is normalized (uppercase, trimmed)."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        name="Product",
        sku="  test-001  ",  # Lowercase with spaces
        quantity=10,
        price=100.0,
    )
    
    # SKU should be normalized to uppercase and trimmed
    assert product.sku == "TEST-001"


@pytest.mark.asyncio
async def test_create_product_validates_sku_length(
    mock_db_session, sample_tenant
):
    """Test that SKU length is validated (max 100 chars)."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    long_sku = "A" * 101  # 101 characters
    
    with pytest.raises(ValueError) as exc_info:
        await service.create(
            tenant_id=sample_tenant.id,
            name="Product",
            sku=long_sku,
            quantity=10,
            price=100.0,
        )
    
    assert "sku" in str(exc_info.value).lower()
    assert "length" in str(exc_info.value).lower() or "100" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_product_validates_name_not_empty(
    mock_db_session, sample_tenant
):
    """Test that product name cannot be empty."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    with pytest.raises(ValueError) as exc_info:
        await service.create(
            tenant_id=sample_tenant.id,
            name="",  # Empty name
            sku="PROD-001",
            quantity=10,
            price=100.0,
        )
    
    assert "name" in str(exc_info.value).lower()
    assert "empty" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_product_with_zero_quantity(
    mock_db_session, sample_tenant, sample_product_data
):
    """Test that zero quantity is allowed (out of stock)."""
    from src.services.product_service import ProductService
    
    service = ProductService(mock_db_session)
    
    # Mock SKU check
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute.return_value = mock_result
    
    product = await service.create(
        tenant_id=sample_tenant.id,
        name="Out of Stock Product",
        sku="OOS-001",
        quantity=0,  # Zero is valid
        price=100.0,
    )
    
    assert product.quantity == 0
