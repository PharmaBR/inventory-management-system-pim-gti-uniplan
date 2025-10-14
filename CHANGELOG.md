# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 3: User Story 1 - Products (Planned)
- Products CRUD API endpoints
- Product management UI
- Custom fields support
- Category assignment
- Stock quantity tracking

## [0.2.0] - 2025-10-14

### Phase 2: Foundational Infrastructure ✅

#### Added - Backend
- **Database Layer**
  - SQLAlchemy 2.0 async engine with connection pooling (pool_size=10, max_overflow=20)
  - 8 ORM models with full relationships and 55 indexes:
    - `Tenants` - Client configurations with branding and limits
    - `Users` - RBAC (admin/manager/operator) with password hashing
    - `Categories` - Hierarchical product categorization
    - `Products` - Inventory items with JSONB custom fields (GIN indexed)
    - `Movements` - Stock movement tracking (entry/exit/adjustment/transfer)
    - `Alerts` - Stock notifications (low_stock/out_of_stock/expiring_soon)
    - `CustomFieldDefinitions` - Dynamic field schema definitions
    - `AuditLogs` - Complete change tracking with before/after snapshots
  - Alembic migration system with async support
  - Database initialization on startup (development mode only)

- **Authentication & Security**
  - JWT token system with access (15min) and refresh (7 days) tokens
  - Bcrypt password hashing with passlib
  - Token creation and verification utilities
  - Token response builder for login endpoints

- **Middleware Pipeline**
  - **TenantMiddleware**: Multi-tenant identification via subdomain/query/header
    - Subdomain extraction (tenant1.sistema.com → tenant1)
    - Query parameter fallback (?tenant=tenant1)
    - Custom header support (X-Tenant-Slug)
    - Slug format validation (alphanumeric + hyphens, 3-100 chars)
  - **AuthMiddleware**: JWT validation and RBAC enforcement
    - HTTPBearer security scheme
    - Token extraction and validation
    - Role-based access control decorators
  - **ErrorHandlerMiddleware**: Global exception handling
    - HTTP exceptions (400, 404, etc.)
    - Pydantic validation errors (422)
    - Database integrity errors (409)
    - SQLAlchemy errors (500)
    - Catch-all exception handler

- **Dependency Injection**
  - `get_db()` - Async database session with auto commit/rollback
  - `get_current_user()` - Full user object from database
  - `get_current_user_id()` - Lightweight user ID extraction
  - `get_current_tenant()` - Tenant object from database
  - `get_current_tenant_id()` - Tenant ID extraction
  - `validate_tenant_access()` - Cross-tenant prevention
  - `ensure_tenant_user_match()` - Combined validation

- **Infrastructure**
  - **Redis Caching**:
    - Async Redis client with connection pooling (max 50)
    - Cache helper class with get/set/delete/invalidate_pattern
    - Key builders for tenant/product/user caching
    - Default TTL of 3600s (1 hour)
  - **Structured Logging**:
    - JSON formatter for production logs
    - Pretty printing for development
    - Custom fields (tenant_id, user_id, request_id)
    - Configurable log levels
  - **Base Pydantic Schemas**:
    - BaseSchema with common config
    - TimestampSchema with created_at/updated_at
    - IdentifiedSchema with ID + timestamps
    - PaginationParams with offset/limit calculation
    - PaginatedResponse[T] generic type
    - StatusResponse, ErrorResponse, DataResponse[T]

- **Application Lifecycle**
  - Lifespan context manager for startup/shutdown events
  - Database initialization on startup (development only)
  - Redis client setup
  - Graceful shutdown with connection cleanup

#### Added - Frontend
- **Internationalization (i18n)**
  - react-i18next configuration
  - Portuguese (PT-BR) translations (complete)
  - English (EN-US) translations (complete)
  - Browser language detection
  - LocalStorage persistence
  - Fallback to PT-BR
  - Translation namespaces: common, auth, products, movements, alerts, validation, errors

- **UI Component Library**
  - **Button**: 4 variants (primary/secondary/danger/ghost), 3 sizes (sm/md/lg), loading state with spinner
  - **Input**: Label support, error/helper text, required indicator, focus states
  - **Modal**: 4 sizes (sm/md/lg/xl), ESC key close, backdrop click close, header/body/footer structure
  - **Toast**: Provider context, 4 types (success/error/warning/info), auto-dismiss with TTL, stacking support

- **Layout Components**
  - **Header**: Tenant logo/name display, language toggle (PT/EN), user menu with logout
  - **Sidebar**: Navigation menu (Dashboard, Products, Movements, Alerts), active state highlighting
  - **Footer**: Copyright notice, help/privacy/terms links

- **API Integration**
  - Axios client with base URL configuration
  - Request interceptor: JWT token injection, tenant slug header injection
  - Response interceptor: Auto token refresh on 401, error handling
  - Typed API modules: authAPI, productsAPI, movementsAPI, alertsAPI, tenantAPI
  - 30s timeout with automatic retry

- **Custom Hooks**
  - **useAuth**: AuthProvider context, login/logout functions, user state management, RBAC helpers (hasRole), token validation, localStorage persistence
  - **useTenant**: TenantProvider context, tenant state, subdomain extraction, branding application (CSS variables), refetch function

- **Utilities**
  - `cn()` function for Tailwind class merging with clsx and tailwind-merge

#### Fixed
- Database model import issue: All 8 models now imported in `base.py` to register with `Base.metadata`
- AuditLog column name conflict: Renamed `metadata` to `extra_data` to avoid SQLAlchemy reserved keyword
- Database initialization: Added logging to track table creation process
- Table verification: Added information_schema query to confirm successful creation

#### Testing
- Created comprehensive Phase 2 validation script (`scripts/test-phase2.sh`)
- **10 automated tests**:
  1. ✅ Database tables creation (8 tables)
  2. ✅ Backend health check
  3. ✅ Swagger documentation accessibility
  4. ✅ Redis connection
  5. ✅ Frontend accessibility
  6. ✅ CORS configuration
  7. ✅ Tenant middleware
  8. ✅ Database indexes (55 indexes)
  9. ✅ Backend logs (no critical errors)
  10. ✅ Table schemas verification

#### Statistics
- 📦 **40+ files** created/modified
- 💻 **~3,500 lines** of code
- 🔨 **7 commits** with detailed messages
- ✅ **27 tasks** completed (T014-T040)
- 🎯 **100% test pass rate**

## [0.1.0] - 2025-10-13

### Phase 1: Project Setup ✅

#### Added - Infrastructure
- Docker Compose orchestration with 4 services:
  - PostgreSQL 15.14-alpine (database)
  - Redis 7-alpine (caching)
  - Python 3.11 FastAPI backend
  - Node 20-alpine React frontend
- Backend project structure with FastAPI
- Frontend project structure with React + Vite + TypeScript
- CORS middleware configuration
- Basic health check endpoint
- README with project overview
- Docker-specific documentation (README_DOCKER.md)

#### Added - Development Tools
- Backend linting with Ruff
- Frontend linting with ESLint
- Code formatting configuration
- Git ignore files
- Environment variable templates

#### Added - Testing
- Test directory structures (unit/integration/contract/e2e)
- Docker stack validation script (`scripts/test-docker-stack.sh`)
- Test configuration files (pytest.ini, vitest.config.ts)

#### Testing
- ✅ Backend health check (200 OK)
- ✅ Frontend accessibility (200 OK)
- ✅ PostgreSQL connection
- ✅ Redis connection
- ✅ CORS headers validation

#### Statistics
- 📦 **30+ files** created
- 🔨 **13 tasks** completed (T001-T013)
- 🐳 **4 Docker services** configured
- ✅ **All integration tests** passing

## [0.0.1] - 2025-10-12

### Initial Setup

#### Added - Governance
- Project constitution v1.0.0 with 4 core principles:
  1. **Code Quality** - Type safety, documentation, code reviews
  2. **Testing Standards** - TDD, 80% coverage, test pyramid
  3. **UX Consistency** - Design system, accessibility, i18n
  4. **Performance** - API < 200ms, bundle < 500kb, caching
- Feature specification with 6 user stories and 27 functional requirements
- Implementation plan with technology stack decisions
- Task breakdown: 225 tasks across 9 phases
- Data model with 8 entities and relationships
- API contracts for all endpoints

#### Added - Documentation
- Project README
- Quick start guide
- Architecture decision records (7 ADRs)
- Development guidelines

---

## Version History

- **0.2.0** (2025-10-14) - Phase 2: Foundational Infrastructure ✅
- **0.1.0** (2025-10-13) - Phase 1: Project Setup ✅
- **0.0.1** (2025-10-12) - Initial governance and planning ✅

## Next Release: 0.3.0 (Planned)

### Phase 3: User Story 1 - Products CRUD

#### Planned Features
- [ ] Product API endpoints (list, get, create, update, delete)
- [ ] Product management UI components
- [ ] Custom fields integration
- [ ] Category assignment
- [ ] Stock quantity tracking
- [ ] SKU validation and uniqueness
- [ ] Image upload support
- [ ] Product search and filtering
- [ ] Pagination and sorting
- [ ] Import/export functionality

**Target Date**: TBD  
**Tasks**: T041-T072 (32 tasks)  
**Estimated Effort**: 2-3 development sessions

---

[Unreleased]: https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan/releases/tag/v0.0.1
