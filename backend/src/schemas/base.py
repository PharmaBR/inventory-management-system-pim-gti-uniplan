"""Base Pydantic schemas for request/response models."""
from datetime import datetime
from typing import Generic, TypeVar, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# Base schema with common configuration
class BaseSchema(BaseModel):
    """Base schema with common Pydantic configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


# Schema with timestamps
class TimestampSchema(BaseSchema):
    """Schema with created_at and updated_at timestamps."""
    
    created_at: datetime
    updated_at: datetime


# Schema with ID and timestamps
class IdentifiedSchema(TimestampSchema):
    """Schema with ID, created_at, and updated_at."""
    
    id: UUID


# Pagination schemas
class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.per_page


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""
    
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int,
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response.
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            per_page: Items per page
            
        Returns:
            PaginatedResponse instance
        """
        pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        )


# Status response
class StatusResponse(BaseSchema):
    """Generic status response."""
    
    status: str
    message: Optional[str] = None


# Error response
class ErrorResponse(BaseSchema):
    """Error response format."""
    
    code: int
    message: str
    details: Optional[dict] = None


# Success response with data
class DataResponse(BaseSchema, Generic[T]):
    """Generic data response."""
    
    data: T
    message: Optional[str] = None
