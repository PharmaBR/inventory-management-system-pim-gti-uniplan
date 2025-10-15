"""
Authentication Schemas

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """Response model for user information"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User full name")
    is_active: bool = Field(..., description="Whether user is active")
    tenant_id: str = Field(..., description="Tenant ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
