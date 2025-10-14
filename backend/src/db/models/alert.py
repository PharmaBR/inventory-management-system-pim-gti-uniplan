"""Alert model for stock notifications."""
from sqlalchemy import Column, String, ForeignKey, Boolean, Text, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.db.models import BaseModel


class AlertType(str, enum.Enum):
    """Types of alerts."""
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRING_SOON = "expiring_soon"
    CUSTOM = "custom"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    """
    Alert model - notifications for stock issues.
    
    Alerts are automatically generated when:
    - Product quantity falls below min_quantity (LOW_STOCK)
    - Product quantity reaches zero (OUT_OF_STOCK)
    - Custom conditions are met
    """
    
    __tablename__ = "alerts"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Product relationship (optional, some alerts may be tenant-wide)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Alert details
    type = Column(
        Enum(AlertType, name="alert_type", native_enum=False),
        nullable=False,
    )
    severity = Column(
        Enum(AlertSeverity, name="alert_severity", native_enum=False),
        default=AlertSeverity.INFO,
        nullable=False,
    )
    message = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('ix_alerts_tenant_unread', 'tenant_id', 'is_read'),
        Index('ix_alerts_tenant_unresolved', 'tenant_id', 'is_resolved'),
        Index('ix_alerts_tenant_severity', 'tenant_id', 'severity'),
        Index('ix_alerts_product_type', 'product_id', 'type'),
    )
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.type}, severity={self.severity}, read={self.is_read})>"
