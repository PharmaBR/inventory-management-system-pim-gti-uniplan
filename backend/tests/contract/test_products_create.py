"""
Contract tests for POST /products endpoint.

Tests the API contract for product creation, ensuring:
- Request/response format matches specification
- Validation rules are enforced
- Tenant isolation works correctly  
- Authentication is required

Following TDD: These tests are written FIRST and will FAIL until implementation.
"""
import pytest
from fastapi import status
from httpx import AsyncClient


class TestProductCreateContract:
    """Contract tests for POST /products."""
    
    @pytest.mark.asyncio
    async def test_create_product_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        tenant_id: str
    ):
        """Test successful product creation with valid data."""
        # Arrange
        product_data = {
            "sku": "TEST-001",
            "name": "Test Product",
            "description": "A test product description",
            "category_id": None,  # Optional
            "quantity": 100,
            "min_quantity": 10,
            "max_quantity": 1000,
            "price": 99.99,
            "custom_fields": {}  # Optional JSONB
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["sku"] == product_data["sku"]
        assert data["name"] == product_data["name"]
        assert data["description"] == product_data["description"]
        assert data["quantity"] == product_data["quantity"]
        assert data["min_quantity"] == product_data["min_quantity"]
        assert data["max_quantity"] == product_data["max_quantity"]
        assert data["price"] == product_data["price"]
        assert "id" in data
        assert "tenant_id" in data
        assert data["tenant_id"] == tenant_id
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_product_requires_auth(self, async_client: AsyncClient):
        """Test that product creation requires authentication."""
        # Arrange
        product_data = {
            "sku": "TEST-002",
            "name": "Test Product",
            "quantity": 100,
            "price": 99.99
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data
            # No auth headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that duplicate SKU within same tenant is rejected."""
        # Arrange
        product_data = {
            "sku": "DUPLICATE-SKU",
            "name": "First Product",
            "quantity": 50,
            "price": 10.00
        }
        
        # Act - Create first product
        response1 = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Act - Try to create duplicate
        response2 = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "SKU" in response2.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_product_missing_required_fields(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for missing required fields."""
        # Arrange - Missing 'name', 'quantity', 'unit_price'
        product_data = {
            "sku": "TEST-003"
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(err["loc"][-1] == "name" for err in errors)
        assert any(err["loc"][-1] == "quantity" for err in errors)
        assert any(err["loc"][-1] == "price" for err in errors)
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_quantity(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for negative quantity."""
        # Arrange
        product_data = {
            "sku": "TEST-004",
            "name": "Test Product",
            "quantity": -10,  # Invalid
            "price": 99.99
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            err["loc"][-1] == "quantity" and "greater than or equal to 0" in err["msg"]
            for err in errors
        )
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_price(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for negative price."""
        # Arrange
        product_data = {
            "sku": "TEST-005",
            "name": "Test Product",
            "quantity": 100,
            "price": -5.00  # Invalid
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_product_sku_too_long(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for SKU exceeding max length."""
        # Arrange
        product_data = {
            "sku": "A" * 101,  # Max is 100 characters
            "name": "Test Product",
            "quantity": 100,
            "price": 99.99
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_product_with_category(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        category_id: str
    ):
        """Test creating product with valid category."""
        # Arrange
        product_data = {
            "sku": "TEST-006",
            "name": "Categorized Product",
            "category_id": category_id,
            "quantity": 50,
            "price": 25.50
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["category_id"] == category_id
    
    @pytest.mark.asyncio
    async def test_create_product_with_custom_fields(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating product with custom JSONB fields."""
        # Arrange
        product_data = {
            "sku": "TEST-007",
            "name": "Custom Fields Product",
            "quantity": 100,
            "price": 99.99,
            "custom_fields": {
                "color": "blue",
                "size": "L",
                "manufacturer": "ACME Corp"
            }
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["custom_fields"] == product_data["custom_fields"]
    
    @pytest.mark.asyncio
    async def test_create_product_tenant_isolation(
        self,
        async_client: AsyncClient,
        auth_headers_tenant1: dict,
        auth_headers_tenant2: dict
    ):
        """Test that same SKU can exist in different tenants."""
        # Arrange
        product_data = {
            "sku": "SHARED-SKU",
            "name": "Product in Tenant 1",
            "quantity": 100,
            "price": 10.00
        }
        
        # Act - Create in tenant 1
        response1 = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers_tenant1
        )
        
        # Act - Create same SKU in tenant 2
        product_data["name"] = "Product in Tenant 2"
        response2 = await async_client.post(
            "/api/v1/products",
            json=product_data,
            headers=auth_headers_tenant2
        )
        
        # Assert
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response1.json()["tenant_id"] != response2.json()["tenant_id"]
