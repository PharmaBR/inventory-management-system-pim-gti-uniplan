"""
Integration tests for product list filtering and sorting.

Tests real database queries with various filter combinations.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_products_with_name_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by name."""
    # Create test products
    products = [
        {"sku": "LAPTOP-001", "name": "Laptop Dell", "quantity": 10, "price": 1000},
        {"sku": "MOUSE-001", "name": "Mouse Logitech", "quantity": 50, "price": 25},
        {"sku": "KEYBOARD-001", "name": "Keyboard Mechanical", "quantity": 30, "price": 150},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by name "Laptop"
    response = await async_client.get(
        "/api/v1/products?name=Laptop",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Laptop Dell"


@pytest.mark.asyncio
async def test_list_products_with_sku_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by SKU."""
    # Create test products
    products = [
        {"sku": "LAPTOP-001", "name": "Laptop", "quantity": 10, "price": 1000},
        {"sku": "LAPTOP-002", "name": "Laptop Pro", "quantity": 5, "price": 2000},
        {"sku": "MOUSE-001", "name": "Mouse", "quantity": 50, "price": 25},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by SKU containing "LAPTOP"
    response = await async_client.get(
        "/api/v1/products?sku=LAPTOP",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_list_products_with_category_filter(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test filtering products by category."""
    # Create products with and without category
    products = [
        {"sku": "CAT-001", "name": "With Category", "quantity": 10, "price": 100, "category_id": category_id},
        {"sku": "NOCAT-001", "name": "Without Category", "quantity": 10, "price": 100},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by category
    response = await async_client.get(
        f"/api/v1/products?category_id={category_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "CAT-001"


@pytest.mark.asyncio
async def test_list_products_with_quantity_filters(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by quantity range."""
    # Create products with different quantities
    products = [
        {"sku": "LOW-001", "name": "Low Stock", "quantity": 5, "price": 100},
        {"sku": "MED-001", "name": "Medium Stock", "quantity": 50, "price": 100},
        {"sku": "HIGH-001", "name": "High Stock", "quantity": 500, "price": 100},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by min_quantity
    response = await async_client.get(
        "/api/v1/products?min_quantity=50",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # MED and HIGH
    
    # Filter by max_quantity
    response = await async_client.get(
        "/api/v1/products?max_quantity=50",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # LOW and MED


@pytest.mark.asyncio
async def test_list_products_with_price_filters(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by price range."""
    # Create products with different prices
    products = [
        {"sku": "CHEAP-001", "name": "Cheap", "quantity": 10, "price": 10.00},
        {"sku": "MEDIUM-001", "name": "Medium", "quantity": 10, "price": 100.00},
        {"sku": "EXPENSIVE-001", "name": "Expensive", "quantity": 10, "price": 1000.00},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by min_price
    response = await async_client.get(
        "/api/v1/products?min_price=100",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # MEDIUM and EXPENSIVE
    
    # Filter by max_price
    response = await async_client.get(
        "/api/v1/products?max_price=100",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # CHEAP and MEDIUM


@pytest.mark.asyncio
async def test_list_products_with_status_filter(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test filtering products by status."""
    # Create product
    response = await async_client.post(
        "/api/v1/products",
        json={"sku": "STATUS-001", "name": "Product", "quantity": 10, "price": 100},
        headers=auth_headers
    )
    product_id = response.json()["id"]
    
    # Delete product
    await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers
    )
    
    # Filter by status=active (should not show deleted)
    response = await async_client.get(
        "/api/v1/products?status=active",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "active" for item in data["items"])


@pytest.mark.asyncio
async def test_list_products_sorting_by_name_asc(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test sorting products by name ascending."""
    # Create products
    products = [
        {"sku": "C-001", "name": "Charlie", "quantity": 10, "price": 100},
        {"sku": "A-001", "name": "Alpha", "quantity": 10, "price": 100},
        {"sku": "B-001", "name": "Bravo", "quantity": 10, "price": 100},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Sort by name ascending
    response = await async_client.get(
        "/api/v1/products?sort_by=name&sort_order=asc",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    names = [item["name"] for item in data["items"]]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_list_products_sorting_by_price_desc(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test sorting products by price descending."""
    # Create products
    products = [
        {"sku": "LOW-001", "name": "Low", "quantity": 10, "price": 10},
        {"sku": "HIGH-001", "name": "High", "quantity": 10, "price": 1000},
        {"sku": "MED-001", "name": "Medium", "quantity": 10, "price": 100},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Sort by price descending
    response = await async_client.get(
        "/api/v1/products?sort_by=price&sort_order=desc",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    prices = [item["price"] for item in data["items"]]
    assert prices == sorted(prices, reverse=True)


@pytest.mark.asyncio
async def test_list_products_pagination(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test pagination of product list."""
    # Create 15 products
    for i in range(15):
        await async_client.post(
            "/api/v1/products",
            json={"sku": f"PROD-{i:03d}", "name": f"Product {i}", "quantity": 10, "price": 100},
            headers=auth_headers
        )
    
    # Get page 1 with page_size=5
    response = await async_client.get(
        "/api/v1/products?page=1&page_size=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["pages"] == 3
    
    # Get page 2
    response = await async_client.get(
        "/api/v1/products?page=2&page_size=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_products_combined_filters(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test combining multiple filters."""
    # Create various products
    products = [
        {"sku": "LAPTOP-001", "name": "Laptop Dell", "quantity": 50, "price": 1000, "category_id": category_id},
        {"sku": "LAPTOP-002", "name": "Laptop HP", "quantity": 5, "price": 1500, "category_id": category_id},
        {"sku": "MOUSE-001", "name": "Mouse Logitech", "quantity": 100, "price": 25},
    ]
    
    for product_data in products:
        await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
    
    # Filter by name, category, and min_quantity
    response = await async_client.get(
        f"/api/v1/products?name=Laptop&category_id={category_id}&min_quantity=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "LAPTOP-001"
