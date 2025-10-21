"""Movement service - business logic for stock movements.

Creates and lists movements, adjusting product stock accordingly with
strict tenant isolation.
"""
from __future__ import annotations

from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.movement import Movement, MovementType
from src.db.models.product import Product
from src.schemas.movement import MovementCreate, MovementFilterParams
from src.core.logging import logger


class MovementService:
    """Service handling stock movements and inventory balance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_product(self, product_id: UUID, tenant_id: UUID) -> Optional[Product]:
        stmt = select(Product).where(
            and_(
                Product.id == product_id,
                Product.tenant_id == tenant_id,
                Product.status != "deleted",
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, tenant_id: UUID, user_id: Optional[UUID], data: MovementCreate) -> Movement:
        """Create a movement and update product quantity.

        Rules:
        - ENTRY: increases stock by data.quantity
        - EXIT: decreases stock by data.quantity (must not drop below 0)
        - ADJUSTMENT: sets stock to data.quantity (absolute target)
        """
        product = await self._get_product(data.product_id, tenant_id)
        if not product:
            raise ValueError("Product not found for this tenant")

        # Access SQLAlchemy attribute in a type-checker friendly way
        current_qty = int(getattr(product, "quantity") or 0)

        if data.type == MovementType.ENTRY.value:
            delta = int(data.quantity)
            new_balance = current_qty + delta
        elif data.type == MovementType.EXIT.value:
            delta = -int(data.quantity)
            new_balance = current_qty + delta
            if new_balance < 0:
                raise ValueError("Insufficient stock for EXIT movement")
        elif data.type == MovementType.ADJUSTMENT.value:
            # For adjustment, quantity is treated as target absolute balance
            target = int(data.quantity)
            delta = target - current_qty
            new_balance = target
            if new_balance < 0:
                raise ValueError("Adjusted balance cannot be negative")
        else:
            raise ValueError("Unsupported movement type")

        # Update product quantity first for consistency
        setattr(product, "quantity", new_balance)

        movement = Movement(
            tenant_id=tenant_id,
            product_id=data.product_id,
            type=MovementType(data.type),
            quantity=delta,  # store signed delta
            balance_after=new_balance,
            reason=data.reason,
            notes=data.notes,
            user_id=user_id,
        )

        self.db.add(movement)
        await self.db.commit()
        await self.db.refresh(movement)

        logger.info(
            "Movement created",
            extra={
                "movement_id": str(movement.id),
                "tenant_id": str(tenant_id),
                "product_id": str(data.product_id),
                "type": data.type,
                "delta": delta,
                "balance_after": new_balance,
            },
        )

        return movement

    async def list(
        self,
        tenant_id: UUID,
        filters: Optional[MovementFilterParams] = None,
    ) -> Tuple[List[Movement], int]:
        """List movements for a tenant with optional filters and pagination."""
        stmt = select(Movement).where(Movement.tenant_id == tenant_id)

        if filters:
            if filters.product_id:
                stmt = stmt.where(Movement.product_id == filters.product_id)
            if filters.type:
                stmt = stmt.where(Movement.type == filters.type)
            if filters.min_date:
                stmt = stmt.where(Movement.created_at >= filters.min_date)
            if filters.max_date:
                stmt = stmt.where(Movement.created_at <= filters.max_date)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.alias())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Order by newest first
        stmt = stmt.order_by(Movement.created_at.desc())

        # Pagination
        page = filters.page if filters else 1
        page_size = filters.page_size if filters else 50
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        res = await self.db.execute(stmt)
        items = list(res.scalars().all())
        return items, int(total)
