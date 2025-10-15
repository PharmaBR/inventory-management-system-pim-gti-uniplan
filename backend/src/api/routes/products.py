"""
Product API endpoints.

Handles HTTP requests for product CRUD operations.
Enforces authentication and tenant isolation.

Tasks: T060-T064
"""

from typing import Optional
from uuid import UUID
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_db
from src.api.dependencies.auth import get_current_user
from src.api.dependencies.tenant import get_tenant_id
from src.services.product import ProductService
from src.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductFilterParams,
    ProductSortParams,
)
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product in the tenant's catalog",
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
) -> ProductResponse:
    """
    Create a new product.
    
    Task: T060 - POST /api/v1/products
    
    Requirements:
    - Authentication required
    - SKU must be unique per tenant
    - Validates all business rules
    
    Returns:
        201: Product created successfully
        401: Unauthorized
        409: SKU already exists
        422: Validation error
    """
    service = ProductService(db)
    
    try:
        product = await service.create(
            tenant_id=tenant_id,
            **product_data.model_dump(),
        )
        
        return ProductResponse.model_validate(product)
        
    except ValueError as e:
        # Business rule violation
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="Get paginated list of products with filters and sorting",
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    sku: Optional[str] = Query(None, description="Filter by SKU (partial match)"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_quantity: Optional[int] = Query(None, ge=0, description="Minimum quantity"),
    max_quantity: Optional[int] = Query(None, ge=0, description="Maximum quantity"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
) -> ProductListResponse:
    """
    List products with pagination, filtering, and sorting.
    
    Task: T061 - GET /api/v1/products (list)
    
    Requirements:
    - Authentication required
    - Returns only products for current tenant
    - Supports multiple filters
    - Configurable sorting
    - Pagination with metadata
    
    Returns:
        200: Products list with pagination metadata
        401: Unauthorized
        422: Invalid parameters
    """
    service = ProductService(db)
    
    # Build filters
    filters = ProductFilterParams(
        name=name,
        sku=sku,
        category_id=category_id,
        status=status,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        min_price=min_price,
        max_price=max_price,
    )
    
    # Build sort params
    try:
        sort_params = ProductSortParams(
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    
    # Get products
    products, total = await service.list(
        tenant_id=tenant_id,
        filters=filters,
        sort=sort_params,
        page=page,
        page_size=page_size,
    )
    
    # Calculate pages
    pages = ceil(total / page_size) if total > 0 else 0
    
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product",
    description="Get product details by ID",
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
) -> ProductResponse:
    """
    Get product by ID.
    
    Task: T062 - GET /api/v1/products/{id}
    
    Requirements:
    - Authentication required
    - Returns only if product belongs to current tenant
    - 404 if not found or deleted
    
    Returns:
        200: Product details
        401: Unauthorized
        404: Product not found
        422: Invalid UUID
    """
    service = ProductService(db)
    
    product = await service.get(product_id, tenant_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    return ProductResponse.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update product details",
)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
) -> ProductResponse:
    """
    Update product.
    
    Task: T063 - PUT /api/v1/products/{id}
    
    Requirements:
    - Authentication required
    - Updates only if product belongs to current tenant
    - Partial updates supported
    - Validates business rules
    
    Returns:
        200: Product updated successfully
        401: Unauthorized
        404: Product not found
        409: SKU conflict
        422: Validation error
    """
    service = ProductService(db)
    
    try:
        product = await service.update(product_id, tenant_id, product_data)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        
        return ProductResponse.model_validate(product)
        
    except ValueError as e:
        # Business rule violation
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Soft delete product (sets status to 'deleted')",
)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
) -> None:
    """
    Soft delete product.
    
    Task: T064 - DELETE /api/v1/products/{id}
    
    Requirements:
    - Authentication required
    - Deletes only if product belongs to current tenant
    - Soft delete (sets status='deleted')
    - 404 if not found or already deleted
    
    Returns:
        204: Product deleted successfully
        401: Unauthorized
        404: Product not found
    """
    service = ProductService(db)
    
    deleted = await service.soft_delete(product_id, tenant_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
