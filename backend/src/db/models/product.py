"""Product model with JSONB custom fields support."""
from sqlalchemy import Column, String, ForeignKey, Numeric, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.db.models import BaseModel


class Product(BaseModel):
    """
    Product model - core inventory item.
    
    Features:
    - Unique SKU per tenant
    - JSONB custom_fields for tenant-specific attributes
    - Category relationship
    - Stock tracking via movements
    - RLS for multi-tenant isolation
    """
    
    __tablename__ = "products"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Product identification
    sku = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Category
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Stock Management
    quantity = Column(Integer, default=0, nullable=False)
    min_quantity = Column(Integer, default=0, nullable=False)
    max_quantity = Column(Integer, nullable=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=True)
    
    # Custom Fields (JSONB for flexibility)
    # Example: {"color": "blue", "size": "M", "supplier": "ACME Corp"}
    custom_fields = Column(JSONB, default=dict, nullable=False)
    
    # Status
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    
    # Relationships
    tenant = relationship("Tenant", back_populates="products")
    category = relationship("Category", back_populates="products")
    movements = relationship("Movement", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        # SKU must be unique per tenant
        Index('ix_products_tenant_sku', 'tenant_id', 'sku', unique=True),
        # Fast filtering by status and category
        Index('ix_products_tenant_status', 'tenant_id', 'status'),
        Index('ix_products_tenant_category', 'tenant_id', 'category_id'),
        # Search by name
        Index('ix_products_tenant_name', 'tenant_id', 'name'),
        # GIN index for JSONB custom_fields (enables fast queries on custom attributes)
        Index('ix_products_custom_fields', 'custom_fields', postgresql_using='gin'),
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name}, qty={self.quantity})>"
