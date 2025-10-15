"""
Integration tests for complete Product CRUD flow.

Tests the entire workflow from product creation through deletion,
verifying that all components work together correctly.
Following TDD methodology - tests written FIRST.

Task: T048 - Integration test: CRUD flow
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_product_lifecycle(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test complete product lifecycle: Create -> Read -> Update -> Delete."""
    
    # 1. CREATE: Create a new product
    create_data = {
        "name": "Lifecycle Product",
        "sku": "LIFECYCLE-001",
        "quantity": 100,
        "price": 299.99,
        "description": "Product for lifecycle testing",
        "category_id": category_id,
        "custom_fields": {
            "brand": "TestBrand",
            "warranty_months": 24,
        },
    }
    
    create_response = await async_client.post(
        "/api/v1/products",
        json=create_data,
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    created_product = create_response.json()
    product_id = created_product["id"]
    
    assert created_product["name"] == "Lifecycle Product"
    assert created_product["sku"] == "LIFECYCLE-001"
    assert created_product["status"] == "active"
    
    # 2. READ: Get the product by ID
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_response.status_code == 200
    retrieved_product = get_response.json()
    assert retrieved_product["id"] == product_id
    assert retrieved_product["name"] == "Lifecycle Product"
    assert retrieved_product["custom_fields"]["brand"] == "TestBrand"
    
    # 3. LIST: Verify product appears in list
    list_response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert list_response.status_code == 200
    product_list = list_response.json()
    assert any(p["id"] == product_id for p in product_list["items"])
    
    # 4. UPDATE: Update the product
    update_data = {
        "name": "Updated Lifecycle Product",
        "quantity": 150,
        "price": 349.99,
        "description": "Updated description",
    }
    
    update_response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json=update_data,
        headers=auth_headers,
    )
    
    assert update_response.status_code == 200
    updated_product = update_response.json()
    assert updated_product["name"] == "Updated Lifecycle Product"
    assert updated_product["quantity"] == 150
    assert updated_product["price"] == 349.99
    assert updated_product["sku"] == "LIFECYCLE-001"  # SKU unchanged
    
    # 5. READ AGAIN: Verify changes persisted
    verify_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert verify_response.status_code == 200
    verified_product = verify_response.json()
    assert verified_product["name"] == "Updated Lifecycle Product"
    assert verified_product["quantity"] == 150
    
    # 6. DELETE: Soft delete the product
    delete_response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert delete_response.status_code == 204
    
    # 7. VERIFY DELETION: Product should not be accessible
    get_deleted_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_deleted_response.status_code == 404
    
    # 8. LIST AGAIN: Product should not appear in list
    final_list_response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert final_list_response.status_code == 200
    final_list = final_list_response.json()
    assert not any(p["id"] == product_id for p in final_list["items"])


@pytest.mark.asyncio
async def test_multi_product_workflow(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test working with multiple products in various operations."""
    
    # Create multiple products
    products = []
    for i in range(5):
        response = await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "sku": f"MULTI-{i:03d}",
                "quantity": (i + 1) * 10,
                "price": (i + 1) * 50.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        products.append(response.json())
    
    # List all products
    list_response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 5
    
    # Filter by name
    filter_response = await async_client.get(
        "/api/v1/products",
        params={"name": "Product 2"},
        headers=auth_headers,
    )
    
    assert filter_response.status_code == 200
    filtered = filter_response.json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["name"] == "Product 2"
    
    # Sort by price descending
    sort_response = await async_client.get(
        "/api/v1/products",
        params={"sort_by": "price", "sort_order": "desc"},
        headers=auth_headers,
    )
    
    assert sort_response.status_code == 200
    sorted_items = sort_response.json()["items"]
    prices = [item["price"] for item in sorted_items[:5]]
    assert prices == sorted(prices, reverse=True)
    
    # Update one product
    product_to_update = products[2]
    update_response = await async_client.put(
        f"/api/v1/products/{product_to_update['id']}",
        json={"quantity": 999},
        headers=auth_headers,
    )
    
    assert update_response.status_code == 200
    assert update_response.json()["quantity"] == 999
    
    # Delete two products
    for product in products[:2]:
        delete_response = await async_client.delete(
            f"/api/v1/products/{product['id']}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204
    
    # Verify remaining products
    final_list = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    remaining_ids = [p["id"] for p in final_list.json()["items"]]
    assert products[0]["id"] not in remaining_ids
    assert products[1]["id"] not in remaining_ids
    assert products[2]["id"] in remaining_ids


@pytest.mark.asyncio
async def test_product_category_relationship(
    async_client: AsyncClient,
    auth_headers: dict,
    category_id: str,
):
    """Test product-category relationship throughout CRUD operations."""
    
    # Create product with category
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Categorized Product",
            "sku": "CAT-REL-001",
            "quantity": 10,
            "price": 100.0,
            "category_id": category_id,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    assert create_response.json()["category_id"] == category_id
    
    # Verify category in GET
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["category_id"] == category_id
    
    # Filter by category
    filter_response = await async_client.get(
        "/api/v1/products",
        params={"category_id": category_id},
        headers=auth_headers,
    )
    
    assert filter_response.status_code == 200
    assert any(p["id"] == product_id for p in filter_response.json()["items"])
    
    # Update to remove category
    update_response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": None},
        headers=auth_headers,
    )
    
    assert update_response.status_code == 200
    assert update_response.json()["category_id"] is None


@pytest.mark.asyncio
async def test_product_custom_fields_workflow(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test custom_fields throughout product lifecycle."""
    
    # Create with custom fields
    initial_custom_fields = {
        "color": "red",
        "size": "M",
        "material": "cotton",
    }
    
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Custom Fields Product",
            "sku": "CUSTOM-001",
            "quantity": 10,
            "price": 50.0,
            "custom_fields": initial_custom_fields,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    assert create_response.json()["custom_fields"] == initial_custom_fields
    
    # Update custom fields
    updated_custom_fields = {
        "color": "blue",
        "size": "L",
        "material": "polyester",
        "brand": "NewBrand",  # Add new field
    }
    
    update_response = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"custom_fields": updated_custom_fields},
        headers=auth_headers,
    )
    
    assert update_response.status_code == 200
    assert update_response.json()["custom_fields"]["color"] == "blue"
    assert update_response.json()["custom_fields"]["brand"] == "NewBrand"
    
    # Verify persistence
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["custom_fields"] == updated_custom_fields


@pytest.mark.asyncio
async def test_concurrent_product_operations(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test handling concurrent operations on different products."""
    
    import asyncio
    
    # Create multiple products concurrently
    async def create_product(index: int):
        return await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Concurrent Product {index}",
                "sku": f"CONCURRENT-{index:03d}",
                "quantity": index * 10,
                "price": index * 100.0,
            },
            headers=auth_headers,
        )
    
    # Create 10 products concurrently
    create_tasks = [create_product(i) for i in range(10)]
    responses = await asyncio.gather(*create_tasks)
    
    # All should succeed
    assert all(r.status_code == 201 for r in responses)
    product_ids = [r.json()["id"] for r in responses]
    
    # Update them concurrently
    async def update_product(product_id: str, new_quantity: int):
        return await async_client.put(
            f"/api/v1/products/{product_id}",
            json={"quantity": new_quantity},
            headers=auth_headers,
        )
    
    update_tasks = [update_product(pid, i * 100) for i, pid in enumerate(product_ids)]
    update_responses = await asyncio.gather(*update_tasks)
    
    # All should succeed
    assert all(r.status_code == 200 for r in update_responses)


@pytest.mark.asyncio
async def test_error_recovery_workflow(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test system behavior with errors and recovery."""
    
    # Create valid product
    valid_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Valid Product",
            "sku": "VALID-001",
            "quantity": 10,
            "price": 100.0,
        },
        headers=auth_headers,
    )
    
    assert valid_response.status_code == 201
    product_id = valid_response.json()["id"]
    
    # Try invalid update (negative quantity)
    invalid_update = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"quantity": -10},
        headers=auth_headers,
    )
    
    assert invalid_update.status_code == 422
    
    # Verify product unchanged
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["quantity"] == 10  # Original value
    
    # Make valid update
    valid_update = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"quantity": 20},
        headers=auth_headers,
    )
    
    assert valid_update.status_code == 200
    assert valid_update.json()["quantity"] == 20


@pytest.mark.asyncio
async def test_pagination_workflow(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test pagination through large product list."""
    
    # Create 25 products
    for i in range(25):
        await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Page Product {i}",
                "sku": f"PAGE-{i:03d}",
                "quantity": 10,
                "price": 100.0,
            },
            headers=auth_headers,
        )
    
    # Get first page
    page1 = await async_client.get(
        "/api/v1/products",
        params={"page": 1, "page_size": 10},
        headers=auth_headers,
    )
    
    assert page1.status_code == 200
    page1_data = page1.json()
    assert len(page1_data["items"]) == 10
    assert page1_data["page"] == 1
    assert page1_data["total"] >= 25
    
    # Get second page
    page2 = await async_client.get(
        "/api/v1/products",
        params={"page": 2, "page_size": 10},
        headers=auth_headers,
    )
    
    assert page2.status_code == 200
    page2_data = page2.json()
    assert len(page2_data["items"]) == 10
    assert page2_data["page"] == 2
    
    # Verify no duplicate items between pages
    page1_ids = {p["id"] for p in page1_data["items"]}
    page2_ids = {p["id"] for p in page2_data["items"]}
    assert page1_ids.isdisjoint(page2_ids)
