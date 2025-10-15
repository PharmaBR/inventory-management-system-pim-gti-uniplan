"""
Unit tests to boost coverage to 80%.

Targets specific uncovered lines in services, utils, and schemas.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from src.services.product import ProductService
from src.schemas.product import ProductUpdate
from src.utils.validators import generate_sku
from src.db.models.product import Product


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.add = Mock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def tenant_id():
    """Fixture for tenant ID."""
    return uuid4()


# =============================================================================
# ProductService.update() - Coverage for validation paths
# =============================================================================

@pytest.mark.asyncio
async def test_update_with_description_whitespace(mock_db, tenant_id):
    """Test update trims description with only whitespace."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Product Name",
        quantity=10,
        price=100,
        status="active",
        description="  ",  # Only whitespace
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    data = ProductUpdate(description="  Clean Description  ")
    
    result = await service.update(product_id, tenant_id, data)
    
    # Should trim description
    assert result.description == "Clean Description"


@pytest.mark.asyncio
async def test_update_integrity_error_triggers_rollback(mock_db, tenant_id):
    """Test that IntegrityError in update triggers rollback."""
    service = ProductService(mock_db)
    
    product_id = uuid4()
    existing_product = Product(
        id=product_id,
        tenant_id=tenant_id,
        sku="SKU-001",
        name="Product Name",
        quantity=10,
        price=100,
        status="active",
    )
    
    # Mock get
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = existing_product
    mock_db.execute.return_value = mock_result
    
    # Mock commit to raise IntegrityError
    mock_db.commit = AsyncMock(side_effect=IntegrityError("test", "test", "test"))
    
    data = ProductUpdate(name="Updated Name")
    
    with pytest.raises(IntegrityError):
        await service.update(product_id, tenant_id, data)
    
    # Verify rollback was called
    mock_db.rollback.assert_called_once()


# =============================================================================
# generate_sku() - Coverage for edge cases
# =============================================================================

@pytest.mark.asyncio
async def test_generate_sku_single_word_short(tenant_id):
    """Test SKU generation with single short word."""
    sku = await generate_sku("AB", tenant_id)
    assert sku == "AB"


@pytest.mark.asyncio
async def test_generate_sku_single_word_long(tenant_id):
    """Test SKU generation with single long word uses first 6 chars."""
    sku = await generate_sku("VERYLONGPRODUCTNAME", tenant_id)
    assert sku == "VERYLO"


@pytest.mark.asyncio
async def test_generate_sku_with_special_chars_only(tenant_id):
    """Test SKU generation with only special characters."""
    sku = await generate_sku("@#$%^&", tenant_id)
    assert sku == "PROD"  # Falls back to PROD


@pytest.mark.asyncio
async def test_generate_sku_with_duplicate_needs_suffix(tenant_id):
    """Test SKU generation adds suffix when base exists."""
    existing = ["AT"]  # "AB Test" -> "AT" (initials)
    sku = await generate_sku("AB Test", tenant_id, existing_skus=existing)
    assert sku == "AT-001"  # Should add numeric suffix


@pytest.mark.asyncio
async def test_generate_sku_with_multiple_duplicates(tenant_id):
    """Test SKU generation increments suffix for multiple duplicates."""
    existing = ["PRODUC", "PRODUC-001", "PRODUC-002"]  # "Product" -> "PRODUC" (first 6 chars)
    sku = await generate_sku("Product", tenant_id, existing_skus=existing)
    assert sku == "PRODUC-003"


@pytest.mark.asyncio
async def test_generate_sku_fallback_to_random(tenant_id):
    """Test SKU generation falls back to random when many duplicates."""
    # Create 1000 duplicates to force random fallback
    existing = ["PRODUC"] + [f"PRODUC-{i:03d}" for i in range(1, 1000)]
    sku = await generate_sku("Product", tenant_id, existing_skus=existing)
    
    # Should have PRODUC- prefix and 4 digits
    assert sku.startswith("PRODUC-")
    assert len(sku) == 11  # PRODUC-XXXX
    assert sku[-4:].isdigit()


# =============================================================================
# ProductUpdate schema - Coverage for validators
# =============================================================================

def test_product_update_empty_name_validation():
    """Test ProductUpdate validates empty name."""
    
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(name="")
    
    assert "name" in str(exc.value).lower()


def test_product_update_whitespace_only_name_validation():
    """Test ProductUpdate validates whitespace-only name."""
    
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(name="     ")
    
    assert "name" in str(exc.value).lower()


def test_product_update_negative_quantity_validation():
    """Test ProductUpdate validates negative quantity."""
    
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(quantity=-10)
    
    assert "quantity" in str(exc.value).lower()


def test_product_update_negative_price_validation():
    """Test ProductUpdate validates negative price."""
    
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(price=-50.0)
    
    assert "price" in str(exc.value).lower()


def test_product_update_zero_values_allowed():
    """Test ProductUpdate allows zero for quantity and price."""
    data = ProductUpdate(quantity=0, price=0.0)
    assert data.quantity == 0
    assert data.price == 0.0
