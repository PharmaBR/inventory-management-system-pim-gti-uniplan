"""
Pytest configuration and fixtures.

This file contains common fixtures and configuration for all tests.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.api.main import app
from src.db.base import Base

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory_test_db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        # Don't rollback - let fixtures commit their data
        # The db_engine fixture will clean up between tests


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with overridden database dependency."""
    from src.api.dependencies.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Aliases for consistency with test code
@pytest_asyncio.fixture
async def async_client(client) -> AsyncClient:
    """Alias for client fixture."""
    return client


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> dict:
    """Create a test tenant."""
    from uuid import uuid4
    from src.db.models.tenant import Tenant
    
    tenant_uuid = uuid4()
    tenant = Tenant(
        id=tenant_uuid,
        name="Test Tenant",
        slug=f"test-tenant-{str(tenant_uuid)[:8]}",  # Unique slug per test
        logo_url="https://example.com/logo.png",
        primary_color="#000000",
        secondary_color="#FFFFFF",
        max_users=10,
        max_products=1000,
        max_storage_mb=10000,  # 10GB in MB
        settings={},
        is_active=True
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    return {
        "id": str(tenant.id),
        "slug": tenant.slug,
        "name": tenant.name
    }


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: dict) -> dict:
    """Create a test user."""
    from uuid import uuid4, UUID
    from src.db.models.user import User
    from src.core.security import hash_password
    
    user = User(
        id=uuid4(),
        tenant_id=UUID(test_tenant["id"]),
        email="test@example.com",
        full_name="Test User",
        password_hash=hash_password("testpassword123"),
        role="admin",
        is_active="active"  # String, not boolean
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "tenant_id": test_tenant["id"],
        "role": user.role
    }


@pytest_asyncio.fixture
async def auth_headers(test_user: dict, test_tenant: dict) -> dict:
    """Create authentication headers with JWT token."""
    from src.core.security import create_access_token
    
    token = create_access_token(
        user_id=test_user["id"],
        tenant_id=test_user["tenant_id"],
        email=test_user["email"],
        role=test_user["role"]
    )
    
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-Slug": test_tenant["slug"]  # Use dynamic tenant slug
    }


@pytest_asyncio.fixture
async def tenant_id(test_tenant: dict) -> str:
    """Get test tenant ID."""
    return test_tenant["id"]


@pytest_asyncio.fixture
async def category_id(db_session: AsyncSession, test_tenant: dict) -> str:
    """Create a test category."""
    from uuid import uuid4, UUID
    from src.db.models.category import Category
    
    category = Category(
        id=uuid4(),
        tenant_id=UUID(test_tenant["id"]),
        name="Test Category",
        description="A test category",
        status="active"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    
    return str(category.id)


# Fixtures for multi-tenant testing
@pytest_asyncio.fixture
async def test_tenant_2(db_session: AsyncSession) -> dict:
    """Create a second test tenant."""
    from uuid import uuid4
    from src.db.models.tenant import Tenant
    
    tenant_uuid = uuid4()
    tenant = Tenant(
        id=tenant_uuid,
        name="Test Tenant 2",
        slug=f"test-tenant-2-{str(tenant_uuid)[:8]}",  # Unique slug per test
        logo_url="https://example.com/logo2.png",
        primary_color="#FF0000",
        secondary_color="#00FF00",
        max_users=10,
        max_products=1000,
        max_storage_mb=10000,
        settings={},
        is_active=True
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    return {
        "id": str(tenant.id),
        "slug": tenant.slug,
        "name": tenant.name
    }


@pytest_asyncio.fixture
async def test_user_2(db_session: AsyncSession, test_tenant_2: dict) -> dict:
    """Create a user for second tenant."""
    from uuid import uuid4, UUID
    from src.db.models.user import User
    from src.core.security import hash_password
    
    user = User(
        id=uuid4(),
        tenant_id=UUID(test_tenant_2["id"]),
        email="test2@example.com",
        full_name="Test User 2",
        password_hash=hash_password("testpassword123"),
        role="admin",
        is_active="active"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "tenant_id": test_tenant_2["id"],
        "role": user.role
    }


@pytest_asyncio.fixture
async def auth_headers_tenant1(auth_headers: dict) -> dict:
    """Alias for tenant 1 auth headers."""
    return auth_headers


@pytest_asyncio.fixture
async def auth_headers_tenant2(test_user_2: dict, test_tenant_2: dict) -> dict:
    """Create authentication headers for tenant 2."""
    from src.core.security import create_access_token
    
    token = create_access_token(
        user_id=test_user_2["id"],
        tenant_id=test_user_2["tenant_id"],
        email=test_user_2["email"],
        role=test_user_2["role"]
    )
    
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-Slug": test_tenant_2["slug"]  # Use dynamic tenant slug
    }
