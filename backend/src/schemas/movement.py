"""Pydantic schemas for stock Movements."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MovementType(str):
    ENTRY = "entry"
    EXIT = "exit"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class MovementBase(BaseModel):
    type: str = Field(..., description="Movement type: entry, exit, adjustment")
    quantity: int = Field(..., ge=1, description="Quantity involved in the movement; positive integer")
    reason: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {MovementType.ENTRY, MovementType.EXIT, MovementType.ADJUSTMENT}
        if v not in allowed:
            raise ValueError(f"type must be one of {sorted(allowed)}")
        return v


class MovementCreate(MovementBase):
    product_id: UUID


class MovementResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    product_id: UUID
    type: str
    quantity: int
    balance_after: int
    reason: Optional[str]
    notes: Optional[str]
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MovementListResponse(BaseModel):
    items: List[MovementResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MovementFilterParams(BaseModel):
    page: int = 1
    page_size: int = 50
    product_id: Optional[UUID] = None
    type: Optional[str] = None
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None

    @field_validator("page", "page_size")
    @classmethod
    def positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("must be >= 1")
        return v
