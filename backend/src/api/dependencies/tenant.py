"""Tenant context dependencies."""
from uuid import UUID
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.tenant import get_tenant_slug
from src.api.middleware.auth import get_current_user_token, get_optional_user_token
from src.core.security import TokenPayload
from src.db.models.tenant import Tenant
from src.api.dependencies.database import get_db


async def get_current_tenant(
    tenant_slug: str = Depends(get_tenant_slug),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """
    Dependency to get current tenant from database based on subdomain.
    
    Args:
        tenant_slug: Tenant slug from subdomain/header/query
        db: Database session
        
    Returns:
        Tenant object from database
        
    Raises:
        HTTPException: If tenant not found or inactive
    """
    stmt = select(Tenant).where(
        Tenant.slug == tenant_slug,
        Tenant.is_active == True
    )
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_slug}' not found or inactive"
        )
    
    return tenant


async def get_current_tenant_id(
    tenant: Tenant = Depends(get_current_tenant),
) -> UUID:
    """
    Lightweight dependency to get just the tenant ID.
    
    Args:
        tenant: Current tenant object
        
    Returns:
        Tenant UUID
    """
    return tenant.id


async def validate_tenant_access(
    tenant: Tenant = Depends(get_current_tenant),
    token: Optional[TokenPayload] = Depends(get_optional_user_token),
) -> None:
    """
    Dependency to validate that user belongs to the accessed tenant.
    
    Prevents cross-tenant access even if user has valid token.
    
    Args:
        tenant: Current tenant from subdomain
        token: User token (optional)
        
    Raises:
        HTTPException: If user tries to access different tenant's data
    """
    if token and str(tenant.id) != token.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't belong to this tenant"
        )


async def ensure_tenant_user_match(
    tenant_id: UUID = Depends(get_current_tenant_id),
    token: TokenPayload = Depends(get_current_user_token),
) -> UUID:
    """
    Dependency to ensure authenticated user belongs to current tenant.
    
    Returns tenant_id if match, raises exception otherwise.
    Used for protected endpoints that require both authentication and tenant validation.
    
    Args:
        tenant_id: Current tenant ID from subdomain
        token: Validated user token
        
    Returns:
        Tenant UUID if validation passes
        
    Raises:
        HTTPException: If tenant mismatch
    """
    if str(tenant_id) != token.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied"
        )
    
    return tenant_id
