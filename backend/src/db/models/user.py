"""User model with role-based access control."""
from sqlalchemy import Column, String, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
import enum

from src.db.models import BaseModel, GUID


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"


class User(BaseModel):
    """
    User model - represents a user within a tenant.
    
    Uses Row-Level Security (RLS) to ensure users only access their tenant's data.
    """
    
    __tablename__ = "users"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # User Info
    email = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Role-Based Access Control
    role = Column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.OPERATOR,
        nullable=False,
    )
    
    # Status
    is_active = Column(String(20), default="active", nullable=False)  # active, inactive
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")
    
    # Indexes for performance and uniqueness
    __table_args__ = (
        Index('ix_users_tenant_email', 'tenant_id', 'email', unique=True),
        Index('ix_users_tenant_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
