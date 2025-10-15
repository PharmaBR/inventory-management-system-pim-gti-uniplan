"""
Integration tests for product update and delete operations.

Tests real database update logic and soft delete functionality.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_product_name_validation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that update validates name cannot be empty."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-001", "name": "Original Name", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Try to update with empty name
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": ""},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    # detail is a list of validation errors
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "name" for err in errors)


@pytest.mark.asyncio
async def test_update_product_description_trim(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that update trims whitespace from description."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-002", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update with whitespace description
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"description": "  New Description  "},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["description"] == "New Description"


@pytest.mark.asyncio
async def test_update_product_quantity_validation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that update validates quantity is non-negative."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-003", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Try to update with negative quantity
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"quantity": -5},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "quantity" for err in errors)


@pytest.mark.asyncio
async def test_update_product_price_validation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that update validates price is non-negative."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-004", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Try to update with negative price
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"price": -50.00},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "price" for err in errors)


@pytest.mark.asyncio
async def test_update_product_sku_normalization(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that SKU is normalized during update."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "TEST-005", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update with lowercase SKU
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"sku": "new-sku-001"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["sku"] == "NEW-SKU-001"


@pytest.mark.asyncio
async def test_update_product_sku_duplicate_validation(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that update prevents duplicate SKU."""
    # Create two products
    await async_client.post(
        "/api/v1/products",
        json={"sku": "EXISTING-SKU", "name": "Product 1", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "OTHER-SKU", "name": "Product 2", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product2_id = response.json()["id"]
    
    # Try to update Product 2 to use Product 1's SKU
    response = await async_client.put(
        f"/api/v1/products/{product2_id}",
        json={"sku": "EXISTING-SKU"},
        headers=auth_headers
    )
    
    assert response.status_code == 409
    assert "SKU" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_product_can_keep_same_sku(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that product can keep its own SKU during update."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "SAME-SKU", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update with same SKU
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"sku": "SAME-SKU", "name": "Updated Name"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["sku"] == "SAME-SKU"
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_product_multiple_fields(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test updating multiple fields at once."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "MULTI-001", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Update multiple fields
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "New description",
            "quantity": 50,
            "price": 150.00,
            "category_id": category_id,
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["description"] == "New description"
    assert data["quantity"] == 50
    assert data["price"] == 150.00
    assert data["category_id"] == category_id


@pytest.mark.asyncio
async def test_soft_delete_product_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test successful soft delete."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "DELETE-001", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Soft delete
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify product is not in list
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(item["id"] != product_id for item in data["items"])


@pytest.mark.asyncio
async def test_soft_delete_product_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test soft delete of non-existent product."""
    from uuid import uuid4
    
    fake_id = str(uuid4())
    
    response = await async_client.delete(
        f"/api/v1/products/{fake_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_soft_delete_twice_returns_404(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that deleting an already deleted product returns 404."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "DELETE-002", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # First delete
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Second delete should fail
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_deleted_product_returns_404(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that getting a deleted product returns 404."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "DELETE-003", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Delete product
    await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    
    # Try to get deleted product
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_deleted_product_returns_404(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that updating a deleted product returns 404."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "DELETE-004", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Delete product
    await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    
    # Try to update deleted product
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "New Name"},
        headers=auth_headers
    )
    
    assert response.status_code == 404
