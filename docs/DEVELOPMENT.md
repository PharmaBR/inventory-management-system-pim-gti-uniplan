# 🛠️ Developer Guide

## Table of Contents
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Database](#database)
- [Debugging](#debugging)

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Python 3.11+, Node.js 18+ for local development

### First-Time Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan.git
   cd inventory-management-system-pim-gti-uniplan
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify installation:**
   ```bash
   ./scripts/test-docker-stack.sh
   # or for Phase 2 validation:
   ./scripts/test-phase2.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs

## Project Structure

```
.
├── backend/                      # Python FastAPI backend
│   ├── src/
│   │   ├── api/                 # API layer
│   │   │   ├── main.py          # FastAPI app entry point
│   │   │   ├── dependencies/    # Dependency injection
│   │   │   ├── middleware/      # Request/response middleware
│   │   │   └── routes/          # API route handlers (coming Phase 3+)
│   │   ├── core/                # Core functionality
│   │   │   ├── config.py        # Settings (env vars)
│   │   │   ├── security.py      # JWT + password hashing
│   │   │   ├── logging.py       # Structured logging
│   │   │   └── cache.py         # Redis caching
│   │   ├── db/                  # Database layer
│   │   │   ├── base.py          # SQLAlchemy config
│   │   │   └── models/          # ORM models (8 tables)
│   │   ├── schemas/             # Pydantic schemas
│   │   │   └── base.py          # Base schemas + pagination
│   │   ├── services/            # Business logic (coming Phase 3+)
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   ├── requirements/
│   │   ├── base.txt             # Production deps
│   │   └── dev.txt              # Development deps
│   └── Dockerfile
│
├── frontend/                     # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # UI components (Button, Input, Modal, Toast)
│   │   │   └── layout/          # Layout components (Header, Sidebar, Footer)
│   │   ├── hooks/               # Custom hooks (useAuth, useTenant)
│   │   ├── i18n/                # Internationalization (PT-BR, EN-US)
│   │   ├── pages/               # Page components (coming Phase 3+)
│   │   ├── services/
│   │   │   └── api.ts           # Axios client with interceptors
│   │   └── utils/
│   │       └── cn.ts            # Tailwind class merger
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/
│   └── Dockerfile
│
├── specs/                        # Feature specifications
│   └── 001-sistema-de-gerenciamento/
│       ├── spec.md              # Feature requirements
│       ├── plan.md              # Implementation plan
│       ├── data-model.md        # Database schema
│       ├── tasks.md             # Task breakdown (225 tasks)
│       └── contracts/
│           └── api-contracts.md # API endpoint contracts
│
├── scripts/                      # Utility scripts
│   ├── test-docker-stack.sh    # Test Phase 1
│   └── test-phase2.sh          # Test Phase 2
│
├── docker-compose.yml           # Multi-service orchestration
└── README.md                    # Project overview
```

## Development Workflow

### Backend Development

#### Local Development (without Docker)

1. **Setup Python environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements/dev.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start development server:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### With Docker (recommended)

```bash
# Rebuild backend after code changes
docker-compose build backend

# Restart backend service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute commands inside container
docker-compose exec backend bash
docker-compose exec backend python -c "from src.api.main import app; print(app.version)"
```

### Frontend Development

#### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start dev server:**
   ```bash
   npm run dev
   ```

3. **Access at:** http://localhost:3000

#### With Docker (recommended)

```bash
# Rebuild frontend after code changes
docker-compose build frontend

# Restart frontend service
docker-compose restart frontend

# View logs
docker-compose logs -f frontend
```

### Database Operations

#### Create Migration

```bash
# Inside backend container
docker-compose exec backend alembic revision --autogenerate -m "description"

# Review generated migration in alembic/versions/
# Edit if needed, then apply:
docker-compose exec backend alembic upgrade head
```

#### Reset Database

```bash
# Drop and recreate
docker exec inventory_db psql -U postgres -c "DROP DATABASE inventory_db"
docker exec inventory_db psql -U postgres -c "CREATE DATABASE inventory_db"
docker-compose restart backend
```

#### Access PostgreSQL

```bash
# Via psql
docker exec -it inventory_db psql -U postgres -d inventory_db

# List tables
\dt

# Describe table
\d tenants

# Query
SELECT * FROM tenants;
```

#### Access Redis

```bash
# Via redis-cli
docker exec -it inventory_redis redis-cli

# Test connection
PING

# List keys
KEYS *

# Get value
GET tenant:acme:config
```

## Code Standards

### Python (Backend)

Follow [PEP 8](https://pep8.org/) and project [Constitution](.specify/memory/constitution.md).

**Key Principles:**
- Use type hints everywhere
- Write docstrings (Google style)
- Keep functions small (< 50 lines)
- Prefer composition over inheritance
- Handle errors explicitly

**Example:**
```python
async def create_product(
    product_data: ProductCreate,
    tenant_id: UUID,
    db: AsyncSession
) -> Product:
    """
    Create a new product for a tenant.
    
    Args:
        product_data: Product creation data
        tenant_id: Tenant identifier
        db: Database session
        
    Returns:
        Created product instance
        
    Raises:
        ValueError: If SKU already exists
    """
    # Implementation
    pass
```

**Linting:**
```bash
# In backend/
ruff check .
ruff format .
```

### TypeScript (Frontend)

Follow [Airbnb style guide](https://github.com/airbnb/javascript) and project Constitution.

**Key Principles:**
- Use TypeScript strict mode
- Prefer functional components + hooks
- Keep components small (< 200 lines)
- Use custom hooks for logic reuse
- Handle loading/error states

**Example:**
```typescript
interface ProductFormProps {
  product?: Product;
  onSubmit: (data: ProductCreate) => Promise<void>;
  onCancel: () => void;
}

export const ProductForm: React.FC<ProductFormProps> = ({
  product,
  onSubmit,
  onCancel
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  
  // Implementation
  return <form>...</form>;
};
```

**Linting:**
```bash
# In frontend/
npm run lint
npm run format
```

## Testing

### Backend Tests

#### Unit Tests
```bash
# Run all unit tests
docker-compose exec backend pytest tests/unit/

# Run specific test file
docker-compose exec backend pytest tests/unit/test_security.py

# With coverage
docker-compose exec backend pytest --cov=src tests/
```

#### Integration Tests
```bash
docker-compose exec backend pytest tests/integration/
```

#### Contract Tests
```bash
docker-compose exec backend pytest tests/contract/
```

### Frontend Tests

#### Unit Tests (Vitest)
```bash
docker-compose exec frontend npm test

# Watch mode
docker-compose exec frontend npm test -- --watch
```

#### E2E Tests (Playwright)
```bash
docker-compose exec frontend npm run test:e2e
```

### Stack Validation Tests

```bash
# Phase 1 validation
./scripts/test-docker-stack.sh

# Phase 2 validation
./scripts/test-phase2.sh
```

## Debugging

### Backend Debugging

#### View Logs
```bash
# All logs
docker-compose logs backend

# Follow logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail 100 backend
```

#### Python Debugger (pdb)

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

Attach to container:
```bash
docker attach inventory_backend
```

#### Database Queries

Enable SQLAlchemy echo in `.env`:
```bash
DEBUG=true
```

This will log all SQL queries to console.

### Frontend Debugging

#### Browser DevTools
- React DevTools extension
- Network tab for API calls
- Console for errors

#### View Logs
```bash
docker-compose logs -f frontend
```

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart
docker-compose restart db
```

#### Module Not Found
```bash
# Backend
docker-compose exec backend pip install -r requirements/dev.txt

# Frontend
docker-compose exec frontend npm install
```

## Environment Variables

### Backend (.env in backend/)

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/inventory_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://*.localhost:3000

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env in frontend/)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_LANGUAGE=pt-BR
```

## Git Workflow

### Branch Naming
- `main` - Production-ready code
- `001-sistema-de-gerenciamento` - Feature branch (current)
- `feature/xxx` - New features
- `fix/xxx` - Bug fixes
- `docs/xxx` - Documentation updates

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(products): implement product CRUD endpoints

- Add ProductService with create/read/update/delete methods
- Implement API routes with authentication
- Add Pydantic schemas for validation
- Include unit and integration tests

Closes #42
```

## Next Steps

- Review [Constitution](.specify/memory/constitution.md) for mandatory principles
- Read [API Contracts](specs/001-sistema-de-gerenciamento/contracts/api-contracts.md)
- Check [Tasks Breakdown](specs/001-sistema-de-gerenciamento/tasks.md) for next features
- Join development with Phase 3 (Products CRUD)

---

**Questions?** Check the [README](README.md) or open an issue on GitHub.
