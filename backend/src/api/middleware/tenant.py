"""Tenant identification middleware - extracts tenant from subdomain."""
from typing import Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import re


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to identify and validate tenant from subdomain.
    
    Extracts tenant slug from subdomain and stores in request state.
    Example: tenant1.sistema.com -> tenant_slug = "tenant1"
    
    In development, also supports tenant query parameter: ?tenant=tenant1
    """
    
    def __init__(self, app: ASGIApp, development_mode: bool = False):
        super().__init__(app)
        self.development_mode = development_mode
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request to extract tenant information."""
        
        tenant_slug = None
        
        # Method 1: Extract from subdomain (production)
        host = request.headers.get("host", "")
        
        # Pattern: tenant.domain.com or tenant.localhost:port
        subdomain_pattern = r"^([a-z0-9-]+)\."
        match = re.match(subdomain_pattern, host)
        
        if match:
            tenant_slug = match.group(1)
        
        # Method 2: Extract from query parameter (development fallback)
        elif self.development_mode:
            tenant_slug = request.query_params.get("tenant")
        
        # Method 3: Extract from custom header (mobile apps, testing)
        if not tenant_slug:
            tenant_slug = request.headers.get("x-tenant-slug")
        
        # Validate tenant slug format
        if tenant_slug:
            if not re.match(r"^[a-z0-9-]{3,100}$", tenant_slug):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant identifier format"
                )
        
        # Store in request state for use in dependencies
        request.state.tenant_slug = tenant_slug
        
        # Continue processing
        response = await call_next(request)
        
        # Add tenant to response headers (useful for debugging)
        if tenant_slug:
            response.headers["X-Tenant-Slug"] = tenant_slug
        
        return response


def get_tenant_slug(request: Request) -> str:
    """
    Dependency to get tenant slug from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tenant slug string
        
    Raises:
        HTTPException: If tenant not identified
    """
    tenant_slug = getattr(request.state, "tenant_slug", None)
    
    if not tenant_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant not identified. Ensure you're accessing via subdomain or provide tenant parameter."
        )
    
    return tenant_slug
