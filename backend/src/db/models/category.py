"""Category model for product organization."""
from sqlalchemy import Column, String, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.db.models import BaseModel, GUID


class Category(BaseModel):
    """
    Category model - hierarchical product categorization.
    
    Supports parent-child relationships for nested categories.
    Isolated per tenant via RLS.
    """
    
    __tablename__ = "categories"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Category Info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchical structure (optional parent category)
    parent_id = Column(
        GUID(),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Status
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    
    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    parent = relationship("Category", remote_side="Category.id", backref="children")
    products = relationship("Product", back_populates="category")
    
    # Indexes
    __table_args__ = (
        Index('ix_categories_tenant_name', 'tenant_id', 'name', unique=True),
        Index('ix_categories_tenant_status', 'tenant_id', 'status'),
        Index('ix_categories_tenant_parent', 'tenant_id', 'parent_id'),
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
