# API Contracts: Sistema de Gerenciamento de Estoque White Label

**Feature**: 001-sistema-de-gerenciamento  
**Date**: 2025-10-07  
**API Version**: v1  
**Base URL**: `https://{tenant-slug}.sistema.com/api/v1`

## Authentication

All endpoints require JWT authentication except `/auth/login` and `/auth/refresh`.

**Headers**:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
Accept-Language: pt-BR | en-US
```

---

## Endpoints Summary

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (invalidate refresh token)

### Products
- `GET /products` - List products (paginated)
- `POST /products` - Create product
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Deactivate product (soft delete)
- `POST /products/import` - Bulk import from CSV/Excel

### Movements
- `GET /movements` - List movements (paginated, filterable by product/date)
- `POST /movements` - Create movement (inbound/outbound)
- `GET /movements/{id}` - Get movement details
- `GET /products/{id}/movements` - Get product movement history

### Users (Admin/Manager only)
- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Deactivate user

### Categories
- `GET /categories` - List categories
- `POST /categories` - Create category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Reports
- `GET /reports/stock` - Current stock report
- `GET /reports/low-stock` - Low stock products
- `GET /reports/movements` - Movement report (by date range)
- `POST /reports/export` - Export report (CSV/Excel)

### Alerts
- `GET /alerts` - List unread alerts
- `PUT /alerts/{id}/read` - Mark alert as read

### Tenant Settings (Admin only)
- `GET /tenant/config` - Get tenant configuration
- `PUT /tenant/config` - Update tenant configuration
- `GET /tenant/custom-fields` - List custom field definitions
- `POST /tenant/custom-fields` - Create custom field definition

---

## Detailed Endpoint Specifications

### POST /auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "User Name",
    "role": "manager"
  }
}
```

---

### GET /products

**Query Parameters**:
- `page` (int, default=1)
- `per_page` (int, default=50, max=100)
- `search` (string): Search by name/SKU
- `category_id` (uuid): Filter by category
- `status` (string): active|inactive
- `min_quantity` (decimal): Minimum stock
- `max_quantity` (decimal): Maximum stock

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "sku": "PROD-001",
      "name": "Product Name",
      "description": "Description",
      "current_quantity": 100.5,
      "unit_price": 25.99,
      "category": {
        "id": "uuid",
        "name": "Category Name"
      },
      "supplier": "Supplier Name",
      "image_url": "https://...",
      "minimum_quantity": 10,
      "custom_fields": {
        "lote": "ABC123",
        "validade": "2025-12-31"
      },
      "status": "active",
      "created_at": "2025-10-07T10:00:00Z",
      "updated_at": "2025-10-07T12:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 50,
  "pages": 3
}
```

---

### POST /products

**Request**:
```json
{
  "sku": "PROD-001",
  "name": "Product Name",
  "description": "Optional description",
  "current_quantity": 100,
  "unit_price": 25.99,
  "category_id": "uuid",
  "supplier": "Supplier Name",
  "image_url": "https://...",
  "minimum_quantity": 10,
  "custom_fields": {
    "lote": "ABC123"
  }
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "sku": "PROD-001",
  "name": "Product Name",
  // ... full product object
  "created_at": "2025-10-07T10:00:00Z"
}
```

**Errors**:
- `400`: Validation error (e.g., SKU already exists)
- `403`: Insufficient permissions
- `422`: Invalid custom field

---

### POST /movements

**Request**:
```json
{
  "product_id": "uuid",
  "movement_type": "inbound",  // or "outbound"
  "quantity": 50,
  "reason": "purchase",
  "notes": "Optional notes"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "product_id": "uuid",
  "movement_type": "inbound",
  "quantity": 50,
  "balance_before": 100,
  "balance_after": 150,
  "reason": "purchase",
  "notes": "Optional notes",
  "created_by": {
    "id": "uuid",
    "full_name": "User Name"
  },
  "created_at": "2025-10-07T10:00:00Z"
}
```

**Side Effects**:
- Updates `products.current_quantity`
- Creates alert if quantity falls below `minimum_quantity`

---

### POST /products/import

**Request** (multipart/form-data):
```
file: products.csv
```

**CSV Format**:
```csv
sku,name,description,quantity,unit_price,category,supplier,minimum_quantity
PROD-001,Product 1,Description,100,25.99,Electronics,Supplier A,10
PROD-002,Product 2,Description,50,15.50,Electronics,Supplier B,5
```

**Response 200** (Success):
```json
{
  "status": "success",
  "imported": 2,
  "message": "2 products imported successfully"
}
```

**Response 400** (Validation Errors):
```json
{
  "status": "error",
  "errors": [
    {
      "line": 2,
      "field": "sku",
      "error": "SKU PROD-001 already exists"
    },
    {
      "line": 3,
      "field": "unit_price",
      "error": "Invalid decimal format"
    }
  ],
  "message": "Import failed. Fix errors and retry."
}
```

**Notes**:
- Transactional: ALL rows validated before any insert
- If ANY row fails validation, ENTIRE import is rejected
- Returns detailed error report with line numbers

---

### GET /reports/stock

**Query Parameters**:
- `category_id` (uuid, optional)
- `status` (string, optional): active|inactive|all
- `sort_by` (string, optional): quantity_asc|quantity_desc|name_asc|name_desc

**Response 200**:
```json
{
  "items": [
    {
      "product_id": "uuid",
      "sku": "PROD-001",
      "name": "Product Name",
      "category": "Category Name",
      "current_quantity": 5,
      "minimum_quantity": 10,
      "status": "low_stock"  // "normal", "low_stock", "out_of_stock"
    }
  ],
  "summary": {
    "total_products": 150,
    "low_stock_count": 15,
    "out_of_stock_count": 3,
    "total_value": 125000.50
  }
}
```

---

### GET /tenant/config

**Response 200**:
```json
{
  "slug": "empresa1",
  "name": "Empresa 1 Ltda",
  "logo_url": "https://...",
  "primary_color": "#FF5733",
  "secondary_color": "#3366FF",
  "limits": {
    "max_products": 10000,
    "max_users": 50,
    "current_products": 1500,
    "current_users": 12
  }
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "sku",
        "message": "SKU already exists"
      }
    ]
  }
}
```

### Error Codes

- `400 BAD_REQUEST`: Invalid request data
- `401 UNAUTHORIZED`: Missing or invalid auth token
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `409 CONFLICT`: Duplicate resource (e.g., SKU exists)
- `422 UNPROCESSABLE_ENTITY`: Validation failed
- `429 TOO_MANY_REQUESTS`: Rate limit exceeded
- `500 INTERNAL_SERVER_ERROR`: Server error

---

## Rate Limiting

- **Authenticated users**: 1000 requests/hour per user
- **Per tenant**: 10000 requests/hour
- **Import endpoint**: 10 imports/hour per tenant

**Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1633024800
```

---

## Pagination

**Standard pagination** for list endpoints:

**Request**:
```
GET /products?page=2&per_page=50
```

**Response headers**:
```
X-Total-Count: 150
X-Page: 2
X-Per-Page: 50
X-Total-Pages: 3
Link: <https://...?page=1>; rel="first", <https://...?page=3>; rel="last", <https://...?page=3>; rel="next"
```

---

## Webhooks (Future)

Future support for webhook notifications:
- `product.created`
- `product.updated`
- `product.deleted`
- `movement.created`
- `alert.created`

---

## Full OpenAPI Specification

See [openapi.yaml](./openapi.yaml) for complete OpenAPI 3.0 specification with all schemas, parameters, and responses.

---

## Testing Contracts

**Contract Tests** verify API compliance with this specification:

```python
# tests/contract/test_products_api.py
def test_get_products_returns_valid_schema(client, auth_headers):
    response = client.get("/api/v1/products", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    
    if data["items"]:
        product = data["items"][0]
        assert "id" in product
        assert "sku" in product
        assert "name" in product
```

**Performance Contract**:
- API endpoints: p95 < 200ms
- List endpoints: p95 < 150ms with pagination
- Import endpoint: < 5s for files with <1000 rows

---

## Summary

- **Base URL**: `https://{tenant}.sistema.com/api/v1`
- **Authentication**: JWT Bearer tokens
- **Format**: JSON request/response
- **Pagination**: Query params (page, per_page)
- **i18n**: Accept-Language header
- **Rate Limiting**: Per user and per tenant
- **Error Handling**: Standard error format with codes

**API contracts ready for implementation!**
