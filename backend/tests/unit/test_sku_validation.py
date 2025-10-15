"""
Unit tests for SKU validation logic.

Tests the SKU validation business rules in isolation.
Following TDD methodology - tests written FIRST.

Task: T047 - Unit test: SKU validation
"""

import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_sku_is_unique_per_tenant():
    """Test that SKU uniqueness is enforced per tenant."""
    from src.utils.validators import validate_sku_unique
    
    tenant_id = uuid4()
    sku = "TEST-001"
    
    # Mock database query that returns existing product
    existing_product = {"sku": "TEST-001", "tenant_id": tenant_id}
    
    # Should raise error when SKU exists in same tenant
    with pytest.raises(ValueError) as exc_info:
        await validate_sku_unique(sku, tenant_id, existing_product=existing_product)
    
    assert "already exists" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_sku_can_be_same_in_different_tenants():
    """Test that same SKU can exist in different tenants."""
    from src.utils.validators import validate_sku_unique
    
    tenant_id_1 = uuid4()
    tenant_id_2 = uuid4()
    sku = "SHARED-SKU"
    
    # Existing product in tenant 1
    existing_product = {"sku": "SHARED-SKU", "tenant_id": tenant_id_1}
    
    # Should NOT raise error for same SKU in different tenant
    try:
        await validate_sku_unique(sku, tenant_id_2, existing_product=existing_product)
    except ValueError:
        pytest.fail("SKU should be allowed in different tenant")


@pytest.mark.asyncio
async def test_sku_normalization_uppercase():
    """Test that SKU is normalized to uppercase."""
    from src.utils.validators import normalize_sku
    
    assert normalize_sku("abc-123") == "ABC-123"
    assert normalize_sku("xyz-456") == "XYZ-456"
    assert normalize_sku("MixedCase-789") == "MIXEDCASE-789"


@pytest.mark.asyncio
async def test_sku_normalization_trim_whitespace():
    """Test that SKU whitespace is trimmed."""
    from src.utils.validators import normalize_sku
    
    assert normalize_sku("  ABC-123  ") == "ABC-123"
    assert normalize_sku("\tXYZ-456\n") == "XYZ-456"
    assert normalize_sku("  spaces  ") == "SPACES"


@pytest.mark.asyncio
async def test_sku_validation_max_length():
    """Test that SKU length is limited to 100 characters."""
    from src.utils.validators import validate_sku_format
    
    # Valid length
    valid_sku = "A" * 100
    validate_sku_format(valid_sku)  # Should not raise
    
    # Invalid length
    invalid_sku = "A" * 101
    with pytest.raises(ValueError) as exc_info:
        validate_sku_format(invalid_sku)
    
    assert "length" in str(exc_info.value).lower() or "100" in str(exc_info.value)


@pytest.mark.asyncio
async def test_sku_validation_not_empty():
    """Test that SKU cannot be empty."""
    from src.utils.validators import validate_sku_format
    
    with pytest.raises(ValueError) as exc_info:
        validate_sku_format("")
    
    assert "empty" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
    
    # Whitespace only should also fail
    with pytest.raises(ValueError):
        validate_sku_format("   ")


@pytest.mark.asyncio
async def test_sku_validation_allowed_characters():
    """Test that SKU allows alphanumeric and common separators."""
    from src.utils.validators import validate_sku_format
    
    # Valid SKUs
    valid_skus = [
        "ABC123",
        "ABC-123",
        "ABC_123",
        "ABC.123",
        "ABC-DEF-123",
        "PRODUCT_2024_001",
    ]
    
    for sku in valid_skus:
        validate_sku_format(sku)  # Should not raise
    
    # Invalid SKUs (special characters)
    invalid_skus = [
        "ABC@123",
        "ABC#123",
        "ABC$123",
        "ABC%123",
        "ABC 123",  # Space not allowed
    ]
    
    for sku in invalid_skus:
        with pytest.raises(ValueError) as exc_info:
            validate_sku_format(sku)
        assert "character" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_sku_validation_case_insensitive_uniqueness():
    """Test that SKU uniqueness check is case-insensitive."""
    from src.utils.validators import validate_sku_unique
    
    tenant_id = uuid4()
    
    # Existing product with lowercase SKU
    existing_product = {"sku": "ABC-123", "tenant_id": tenant_id}
    
    # Should detect duplicate even with different case
    with pytest.raises(ValueError):
        await validate_sku_unique("abc-123", tenant_id, existing_product=existing_product)
    
    with pytest.raises(ValueError):
        await validate_sku_unique("AbC-123", tenant_id, existing_product=existing_product)


@pytest.mark.asyncio
async def test_sku_allows_update_same_product():
    """Test that SKU validation allows keeping same SKU when updating."""
    from src.utils.validators import validate_sku_unique
    
    tenant_id = uuid4()
    product_id = uuid4()
    sku = "SAME-SKU"
    
    # Existing product is the same product being updated
    existing_product = {
        "id": product_id,
        "sku": "SAME-SKU",
        "tenant_id": tenant_id,
    }
    
    # Should NOT raise error when updating same product
    try:
        await validate_sku_unique(
            sku,
            tenant_id,
            existing_product=existing_product,
            current_product_id=product_id,
        )
    except ValueError:
        pytest.fail("Should allow keeping same SKU when updating product")


@pytest.mark.asyncio
async def test_sku_prevents_update_to_existing_sku():
    """Test that SKU validation prevents updating to another product's SKU."""
    from src.utils.validators import validate_sku_unique
    
    tenant_id = uuid4()
    product_id_1 = uuid4()
    product_id_2 = uuid4()
    
    # Product 1 already has this SKU
    existing_product = {
        "id": product_id_1,
        "sku": "TAKEN-SKU",
        "tenant_id": tenant_id,
    }
    
    # Product 2 trying to update to Product 1's SKU
    with pytest.raises(ValueError):
        await validate_sku_unique(
            "TAKEN-SKU",
            tenant_id,
            existing_product=existing_product,
            current_product_id=product_id_2,
        )


@pytest.mark.asyncio
async def test_sku_validation_min_length():
    """Test that SKU has minimum length requirement."""
    from src.utils.validators import validate_sku_format
    
    # Valid minimum length (e.g., 3 characters)
    validate_sku_format("ABC")  # Should not raise
    
    # Too short
    with pytest.raises(ValueError) as exc_info:
        validate_sku_format("AB")
    
    assert "length" in str(exc_info.value).lower() or "minimum" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_sku_format_recommendation():
    """Test that SKU follows recommended format patterns."""
    from src.utils.validators import suggest_sku_format
    
    # Should suggest proper format
    suggestions = suggest_sku_format()
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert any("PREFIX-" in s for s in suggestions)


@pytest.mark.asyncio
async def test_sku_auto_generation():
    """Test SKU auto-generation when not provided."""
    from src.utils.validators import generate_sku
    
    tenant_id = uuid4()
    product_name = "Test Product"
    
    # Generate SKU from product name
    sku = await generate_sku(product_name, tenant_id)
    
    assert sku is not None
    assert len(sku) >= 2  # At least 2 characters (e.g., "TP" for "Test Product")
    assert sku.isupper()
    
    # Should be based on product name (either full words or initials)
    # For "Test Product" it could be "TP" (initials) or "TEST-PRODUCT" (full words)
    assert "T" in sku and "P" in sku  # At minimum should have initials


@pytest.mark.asyncio
async def test_sku_generation_handles_duplicates():
    """Test that SKU generation handles duplicates by adding suffix."""
    from src.utils.validators import generate_sku
    
    tenant_id = uuid4()
    product_name = "Duplicate Product"
    
    # First generation
    sku1 = await generate_sku(product_name, tenant_id)
    
    # Second generation should add suffix
    existing_skus = [sku1]
    sku2 = await generate_sku(product_name, tenant_id, existing_skus=existing_skus)
    
    assert sku1 != sku2
    assert sku2.endswith(("-1", "-2", "-001", "-002"))  # Common suffix patterns


@pytest.mark.asyncio
async def test_sku_validation_combined():
    """Test complete SKU validation pipeline."""
    from src.utils.validators import validate_sku
    
    tenant_id = uuid4()
    
    # Valid SKU
    valid_result = await validate_sku(
        "VALID-SKU-123",
        tenant_id,
        existing_product=None,
    )
    
    assert valid_result is True or valid_result == "VALID-SKU-123"
    
    # Invalid format
    with pytest.raises(ValueError):
        await validate_sku("@@@", tenant_id)
    
    # Duplicate SKU
    existing = {"sku": "DUPLICATE", "tenant_id": tenant_id}
    with pytest.raises(ValueError):
        await validate_sku("DUPLICATE", tenant_id, existing_product=existing)
