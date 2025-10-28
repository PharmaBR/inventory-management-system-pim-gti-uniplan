"""Script to create admin user and tenant."""
import asyncio
from uuid import uuid4
from src.core.security import hash_password
from src.db.base import async_session_maker
from src.db.models.user import User
from src.db.models.tenant import Tenant


async def create_admin():
    async with async_session_maker() as db:
        # Check if tenant exists
        from sqlalchemy import select
        result = await db.execute(select(Tenant).where(Tenant.slug == 'test-company'))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            # Create tenant
            tenant = Tenant(
                id=uuid4(),
                name='Test Company',
                slug='test-company',
                is_active=True
            )
            db.add(tenant)
            await db.flush()
            print(f"✅ Tenant created: {tenant.name} (ID: {tenant.id})")
        else:
            print(f"ℹ️  Tenant already exists: {tenant.name} (ID: {tenant.id})")
        
        # Check if admin exists
        result = await db.execute(select(User).where(User.email == 'admin@example.com'))
        admin = result.scalar_one_or_none()
        
        if not admin:
            # Create admin
            admin = User(
                id=uuid4(),
                tenant_id=tenant.id,
                email='admin@example.com',
                full_name='Admin User',
                password_hash=hash_password('admin123'),
                role='admin',
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print(f"✅ Admin user created: {admin.email}")
        else:
            print(f"ℹ️  Admin user already exists: {admin.email}")
        
        print("\n🎉 Setup complete!")
        print("Login credentials:")
        print("  Email: admin@example.com")
        print("  Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_admin())
