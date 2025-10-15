#!/usr/bin/env python3
"""
Script rápido para criar usuário usando bcrypt diretamente.
"""
import asyncio
import sqlite3
import uuid
from datetime import datetime
import bcrypt

async def create_user():
    # Gerar hash da senha usando bcrypt diretamente
    password = "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    # Conectar ao banco
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # IDs
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Criar tenant
    cursor.execute("""
        INSERT OR REPLACE INTO tenants 
        (id, name, slug, is_active, created_at, updated_at, max_users, max_products, max_storage_mb, settings)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tenant_id, "Test Company", "test-company", 1, now, now, 10, 1000, 100, '{}'))
    
    # Criar usuário
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (id, tenant_id, email, full_name, password_hash, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, tenant_id, "admin@example.com", "Admin User", password_hash, "admin", "active", now, now))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Tenant criado: Test Company (ID: {tenant_id})")
    print(f"✅ Usuário criado: admin@example.com (ID: {user_id})")
    print(f"✅ Senha: admin123")
    print(f"✅ Hash gerado com sucesso")

if __name__ == "__main__":
    asyncio.run(create_user())
