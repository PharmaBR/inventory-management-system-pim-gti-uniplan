"""Movement API routes for stock operations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.api.dependencies.database import get_db
from src.api.dependencies.tenant import get_current_tenant_id, ensure_tenant_user_match
from src.api.middleware.auth import get_current_user_token
from src.core.security import TokenPayload
from src.schemas.movement import (
    MovementCreate,
    MovementResponse,
    MovementListResponse,
    MovementFilterParams,
)
from src.services.movement import MovementService

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    data: MovementCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(ensure_tenant_user_match),
    user: TokenPayload = Depends(get_current_user_token),
):
    """Create a new stock movement and update product balance."""
    service = MovementService(db)
    from uuid import UUID
    try:
        user_id = UUID(user.sub) if not isinstance(user.sub, UUID) else user.sub
        movement = await service.create(tenant_id, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MovementResponse.model_validate(movement)


@router.get("/", response_model=MovementListResponse)
async def list_movements(
    filters: MovementFilterParams = Depends(),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List movements for current tenant with filters and pagination."""
    service = MovementService(db)
    items, total = await service.list(tenant_id, filters)
    pages = (total + filters.page_size - 1) // filters.page_size if filters.page_size else 1
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=pages,
    )


@router.get("/{movement_id}", response_model=MovementResponse)
async def get_movement(
    movement_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get a movement by ID (tenant-scoped)."""
    service = MovementService(db)
    # ORM query for movement by id and tenant
    from sqlalchemy import select
    from src.db.models.movement import Movement
    stmt = select(Movement).where(Movement.id == movement_id, Movement.tenant_id == tenant_id)
    result = await db.execute(stmt)
    movement = result.scalar_one_or_none()
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    return MovementResponse.model_validate(movement)
