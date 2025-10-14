# Data Model: Sistema de Gerenciamento de Estoque White Label

**Feature**: 001-sistema-de-gerenciamento  
**Date**: 2025-10-07  
**Phase**: 1 - Database Schema Design

## Overview

Este documento define o modelo de dados completo do sistema, incluindo todas as entidades, relacionamentos, índices e constraints. O modelo usa PostgreSQL com Row-Level Security (RLS) para isolamento multi-tenant.

## Database Configuration

**Database**: PostgreSQL 15+  
**Character Set**: UTF-8  
**Timezone**: UTC (all timestamps stored in UTC)  
**Extensions**:
- `uuid-ossp`: UUID generation
- `pgcrypto`: Additional crypto functions if needed

## Core Entities

### 1. Tenant (Cliente/Inquilino)

Representa um cliente da plataforma white label.

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(50) UNIQUE NOT NULL,  -- Subdomain identifier (lowercase, alphanumeric, hyphens)
    name VARCHAR(200) NOT NULL,         -- Display name
    logo_url VARCHAR(500),              -- URL to logo image
    primary_color VARCHAR(7),            -- Hex color #RRGGBB
    secondary_color VARCHAR(7),          -- Hex color #RRGGBB
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active', 'inactive', 'suspended'
    
    -- Limits
    max_products INTEGER DEFAULT 10000,
    max_users INTEGER DEFAULT 50,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT slug_format CHECK (slug ~ '^[a-z0-9-]+$'),
    CONSTRAINT status_values CHECK (status IN ('active', 'inactive', 'suspended')),
    CONSTRAINT color_format CHECK (
        (primary_color IS NULL OR primary_color ~ '^#[0-9A-Fa-f]{6}$') AND
        (secondary_color IS NULL OR secondary_color ~ '^#[0-9A-Fa-f]{6}$')
    )
);

-- Indexes
CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_status ON tenants(status) WHERE status = 'active';

-- Trigger for updated_at
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Attributes**:
- `id`: Unique identifier (UUID)
- `slug`: Subdomain slug (empresa1, empresa2)
- `name`: Tenant display name
- `logo_url`: URL to branded logo
- `primary_color`, `secondary_color`: Brand colors
- `status`: Tenant state (active/inactive/suspended)
- `max_products`, `max_users`: Plan limits
- `created_at`, `updated_at`: Audit timestamps

---

### 2. User (Usuário)

Usuários pertencentes a um tenant com perfis de acesso.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Credentials
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Bcrypt hash
    
    -- Profile
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',  -- 'admin', 'manager', 'operator'
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active', 'inactive'
    
    -- Metadata
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT users_tenant_email_unique UNIQUE (tenant_id, email),
    CONSTRAINT role_values CHECK (role IN ('admin', 'manager', 'operator')),
    CONSTRAINT status_values CHECK (status IN ('active', 'inactive'))
);

-- Indexes
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(tenant_id, email);
CREATE INDEX idx_users_status ON users(tenant_id, status) WHERE status = 'active';

-- Row-Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON users
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Trigger
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Attributes**:
- `id`: Unique identifier
- `tenant_id`: Foreign key to tenant
- `email`: User email (unique per tenant)
- `password_hash`: Bcrypt hashed password
- `full_name`: User's full name
- `role`: Access level (admin/manager/operator)
- `status`: User state
- `last_login_at`: Last login timestamp
- `created_at`, `updated_at`: Audit timestamps

**Roles**:
- **admin**: Full access (CRUD products, users, settings)
- **manager**: Manage products, movements, view reports
- **operator**: View-only access

---

### 3. Category (Categoria)

Product categorization.

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT categories_tenant_name_unique UNIQUE (tenant_id, name)
);

-- Indexes
CREATE INDEX idx_categories_tenant ON categories(tenant_id);

-- RLS
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON categories
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Trigger
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 4. Product (Produto)

Product catalog with custom fields support.

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    
    -- Core fields
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    current_quantity DECIMAL(15, 3) NOT NULL DEFAULT 0,  -- Supports fractional quantities
    unit_price DECIMAL(15, 2),
    supplier VARCHAR(200),
    image_url VARCHAR(500),
    
    -- Inventory control
    minimum_quantity DECIMAL(15, 3) DEFAULT 0,  -- Alert threshold
    
    -- Custom fields (JSONB)
    custom_fields JSONB DEFAULT '{}',  -- e.g., {"lote": "ABC123", "validade": "2025-12-31"}
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active', 'inactive'
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT products_tenant_sku_unique UNIQUE (tenant_id, sku),
    CONSTRAINT status_values CHECK (status IN ('active', 'inactive')),
    CONSTRAINT quantity_non_negative CHECK (current_quantity >= -999999)  -- Allow negative for backorders
);

-- Indexes
CREATE INDEX idx_products_tenant ON products(tenant_id);
CREATE INDEX idx_products_tenant_sku ON products(tenant_id, sku);
CREATE INDEX idx_products_tenant_name ON products(tenant_id, name);
CREATE INDEX idx_products_tenant_category ON products(tenant_id, category_id);
CREATE INDEX idx_products_tenant_status ON products(tenant_id) WHERE status = 'active';
CREATE INDEX idx_products_custom_fields ON products USING GIN (custom_fields);  -- For JSONB queries

-- RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON products
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Trigger
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Attributes**:
- `id`: Unique identifier
- `tenant_id`: Foreign key to tenant
- `category_id`: Optional category
- `sku`: Stock Keeping Unit (unique per tenant)
- `name`, `description`: Product details
- `current_quantity`: Current stock level
- `unit_price`: Price per unit
- `supplier`: Supplier name
- `image_url`: Product image URL
- `minimum_quantity`: Alert threshold
- `custom_fields`: Tenant-specific fields (JSONB)
- `status`: Active/inactive
- `created_by`, `updated_by`: User audit trail

---

### 5. Movement (Movimentação)

Stock movements (inbound/outbound).

```sql
CREATE TABLE movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Movement details
    movement_type VARCHAR(20) NOT NULL,  -- 'inbound', 'outbound'
    quantity DECIMAL(15, 3) NOT NULL,
    
    -- Balances (snapshot at time of movement)
    balance_before DECIMAL(15, 3) NOT NULL,
    balance_after DECIMAL(15, 3) NOT NULL,
    
    -- Reason/notes
    reason VARCHAR(100),  -- 'purchase', 'sale', 'return', 'loss', 'adjustment'
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT movement_type_values CHECK (movement_type IN ('inbound', 'outbound')),
    CONSTRAINT quantity_positive CHECK (quantity > 0)
);

-- Indexes
CREATE INDEX idx_movements_tenant ON movements(tenant_id);
CREATE INDEX idx_movements_product ON movements(tenant_id, product_id);
CREATE INDEX idx_movements_tenant_date ON movements(tenant_id, created_at DESC);
CREATE INDEX idx_movements_product_date ON movements(tenant_id, product_id, created_at DESC);
CREATE INDEX idx_movements_user ON movements(tenant_id, user_id);

-- RLS
ALTER TABLE movements ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON movements
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
```

**Attributes**:
- `id`: Unique identifier
- `tenant_id`: Foreign key to tenant
- `product_id`: Product affected
- `user_id`: User who created movement
- `movement_type`: Inbound (entry) or outbound (exit)
- `quantity`: Movement quantity
- `balance_before`, `balance_after`: Stock snapshots
- `reason`: Movement reason
- `notes`: Additional details
- `created_at`: Movement timestamp

**Movement Types**:
- **inbound**: Entrada (compra, devolução de cliente, ajuste positivo)
- **outbound**: Saída (venda, perda, ajuste negativo)

---

### 6. Alert (Alerta)

Stock level alerts.

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(20) NOT NULL,  -- 'low_stock', 'out_of_stock'
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Snapshot at alert time
    product_quantity DECIMAL(15, 3),
    minimum_quantity DECIMAL(15, 3),
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP,
    
    CONSTRAINT alert_type_values CHECK (alert_type IN ('low_stock', 'out_of_stock'))
);

-- Indexes
CREATE INDEX idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX idx_alerts_tenant_unread ON alerts(tenant_id) WHERE is_read = FALSE;
CREATE INDEX idx_alerts_product ON alerts(tenant_id, product_id);
CREATE INDEX idx_alerts_created ON alerts(tenant_id, created_at DESC);

-- RLS
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON alerts
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
```

---

### 7. CustomFieldDefinition (Definição de Campo Customizado)

Metadata for tenant-configurable custom fields.

```sql
CREATE TABLE custom_field_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    field_name VARCHAR(50) NOT NULL,    -- Internal name (snake_case)
    label VARCHAR(100) NOT NULL,         -- Display label
    field_type VARCHAR(20) NOT NULL,     -- 'text', 'number', 'date', 'select'
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- For 'select' type
    options JSONB,  -- ["option1", "option2", "option3"]
    
    -- Which entity this applies to
    entity_type VARCHAR(50) NOT NULL DEFAULT 'product',  -- Future: 'movement', etc.
    
    -- Display order
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT field_definitions_tenant_name_unique UNIQUE (tenant_id, entity_type, field_name),
    CONSTRAINT field_type_values CHECK (field_type IN ('text', 'number', 'date', 'select')),
    CONSTRAINT entity_type_values CHECK (entity_type IN ('product'))  -- Expandable
);

-- Indexes
CREATE INDEX idx_custom_field_defs_tenant ON custom_field_definitions(tenant_id);
CREATE INDEX idx_custom_field_defs_entity ON custom_field_definitions(tenant_id, entity_type);

-- RLS
ALTER TABLE custom_field_definitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON custom_field_definitions
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Trigger
CREATE TRIGGER update_custom_field_defs_updated_at
    BEFORE UPDATE ON custom_field_definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 8. AuditLog (Log de Auditoria)

Audit trail for critical operations.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- NULL if user deleted
    
    -- What was changed
    entity_type VARCHAR(50) NOT NULL,  -- 'product', 'user', 'tenant', 'movement'
    entity_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,       -- 'create', 'update', 'delete'
    
    -- Change details
    changes JSONB,  -- {"field": {"old": "value", "new": "value"}}
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT action_values CHECK (action IN ('create', 'update', 'delete')),
    CONSTRAINT entity_type_values CHECK (entity_type IN ('product', 'user', 'tenant', 'movement', 'category'))
);

-- Indexes
CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(tenant_id, entity_type, entity_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(tenant_id, user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(tenant_id, created_at DESC);

-- RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON audit_logs
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
```

---

## Helper Functions

### Update Timestamp Trigger Function

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## Entity Relationship Diagram (ERD)

```
┌──────────────┐
│   Tenant     │
│--------------│
│ id (PK)      │◄────┐
│ slug (UQ)    │     │
│ name         │     │
│ logo_url     │     │
│ colors       │     │
└──────────────┘     │
                     │
      ┌──────────────┼──────────────┬──────────────┬──────────────┐
      │              │              │              │              │
┌─────▼──────┐ ┌────▼────────┐ ┌──▼──────────┐ ┌─▼────────────┐ ┌▼─────────────────┐
│   User     │ │  Product    │ │  Category   │ │  Alert       │ │ CustomFieldDef   │
│------------│ │-------------│ │-------------│ │--------------│ │------------------│
│ id (PK)    │ │ id (PK)     │ │ id (PK)     │ │ id (PK)      │ │ id (PK)          │
│ tenant_id  │ │ tenant_id   │ │ tenant_id   │ │ tenant_id    │ │ tenant_id        │
│ email      │ │ category_id ├─┤ name        │ │ product_id   │ │ field_name       │
│ role       │ │ sku (UQ)    │ └─────────────┘ │ alert_type   │ │ field_type       │
└────┬───────┘ │ name        │                 └──────────────┘ └──────────────────┘
     │         │ quantity    │
     │         │ custom_flds │
     │         └─────┬───────┘
     │               │
     │         ┌─────▼────────┐
     │         │  Movement    │
     │         │--------------│
     │         │ id (PK)      │
     │         │ tenant_id    │
     └────────►│ user_id      │
               │ product_id   │
               │ type         │
               │ quantity     │
               └──────────────┘
                      │
               ┌──────▼────────┐
               │  AuditLog     │
               │---------------│
               │ id (PK)       │
               │ tenant_id     │
               │ user_id       │
               │ entity_type   │
               │ action        │
               │ changes       │
               └───────────────┘
```

---

## Database Migrations Strategy

**Tool**: Alembic

**Migration Workflow**:
1. Generate migration: `alembic revision --autogenerate -m "description"`
2. Review generated SQL
3. Test on development database
4. Apply to production: `alembic upgrade head`

**Initial Migration** (001_initial_schema.py):
```python
def upgrade():
    # Create uuid extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create all tables (tenants first, then dependent tables)
    # Enable RLS on all tenant-scoped tables
    # Create indexes
    # Create triggers
    pass

def downgrade():
    # Drop all tables in reverse order
    pass
```

---

## Data Validation Rules

### Product
- SKU: Max 100 chars, unique per tenant, alphanumeric + hyphens
- Name: Required, max 200 chars
- Quantity: Decimal(15,3), allows negative for backorders
- Price: Decimal(15,2), >= 0

### User
- Email: Valid email format, unique per tenant
- Password: Min 8 chars, hashed with bcrypt
- Role: Must be admin/manager/operator

### Movement
- Quantity: Must be positive
- Type: Must be inbound/outbound
- Product: Must exist and be active

### Custom Fields
- Field name: snake_case, max 50 chars
- Field type: text/number/date/select
- Options: Required for select type

---

## Performance Considerations

### Query Optimization
- All tenant-scoped queries use composite indexes (tenant_id + query field)
- RLS policies automatically filter by tenant_id
- Pagination mandatory for lists > 50 items
- Use EXPLAIN ANALYZE for slow queries (> 100ms)

### Indexing Strategy
- Composite indexes on frequently filtered columns
- GIN index on JSONB custom_fields for queries
- Partial indexes on status='active' for common filters

### Connection Pooling
- SQLAlchemy pool size: 20-50 connections
- Connection timeout: 30s
- Recycle connections every hour

---

## Security Measures

### Row-Level Security (RLS)
- All tenant-scoped tables have RLS enabled
- Policy: `tenant_id = current_setting('app.current_tenant_id')::UUID`
- Set context per request: `SET app.current_tenant_id = '{uuid}'`

### Password Security
- Bcrypt hashing with 12 rounds
- Salting automatic
- Never store plain text

### SQL Injection Prevention
- All queries parameterized
- SQLAlchemy ORM handles escaping
- User input validated via Pydantic

---

## Data Retention & Archival

### Soft Deletes
- Products: `status = 'inactive'` instead of DELETE
- Users: `status = 'inactive'` instead of DELETE
- Preserves audit trail and historical data

### Audit Logs
- Retain indefinitely (or per compliance requirements)
- Archive logs >1 year to separate table/storage

### Movements
- Never delete (immutable ledger)
- Archive old movements (>2 years) if performance degrades

---

## Backup & Recovery

### Backup Strategy
- **Daily**: Full backup at 2 AM UTC
- **Retention**: 30 days
- **Tool**: `pg_dump` or cloud provider backup (AWS RDS automated backups)

### Recovery Procedure
- RTO: 24 hours (manual restore acceptable)
- RPO: 24 hours (daily backup, data since last backup may be lost)
- Test restore procedure quarterly

---

## Future Enhancements

1. **Partitioning**: Partition movements table by date for performance at scale
2. **Read Replicas**: For read-heavy operations (reports, exports)
3. **Archival Storage**: Move old audit logs to cold storage (S3 Glacier)
4. **CQRS**: Separate read/write models for complex queries
5. **Event Sourcing**: For complete audit trail of state changes

---

## Summary

- **8 Core Tables**: Tenant, User, Category, Product, Movement, Alert, CustomFieldDefinition, AuditLog
- **Multi-Tenant Isolation**: PostgreSQL RLS with tenant_id context
- **Performance**: Comprehensive indexing, connection pooling, query optimization
- **Security**: RLS, password hashing, parameterized queries, soft deletes
- **Scalability**: Supports 100 tenants, 100k products/tenant, 1M movements total
- **Audit Trail**: Complete history via audit_logs and immutable movements

**Database ready for implementation!**
