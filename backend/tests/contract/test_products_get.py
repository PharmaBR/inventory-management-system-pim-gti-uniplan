"""
Contract tests for GET /products/{id} endpoint (get product by ID).

Tests the product retrieval endpoint with authentication, tenant isolation,
and error handling. Following TDD methodology - tests written FIRST.

Task: T043 - Contract test: GET /products/{id}
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_product_success(
    async_client: AsyncClient,
    auth_headers: dict,
    tenant_id: str,
):
    """Test successful product retrieval by ID."""
    # Create a product
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Test Product",
            "sku": "TEST-001",
            "quantity": 10,
            "price": 100.50,
            "description": "A test product",
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Get the product
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all fields
    assert data["id"] == product_id
    assert data["name"] == "Test Product"
    assert data["sku"] == "TEST-001"
    assert data["quantity"] == 10
    assert data["price"] == 100.50
    assert data["description"] == "A test product"
    assert data["tenant_id"] == tenant_id
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_product_requires_auth(async_client: AsyncClient):
    """Test that getting a product requires authentication."""
    response = await async_client.get("/api/v1/products/123e4567-e89b-12d3-a456-426614174000")
    
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_product_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test getting a non-existent product returns 404."""
    # Use a valid UUID that doesn't exist
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    
    response = await async_client.get(
        f"/api/v1/products/{fake_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_product_invalid_uuid(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test getting a product with invalid UUID format."""
    response = await async_client.get(
        "/api/v1/products/invalid-uuid",
        headers=auth_headers,
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_product_tenant_isolation(
    async_client: AsyncClient,
    auth_headers_tenant1: dict,
    auth_headers_tenant2: dict,
):
    """Test that users can only get products from their own tenant."""
    # Create product in tenant 1
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Tenant 1 Product",
            "sku": "T1-PROD-001",
            "quantity": 10,
            "price": 100.0,
        },
        headers=auth_headers_tenant1,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Try to get product from tenant 2
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_tenant2,
    )
    
    # Should return 404 (not found) for security reasons
    # Don't reveal that the product exists in another tenant
    assert response.status_code == 404
    
    # Verify tenant 1 can still get it
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_tenant1,
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Tenant 1 Product"


@pytest.mark.asyncio
async def test_get_product_with_category(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test getting a product with category information."""
    # Create product with category
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Categorized Product",
            "sku": "CAT-001",
            "quantity": 5,
            "price": 50.0,
            "category_id": category_id,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Get the product
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["category_id"] == category_id
    # Optionally check if category details are included
    # This depends on whether we use relationships or separate calls


@pytest.mark.asyncio
async def test_get_product_with_custom_fields(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test getting a product with custom fields."""
    custom_fields = {
        "brand": "ACME",
        "warranty_months": 12,
        "specifications": {
            "weight": "2.5kg",
            "dimensions": "30x20x10cm",
        }
    }
    
    # Create product with custom fields
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product with Custom Fields",
            "sku": "CUSTOM-001",
            "quantity": 3,
            "price": 299.99,
            "custom_fields": custom_fields,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Get the product
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["custom_fields"] == custom_fields
    assert data["custom_fields"]["brand"] == "ACME"
    assert data["custom_fields"]["specifications"]["weight"] == "2.5kg"
