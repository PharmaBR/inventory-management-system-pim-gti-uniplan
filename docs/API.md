# 📡 API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.{tenant}.yourdomain.com`

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```http
Authorization: Bearer {access_token}
```

### Token Endpoints (Coming in Phase 3)

```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

## Multi-Tenant Configuration

The API supports multiple methods for tenant identification:

### 1. Subdomain (Recommended for Production)
```
https://acme.yourdomain.com/api/v1/products
```

### 2. Query Parameter (Development)
```
http://localhost:8000/api/v1/products?tenant=acme
```

### 3. Custom Header (Mobile/Testing)
```http
X-Tenant-Slug: acme
```

## Current Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### API Documentation

```http
GET /docs
```
Interactive Swagger UI documentation (only available in development mode)

```http
GET /redoc
```
ReDoc alternative documentation (only available in development mode)

## Phase 2 Infrastructure

### Database Models (8 tables created)

1. **Tenants** - Client configurations
   - Fields: name, slug, logo_url, colors, limits, settings
   - Indexes: slug (unique), is_active

2. **Users** - System users with RBAC
   - Fields: email, full_name, password_hash, role (admin/manager/operator)
   - Indexes: (tenant_id, email) unique, role
   - Relationships: belongs_to tenant, has_many audit_logs/movements

3. **Categories** - Hierarchical product categories
   - Fields: name, description, parent_id, status
   - Indexes: (tenant_id, name) unique, parent_id, status
   - Features: Self-referential hierarchy

4. **Products** - Inventory items
   - Fields: sku, name, description, quantity, min/max_quantity, unit_price, custom_fields (JSONB)
   - Indexes: (tenant_id, sku) unique, category_id, custom_fields (GIN index)
   - Relationships: belongs_to category, has_many movements/alerts

5. **Movements** - Stock movements
   - Fields: type (entry/exit/adjustment/transfer), quantity, balance_after, reason
   - Indexes: (tenant_id, created_at), product_id, user_id, type
   - Relationships: belongs_to product/user

6. **Alerts** - Stock notifications
   - Fields: type (low_stock/out_of_stock/expiring_soon), severity, is_read, is_resolved
   - Indexes: (tenant_id, created_at), product_id, is_read, is_resolved
   - Relationships: belongs_to product

7. **CustomFieldDefinitions** - Dynamic field schemas
   - Fields: name, label, field_type, is_required, validation_rules, options
   - Indexes: (tenant_id, name) unique
   - Features: Supports text/number/date/boolean/select/multiselect

8. **AuditLogs** - Change tracking
   - Fields: action, entity_type, entity_id, changes (JSONB), extra_data (JSONB)
   - Indexes: (tenant_id, created_at), (tenant_id, user_id), entity_type/entity_id
   - Features: Stores before/after snapshots

### Middleware Pipeline

1. **CORS Middleware**
   - Allows: http://localhost:3000, http://*.localhost:3000
   - Methods: All
   - Headers: All
   - Credentials: Enabled

2. **Tenant Middleware**
   - Extracts tenant from subdomain/query/header
   - Validates slug format (alphanumeric + hyphens, 3-100 chars)
   - Stores in request.state.tenant_slug
   - Development mode: Allows requests without tenant

3. **Auth Middleware** (via dependencies)
   - Validates JWT tokens
   - Extracts user information
   - Enforces RBAC (Role-Based Access Control)
   - Auto-refreshes expired tokens

### Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "validation_error"
}
```

**Common Status Codes:**
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate entries, integrity violations)
- `422` - Unprocessable Entity (Pydantic validation)
- `500` - Internal Server Error

### Logging

All requests are logged with structured JSON format:

```json
{
  "timestamp": "2025-10-14T23:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "request_id": "uuid",
  "method": "GET",
  "path": "/api/v1/products",
  "status_code": 200,
  "duration_ms": 45
}
```

### Caching Strategy

- **Redis** used for tenant configurations and frequent queries
- **Default TTL**: 3600 seconds (1 hour)
- **Cache Keys**: `tenant:{slug}:config`, `product:{id}`, `user:{id}:profile`
- **Invalidation**: Pattern-based (e.g., `tenant:{slug}:*`)

## Coming in Phase 3

### Products API

```http
GET    /api/v1/products          # List products with pagination
GET    /api/v1/products/{id}     # Get product details
POST   /api/v1/products          # Create product
PUT    /api/v1/products/{id}     # Update product
DELETE /api/v1/products/{id}     # Delete product
```

**Features:**
- Pagination (default 20 items per page)
- Filtering by category, status, custom fields
- Sorting by name, sku, quantity, price
- Search by name/sku/description
- Custom fields validation

See [API Contracts](../specs/001-sistema-de-gerenciamento/contracts/api-contracts.md) for full specification.

## Rate Limiting (Coming Soon)

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Admin**: Unlimited

## Versioning

API uses URL versioning: `/api/v1/...`

Breaking changes will be released under a new version (e.g., `/api/v2/...`).

---

**Last Updated**: Phase 2 Complete - October 14, 2025
