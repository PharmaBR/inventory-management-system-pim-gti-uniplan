# Quickstart: Sistema de Gerenciamento de Estoque White Label

**Feature**: 001-sistema-de-gerenciamento  
**Date**: 2025-10-07  
**Environment**: Development Setup Guide

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7.x or higher (for caching)
- **Docker**: 24.x or higher (recommended for local development)
- **Git**: 2.x or higher

### Optional Tools

- **Poetry**: Python dependency management (recommended)
- **pnpm**: Fast Node package manager (alternative to npm)
- **pgAdmin**: PostgreSQL GUI (for database inspection)
- **Postman/Insomnia**: API testing

---

## Quick Start with Docker Compose

**Fastest way to get started**:

```bash
# Clone repository
git clone <repository-url>
cd <repository-name>

# Start all services (backend, frontend, PostgreSQL, Redis)
docker-compose up -d

# Wait for services to be ready (~30 seconds)
# Backend will be available at: http://localhost:8000
# Frontend will be available at: http://localhost:3000
# PostgreSQL will be available at: localhost:5432

# Create initial tenant
docker-compose exec backend python scripts/create_tenant.py \
  --slug=demo \
  --name="Demo Company" \
  --admin-email=admin@demo.com \
  --admin-password=Admin123!

# Access the application
# http://demo.localhost:3000 (requires /etc/hosts entry)
```

**Add to `/etc/hosts`**:
```
127.0.0.1 demo.localhost
127.0.0.1 empresa1.localhost
```

---

## Manual Setup (Without Docker)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# OR using Poetry
poetry install

# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**`.env` file**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/inventory_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-min-32-chars-CHANGE-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,http://*.localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=True

# Logging
LOG_LEVEL=INFO
```

**Create database**:
```bash
# Using psql
createdb inventory_db

# OR using SQL
psql -U postgres
CREATE DATABASE inventory_db;
\q
```

**Run migrations**:
```bash
# Initialize Alembic (first time only)
alembic init migrations

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

**Create seed data**:
```bash
# Create initial tenant and admin user
python scripts/seed_data.py
```

**Run backend server**:
```bash
# Development server with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at: http://localhost:8000
# API docs (Swagger): http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# OR
pnpm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**`.env.local` file**:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ENVIRONMENT=development
```

**Run frontend dev server**:
```bash
# Start Vite dev server
npm run dev
# OR
pnpm dev

# Frontend will be available at: http://localhost:3000
```

---

## Development Workflow

### Running Tests

**Backend Tests**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_products.py

# Run tests matching pattern
pytest -k "test_create_product"

# View coverage report
open htmlcov/index.html
```

**Frontend Tests**:
```bash
cd frontend

# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run e2e tests (requires backend running)
npm run test:e2e

# Coverage report
npm run test:coverage
```

---

### Code Quality Checks

**Backend Linting & Formatting**:
```bash
cd backend

# Format code with Black
black src tests

# Sort imports
isort src tests

# Lint with Ruff
ruff check src tests

# Type checking (if using mypy)
mypy src

# Run all checks
pre-commit run --all-files
```

**Frontend Linting & Formatting**:
```bash
cd frontend

# Lint with ESLint
npm run lint

# Format with Prettier
npm run format

# Type checking
npm run type-check
```

---

### Database Management

**Create new migration**:
```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add custom_fields to products"

# Review generated migration in migrations/versions/
nano migrations/versions/xxx_add_custom_fields.py

# Apply migration
alembic upgrade head
```

**Rollback migration**:
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show migration history
alembic history
```

**Database utilities**:
```bash
# Reset database (DESTRUCTIVE!)
dropdb inventory_db
createdb inventory_db
alembic upgrade head
python scripts/seed_data.py

# Backup database
pg_dump inventory_db > backup_$(date +%Y%m%d).sql

# Restore database
psql inventory_db < backup_20251007.sql
```

---

### Creating a New Tenant

**Using script**:
```bash
cd backend
python scripts/create_tenant.py \
  --slug=empresa1 \
  --name="Empresa 1 Ltda" \
  --admin-email=admin@empresa1.com \
  --admin-password=SecurePass123! \
  --primary-color="#FF5733" \
  --secondary-color="#3366FF"
```

**Using API** (requires platform admin token):
```bash
curl -X POST http://localhost:8000/api/v1/admin/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "empresa1",
    "name": "Empresa 1 Ltda",
    "admin_email": "admin@empresa1.com",
    "admin_password": "SecurePass123!",
    "primary_color": "#FF5733"
  }'
```

---

## Project Structure Navigation

```
backend/
├── src/
│   ├── api/               # FastAPI routes and endpoints
│   │   ├── main.py        # App initialization
│   │   ├── dependencies/  # Dependency injection
│   │   ├── middleware/    # Tenant, auth, CORS
│   │   └── routes/        # Endpoint modules
│   ├── core/              # Configuration, security, logging
│   ├── db/                # Database models and sessions
│   ├── schemas/           # Pydantic validation schemas
│   ├── services/          # Business logic
│   └── utils/             # Helper functions
├── tests/                 # Test suite
├── migrations/            # Alembic migrations
├── scripts/               # Utility scripts
└── requirements/          # Dependencies

frontend/
├── src/
│   ├── components/        # React components
│   │   ├── ui/            # Base UI components (Shadcn)
│   │   ├── layout/        # Layout components
│   │   └── features/      # Feature-specific components
│   ├── pages/             # Page components
│   ├── services/          # API client functions
│   ├── hooks/             # Custom React hooks
│   ├── i18n/              # Translations
│   ├── utils/             # Helper functions
│   └── App.tsx            # Main app component
├── tests/                 # Test suite
└── public/                # Static assets
```

---

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic schema** (`backend/src/schemas/products.py`):
```python
class ProductCreate(BaseModel):
    sku: str
    name: str
    quantity: Decimal
```

2. **Create route** (`backend/src/api/routes/products.py`):
```python
@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await product_service.create(db, product, current_user)
```

3. **Implement service** (`backend/src/services/product.py`):
```python
async def create(db: AsyncSession, data: ProductCreate, user: User):
    # Business logic here
    product = Product(**data.dict(), tenant_id=user.tenant_id)
    db.add(product)
    await db.commit()
    return product
```

4. **Write tests** (`backend/tests/unit/test_products.py`):
```python
async def test_create_product(client, auth_headers):
    response = await client.post("/api/v1/products", json={...}, headers=auth_headers)
    assert response.status_code == 201
```

---

### Adding a New Frontend Component

1. **Create component** (`frontend/src/components/products/ProductCard.tsx`):
```tsx
export function ProductCard({ product }: { product: Product }) {
  const { t } = useTranslation();
  return <div>{product.name}</div>;
}
```

2. **Add translations** (`frontend/src/i18n/pt-BR.json`):
```json
{
  "products": {
    "card_title": "Produto"
  }
}
```

3. **Write tests** (`frontend/tests/unit/ProductCard.test.tsx`):
```tsx
test('renders product name', () => {
  render(<ProductCard product={mockProduct} />);
  expect(screen.getByText(mockProduct.name)).toBeInTheDocument();
});
```

---

## Troubleshooting

### Backend Issues

**Database connection errors**:
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**Module import errors**:
```bash
# Reinstall dependencies
pip install -r requirements/dev.txt --force-reinstall

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

**Migration errors**:
```bash
# Check current migration version
alembic current

# Show pending migrations
alembic heads

# Reset migrations (DESTRUCTIVE!)
alembic downgrade base
rm migrations/versions/*.py
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

### Frontend Issues

**Dependency conflicts**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Vite build errors**:
```bash
# Clear Vite cache
rm -rf node_modules/.vite

# Restart dev server
npm run dev
```

**CORS errors**:
- Check `ALLOWED_ORIGINS` in backend `.env`
- Verify frontend is making requests to correct backend URL
- Check browser console for specific CORS error

---

## Environment Variables Reference

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `ALLOWED_ORIGINS` | Yes | - | CORS allowed origins (comma-separated) |
| `ENVIRONMENT` | No | `development` | Environment name |
| `DEBUG` | No | `False` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | Yes | - | Backend API base URL |
| `VITE_ENVIRONMENT` | No | `development` | Environment name |

---

## Next Steps

1. ✅ Environment set up
2. ✅ Backend and frontend running
3. ✅ Initial tenant created
4. ➡️ Start implementing user stories (see `tasks.md` when generated)
5. ➡️ Write tests following TDD workflow
6. ➡️ Run constitution compliance checks

**Ready to start development! 🚀**

For implementation tasks, run `/speckit.tasks` to generate detailed task breakdown.
