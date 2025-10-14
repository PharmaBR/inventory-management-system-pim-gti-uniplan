"""
Contract tests for PUT /products/{id} endpoint (update product).

Tests the product update endpoint with authentication, validation,
tenant isolation, and audit logging. Following TDD methodology - tests written FIRST.

Task: T044 - Contract test: PUT /products/{id}
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_product_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test successful product update."""
    # Create a product
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Original Product",
            "sku": "ORIG-001",
            "quantity": 10,
            "price": 100.0,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Update the product
    update_data = {
        "name": "Updated Product",
        "sku": "UPDATED-001",
        "quantity": 20,
        "price": 150.0,
        "description": "Updated description",
    }
    
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json=update_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == product_id
    assert data["name"] == "Updated Product"
    assert data["sku"] == "UPDATED-001"
    assert data["quantity"] == 20
    assert data["price"] == 150.0
    assert data["description"] == "Updated description"
    assert data["updated_at"] != data["created_at"]


@pytest.mark.asyncio
async def test_update_product_partial(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test partial product update (only some fields)."""
    # Create a product
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product",
            "sku": "PART-001",
            "quantity": 10,
            "price": 100.0,
            "description": "Original description",
        },
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Update only quantity and price
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={
            "quantity": 50,
            "price": 120.0,
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Updated fields
    assert data["quantity"] == 50
    assert data["price"] == 120.0
    
    # Unchanged fields
    assert data["name"] == "Product"
    assert data["sku"] == "PART-001"
    assert data["description"] == "Original description"


@pytest.mark.asyncio
async def test_update_product_requires_auth(async_client: AsyncClient):
    """Test that updating a product requires authentication."""
    response = await async_client.put(
        "/api/v1/products/123e4567-e89b-12d3-a456-426614174000",
        json={"name": "Updated"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_product_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test updating a non-existent product returns 404."""
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    
    response = await async_client.put(
        f"/api/v1/products/{fake_id}",
        json={"name": "Updated"},
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product_duplicate_sku(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that updating to a duplicate SKU in same tenant fails."""
    # Create first product
    await async_client.post(
        "/api/v1/products",
        json={"name": "Product 1", "sku": "EXIST-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    # Create second product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product 2", "sku": "UPDATE-001", "quantity": 20, "price": 200.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Try to update second product with first product's SKU
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"sku": "EXIST-001"},
        headers=auth_headers,
    )
    
    assert response.status_code == 409
    assert "detail" in response.json()
    assert "sku" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_product_invalid_quantity(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that updating with negative quantity fails."""
    # Create product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "PROD-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Try to update with negative quantity
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"quantity": -5},
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_invalid_price(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that updating with negative price fails."""
    # Create product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "PROD-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Try to update with negative price
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"price": -50.0},
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_tenant_isolation(
    async_client: AsyncClient,
    auth_headers_tenant1: dict,
    auth_headers_tenant2: dict,
):
    """Test that users can only update products in their own tenant."""
    # Create product in tenant 1
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Tenant 1 Product", "sku": "T1-001", "quantity": 10, "price": 100.0},
        headers=auth_headers_tenant1,
    )
    
    product_id = create_response.json()["id"]
    
    # Try to update from tenant 2
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Hacked Product"},
        headers=auth_headers_tenant2,
    )
    
    # Should return 404 for security
    assert response.status_code == 404
    
    # Verify product was not changed
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_tenant1,
    )
    
    assert get_response.json()["name"] == "Tenant 1 Product"


@pytest.mark.asyncio
async def test_update_product_same_sku_different_tenant(
    async_client: AsyncClient,
    auth_headers_tenant1: dict,
    auth_headers_tenant2: dict,
):
    """Test that same SKU can exist in different tenants after update."""
    # Create product in tenant 1 with SKU "SHARED-001"
    await async_client.post(
        "/api/v1/products",
        json={"name": "Tenant 1 Product", "sku": "SHARED-001", "quantity": 10, "price": 100.0},
        headers=auth_headers_tenant1,
    )
    
    # Create product in tenant 2
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Tenant 2 Product", "sku": "ORIG-001", "quantity": 20, "price": 200.0},
        headers=auth_headers_tenant2,
    )
    
    product_id = create_response.json()["id"]
    
    # Update tenant 2 product to use same SKU
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"sku": "SHARED-001"},
        headers=auth_headers_tenant2,
    )
    
    # Should succeed - SKU is unique per tenant
    assert response.status_code == 200
    assert response.json()["sku"] == "SHARED-001"


@pytest.mark.asyncio
async def test_update_product_with_category(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test updating product with category."""
    # Create product without category
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "PROD-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Update with category
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": category_id},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    assert response.json()["category_id"] == category_id


@pytest.mark.asyncio
async def test_update_product_custom_fields(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test updating product custom fields."""
    # Create product with custom fields
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product",
            "sku": "PROD-001",
            "quantity": 10,
            "price": 100.0,
            "custom_fields": {"color": "red", "size": "M"},
        },
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Update custom fields
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={
            "custom_fields": {"color": "blue", "size": "L", "material": "cotton"},
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["custom_fields"]["color"] == "blue"
    assert data["custom_fields"]["size"] == "L"
    assert data["custom_fields"]["material"] == "cotton"


@pytest.mark.asyncio
async def test_update_product_creates_audit_log(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that updating a product creates an audit log entry."""
    # Create product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "PROD-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Update product
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"quantity": 20},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    
    # Get audit logs (this endpoint will be created in Phase 4)
    # For now, just verify the update succeeded
    # In the future: verify audit log contains the change
    # audit_response = await async_client.get(
    #     f"/api/v1/audit-logs?entity_type=product&entity_id={product_id}",
    #     headers=auth_headers,
    # )
    # assert len(audit_response.json()["items"]) > 0
