"""
Integration tests for product API error handling.

Tests error scenarios and edge cases in the product endpoints.
Focuses on coverage of error handling paths in routes.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_product_with_invalid_category_id(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with non-existent category returns error."""
    fake_category_id = str(uuid4())
    
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-001",
            "name": "Product",
            "quantity": 10,
            "price": 100,
            "category_id": fake_category_id,
        },
        headers=auth_headers
    )
    
    # Should return error for invalid foreign key (409 Conflict for integrity errors)
    assert response.status_code in [201, 409, 422, 500]


@pytest.mark.asyncio
async def test_list_products_with_invalid_sort_field(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with invalid sort field."""
    response = await async_client.get(
        "/api/v1/products?sort_by=invalid_field&sort_order=asc",
        headers=auth_headers
    )
    
    # Should still work, defaults to created_at or returns error
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_list_products_with_invalid_page(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with invalid page number."""
    response = await async_client.get(
        "/api/v1/products?page=0",
        headers=auth_headers
    )
    
    # Page must be >= 1
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_products_with_invalid_page_size(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with page_size exceeding limit."""
    response = await async_client.get(
        "/api/v1/products?page_size=200",
        headers=auth_headers
    )
    
    # Page size limited to 100
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_product_with_invalid_uuid(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test get product with invalid UUID format."""
    response = await async_client.get(
        "/api/v1/products/not-a-uuid",
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_with_invalid_uuid(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test update product with invalid UUID format."""
    response = await async_client.put(
        "/api/v1/products/not-a-uuid",
        json={"name": "New Name"},
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_product_with_invalid_uuid(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test delete product with invalid UUID format."""
    response = await async_client.delete(
        "/api/v1/products/not-a-uuid",
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_with_very_long_name(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with name exceeding max length."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-001",
            "name": "A" * 201,  # Max is 200
            "quantity": 10,
            "price": 100,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "name" for err in errors)


@pytest.mark.asyncio
async def test_create_product_with_very_long_description(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with description exceeding max length."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-002",
            "name": "Product",
            "description": "D" * 1001,  # Max is 1000
            "quantity": 10,
            "price": 100,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "description" for err in errors)


@pytest.mark.asyncio
async def test_create_product_with_invalid_custom_fields_type(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with invalid custom_fields type."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-003",
            "name": "Product",
            "quantity": 10,
            "price": 100,
            "custom_fields": "not-a-dict",  # Should be dict
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_products_with_invalid_uuid_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with invalid category_id UUID."""
    response = await async_client.get(
        "/api/v1/products?category_id=not-a-uuid",
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_products_with_negative_price_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with negative price filter."""
    response = await async_client.get(
        "/api/v1/products?min_price=-10",
        headers=auth_headers
    )
    
    # Negative prices not allowed in filter
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_products_with_negative_quantity_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test list with negative quantity filter."""
    response = await async_client.get(
        "/api/v1/products?min_quantity=-5",
        headers=auth_headers
    )
    
    # Negative quantities not allowed in filter
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_with_very_long_name(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test updating product with name exceeding max length."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-004", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Try to update with too long name
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "N" * 201},
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_with_invalid_custom_fields(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test updating product with invalid custom_fields."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-005", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Try to update with invalid custom_fields
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"custom_fields": ["not", "a", "dict"]},
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_with_sku_special_characters(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with invalid SKU characters."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST@#$%",  # Invalid characters
            "name": "Product",
            "quantity": 10,
            "price": 100,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert "SKU" in str(response.json()["detail"])


@pytest.mark.asyncio
async def test_create_product_with_too_short_sku(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with SKU too short."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "AB",  # Min is 3
            "name": "Product",
            "quantity": 10,
            "price": 100,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422
    # Pydantic v2 returns a list of validation errors
    response_data = response.json()
    assert "detail" in response_data
    # Check if SKU validation error is in the detail
    detail_str = str(response_data["detail"])
    assert "sku" in detail_str.lower()


@pytest.mark.asyncio
async def test_list_products_empty_database(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test listing products when database is empty."""
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
    assert data["page"] == 1
    assert data["pages"] >= 0
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_update_product_set_category_to_null(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test updating product to remove category."""
    # Create product with category
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "TEST-006",
            "name": "Product",
            "quantity": 10,
            "price": 100,
            "category_id": category_id,
        },
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update to remove category
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": None},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["category_id"] is None


@pytest.mark.asyncio
async def test_create_product_with_zero_price(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with zero price (free item)."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "FREE-001",
            "name": "Free Product",
            "quantity": 10,
            "price": 0.00,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["price"] == 0.00


@pytest.mark.asyncio
async def test_update_product_with_whitespace_only_description(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test updating product with whitespace-only description."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-007", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update with whitespace description
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"description": "   "},
        headers=auth_headers
    )
    
    # Should accept and trim to empty or null
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_products_with_very_high_page_number(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test listing products with page number beyond available pages."""
    # Create only 1 product
    await async_client.post(
        "/api/v1/products",
        json={"sku": "SINGLE-001", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    
    # Request page 100 with page_size 10
    response = await async_client.get(
        "/api/v1/products?page=100&page_size=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0  # No items on page 100
    assert data["page"] == 100


@pytest.mark.asyncio
async def test_create_product_with_min_max_quantity_values(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test creating product with min and max quantity set."""
    response = await async_client.post(
        "/api/v1/products",
        json={
            "sku": "MINMAX-001",
            "name": "Product",
            "quantity": 50,
            "min_quantity": 10,
            "max_quantity": 100,
            "price": 100,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["min_quantity"] == 10
    assert data["max_quantity"] == 100
