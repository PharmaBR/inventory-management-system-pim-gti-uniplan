#!/usr/bin/env python3
"""
Script to create a test user for development

Creates:
- Test tenant (empresa de teste)
- Admin user with credentials:
  - Email: admin@example.com
  - Password: admin123
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))
os.chdir(backend_root)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings
from src.core.security import hash_password
from src.db.base import Base
from src.db.models.tenant import Tenant
from src.db.models.user import User


async def create_test_data():
    """Create test tenant and user"""
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        # Check if tenant already exists
        result = await session.execute(
            select(Tenant).where(Tenant.slug == "test-company")
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            print(f"✅ Tenant já existe: {tenant.name} (slug: {tenant.slug})")
        else:
            # Create tenant
            tenant = Tenant(
                name="Test Company",
                slug="test-company",
                is_active=True,
            )
            session.add(tenant)
            await session.flush()
            print(f"✅ Tenant criado: {tenant.name} (slug: {tenant.slug})")
        
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ Usuário já existe: {user.email}")
            print("\n⚠️  Usuário já cadastrado. Use as credenciais existentes.")
        else:
            # Create user
            user = User(
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                full_name="Admin User",
                is_active="active",
                tenant_id=tenant.id,
            )
            session.add(user)
            await session.commit()
            
            print(f"✅ Usuário criado: {user.email}")
            print(f"   Nome: {user.full_name}")
            print(f"   Tenant: {tenant.name}")
        
        print("\n" + "="*50)
        print("🎉 Credenciais de Teste:")
        print("="*50)
        print(f"E-mail: admin@example.com")
        print(f"Senha:  admin123")
        print(f"Tenant: {tenant.slug}")
        print("="*50)
        print("\n✅ Pronto! Use essas credenciais para fazer login.")
        print("   Frontend: http://localhost:3001/login")
        print("   Backend:  http://localhost:8000/docs")
        print()
    
    await engine.dispose()


if __name__ == "__main__":
    print("🔧 Criando usuário de teste...\n")
    asyncio.run(create_test_data())
