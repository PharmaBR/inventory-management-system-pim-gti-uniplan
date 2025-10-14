# 🐳 Docker Compose Guide

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ destroys data)
docker-compose down -v
```

## Services

### 🐘 PostgreSQL 15
- **Port**: 5432
- **User**: postgres
- **Password**: postgres
- **Database**: inventory_db
- **Volume**: `postgres_data`

**Connect**:
```bash
docker exec -it inventory_db psql -U postgres -d inventory_db
```

### 🔴 Redis 7
- **Port**: 6379
- **Volume**: `redis_data`

**Test**:
```bash
docker exec -it inventory_redis redis-cli ping
# Expected: PONG
```

### 🐍 Backend (FastAPI)
- **Port**: 8000
- **Hot Reload**: Enabled
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**View Logs**:
```bash
docker-compose logs -f backend
```

**Shell Access**:
```bash
docker exec -it inventory_backend /bin/bash
```

### ⚛️ Frontend (React + Vite)
- **Port**: 3000
- **URL**: http://localhost:3000
- **Hot Reload**: Enabled

**View Logs**:
```bash
docker-compose logs -f frontend
```

## Development Workflow

### 1. First Time Setup

```bash
# Build and start all services
docker-compose up -d --build

# Wait for services to be ready (~30 seconds)
# Check health status
docker-compose ps
```

### 2. Daily Development

```bash
# Start services (uses cached images)
docker-compose up -d

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### 3. Code Changes

**Backend Changes**:
- Files auto-reload (no restart needed)
- If you change dependencies: `docker-compose restart backend`

**Frontend Changes**:
- Files auto-reload (no restart needed)
- If you change dependencies: `docker-compose restart frontend`

### 4. Database Operations

**Run migrations**:
```bash
docker exec -it inventory_backend alembic upgrade head
```

**Create migration**:
```bash
docker exec -it inventory_backend alembic revision --autogenerate -m "description"
```

**Access database**:
```bash
docker exec -it inventory_db psql -U postgres -d inventory_db
```

### 5. Cleanup

**Stop services**:
```bash
docker-compose stop
```

**Remove containers**:
```bash
docker-compose down
```

**Remove everything (including data)**:
```bash
docker-compose down -v
rm -rf backend/venv frontend/node_modules
```

## Troubleshooting

### Services won't start

```bash
# Stop all
docker-compose down

# Remove old containers
docker-compose rm -f

# Rebuild and start
docker-compose up -d --build
```

### Port conflicts

If ports 5432, 6379, 8000, or 3000 are in use:

```bash
# Find what's using the port
lsof -i :5432
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Database connection errors

```bash
# Check if PostgreSQL is healthy
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend build errors

```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## Environment Variables

Create `.env` file in project root (optional):

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=inventory_db

# Backend
SECRET_KEY=your-secret-key-here
DEBUG=True

# Ports (if you need to change)
POSTGRES_PORT=5432
REDIS_PORT=6379
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## Testing the Stack

```bash
# Test PostgreSQL
docker exec inventory_db psql -U postgres -c "SELECT version();"

# Test Redis
docker exec inventory_redis redis-cli ping

# Test Backend
curl http://localhost:8000/health

# Test Frontend
curl http://localhost:3000

# All-in-one test
./scripts/test-docker-stack.sh
```

## Production Deployment

⚠️ **DO NOT use this docker-compose.yml in production as-is**

For production:
1. Use secrets management (not environment variables)
2. Use production-grade PostgreSQL settings
3. Enable SSL/TLS
4. Use reverse proxy (nginx/traefik)
5. Configure proper backups
6. Use orchestration (Kubernetes/ECS)
7. Set `DEBUG=False`

## Performance Optimization

### Development
```yaml
# In docker-compose.yml
services:
  backend:
    # Use tmpfs for faster file operations
    tmpfs:
      - /tmp
```

### Resource Limits
```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## Useful Commands

```bash
# View resource usage
docker stats

# Clean up unused images/volumes
docker system prune -a --volumes

# Export database
docker exec inventory_db pg_dump -U postgres inventory_db > backup.sql

# Import database
docker exec -i inventory_db psql -U postgres inventory_db < backup.sql

# Shell into any container
docker exec -it <container_name> /bin/sh
```

## Next Steps

- [ ] Run Phase 2 setup (database models)
- [ ] Create first tenant via script
- [ ] Test API endpoints
- [ ] Develop user stories
