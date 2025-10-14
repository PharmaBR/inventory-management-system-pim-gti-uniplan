"""Database dependencies for dependency injection."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to inject database session into route handlers.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # use db session
            
    Yields:
        AsyncSession: Database session with automatic commit/rollback
    """
    async for session in get_async_session():
        yield session
