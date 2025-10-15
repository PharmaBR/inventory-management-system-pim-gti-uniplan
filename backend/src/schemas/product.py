"""
Pydantic schemas for Product API requests and responses.

Provides validation and serialization for product CRUD operations.
Following TDD methodology - schemas created to satisfy test contracts.

Tasks: T052, T053, T054
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)

from .base import BaseSchema, IdentifiedSchema


class ProductBase(BaseSchema):
    """Base product schema with common fields."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Product name",
        examples=["Laptop Dell Inspiron 15"],
    )
    sku: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Stock Keeping Unit - unique identifier per tenant",
        examples=["LAPTOP-DELL-001"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed product description",
    )
    quantity: int = Field(
        ...,
        ge=0,
        description="Current stock quantity (non-negative)",
        examples=[100],
    )
    min_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum stock threshold for alerts (optional)",
        examples=[10],
    )
    max_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum stock capacity (optional)",
        examples=[1000],
    )
    price: Decimal = Field(
        ...,
        ge=0,
        description="Product price (non-negative, 2 decimal places)",
        examples=[1499.99],
    )
    category_id: Optional[UUID] = Field(
        None,
        description="Category UUID (optional)",
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom JSONB fields for tenant-specific data",
        examples=[{"brand": "Dell", "warranty_months": 12}],
    )
    
    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Validate that name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Product name cannot be empty")
        return v.strip()
    
    @field_validator('sku')
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        """Normalize SKU to uppercase and trim whitespace."""
        if not v or not v.strip():
            raise ValueError("SKU cannot be empty")
        
        sku = v.strip().upper()
        
        # Validate length after normalization
        if len(sku) < 3:
            raise ValueError("SKU must be at least 3 characters long")
        if len(sku) > 100:
            raise ValueError("SKU must not exceed 100 characters")
        
        # Validate allowed characters (alphanumeric and -, _, .)
        import re
        if not re.match(r'^[A-Z0-9\-_.]+$', sku):
            raise ValueError(
                "SKU can only contain alphanumeric characters, hyphens, underscores, and periods"
            )
        
        return sku
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace."""
        if v:
            return v.strip() if v.strip() else None
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price_positive(cls, v: Decimal) -> Decimal:
        """Validate that price is non-negative."""
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_non_negative(cls, v: int) -> int:
        """Validate that quantity is non-negative."""
        if v < 0:
            raise ValueError("Quantity must be non-negative")
        return v


class ProductCreate(ProductBase):
    """
    Schema for creating a new product.
    
    Task: T052 - ProductCreate schema
    
    All fields from ProductBase are required except:
    - description (optional)
    - category_id (optional)
    - custom_fields (optional)
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop Dell Inspiron 15",
                "sku": "LAPTOP-DELL-001",
                "description": "15.6\" Full HD, Intel i5, 8GB RAM, 256GB SSD",
                "quantity": 50,
                "price": 1499.99,
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "custom_fields": {
                    "brand": "Dell",
                    "warranty_months": 12,
                    "color": "Silver",
                },
            }
        }
    )


class ProductUpdate(BaseSchema):
    """
    Schema for updating an existing product.
    
    Task: T053 - ProductUpdate schema
    
    All fields are optional - partial updates are supported.
    Only provided fields will be updated.
    """
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Product name",
    )
    sku: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Stock Keeping Unit",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Product description",
    )
    quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Stock quantity",
    )
    price: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Product price",
    )
    category_id: Optional[UUID] = Field(
        None,
        description="Category UUID",
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom JSONB fields",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity": 45,
                "price": 1399.99,
                "custom_fields": {
                    "brand": "Dell",
                    "warranty_months": 24,
                    "on_sale": True,
                },
            }
        }
    )
    
    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that name is not empty if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Product name cannot be empty")
            return v.strip()
        return v
    
    @field_validator('sku')
    @classmethod
    def normalize_sku(cls, v: Optional[str]) -> Optional[str]:
        """Normalize SKU to uppercase and trim whitespace if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("SKU cannot be empty")
            
            sku = v.strip().upper()
            
            if len(sku) < 3:
                raise ValueError("SKU must be at least 3 characters long")
            if len(sku) > 100:
                raise ValueError("SKU must not exceed 100 characters")
            
            import re
            if not re.match(r'^[A-Z0-9\-_.]+$', sku):
                raise ValueError(
                    "SKU can only contain alphanumeric characters, hyphens, underscores, and periods"
                )
            
            return sku
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace if provided."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that price is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError("Price must be non-negative")
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_non_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate that quantity is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError("Quantity must be non-negative")
        return v
    
    @model_validator(mode='after')
    def validate_at_least_one_field(self) -> 'ProductUpdate':
        """Validate that at least one field is provided for update."""
        # Check if at least one field was explicitly set (even if set to None)
        if len(self.model_fields_set) == 0:
            raise ValueError("At least one field must be provided for update")
        return self


class ProductResponse(IdentifiedSchema):
    """
    Schema for product API responses.
    
    Task: T054 - ProductResponse schema
    
    Includes all product fields plus metadata:
    - id (UUID)
    - tenant_id (UUID)
    - status (active/inactive/deleted)
    - created_at (datetime)
    - updated_at (datetime)
    """
    
    tenant_id: UUID = Field(
        ...,
        description="Tenant UUID - products are isolated by tenant",
    )
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Stock Keeping Unit")
    description: Optional[str] = Field(None, description="Product description")
    quantity: int = Field(..., description="Current stock quantity")
    min_quantity: Optional[int] = Field(None, description="Minimum stock quantity")
    max_quantity: Optional[int] = Field(None, description="Maximum stock quantity")
    price: Decimal = Field(..., description="Product price")
    category_id: Optional[UUID] = Field(None, description="Category UUID")
    custom_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom JSONB fields",
    )
    status: str = Field(
        ...,
        description="Product status (active/inactive/deleted)",
        examples=["active"],
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: lambda v: float(v)},
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "987fcdeb-51a2-43d7-9e8f-123456789abc",
                "name": "Laptop Dell Inspiron 15",
                "sku": "LAPTOP-DELL-001",
                "description": "15.6\" Full HD, Intel i5, 8GB RAM, 256GB SSD",
                "quantity": 50,
                "price": 1499.99,
                "category_id": "456e7890-e89b-12d3-a456-426614174111",
                "custom_fields": {
                    "brand": "Dell",
                    "warranty_months": 12,
                },
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }
    )


class ProductListResponse(BaseSchema):
    """
    Schema for paginated product list responses.
    
    Used by GET /products endpoint with pagination, filtering, and sorting.
    """
    
    items: list[ProductResponse] = Field(
        ...,
        description="List of products for current page",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of products matching filters",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)",
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "tenant_id": "987fcdeb-51a2-43d7-9e8f-123456789abc",
                        "name": "Laptop Dell Inspiron 15",
                        "sku": "LAPTOP-DELL-001",
                        "quantity": 50,
                        "price": 1499.99,
                        "status": "active",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 50,
                "pages": 3,
            }
        }
    )


# Query parameter schemas for filtering and sorting
class ProductFilterParams(BaseSchema):
    """Query parameters for filtering products."""
    
    name: Optional[str] = Field(
        None,
        description="Filter by name (case-insensitive partial match)",
    )
    sku: Optional[str] = Field(
        None,
        description="Filter by SKU (case-insensitive partial match)",
    )
    category_id: Optional[UUID] = Field(
        None,
        description="Filter by category UUID",
    )
    status: Optional[str] = Field(
        None,
        description="Filter by status (active/inactive)",
    )
    min_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Filter by minimum quantity",
    )
    max_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Filter by maximum quantity",
    )
    min_price: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Filter by minimum price",
    )
    max_price: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Filter by maximum price",
    )


class ProductSortParams(BaseSchema):
    """Query parameters for sorting products."""
    
    sort_by: Optional[str] = Field(
        "created_at",
        description="Sort field (name/sku/quantity/price/created_at/updated_at)",
        examples=["name", "price", "created_at"],
    )
    sort_order: Optional[str] = Field(
        "desc",
        description="Sort order (asc/desc)",
        examples=["asc", "desc"],
    )
    
    @field_validator('sort_by')
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        """Validate that sort field is allowed."""
        allowed_fields = {'name', 'sku', 'quantity', 'price', 'created_at', 'updated_at'}
        if v not in allowed_fields:
            raise ValueError(
                f"Invalid sort field. Must be one of: {', '.join(allowed_fields)}"
            )
        return v
    
    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate that sort order is asc or desc."""
        if v.lower() not in {'asc', 'desc'}:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v.lower()
