# 🏛️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Browser  │  │   Mobile   │  │  Desktop   │            │
│  │    (Web)   │  │    App     │  │    App     │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │                │                │                   │
│        └────────────────┴────────────────┘                   │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │ HTTP/REST
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                    Frontend Layer (React)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              UI Components (Tailwind)                 │   │
│  │  Button │ Input │ Modal │ Toast │ Header │ Sidebar   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │                  Custom Hooks                         │   │
│  │            useAuth │ useTenant │ useQuery             │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              API Client (Axios)                       │   │
│  │  Interceptors: JWT Injection │ Token Refresh         │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │ HTTP/REST + JSON
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                   API Gateway (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Middleware Pipeline                  │   │
│  │  CORS → Tenant → Auth → Error Handler → Logging      │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │                   Route Handlers                      │   │
│  │  /products │ /movements │ /alerts │ /users │ /auth   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              Dependency Injection                     │   │
│  │    get_db │ get_current_user │ get_current_tenant    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼─────────┐              ┌──────────▼────────┐
│ Business Layer  │              │  Infrastructure   │
├─────────────────┤              ├───────────────────┤
│                 │              │                   │
│  ┌───────────┐  │              │  ┌─────────────┐ │
│  │ Services  │  │              │  │   Logging   │ │
│  │           │  │              │  │ (Structured)│ │
│  │ Product   │  │              │  └─────────────┘ │
│  │ Movement  │  │              │                   │
│  │ Alert     │  │              │  ┌─────────────┐ │
│  │ User      │  │              │  │   Cache     │ │
│  │ Tenant    │  │              │  │   (Redis)   │ │
│  └─────┬─────┘  │              │  └──────┬──────┘ │
│        │        │              │         │        │
└────────┼────────┘              └─────────┼────────┘
         │                                 │
         │                                 │
┌────────▼─────────────────────────────────▼────────┐
│              Data Layer (SQLAlchemy)              │
├───────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐│
│  │                 ORM Models                    ││
│  │  Tenant │ User │ Product │ Movement │ Alert  ││
│  │  Category │ CustomField │ AuditLog           ││
│  └────────────────────┬─────────────────────────┘│
│                       │                           │
│  ┌────────────────────▼─────────────────────────┐│
│  │          Database Migrations (Alembic)       ││
│  └──────────────────────────────────────────────┘│
│                                                    │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│           PostgreSQL 15 + Row-Level Security       │
│              (Multi-tenant Data Isolation)         │
└────────────────────────────────────────────────────┘
```

## Request Flow

### 1. Multi-Tenant Request

```
Client (tenant1.app.com)
    │
    ▼
Frontend (Extract tenant from subdomain)
    │
    ▼
API Request (Header: X-Tenant-Slug: tenant1)
    │
    ▼
TenantMiddleware
    ├─ Extract tenant from subdomain/query/header
    ├─ Validate slug format
    └─ Store in request.state.tenant_slug
    │
    ▼
AuthMiddleware
    ├─ Extract JWT from Authorization header
    ├─ Validate token signature and expiration
    ├─ Decode user_id and tenant_id
    └─ Store user info in request state
    │
    ▼
Route Handler
    │
    ▼
Dependency Injection
    ├─ get_current_tenant() → Query tenant from DB
    ├─ get_current_user() → Query user from DB
    └─ get_db() → Provide async session
    │
    ▼
Service Layer
    ├─ Business logic
    ├─ Validation
    └─ RLS enforcement (tenant_id filter)
    │
    ▼
Database Query (with tenant_id filter)
    │
    ▼
PostgreSQL (Row-Level Security applied)
    │
    ▼
Response (JSON)
```

### 2. Authentication Flow

```
User Login Form
    │
    ▼
POST /api/v1/auth/login
    { email, password }
    │
    ▼
AuthService.login()
    ├─ Find user by email + tenant_id
    ├─ Verify password with bcrypt
    ├─ Generate access_token (15min)
    ├─ Generate refresh_token (7 days)
    └─ Create AuditLog entry
    │
    ▼
Response
    {
      access_token: "eyJ...",
      refresh_token: "eyJ...",
      token_type: "bearer",
      user: { id, email, role }
    }
    │
    ▼
Frontend
    ├─ Store tokens in localStorage
    ├─ Set Axios default headers
    └─ Redirect to dashboard
```

### 3. Token Refresh Flow

```
API Request with expired token
    │
    ▼
Response: 401 Unauthorized
    │
    ▼
Axios Response Interceptor
    ├─ Detect 401 error
    ├─ Extract refresh_token from localStorage
    └─ POST /api/v1/auth/refresh
    │
    ▼
AuthService.refresh()
    ├─ Validate refresh_token
    ├─ Generate new access_token
    └─ Return new token pair
    │
    ▼
Update localStorage
    │
    ▼
Retry original request with new token
```

## Data Flow

### Product Creation

```
ProductForm (Frontend)
    │
    ▼
Validation (Pydantic schema)
    │
    ▼
POST /api/v1/products
    {
      sku: "ABC123",
      name: "Product Name",
      category_id: "uuid",
      quantity: 100,
      unit_price: 99.90
    }
    │
    ▼
ProductService.create()
    ├─ Validate SKU uniqueness (within tenant)
    ├─ Check category exists (same tenant)
    ├─ Create product record
    ├─ Create initial movement (entry)
    ├─ Create AuditLog entry
    └─ Invalidate cache (tenant:products:*)
    │
    ▼
Database Transaction
    ├─ INSERT INTO products (with tenant_id)
    ├─ INSERT INTO movements
    └─ INSERT INTO audit_logs
    │
    ▼
Response: 201 Created
    {
      id: "uuid",
      sku: "ABC123",
      name: "Product Name",
      quantity: 100,
      ...
    }
```

## Technology Stack Layers

### Presentation Layer
- **React 18** - UI library with concurrent features
- **TypeScript 5.3** - Type safety and better DX
- **Vite 5** - Fast build tool with HMR
- **TailwindCSS 3** - Utility-first CSS framework
- **react-i18next** - Internationalization (PT-BR, EN-US)

### API Layer
- **FastAPI 0.104** - Modern async Python framework
- **Pydantic 2.0** - Data validation with type hints
- **Uvicorn** - ASGI server with async support

### Business Logic Layer
- **Services** - Domain logic and orchestration
- **Validators** - Business rules enforcement
- **Mappers** - DTO transformations

### Data Access Layer
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **AsyncPG** - High-performance PostgreSQL driver

### Infrastructure Layer
- **PostgreSQL 15** - Relational database with RLS
- **Redis 7** - In-memory cache and sessions
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration

### Security Layer
- **JWT** - Stateless authentication
- **Bcrypt** - Password hashing (12 rounds)
- **CORS** - Cross-origin resource sharing
- **HTTPS** - TLS/SSL encryption (production)

## Deployment Architecture (Production)

```
┌──────────────────────────────────────────────────────┐
│                    Load Balancer                     │
│                  (NGINX / AWS ALB)                   │
└───────────────────┬──────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌─────────▼───────┐
│  Frontend CDN  │    │   API Servers   │
│  (Static files)│    │   (FastAPI)     │
│                │    │   ┌──────────┐  │
│  - React build │    │   │ Instance │  │
│  - Images      │    │   │    1     │  │
│  - CSS/JS      │    │   └──────────┘  │
└────────────────┘    │   ┌──────────┐  │
                      │   │ Instance │  │
                      │   │    2     │  │
                      │   └──────────┘  │
                      │   ┌──────────┐  │
                      │   │ Instance │  │
                      │   │    N     │  │
                      │   └──────────┘  │
                      └────────┬────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
          ┌─────────▼────────┐  ┌────────▼─────────┐
          │   PostgreSQL     │  │      Redis       │
          │   (Primary)      │  │   (Cluster)      │
          │                  │  │                  │
          │   ┌──────────┐   │  │   ┌──────────┐  │
          │   │ Replica  │   │  │   │  Node 1  │  │
          │   │    1     │   │  │   └──────────┘  │
          │   └──────────┘   │  │   ┌──────────┐  │
          │   ┌──────────┐   │  │   │  Node 2  │  │
          │   │ Replica  │   │  │   └──────────┘  │
          │   │    2     │   │  │   ┌──────────┐  │
          │   └──────────┘   │  │   │  Node 3  │  │
          └──────────────────┘  │   └──────────┘  │
                                └──────────────────┘
```

## Security Architecture

### Defense in Depth

```
Layer 1: Network Security
├─ HTTPS/TLS 1.3 encryption
├─ Rate limiting (1000 req/min per IP)
├─ DDoS protection
└─ Firewall rules

Layer 2: Application Security
├─ JWT token authentication
├─ Role-based access control (RBAC)
├─ Input validation (Pydantic)
├─ SQL injection prevention (ORM)
├─ XSS protection (React escaping)
└─ CSRF tokens

Layer 3: Data Security
├─ Row-Level Security (RLS) in PostgreSQL
├─ Tenant data isolation
├─ Password hashing (Bcrypt, 12 rounds)
├─ Sensitive data encryption at rest
└─ Audit logging

Layer 4: Infrastructure Security
├─ Container isolation (Docker)
├─ Secret management (env variables)
├─ Principle of least privilege
└─ Regular security updates
```

## Monitoring & Observability

```
┌────────────────────────────────────────┐
│          Application Metrics           │
├────────────────────────────────────────┤
│  - Request rate (req/s)                │
│  - Response time (p50, p95, p99)       │
│  - Error rate (%)                      │
│  - Active users                        │
│  - Cache hit rate                      │
└───────────────┬────────────────────────┘
                │
┌───────────────▼────────────────────────┐
│           Structured Logs              │
├────────────────────────────────────────┤
│  - JSON formatted                      │
│  - Correlation IDs (request_id)        │
│  - Tenant/User context                 │
│  - Error stack traces                  │
│  - Performance metrics                 │
└───────────────┬────────────────────────┘
                │
┌───────────────▼────────────────────────┐
│         Database Monitoring            │
├────────────────────────────────────────┤
│  - Connection pool usage               │
│  - Slow query log (> 100ms)            │
│  - Index usage statistics              │
│  - Table sizes and growth              │
│  - Replication lag                     │
└────────────────────────────────────────┘
```

## Scalability Strategy

### Horizontal Scaling

- **API Servers**: Stateless design allows easy scaling
- **Database**: Read replicas for query distribution
- **Redis**: Cluster mode for distributed caching
- **Frontend**: CDN distribution worldwide

### Vertical Scaling

- **Database**: Increase CPU/RAM for complex queries
- **Redis**: Increase memory for larger cache
- **API**: Increase workers for CPU-bound operations

### Performance Optimizations

1. **Database**
   - Indexes on frequently queried columns (55 indexes)
   - Connection pooling (pool_size=10, max_overflow=20)
   - Query optimization with EXPLAIN ANALYZE
   - Materialized views for complex reports

2. **Caching**
   - Tenant configurations (TTL: 1 hour)
   - User sessions (TTL: 15 minutes)
   - Product catalog (TTL: 5 minutes)
   - Pattern-based invalidation

3. **API**
   - Async I/O for concurrent requests
   - Response compression (gzip)
   - Pagination for large datasets
   - Field selection (sparse fieldsets)

4. **Frontend**
   - Code splitting and lazy loading
   - Image optimization and lazy loading
   - Service worker caching
   - Bundle size < 500kb

---

**Architecture Version**: 0.2.0 (Phase 2 Complete)  
**Last Updated**: October 14, 2025
