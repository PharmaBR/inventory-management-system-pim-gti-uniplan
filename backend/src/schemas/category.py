"""
Category schemas for request/response validation.

Handles data validation, serialization, and documentation for Category API.
Uses Pydantic v2 for robust type validation.

Phase: 4 - Categories CRUD
Session: 2 - Implementation
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Request Schemas
# =============================================================================

class CategoryCreate(BaseModel):
    """
    Schema for creating a new category.
    
    Validates:
    - Name is required and non-empty
    - Parent ID is valid UUID if provided
    - Status is valid value
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category name (unique per tenant)",
    )
    description: Optional[str] = Field(
        None,
        description="Optional category description",
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Parent category ID for hierarchical structure",
    )
    status: str = Field(
        default="active",
        pattern="^(active|inactive)$",
        description="Category status",
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean category name."""
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided."""
        if v:
            return v.strip()
        return v


class CategoryUpdate(BaseModel):
    """
    Schema for updating an existing category.
    
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Category name (unique per tenant)",
    )
    description: Optional[str] = Field(
        None,
        description="Category description",
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Parent category ID",
    )
    status: Optional[str] = Field(
        None,
        pattern="^(active|inactive)$",
        description="Category status",
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Category name cannot be empty")
            return v.strip()
        return v
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided."""
        if v:
            return v.strip()
        return v


# =============================================================================
# Response Schemas
# =============================================================================

class CategoryResponse(BaseModel):
    """
    Schema for category response data.
    
    Includes all category fields plus metadata.
    """
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    parent_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    }


class CategoryListResponse(BaseModel):
    """
    Schema for paginated category list response.
    
    Includes pagination metadata.
    """
    items: List[CategoryResponse]
    total: int = Field(..., description="Total number of categories")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "from_attributes": True
    }


# =============================================================================
# Filter Schemas
# =============================================================================

class CategoryFilterParams(BaseModel):
    """
    Schema for category list filtering parameters.
    
    Supports filtering by:
    - Name (partial match, case-insensitive)
    - Status (exact match)
    - Parent ID (subcategories of specific parent)
    - Root only (categories without parent)
    """
    name: Optional[str] = None
    status: Optional[str] = None
    parent_id: Optional[UUID] = None
    root_only: Optional[bool] = False
    
    model_config = {
        "from_attributes": True
    }


class CategorySortParams(BaseModel):
    """
    Schema for category list sorting parameters.
    
    Supports sorting by any field with ASC/DESC order.
    """
    sort_by: str = "created_at"
    sort_order: str = "desc"  # asc or desc
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order is asc or desc."""
        if v.lower() not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v.lower()
    
    model_config = {
        "from_attributes": True
    }
