"""Authentication dependencies for current user extraction."""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user_token
from src.core.security import TokenPayload
from src.db.models.user import User
from src.api.dependencies.database import get_db


async def get_current_user(
    token: TokenPayload = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from database.
    
    Args:
        token: Validated JWT token payload
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If user not found or inactive
    """
    user_id = UUID(token.sub)
    
    stmt = select(User).where(
        User.id == user_id,
        User.is_active == "active"
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    return user


async def get_current_user_id(
    token: TokenPayload = Depends(get_current_user_token),
) -> UUID:
    """
    Lightweight dependency to get just the user ID without database query.
    
    Args:
        token: Validated JWT token payload
        
    Returns:
        User UUID
    """
    return UUID(token.sub)
