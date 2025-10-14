"""Audit log model for tracking all system changes."""
from sqlalchemy import Column, String, ForeignKey, Text, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.models import BaseModel


class AuditLog(BaseModel):
    """
    Audit Log - tracks all important actions in the system.
    
    Records:
    - Who did what
    - When they did it
    - What changed (before/after values)
    - Which tenant it affects
    
    Essential for compliance, debugging, and security.
    """
    
    __tablename__ = "audit_logs"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Who performed the action
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # What happened
    action = Column(String(100), nullable=False)  # e.g., "product.create", "user.update"
    entity_type = Column(String(100), nullable=False)  # e.g., "product", "user", "movement"
    entity_id = Column(UUID(as_uuid=True), nullable=True)  # ID of the affected entity
    
    # Details of the change
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # {"before": {...}, "after": {...}}
    metadata = Column(JSON, nullable=True)  # Additional context (IP, user agent, etc.)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    
    # Indexes for querying
    __table_args__ = (
        Index('ix_audit_logs_tenant_date', 'tenant_id', 'created_at'),
        Index('ix_audit_logs_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_audit_logs_tenant_action', 'tenant_id', 'action'),
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity={self.entity_type})>"
