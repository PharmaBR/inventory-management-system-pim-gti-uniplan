"""
Contract tests for Category API endpoints.

These tests define the expected behavior of the Category API without
implementation details. They serve as a specification and will initially fail.

Phase: 4 - Categories CRUD
Session: 1 - Test Planning
Coverage Target: 80%
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


# =============================================================================
# CREATE Category - POST /api/v1/categories
# =============================================================================

@pytest.mark.asyncio
async def test_create_category_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: POST /api/v1/categories creates a new category.
    
    Given: Valid category data
    When: POST request is made
    Then: Returns 201 with created category
    """
    response = await async_client.post(
        "/api/v1/categories",
        json={
            "name": "Electronics",
            "description": "Electronic products and devices",
            "status": "active",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["name"] == "Electronics"
    assert data["description"] == "Electronic products and devices"
    assert data["status"] == "active"
    assert data["parent_id"] is None
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_subcategory_with_parent(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can create a subcategory with parent_id.
    
    Given: An existing parent category
    When: POST with parent_id
    Then: Creates subcategory linked to parent
    """
    # Create parent
    parent_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    parent_id = parent_response.json()["id"]
    
    # Create subcategory
    response = await async_client.post(
        "/api/v1/categories",
        json={
            "name": "Smartphones",
            "parent_id": parent_id,
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == "Smartphones"
    assert data["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_create_category_duplicate_name_fails(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Cannot create categories with duplicate names (per tenant).
    
    Given: A category already exists
    When: POST with same name
    Then: Returns 409 Conflict
    """
    # Create first category
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    
    # Attempt duplicate
    response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    
    assert response.status_code == 409
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_category_missing_name_fails(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Name is required.
    
    Given: No name provided
    When: POST request
    Then: Returns 422 Validation Error
    """
    response = await async_client.post(
        "/api/v1/categories",
        json={"description": "No name provided"},
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_category_requires_authentication(
    async_client: AsyncClient,
):
    """
    Contract: Authentication required for creation.
    
    Given: No authentication
    When: POST request
    Then: Returns 401 Unauthorized
    """
    response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
    )
    
    assert response.status_code == 401


# =============================================================================
# GET Category by ID - GET /api/v1/categories/{id}
# =============================================================================

@pytest.mark.asyncio
async def test_get_category_by_id_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: GET /api/v1/categories/{id} returns category details.
    
    Given: A category exists
    When: GET by ID
    Then: Returns 200 with category data
    """
    # Create category
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Test category"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    # Get category
    response = await async_client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == category_id
    assert data["name"] == "Electronics"
    assert data["description"] == "Test category"


@pytest.mark.asyncio
async def test_get_category_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Returns 404 for non-existent category.
    
    Given: Category doesn't exist
    When: GET by invalid ID
    Then: Returns 404
    """
    fake_id = str(uuid4())
    response = await async_client.get(
        f"/api/v1/categories/{fake_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_category_from_another_tenant_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    auth_headers_tenant2: dict,
):
    """
    Contract: Cannot access categories from other tenants.
    
    Given: Category belongs to tenant A
    When: Tenant B tries to access
    Then: Returns 404 (not exposing existence)
    """
    # Create as tenant A
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    # Try to access as tenant B
    response = await async_client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers_tenant2,
    )
    
    assert response.status_code == 404


# =============================================================================
# LIST Categories - GET /api/v1/categories
# =============================================================================

@pytest.mark.asyncio
async def test_list_categories_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: GET /api/v1/categories returns paginated list.
    
    Given: Multiple categories exist
    When: GET list
    Then: Returns paginated categories
    """
    # Create test categories
    for i in range(3):
        await async_client.post(
            "/api/v1/categories",
            json={"name": f"Category {i}"},
            headers=auth_headers,
        )
    
    response = await async_client.get(
        "/api/v1/categories",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    
    assert len(data["items"]) >= 3
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_list_categories_with_pagination(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Supports pagination parameters.
    
    Given: Multiple categories
    When: GET with page and page_size
    Then: Returns correct page
    """
    # Create 5 categories
    for i in range(5):
        await async_client.post(
            "/api/v1/categories",
            json={"name": f"Category {i}"},
            headers=auth_headers,
        )
    
    response = await async_client.get(
        "/api/v1/categories?page=1&page_size=2",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_categories_filter_by_name(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can filter by name (partial match).
    
    Given: Categories with different names
    When: GET with name filter
    Then: Returns only matching categories
    """
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Furniture"},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/categories?name=Elec",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) >= 1
    assert any("Elec" in item["name"] for item in data["items"])


@pytest.mark.asyncio
async def test_list_categories_filter_by_status(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can filter by status.
    
    Given: Active and inactive categories
    When: GET with status filter
    Then: Returns only categories with that status
    """
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Active Category", "status": "active"},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Inactive Category", "status": "inactive"},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/categories?status=active",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert all(item["status"] == "active" for item in data["items"])


@pytest.mark.asyncio
async def test_list_categories_filter_by_parent(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can filter by parent_id.
    
    Given: Categories with and without parents
    When: GET with parent_id filter
    Then: Returns only subcategories of that parent
    """
    # Create parent
    parent_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    parent_id = parent_response.json()["id"]
    
    # Create subcategories
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Smartphones", "parent_id": parent_id},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Laptops", "parent_id": parent_id},
        headers=auth_headers,
    )
    
    # Create unrelated category
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Furniture"},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        f"/api/v1/categories?parent_id={parent_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) >= 2
    assert all(item["parent_id"] == parent_id for item in data["items"])


@pytest.mark.asyncio
async def test_list_root_categories_only(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can filter root categories (parent_id is null).
    
    Given: Mix of root and subcategories
    When: GET with parent_id=null
    Then: Returns only root categories
    """
    # Create root
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    
    # Create root with subcategory
    parent_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Furniture"},
        headers=auth_headers,
    )
    parent_id = parent_response.json()["id"]
    
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Chairs", "parent_id": parent_id},
        headers=auth_headers,
    )
    
    response = await async_client.get(
        "/api/v1/categories?root_only=true",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert all(item["parent_id"] is None for item in data["items"])


# =============================================================================
# UPDATE Category - PUT /api/v1/categories/{id}
# =============================================================================

@pytest.mark.asyncio
async def test_update_category_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: PUT /api/v1/categories/{id} updates category.
    
    Given: Category exists
    When: PUT with new data
    Then: Returns 200 with updated category
    """
    # Create
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Old description"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    # Update
    response = await async_client.put(
        f"/api/v1/categories/{category_id}",
        json={
            "name": "Consumer Electronics",
            "description": "New description",
            "status": "inactive",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Consumer Electronics"
    assert data["description"] == "New description"
    assert data["status"] == "inactive"


@pytest.mark.asyncio
async def test_update_category_partial_update(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Can update individual fields.
    
    Given: Category exists
    When: PUT with partial data
    Then: Updates only specified fields
    """
    # Create
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Original"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    # Update only description
    response = await async_client.put(
        f"/api/v1/categories/{category_id}",
        json={"description": "Updated description"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Electronics"  # Unchanged
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_category_duplicate_name_fails(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Cannot update to duplicate name.
    
    Given: Two categories exist
    When: Update one to match other's name
    Then: Returns 409
    """
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Furniture"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    response = await async_client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Electronics"},  # Duplicate
        headers=auth_headers,
    )
    
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_category_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Returns 404 for non-existent category.
    
    Given: Category doesn't exist
    When: PUT to invalid ID
    Then: Returns 404
    """
    fake_id = str(uuid4())
    response = await async_client.put(
        f"/api/v1/categories/{fake_id}",
        json={"name": "Updated"},
        headers=auth_headers,
    )
    
    assert response.status_code == 404


# =============================================================================
# DELETE Category - DELETE /api/v1/categories/{id}
# =============================================================================

@pytest.mark.asyncio
async def test_delete_category_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: DELETE /api/v1/categories/{id} removes category.
    
    Given: Category exists
    When: DELETE request
    Then: Returns 204 and category is deleted
    """
    # Create
    create_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]
    
    # Delete
    response = await async_client.delete(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 204
    
    # Verify deleted
    get_response = await async_client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Returns 404 when deleting non-existent category.
    
    Given: Category doesn't exist
    When: DELETE invalid ID
    Then: Returns 404
    """
    fake_id = str(uuid4())
    response = await async_client.delete(
        f"/api/v1/categories/{fake_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_with_products_fails(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Cannot delete category with associated products.
    
    Given: Category has products
    When: DELETE attempt
    Then: Returns 409 Conflict
    """
    # Create category
    cat_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    category_id = cat_response.json()["id"]
    
    # Create product in this category
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "sku": "PHONE-001",
            "quantity": 10,
            "price": 999.99,
            "category_id": category_id,
        },
        headers=auth_headers,
    )
    
    # Try to delete category
    response = await async_client.delete(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 409
    assert "products" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_parent_category_cascades_to_children(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: Deleting parent updates children's parent_id to null.
    
    Given: Parent with subcategories
    When: DELETE parent
    Then: Subcategories become root categories
    """
    # Create parent
    parent_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=auth_headers,
    )
    parent_id = parent_response.json()["id"]
    
    # Create subcategory
    child_response = await async_client.post(
        "/api/v1/categories",
        json={"name": "Smartphones", "parent_id": parent_id},
        headers=auth_headers,
    )
    child_id = child_response.json()["id"]
    
    # Delete parent
    await async_client.delete(
        f"/api/v1/categories/{parent_id}",
        headers=auth_headers,
    )
    
    # Check child is now root
    child_check = await async_client.get(
        f"/api/v1/categories/{child_id}",
        headers=auth_headers,
    )
    
    assert child_check.status_code == 200
    assert child_check.json()["parent_id"] is None


# =============================================================================
# Summary Statistics
# =============================================================================

@pytest.mark.asyncio
async def test_category_count_metadata(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """
    Contract: List response includes accurate count metadata.
    
    Given: Known number of categories
    When: GET list
    Then: Metadata matches actual count
    """
    # Create exactly 5 categories
    for i in range(5):
        await async_client.post(
            "/api/v1/categories",
            json={"name": f"Category {i}"},
            headers=auth_headers,
        )
    
    response = await async_client.get(
        "/api/v1/categories",
        headers=auth_headers,
    )
    
    data = response.json()
    assert data["total"] >= 5
    assert data["total_pages"] >= 1
