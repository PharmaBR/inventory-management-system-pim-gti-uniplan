"""
Category API routes.

Endpoints:
- POST /api/v1/categories - Create category
- GET /api/v1/categories/{id} - Get category
- GET /api/v1/categories - List categories
- PUT /api/v1/categories/{id} - Update category
- DELETE /api/v1/categories/{id} - Delete category

Phase: 4 - Categories CRUD
Session: 2 - Implementation
"""

from typing import Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.dependencies.auth import get_current_user
from src.db.models.user import User
from src.services.category import CategoryService
from src.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryFilterParams,
    CategorySortParams,
)

logger = logging.getLogger("inventory_system")

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new category with optional parent for hierarchy",
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new category.
    
    - **name**: Category name (required, 1-100 chars, unique per tenant)
    - **description**: Optional description
    - **parent_id**: Optional parent category for hierarchical structure
    - **status**: Status (active/inactive, default: active)
    
    Returns the created category with ID and timestamps.
    """
    service = CategoryService(db)
    
    try:
        category = await service.create(data, current_user.tenant_id)
        return CategoryResponse.model_validate(category)
        
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error creating category: {error_msg}")
        
        # Check if it's a duplicate name error (409 Conflict)
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        
        # Other validation errors (400 Bad Request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category",
    description="Retrieve a specific category by ID",
)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get category by ID.
    
    Returns category details with tenant isolation.
    """
    service = CategoryService(db)
    category = await service.get(category_id, current_user.tenant_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )
    
    return CategoryResponse.model_validate(category)


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="List categories",
    description="List categories with filtering, sorting, and pagination",
)
async def list_categories(
    # Pagination
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    
    # Filters
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category"),
    root_only: Optional[bool] = Query(None, description="Show only root categories"),
    
    # Sorting
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    
    # Dependencies
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List categories with filters and pagination.
    
    **Filters:**
    - name: Partial case-insensitive match
    - status: Exact match (active/inactive)
    - parent_id: Categories with specific parent
    - root_only: Only categories without parent
    
    **Sorting:**
    - sort_by: Field to sort by (name, created_at, etc.)
    - sort_order: asc or desc
    
    **Pagination:**
    - page: Page number (starts at 1)
    - page_size: Items per page (max 100)
    
    Returns paginated list with metadata.
    """
    service = CategoryService(db)
    
    # Build filters
    filters = CategoryFilterParams(
        name=name,
        status=status,
        parent_id=parent_id,
        root_only=root_only,
    )
    
    # Build sorting
    try:
        sort = CategorySortParams(
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameters: {e}",
        )
    
    # Get categories
    categories, total = await service.list(
        tenant_id=current_user.tenant_id,
        filters=filters,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category",
    description="Update category (supports partial updates)",
)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update category.
    
    Supports partial updates (only send fields to change).
    
    - **name**: New name (must be unique per tenant)
    - **description**: New description
    - **parent_id**: New parent (for reorganizing hierarchy)
    - **status**: New status (active/inactive)
    
    Returns the updated category.
    """
    service = CategoryService(db)
    
    try:
        category = await service.update(category_id, current_user.tenant_id, data)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found",
            )
        
        return CategoryResponse.model_validate(category)
        
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error updating category: {error_msg}")
        
        # Check if it's a duplicate name error (409 Conflict)
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        
        # Other validation errors (400 Bad Request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete category (validates no products associated)",
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete category.
    
    Validates:
    - Category has no associated products
    - Children categories become root categories (parent_id set to NULL)
    
    Returns 204 No Content on success.
    """
    service = CategoryService(db)
    
    try:
        deleted = await service.delete(category_id, current_user.tenant_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found",
            )
        
        return None  # 204 No Content
        
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error deleting category: {error_msg}")
        
        # Check if it's a product constraint error (409 Conflict)
        if "product" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        
        # Other validation errors (400 Bad Request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
