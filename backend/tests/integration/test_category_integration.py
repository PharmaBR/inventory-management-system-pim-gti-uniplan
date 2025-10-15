"""
Integration tests for Categories API.

Tests real database integration and complex workflows.
Focus on hierarchical relationships, cascades, and multi-step scenarios.

Phase: 4 - Categories CRUD
Session: 3 - Validation & Testing
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.category import Category
from src.db.models.product import Product


@pytest.mark.asyncio
class TestCategoryHierarchy:
    """Test hierarchical category operations."""
    
    async def test_create_multi_level_hierarchy(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating 3-level category hierarchy."""
        # Create root category
        root_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        assert root_response.status_code == 201
        root_id = root_response.json()["id"]
        
        # Create level 2
        level2_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Computers", "parent_id": root_id},
            headers=auth_headers,
        )
        assert level2_response.status_code == 201
        level2_id = level2_response.json()["id"]
        
        # Create level 3
        level3_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Laptops", "parent_id": level2_id},
            headers=auth_headers,
        )
        assert level3_response.status_code == 201
        level3_data = level3_response.json()
        
        # Verify hierarchy
        assert level3_data["parent_id"] == level2_id
        assert level2_response.json()["parent_id"] == root_id
        assert root_response.json()["parent_id"] is None
    
    async def test_reorganize_category_hierarchy(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test moving category to different parent."""
        # Create categories
        cat1_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        cat1_id = cat1_response.json()["id"]
        
        cat2_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Furniture"},
            headers=auth_headers,
        )
        cat2_id = cat2_response.json()["id"]
        
        child_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Accessories", "parent_id": cat1_id},
            headers=auth_headers,
        )
        child_id = child_response.json()["id"]
        
        # Verify initial parent
        assert child_response.json()["parent_id"] == cat1_id
        
        # Move to different parent
        update_response = await async_client.put(
            f"/api/v1/categories/{child_id}",
            json={"parent_id": cat2_id},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["parent_id"] == cat2_id
    
    async def test_delete_middle_level_category_updates_children(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting middle category makes children root categories."""
        # Create 3-level hierarchy
        root_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        root_id = root_response.json()["id"]
        
        middle_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Computers", "parent_id": root_id},
            headers=auth_headers,
        )
        middle_id = middle_response.json()["id"]
        
        child1_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Laptops", "parent_id": middle_id},
            headers=auth_headers,
        )
        child1_id = child1_response.json()["id"]
        
        child2_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Desktops", "parent_id": middle_id},
            headers=auth_headers,
        )
        child2_id = child2_response.json()["id"]
        
        # Delete middle level
        delete_response = await async_client.delete(
            f"/api/v1/categories/{middle_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204
        
        # Verify children are now root categories
        child1_get = await async_client.get(
            f"/api/v1/categories/{child1_id}",
            headers=auth_headers,
        )
        assert child1_get.json()["parent_id"] is None
        
        child2_get = await async_client.get(
            f"/api/v1/categories/{child2_id}",
            headers=auth_headers,
        )
        assert child2_get.json()["parent_id"] is None


@pytest.mark.asyncio
class TestCategoryProductIntegration:
    """Test category and product relationships."""
    
    async def test_cannot_delete_category_with_products(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test constraint preventing category deletion when products exist."""
        # Create category
        cat_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        category_id = cat_response.json()["id"]
        
        # Create product in category
        product_response = await async_client.post(
            "/api/v1/products",
            json={
                "name": "Laptop",
                "sku": "LAP-001",
                "quantity": 10,
                "price": 999.99,
                "category_id": category_id,
            },
            headers=auth_headers,
        )
        assert product_response.status_code == 201
        
        # Try to delete category
        delete_response = await async_client.delete(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 409
        assert "product" in delete_response.json()["detail"].lower()
    
    async def test_can_delete_category_after_removing_products(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test category can be deleted after moving products to another category."""
        # Create two categories
        cat1_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        category1_id = cat1_response.json()["id"]
        
        cat2_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Furniture"},
            headers=auth_headers,
        )
        category2_id = cat2_response.json()["id"]
        
        # Create product in category 1
        product_response = await async_client.post(
            "/api/v1/products",
            json={
                "name": "Laptop",
                "sku": "LAP-004",
                "quantity": 10,
                "price": 999.99,
                "category_id": category1_id,
            },
            headers=auth_headers,
        )
        product_id = product_response.json()["id"]
        
        # Move product to category 2
        product_update = await async_client.put(
            f"/api/v1/products/{product_id}",
            json={"category_id": category2_id},
            headers=auth_headers,
        )
        assert product_update.status_code == 200
        
        # Now category 1 can be deleted (no products)
        category_delete = await async_client.delete(
            f"/api/v1/categories/{category1_id}",
            headers=auth_headers,
        )
        assert category_delete.status_code == 204


@pytest.mark.asyncio
class TestCategoryFiltering:
    """Test complex filtering scenarios."""
    
    async def test_filter_by_multiple_criteria(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test filtering by name, status, and parent simultaneously."""
        # Create parent
        parent_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics"},
            headers=auth_headers,
        )
        parent_id = parent_response.json()["id"]
        
        # Create active child with "Smart" in name
        await async_client.post(
            "/api/v1/categories",
            json={"name": "Smartphones", "parent_id": parent_id, "status": "active"},
            headers=auth_headers,
        )
        
        # Create inactive child with "Smart" in name
        await async_client.post(
            "/api/v1/categories",
            json={"name": "Smart TVs", "parent_id": parent_id, "status": "inactive"},
            headers=auth_headers,
        )
        
        # Create active child without "Smart" in name
        await async_client.post(
            "/api/v1/categories",
            json={"name": "Laptops", "parent_id": parent_id, "status": "active"},
            headers=auth_headers,
        )
        
        # Filter by name=Smart, status=active, parent_id
        response = await async_client.get(
            f"/api/v1/categories?name=Smart&status=active&parent_id={parent_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return only Smartphones
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Smartphones"
        assert data["items"][0]["status"] == "active"
        assert data["items"][0]["parent_id"] == parent_id
    
    async def test_pagination_with_sorting(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test pagination works correctly with custom sorting."""
        # Create categories with predictable names
        for i in range(1, 11):
            await async_client.post(
                "/api/v1/categories",
                json={"name": f"Category {i:02d}"},
                headers=auth_headers,
            )
        
        # Get first page (sorted by name ascending)
        page1 = await async_client.get(
            "/api/v1/categories?page=1&page_size=5&sort_by=name&sort_order=asc",
            headers=auth_headers,
        )
        page1_data = page1.json()
        
        # Get second page
        page2 = await async_client.get(
            "/api/v1/categories?page=2&page_size=5&sort_by=name&sort_order=asc",
            headers=auth_headers,
        )
        page2_data = page2.json()
        
        # Verify pagination
        assert page1_data["total"] == 10
        assert page1_data["page"] == 1
        assert page1_data["page_size"] == 5
        assert page1_data["total_pages"] == 2
        assert len(page1_data["items"]) == 5
        
        assert page2_data["page"] == 2
        assert len(page2_data["items"]) == 5
        
        # Verify sorting
        assert page1_data["items"][0]["name"] == "Category 01"
        assert page2_data["items"][0]["name"] == "Category 06"


@pytest.mark.asyncio
class TestCategoryUpdateScenarios:
    """Test complex update scenarios."""
    
    async def test_update_category_to_inactive_with_active_products(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test updating category status doesn't affect product relationship."""
        # Create category
        cat_response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics", "status": "active"},
            headers=auth_headers,
        )
        category_id = cat_response.json()["id"]
        
        # Create product
        await async_client.post(
            "/api/v1/products",
            json={
                "name": "Laptop",
                "sku": "LAP-003",
                "quantity": 10,
                "price": 999.99,
                "category_id": category_id,
            },
            headers=auth_headers,
        )
        
        # Update category to inactive
        update_response = await async_client.put(
            f"/api/v1/categories/{category_id}",
            json={"status": "inactive"},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "inactive"
    
    async def test_partial_update_preserves_other_fields(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test partial update only changes specified fields."""
        # Create category with all fields
        create_response = await async_client.post(
            "/api/v1/categories",
            json={
                "name": "Electronics",
                "description": "Electronic items",
                "status": "active",
            },
            headers=auth_headers,
        )
        category_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Partial update (only name)
        update_response = await async_client.put(
            f"/api/v1/categories/{category_id}",
            json={"name": "Consumer Electronics"},
            headers=auth_headers,
        )
        updated_data = update_response.json()
        
        # Verify only name changed
        assert updated_data["name"] == "Consumer Electronics"
        assert updated_data["description"] == original_data["description"]
        assert updated_data["status"] == original_data["status"]
        assert updated_data["parent_id"] == original_data["parent_id"]


@pytest.mark.asyncio
class TestCategoryEdgeCases:
    """Test edge cases and boundary conditions."""
    
    async def test_category_name_with_special_characters(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating category with special characters in name."""
        response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics & Gadgets (2024)"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Electronics & Gadgets (2024)"
    
    async def test_category_with_very_long_description(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating category with long description."""
        long_desc = "A" * 500
        response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Test Category", "description": long_desc},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert len(response.json()["description"]) == 500
    
    async def test_list_empty_categories(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing when no categories exist."""
        # Don't create any categories
        response = await async_client.get(
            "/api/v1/categories",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["total_pages"] == 0
