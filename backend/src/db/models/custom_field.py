"""Custom field definition model for tenant-specific product attributes."""
from sqlalchemy import Column, String, ForeignKey, Boolean, Text, Index, Enum, JSON, Integer
from sqlalchemy.orm import relationship
import enum

from src.db.models import BaseModel, GUID


class FieldType(str, enum.Enum):
    """Types of custom fields."""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"  # Dropdown with predefined options
    MULTISELECT = "multiselect"


class CustomFieldDefinition(BaseModel):
    """
    Custom Field Definition - allows tenants to define custom product attributes.
    
    Example: A clothing store might define fields like "size", "color", "material"
    These definitions are stored here, actual values go in Product.custom_fields JSONB
    """
    
    __tablename__ = "custom_field_definitions"
    
    # Tenant relationship (for RLS)
    tenant_id = Column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Field definition
    name = Column(String(100), nullable=False)  # e.g., "size", "color"
    label = Column(String(200), nullable=False)  # e.g., "Tamanho", "Cor"
    field_type = Column(
        Enum(FieldType, name="field_type", native_enum=False),
        nullable=False,
    )
    
    # Validation and options
    is_required = Column(Boolean, default=False, nullable=False)
    default_value = Column(String(500), nullable=True)
    options = Column(JSON, nullable=True)  # For SELECT/MULTISELECT: ["S", "M", "L", "XL"]
    validation_regex = Column(String(500), nullable=True)  # Optional regex validation
    
    # Metadata
    description = Column(Text, nullable=True)
    help_text = Column(String(500), nullable=True)
    
    # Display order
    display_order = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="custom_field_definitions")
    
    # Indexes
    __table_args__ = (
        Index('ix_custom_fields_tenant_name', 'tenant_id', 'name', unique=True),
        Index('ix_custom_fields_tenant_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<CustomFieldDefinition(id={self.id}, name={self.name}, type={self.field_type})>"
