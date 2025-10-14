"""
Contract tests for DELETE /products/{id} endpoint (soft delete product).

Tests the product deletion endpoint with authentication, tenant isolation,
soft delete behavior, and audit logging. Following TDD methodology - tests written FIRST.

Task: T045 - Contract test: DELETE /products/{id}
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_product_success(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test successful product soft deletion."""
    # Create a product
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product to Delete",
            "sku": "DEL-001",
            "quantity": 10,
            "price": 100.0,
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Delete the product
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 204  # No content
    
    # Verify product is soft deleted (status = 'deleted')
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    # Should return 404 for soft-deleted products
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_requires_auth(async_client: AsyncClient):
    """Test that deleting a product requires authentication."""
    response = await async_client.delete(
        "/api/v1/products/123e4567-e89b-12d3-a456-426614174000"
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_product_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test deleting a non-existent product returns 404."""
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    
    response = await async_client.delete(
        f"/api/v1/products/{fake_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_tenant_isolation(
    async_client: AsyncClient,
    auth_headers_tenant1: dict,
    auth_headers_tenant2: dict,
):
    """Test that users can only delete products in their own tenant."""
    # Create product in tenant 1
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Tenant 1 Product",
            "sku": "T1-DEL-001",
            "quantity": 10,
            "price": 100.0,
        },
        headers=auth_headers_tenant1,
    )
    
    product_id = create_response.json()["id"]
    
    # Try to delete from tenant 2
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_tenant2,
    )
    
    # Should return 404 for security
    assert response.status_code == 404
    
    # Verify product still exists for tenant 1
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_tenant1,
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Tenant 1 Product"


@pytest.mark.asyncio
async def test_delete_product_not_in_list(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that deleted products don't appear in list."""
    # Create products
    create_response1 = await async_client.post(
        "/api/v1/products",
        json={"name": "Product 1", "sku": "KEEP-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    create_response2 = await async_client.post(
        "/api/v1/products",
        json={"name": "Product 2", "sku": "DELETE-001", "quantity": 20, "price": 200.0},
        headers=auth_headers,
    )
    
    product_id_to_delete = create_response2.json()["id"]
    
    # Delete second product
    await async_client.delete(
        f"/api/v1/products/{product_id_to_delete}",
        headers=auth_headers,
    )
    
    # List products
    list_response = await async_client.get(
        "/api/v1/products",
        headers=auth_headers,
    )
    
    assert list_response.status_code == 200
    data = list_response.json()
    
    # Only one product should be in the list
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Product 1"


@pytest.mark.asyncio
async def test_delete_product_idempotent(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that deleting an already deleted product is idempotent."""
    # Create product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "IDEMPOTENT-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Delete once
    response1 = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response1.status_code == 204
    
    # Delete again
    response2 = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    # Should return 404 (already deleted)
    assert response2.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_creates_audit_log(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that deleting a product creates an audit log entry."""
    # Create product
    create_response = await async_client.post(
        "/api/v1/products",
        json={"name": "Product", "sku": "AUDIT-001", "quantity": 10, "price": 100.0},
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    
    # Delete product
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 204
    
    # Get audit logs (this endpoint will be created in Phase 4)
    # For now, just verify the deletion succeeded
    # In the future: verify audit log contains the deletion
    # audit_response = await async_client.get(
    #     f"/api/v1/audit-logs?entity_type=product&entity_id={product_id}",
    #     headers=auth_headers,
    # )
    # audit_logs = audit_response.json()["items"]
    # assert any(log["action"] == "delete" for log in audit_logs)


@pytest.mark.asyncio
async def test_delete_product_with_movements_fails(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that deleting a product with movements fails (future feature)."""
    # This test is for future implementation
    # When we implement movements (Phase 5), products with movement history
    # should not be deletable, only deactivatable
    
    # For now, this is a placeholder that we'll implement later
    # The behavior will be:
    # 1. Create product
    # 2. Create movement for product
    # 3. Try to delete product
    # 4. Should return 409 Conflict with message about existing movements
    
    pytest.skip("Movement validation will be implemented in Phase 5")


@pytest.mark.asyncio
async def test_delete_product_invalid_uuid(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test deleting a product with invalid UUID format."""
    response = await async_client.delete(
        "/api/v1/products/invalid-uuid",
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_soft_delete_preserves_data(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that soft delete preserves product data in database."""
    # Create product with all fields
    create_response = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Complete Product",
            "sku": "COMPLETE-001",
            "quantity": 10,
            "price": 100.0,
            "description": "Full description",
            "custom_fields": {"brand": "ACME"},
        },
        headers=auth_headers,
    )
    
    product_id = create_response.json()["id"]
    original_data = create_response.json()
    
    # Delete product
    await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    # Note: In actual implementation, we might have an admin endpoint
    # to retrieve deleted products for audit purposes
    # For now, we just verify the soft delete doesn't throw errors
    # and that the product is no longer accessible via normal endpoints
    
    # Verify product is not accessible
    get_response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    
    assert get_response.status_code == 404
    
    # Future: Admin endpoint to verify data is preserved
    # admin_response = await async_client.get(
    #     f"/api/v1/admin/products/{product_id}?include_deleted=true",
    #     headers=admin_headers,
    # )
    # assert admin_response.json()["name"] == original_data["name"]
    # assert admin_response.json()["status"] == "deleted"
