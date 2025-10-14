"""Tenant model for multi-tenancy support."""
from sqlalchemy import Column, String, Integer, Boolean, JSON, Index, text
from sqlalchemy.orm import relationship

from src.db.models import BaseModel


class Tenant(BaseModel):
    """
    Tenant model - represents a client organization.
    
    Each tenant has isolated data via Row-Level Security (RLS).
    """
    
    __tablename__ = "tenants"
    
    # Basic Info
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Branding (White-label)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")  # Tailwind blue-500
    secondary_color = Column(String(7), default="#10B981")  # Tailwind green-500
    
    # Limits and Configuration
    max_users = Column(Integer, default=10)
    max_products = Column(Integer, default=1000)
    max_storage_mb = Column(Integer, default=100)
    
    # Custom Settings (JSONB for flexibility)
    settings = Column(JSON, default=dict, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    movements = relationship("Movement", back_populates="tenant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="tenant", cascade="all, delete-orphan")
    custom_field_definitions = relationship(
        "CustomFieldDefinition",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_tenants_slug_active', 'slug', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, name={self.name})>"
