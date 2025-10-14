"""Authentication middleware - validates JWT tokens."""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.security import verify_token, TokenPayload


# Security scheme for Swagger/OpenAPI
security = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Dependency to extract and validate JWT token from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        TokenPayload with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_optional_user_token(
    request: Request,
) -> Optional[TokenPayload]:
    """
    Dependency to optionally extract JWT token (for public endpoints).
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenPayload if token present and valid, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    return verify_token(token, token_type="access")


def require_role(*allowed_roles: str):
    """
    Dependency factory to enforce role-based access control.
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        
    Args:
        *allowed_roles: Roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user_token)
    ) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker
