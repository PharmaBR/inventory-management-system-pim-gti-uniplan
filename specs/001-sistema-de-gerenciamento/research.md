# Research: Sistema de Gerenciamento de Estoque White Label

**Feature**: 001-sistema-de-gerenciamento  
**Date**: 2025-10-07  
**Phase**: 0 - Architecture & Technology Research

## Overview

Este documento consolida as decisões arquiteturais e pesquisas técnicas necessárias para implementar um sistema de gerenciamento de estoque white label multi-tenant com isolamento de dados, personalização de marca e performance escalável.

## Research Topics

### 1. Multi-Tenancy Architecture Pattern

**Question**: Qual padrão de multi-tenancy usar para isolar dados de 100+ tenants?

**Research Findings**:

Três padrões principais avaliados:

1. **Database per Tenant**: Banco de dados separado para cada tenant
   - **Pros**: Isolamento máximo, backup/restore independente, fácil escalar por tenant
   - **Cons**: Alto custo de infraestrutura, complexidade de migração, limite de conexões
   
2. **Schema per Tenant**: Schema/namespace separado por tenant no mesmo DB
   - **Pros**: Bom isolamento, menor custo que DB separado
   - **Cons**: Complexidade de migração, connection pooling complicado, PostgreSQL limit de schemas
   
3. **Shared Schema with Tenant ID**: Todas tabelas têm coluna `tenant_id`
   - **Pros**: Simples, eficiente para queries, easy migrations, connection pooling eficiente
   - **Cons**: Risco de data leakage se query esquecer WHERE tenant_id, índices maiores

**Decision**: **Shared Schema with Tenant ID** (Row-Level Security approach)

**Rationale**:
- PostgreSQL Row-Level Security (RLS) policies garantem isolamento automático
- Suporta 100+ tenants sem overhead de schemas/databases múltiplos
- Migrations aplicam uniformemente para todos tenants
- Connection pooling eficiente (single database)
- Backup/restore simplificado
- Queries são filtradas automaticamente por RLS policies, reduzindo risco de data leakage
- Cost-effective para escala target (100 tenants)

**Implementation Strategy**:
```sql
-- Todas as tabelas incluem tenant_id
CREATE TABLE products (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    sku VARCHAR(100) NOT NULL,
    -- outros campos
    UNIQUE(tenant_id, sku)  -- Unicidade dentro do tenant
);

-- Row-Level Security policy
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON products
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Set tenant context na sessão
SET app.current_tenant_id = '<tenant-uuid>';
```

**Alternatives Considered**:
- Database-per-tenant: Rejeitado pelo custo (100 DBs) e complexidade de migrations
- Schema-per-tenant: Rejeitado pela complexidade e limite de schemas do PostgreSQL

**References**:
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-tenancy Patterns (AWS)](https://docs.aws.amazon.com/whitepapers/latest/saas-architecture-fundamentals/multi-tenancy-models.html)

---

### 2. Subdomain-Based Tenant Identification

**Question**: Como implementar identificação de tenant por subdomínio (tenant1.sistema.com)?

**Research Findings**:

**DNS Configuration**:
- Wildcard DNS record: `*.sistema.com` → Load Balancer IP
- Cada tenant registrado com slug único (validado: lowercase, alphanumeric, hyphens)
- Admin cria tenant → gera slug → subdomínio disponível imediatamente

**Backend Implementation**:
```python
# Middleware FastAPI para extrair tenant do host header
async def tenant_identification_middleware(request: Request, call_next):
    host = request.headers.get("host", "")
    subdomain = host.split(".")[0] if "." in host else None
    
    if not subdomain or subdomain in ["www", "api", "admin"]:
        # Redirecionar para página de seleção de tenant ou erro
        return Response("Tenant not identified", status_code=400)
    
    # Buscar tenant no DB por slug
    tenant = await get_tenant_by_slug(subdomain)
    if not tenant or tenant.status != "active":
        return Response("Tenant not found or inactive", status_code=404)
    
    # Injetar tenant no request state
    request.state.tenant = tenant
    
    # Set PostgreSQL RLS context
    await db.execute(f"SET app.current_tenant_id = '{tenant.id}'")
    
    response = await call_next(request)
    return response
```

**Frontend Implementation**:
- Detect subdomain on load
- Store tenant context in React Context/Zustand
- Apply tenant-specific branding (logo, colors from API `/tenant/config`)
- All API calls include tenant context automatically

**Decision**: **Middleware-based subdomain extraction with RLS context**

**Rationale**:
- Clean user experience (empresa1.sistema.com isolates automatically)
- No tenant selection UI needed (subdomain = tenant)
- Middleware ensures every request has tenant context
- RLS policies enforce isolation at database level
- Easy to add tenant-specific rate limiting/quotas

**Edge Cases Handled**:
- Invalid subdomain → 404 error page with helpful message
- Inactive tenant → maintenance page
- Missing subdomain (direct IP access) → redirect to www
- Reserved subdomains (www, api, admin, app) → special handling

**References**:
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Subdomain routing patterns](https://www.nginx.com/blog/subdomain-routing/)

---

### 3. Custom Fields Storage Strategy

**Question**: Como implementar campos customizados configuráveis por tenant (lote, validade, etc)?

**Research Findings**:

**Options Evaluated**:

1. **EAV (Entity-Attribute-Value)**: Tabelas separadas para attributes
   - **Pros**: Flexível, queryable
   - **Cons**: Complexo, performance ruim, muitos JOINs
   
2. **JSONB Column**: Store custom fields em JSONB
   - **Pros**: Simples, performante com GIN index, schema-less
   - **Cons**: Validação manual, sem foreign keys
   
3. **Dynamic Columns**: ALTER TABLE por tenant
   - **Pros**: Type-safe, queryable
   - **Cons**: Schema explosion, migration nightmare

**Decision**: **JSONB Column** com validação em application layer

**Rationale**:
- PostgreSQL JSONB é performante com GIN indexes
- Permite queries: `WHERE custom_fields->>'lote' = '12345'`
- Schema permanece simples (single column)
- Validação via Pydantic schemas dinamicamente construídos
- Metadata de custom fields armazenado em tabela `custom_field_definitions`

**Implementation**:
```python
# Model
class Product(Base):
    __tablename__ = "products"
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    sku = Column(String(100), nullable=False)
    custom_fields = Column(JSONB, default={})  # {"lote": "ABC123", "validade": "2025-12-31"}
    
# Custom field definition (per tenant)
class CustomFieldDefinition(Base):
    __tablename__ = "custom_field_definitions"
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    field_name = Column(String(50))  # "lote"
    field_type = Column(String(20))  # "text", "number", "date", "select"
    is_required = Column(Boolean, default=False)
    options = Column(JSONB)  # For "select" type: ["opt1", "opt2"]
    
# Dynamic validation
def validate_custom_fields(product_data, tenant_id):
    field_defs = get_custom_field_definitions(tenant_id)
    for field_def in field_defs:
        if field_def.is_required and field_def.field_name not in product_data.custom_fields:
            raise ValidationError(f"{field_def.field_name} is required")
        # Type validation based on field_def.field_type
```

**Query Performance**:
- GIN index on `custom_fields`: `CREATE INDEX idx_product_custom_fields ON products USING GIN (custom_fields);`
- Queries: `WHERE custom_fields @> '{"lote": "ABC123"}'` (containment operator)

**References**:
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [JSONB Indexing](https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING)

---

### 4. File Import Strategy (Transactional)

**Question**: Como implementar importação CSV/Excel transacional (all-or-nothing)?

**Research Findings**:

**Approach**: Two-phase import with pre-validation

**Phase 1 - Validation** (No DB writes):
1. Parse CSV/Excel file (pandas/openpyxl)
2. Validate EVERY row:
   - Schema validation (required fields, types)
   - Business rules (SKU uniqueness, foreign keys)
   - Custom field validation
3. Collect ALL errors with line numbers
4. If ANY error → return error report, reject file

**Phase 2 - Import** (Transactional):
1. BEGIN transaction
2. Bulk insert valid rows (SQLAlchemy bulk operations)
3. COMMIT if successful, ROLLBACK on any error
4. Return success report with count

**Implementation**:
```python
async def import_products_csv(file: UploadFile, tenant_id: UUID):
    # Phase 1: Parse and validate
    df = pd.read_csv(file.file)
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Validate row schema
            ProductImportSchema(**row.to_dict())
            # Validate business rules
            if await product_exists(row['sku'], tenant_id):
                errors.append({"line": idx+2, "error": f"SKU {row['sku']} already exists"})
        except ValidationError as e:
            errors.append({"line": idx+2, "error": str(e)})
    
    if errors:
        return {"status": "error", "errors": errors}
    
    # Phase 2: Transactional insert
    async with db.begin():  # Auto rollback on exception
        products = [Product(**row.to_dict(), tenant_id=tenant_id) for _, row in df.iterrows()]
        db.add_all(products)
        await db.commit()
    
    return {"status": "success", "imported": len(df)}
```

**Decision**: **Two-phase validation + transaction**

**Rationale**:
- Meets FR-021 requirement (validate ALL lines before insert)
- Prevents partial imports (all-or-nothing guarantee)
- Clear error reporting with line numbers
- Performance acceptable for reasonable file sizes (<10k rows)

**Performance Considerations**:
- For files >10k rows, consider async validation with progress updates
- Batch validation in chunks to avoid memory issues
- Timeout limits on import operations

**References**:
- [SQLAlchemy Bulk Operations](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-bulk-insert-statements)
- [Pandas CSV Parsing](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

---

### 5. Performance Optimization Strategies

**Question**: Como atingir p95 < 200ms para 1000 req/s com 100 tenants?

**Research Findings**:

**Database Optimizations**:

1. **Indexing Strategy**:
```sql
-- Composite indexes for common queries
CREATE INDEX idx_products_tenant_sku ON products(tenant_id, sku);
CREATE INDEX idx_products_tenant_name ON products(tenant_id, name);
CREATE INDEX idx_movements_tenant_product_date ON movements(tenant_id, product_id, created_at DESC);
CREATE INDEX idx_products_tenant_category ON products(tenant_id, category_id);

-- Partial indexes for active records
CREATE INDEX idx_products_active ON products(tenant_id) WHERE status = 'active';
```

2. **Connection Pooling**:
- SQLAlchemy pool: 20-50 connections
- Async engine (asyncpg) for non-blocking IO
- Connection timeout: 30s, recycle: 3600s

3. **Query Optimization**:
- Use `select_in_loading` for relationships (avoid N+1)
- Eager loading for frequently accessed relations
- EXPLAIN ANALYZE for slow queries

**Caching Strategy**:

1. **Redis Cache**:
```python
# Cache tenant config (logo, colors) - 1 hour TTL
@cache(ttl=3600)
async def get_tenant_config(tenant_id):
    return await db.query(Tenant).filter_by(id=tenant_id).first()

# Cache product counts - 5 min TTL
@cache(ttl=300)
async def get_product_count(tenant_id):
    return await db.query(Product).filter_by(tenant_id=tenant_id).count()
```

2. **HTTP Caching**:
- `Cache-Control` headers for static assets
- ETags for API responses
- CDN for frontend assets

**API Optimizations**:

1. **Pagination**:
- Default 50 items/page, max 100
- Cursor-based pagination for large datasets
- Count queries cached

2. **Response Compression**:
- Gzip/Brotli compression for responses >1KB
- FastAPI `GZipMiddleware`

3. **Async Processing**:
- Background tasks for exports (Celery/RQ)
- Async report generation
- Webhook notifications async

**Decision**: **Layered caching + database optimization + async processing**

**Rationale**:
- Indexing covers 90% of queries (tenant_id + frequent filters)
- Redis cache reduces DB load for hot data (tenant configs)
- Async processing prevents blocking on heavy operations
- Pagination mandatory prevents expensive full table scans

**Monitoring**:
- Prometheus metrics: request_duration, db_query_duration, cache_hit_rate
- Slow query logging (>100ms)
- Alerts on p95 > 250ms

**References**:
- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/performance/)
- [PostgreSQL Index Tuning](https://www.postgresql.org/docs/current/indexes.html)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)

---

### 6. Authentication & Security

**Question**: Como implementar autenticação segura com password hashing e JWT?

**Research Findings**:

**Password Hashing**:
- **Library**: passlib with bcrypt backend
- **Rounds**: 12 (balance between security and performance)
- **Salting**: Automatic per passlib

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**JWT Authentication**:
- **Library**: python-jose
- **Algorithm**: HS256 (symmetric) for MVP, RS256 (asymmetric) for production scale
- **Token Lifetime**: Access token 15min, Refresh token 7 days
- **Claims**: tenant_id, user_id, role

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

**Security Headers**:
- CORS: Restrictive origins (only tenant subdomains)
- CSP: Content-Security-Policy headers
- HSTS: HTTP Strict Transport Security
- X-Frame-Options: DENY

**Decision**: **Bcrypt + JWT with refresh tokens**

**Rationale**:
- Bcrypt widely vetted, resistant to rainbow tables
- JWT stateless, scales well (no session storage)
- Refresh tokens allow short-lived access tokens (security)
- Tenant context in JWT eliminates DB lookup per request

**References**:
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

### 7. Internationalization (i18n) Implementation

**Question**: Como implementar suporte a PT-BR e EN-US extensível para mais idiomas?

**Research Findings**:

**Backend i18n**:
- Error messages, validation errors traduzidos
- Accept-Language header detection
- Fallback para PT-BR se idioma não suportado

**Frontend i18n**:
- **Library**: react-i18next
- **Structure**:
```
src/i18n/
  ├── pt-BR.json
  ├── en-US.json
  └── config.ts
```

**Translation Files**:
```json
// pt-BR.json
{
  "products": {
    "title": "Produtos",
    "add": "Adicionar Produto",
    "sku": "Código SKU",
    "errors": {
      "sku_duplicate": "SKU já existe"
    }
  }
}

// en-US.json
{
  "products": {
    "title": "Products",
    "add": "Add Product",
    "sku": "SKU Code",
    "errors": {
      "sku_duplicate": "SKU already exists"
    }
  }
}
```

**Usage**:
```tsx
import { useTranslation } from 'react-i18next';

function ProductList() {
  const { t } = useTranslation();
  return <h1>{t('products.title')}</h1>;
}
```

**Decision**: **react-i18next with JSON translation files**

**Rationale**:
- Industry standard, widely supported
- Lazy loading of translation files (performance)
- Pluralization, interpolation built-in
- Easy to add languages (drop in new JSON file)
- Type-safe with TypeScript

**References**:
- [react-i18next Documentation](https://react.i18next.com/)
- [i18n Best Practices](https://phrase.com/blog/posts/i18n-best-practices/)

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+ (async)
- **Database**: PostgreSQL 15+ with Row-Level Security
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: python-jose (JWT), passlib (bcrypt)
- **Caching**: Redis 7+
- **Task Queue**: Celery + Redis (for async exports)
- **Testing**: pytest, pytest-asyncio, pytest-cov, httpx

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: TailwindCSS + Shadcn/ui
- **State Management**: Zustand (lightweight) or React Context
- **API Client**: Axios with interceptors
- **i18n**: react-i18next
- **Forms**: React Hook Form + Zod validation
- **Testing**: Vitest (unit), Playwright (e2e)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (subdomain routing, HTTPS termination)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs, ELK stack optional

### Development Tools
- **Linting**: Ruff (Python), ESLint (TypeScript)
- **Formatting**: Black (Python), Prettier (TypeScript)
- **Pre-commit Hooks**: pre-commit framework
- **API Documentation**: FastAPI auto-generated OpenAPI/Swagger

---

## Architecture Decision Records (ADRs)

### ADR-001: Shared Schema Multi-Tenancy with RLS
**Status**: Accepted  
**Context**: Need to isolate 100+ tenant data securely and cost-effectively  
**Decision**: PostgreSQL Row-Level Security with tenant_id column  
**Consequences**: Simpler migrations, efficient queries, requires careful RLS policy management

### ADR-002: Subdomain-Based Tenant Identification
**Status**: Accepted  
**Context**: White label branding requires clean tenant separation  
**Decision**: Wildcard DNS + middleware tenant extraction  
**Consequences**: Clean UX, requires DNS management, tenant slugs must be unique

### ADR-003: JSONB for Custom Fields
**Status**: Accepted  
**Context**: Tenants need configurable product fields without schema changes  
**Decision**: PostgreSQL JSONB column with application-layer validation  
**Consequences**: Flexible, performant with GIN index, requires dynamic schema validation

### ADR-004: Transactional File Import
**Status**: Accepted  
**Context**: Data integrity critical for inventory management  
**Decision**: Two-phase validation + single transaction for imports  
**Consequences**: All-or-nothing guarantee, slower for large files, clear error reporting

### ADR-005: JWT Stateless Authentication
**Status**: Accepted  
**Context**: Need to scale authentication across multiple backend instances  
**Decision**: JWT with short-lived access tokens + refresh tokens  
**Consequences**: Stateless (scales well), token revocation harder, requires secret management

---

## Open Questions / Future Research

1. **Backup Strategy**: Need to define automated backup schedule and restore procedure (RTO < 24h requirement)
2. **Rate Limiting**: Per-tenant rate limiting strategy to prevent resource abuse
3. **Email Service**: Notification system for alerts (Sendgrid? AWS SES?) - deferred to post-MVP
4. **File Storage**: Product images storage (S3? CloudFlare R2?) - need cost analysis
5. **Mobile App**: PWA vs Native app for future mobile support

---

## Next Steps

With research complete, proceed to:
1. **Phase 1**: Generate `data-model.md` with detailed database schema
2. **Phase 1**: Generate API contracts in `contracts/` directory
3. **Phase 1**: Create `quickstart.md` for development environment setup
4. **Phase 2**: Generate `tasks.md` with implementation task breakdown
