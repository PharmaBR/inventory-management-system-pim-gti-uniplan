"""
Database base configuration with SQLAlchemy 2.0 async support.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator

from src.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Import all models to ensure they're registered with Base.metadata
# This must be done before create_all() is called
from src.db.models.tenant import Tenant  # noqa: E402, F401
from src.db.models.user import User  # noqa: E402, F401
from src.db.models.category import Category  # noqa: E402, F401
from src.db.models.product import Product  # noqa: E402, F401
from src.db.models.movement import Movement  # noqa: E402, F401
from src.db.models.alert import Alert  # noqa: E402, F401
from src.db.models.custom_field import CustomFieldDefinition  # noqa: E402, F401
from src.db.models.audit_log import AuditLog  # noqa: E402, F401


# Create async engine with appropriate settings based on database type
# SQLite doesn't support pool_size and max_overflow parameters
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )
else:
    # PostgreSQL and other databases support connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database - create all tables.
    Only use in development/testing.
    """
    from src.core.logging import logger
    from src.core.config import settings
    
    logger.info(f"Tables registered in Base.metadata: {list(Base.metadata.tables.keys())}")
    
    async with engine.begin() as conn:
        logger.info("Running create_all...")
        # Force checkfirst=True to always check before creating
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
        logger.info("create_all completed")
        
        # Verify tables were created (different query for SQLite vs PostgreSQL)
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite: Query sqlite_master
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            )
        else:
            # PostgreSQL: Query information_schema
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
        
        tables = [row[0] for row in result]
        logger.info(f"Tables now in database: {tables}")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
