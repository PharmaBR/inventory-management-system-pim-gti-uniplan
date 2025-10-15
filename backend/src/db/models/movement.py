"""Movement model for stock tracking."""
from sqlalchemy import Column, String, ForeignKey, Integer, Text, Index, Enum
from sqlalchemy.orm import relationship
import enum

from src.db.models import BaseModel, GUID


class MovementType(str, enum.Enum):
    """Types of stock movements."""
    ENTRY = "entry"  # Stock in
    EXIT = "exit"    # Stock out
    ADJUSTMENT = "adjustment"  # Manual adjustment
    TRANSFER = "transfer"  # Transfer between locations


class Movement(BaseModel):
    """
    Movement model - tracks all stock changes.
    
    Each movement records:
    - Type (entry/exit/adjustment/transfer)
    - Quantity changed
    - Balance after movement
    - Who made the change
    - Why it was made
    """
    
    __tablename__ = "movements"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Product relationship
    product_id = Column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Movement details
    type = Column(
        Enum(MovementType, name="movement_type", native_enum=False),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)  # Positive for entry, negative for exit
    balance_after = Column(Integer, nullable=False)  # Stock level after this movement
    
    # Metadata
    reason = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Who made this movement
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Relationships
    tenant = relationship("Tenant", back_populates="movements")
    product = relationship("Product", back_populates="movements")
    user = relationship("User", foreign_keys=[user_id])
    
    # Indexes for reporting and filtering
    __table_args__ = (
        Index('ix_movements_tenant_product', 'tenant_id', 'product_id'),
        Index('ix_movements_tenant_type', 'tenant_id', 'type'),
        Index('ix_movements_tenant_date', 'tenant_id', 'created_at'),
        Index('ix_movements_product_date', 'product_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Movement(id={self.id}, type={self.type}, qty={self.quantity}, product_id={self.product_id})>"
