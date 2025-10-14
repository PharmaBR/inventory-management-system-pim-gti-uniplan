"""
Contract tests for GET /products endpoint (list products).

Tests the product listing endpoint with pagination, filtering, sorting,
and tenant isolation. Following TDD methodology - tests written FIRST.

Task: T042 - Contract test: GET /products
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_products_success(
    async_client: AsyncClient,
    auth_headers: dict,
    tenant_id: str,
):
    """Test successful product listing with default pagination."""
    # Create some test products first
    products_data = [
        {
            "name": "Product A",
            "sku": "PROD-A-001",
            "quantity": 10,
            "price": 100.00,
            "description": "First product",
        },
        {
            "name": "Product B",
            "sku": "PROD-B-002",
            "quantity": 20,
            "price": 200.00,
            "description": "Second product",
        },
        {
            "name": "Product C",
            "sku": "PROD-C-003",
            "quantity": 30,
            "price": 300.00,
            "description": "Third product",
        },
    ]
    
    for product_data in products_data:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers,
        )
    
    # List products
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    
    # Check data
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 50  # Default page size
    
    # Check first product structure
    first_product = data["items"][0]
    assert "id" in first_product
    assert "name" in first_product
    assert "sku" in first_product
    assert "quantity" in first_product
    assert "price" in first_product
    assert "tenant_id" in first_product
    assert first_product["tenant_id"] == tenant_id


@pytest.mark.asyncio
async def test_list_products_requires_auth(async_client: AsyncClient):
    """Test that listing products requires authentication."""
    response = await async_client.get("/api/v1/products")
    
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_list_products_pagination(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test product listing with custom pagination."""
    # Create 5 test products
    for i in range(5):
        await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "sku": f"PROD-{i:03d}",
                "quantity": i * 10,
                "price": i * 100.0,
            },
            headers=auth_headers,
        )
    
    # Get first page with page_size=2
    response = await async_client.get(
        "/api/v1/products",
        params={"page": 1, "page_size": 2},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["pages"] == 3  # ceil(5/2) = 3
    
    # Get second page
    response = await async_client.get(
        "/api/v1/products",
        params={"page": 2, "page_size": 2},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) == 2
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_products_filter_by_name(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by name (case-insensitive partial match)."""
    # Create test products
    await async_client.post(
        "/api/v1/products",
        json={"name": "Laptop Dell", "sku": "LAPTOP-001", "quantity": 5, "price": 1500.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Mouse Logitech", "sku": "MOUSE-001", "quantity": 10, "price": 50.0},
        headers=auth_headers,
    )
    
    # Filter by "laptop"
    response = await async_client.get(
        "/api/v1/products",
        params={"name": "laptop"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Laptop Dell"


@pytest.mark.asyncio
async def test_list_products_filter_by_sku(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by SKU (case-insensitive partial match)."""
    await async_client.post(
        "/api/v1/products",
        json={"name": "Product 1", "sku": "ABC-123", "quantity": 5, "price": 100.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Product 2", "sku": "XYZ-456", "quantity": 10, "price": 200.0},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/products",
        params={"sku": "ABC"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "ABC-123"


@pytest.mark.asyncio
async def test_list_products_filter_by_category(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test filtering products by category_id."""
    # Create product with category
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Categorized Product",
            "sku": "CAT-001",
            "quantity": 5,
            "price": 100.0,
            "category_id": category_id,
        },
        headers=auth_headers,
    )
    
    # Create product without category
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Uncategorized Product",
            "sku": "UNCAT-001",
            "quantity": 10,
            "price": 200.0,
        },
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/products",
        params={"category_id": category_id},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["category_id"] == category_id


@pytest.mark.asyncio
async def test_list_products_sort_by_name_asc(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test sorting products by name ascending."""
    # Create products in random order
    await async_client.post(
        "/api/v1/products",
        json={"name": "Zebra Product", "sku": "Z-001", "quantity": 1, "price": 10.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Alpha Product", "sku": "A-001", "quantity": 2, "price": 20.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Beta Product", "sku": "B-001", "quantity": 3, "price": 30.0},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/products",
        params={"sort_by": "name", "sort_order": "asc"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    names = [item["name"] for item in data["items"]]
    assert names == ["Alpha Product", "Beta Product", "Zebra Product"]


@pytest.mark.asyncio
async def test_list_products_sort_by_price_desc(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test sorting products by price descending."""
    await async_client.post(
        "/api/v1/products",
        json={"name": "Cheap", "sku": "CHEAP-001", "quantity": 1, "price": 10.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Expensive", "sku": "EXP-001", "quantity": 1, "price": 1000.0},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/products",
        json={"name": "Medium", "sku": "MED-001", "quantity": 1, "price": 100.0},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/products",
        params={"sort_by": "price", "sort_order": "desc"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    prices = [item["price"] for item in data["items"]]
    assert prices == [1000.0, 100.0, 10.0]


@pytest.mark.asyncio
async def test_list_products_tenant_isolation(
    async_client: AsyncClient,
    auth_headers_tenant1: dict,
    auth_headers_tenant2: dict,
):
    """Test that products are isolated by tenant."""
    # Create product in tenant 1
    await async_client.post(
        "/api/v1/products",
        json={"name": "Tenant 1 Product", "sku": "T1-001", "quantity": 10, "price": 100.0},
        headers=auth_headers_tenant1,
    )
    
    # Create product in tenant 2
    await async_client.post(
        "/api/v1/products",
        json={"name": "Tenant 2 Product", "sku": "T2-001", "quantity": 20, "price": 200.0},
        headers=auth_headers_tenant2,
    )
    
    # List products for tenant 1
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers_tenant1,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Tenant 1 Product"
    
    # List products for tenant 2
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers_tenant2,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Tenant 2 Product"


@pytest.mark.asyncio
async def test_list_products_empty_list(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test listing products when there are no products."""
    response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["pages"] == 0


@pytest.mark.asyncio
async def test_list_products_invalid_page(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test listing products with invalid page number."""
    response = await async_client.get(
        "/api/v1/products",
        params={"page": 0},  # Page should be >= 1
        headers=auth_headers,
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_list_products_invalid_page_size(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test listing products with invalid page_size."""
    response = await async_client.get(
        "/api/v1/products",
        params={"page_size": 0},  # Page size should be >= 1
        headers=auth_headers,
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()
    
    # Test page_size too large
    response = await async_client.get(
        "/api/v1/products",
        params={"page_size": 101},  # Max page size is 100
        headers=auth_headers,
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()
