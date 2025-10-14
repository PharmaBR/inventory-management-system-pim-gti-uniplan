# 🧪 Testing Guide

## Quick Test (Automated)

```bash
# Run Phase 2 comprehensive tests
./scripts/test-phase2.sh

# Expected: All 10 tests should pass
```

## Manual Testing

### 1. Backend API Tests

#### Health Check
```bash
curl http://localhost:8000/health
```
**Expected Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

#### Swagger Documentation
Open in browser: http://localhost:8000/docs

**Expected:** Interactive API documentation with:
- Health endpoint visible
- Schema definitions
- Try it out functionality

#### ReDoc Documentation
Open in browser: http://localhost:8000/redoc

**Expected:** Alternative API documentation (more structured)

### 2. Frontend Tests

#### Access Application
Open in browser: http://localhost:3000

**Expected:** React app loads with:
- Clean console (no errors)
- Vite HMR working
- Development mode indicators

#### Language Switching Test
1. Open browser console
2. Check localStorage for `i18nextLng` key
3. Should default to browser language or `pt-BR`

**Test in Console:**
```javascript
// Check current language
localStorage.getItem('i18nextLng')

// Switch to English
localStorage.setItem('i18nextLng', 'en-US')
location.reload()

// Switch back to Portuguese
localStorage.setItem('i18nextLng', 'pt-BR')
location.reload()
```

### 3. Database Tests

#### List All Tables
```bash
docker exec inventory_db psql -U postgres -d inventory_db -c "\dt"
```
**Expected:** 8 tables listed:
- alerts
- audit_logs
- categories
- custom_field_definitions
- movements
- products
- tenants
- users

#### View Table Structure
```bash
# Example: tenants table
docker exec inventory_db psql -U postgres -d inventory_db -c "\d tenants"
```
**Expected:** Full column definitions with:
- id (uuid, primary key)
- name, slug (unique)
- logo_url, colors
- timestamps (created_at, updated_at)

#### Check Indexes
```bash
docker exec inventory_db psql -U postgres -d inventory_db -c "
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;"
```
**Expected:** 55 indexes total

#### Query Example
```bash
docker exec inventory_db psql -U postgres -d inventory_db -c "
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';"
```
**Expected:** 8 tables

### 4. Redis Tests

#### Ping Test
```bash
docker exec inventory_redis redis-cli PING
```
**Expected:** `PONG`

#### Set/Get Test
```bash
# Set a test key
docker exec inventory_redis redis-cli SET test:key "Hello Phase 2"

# Get the key
docker exec inventory_redis redis-cli GET test:key

# Delete the key
docker exec inventory_redis redis-cli DEL test:key
```

#### Monitor Cache Activity
```bash
docker exec inventory_redis redis-cli MONITOR
# Leave running and make API requests to see cache operations
# Press Ctrl+C to stop
```

### 5. Middleware Tests

#### Tenant Middleware (Development Mode)
```bash
# Without tenant (should work in dev mode)
curl -v http://localhost:8000/health 2>&1 | grep "< HTTP"

# With tenant query parameter
curl -v "http://localhost:8000/health?tenant=test" 2>&1 | grep "< HTTP"

# With tenant header
curl -v -H "X-Tenant-Slug: test" http://localhost:8000/health 2>&1 | grep "< HTTP"
```
**Expected:** All should return 200 OK in development mode

#### CORS Headers
```bash
curl -v -H "Origin: http://localhost:3000" http://localhost:8000/health 2>&1 | grep -i "access-control"
```
**Expected Headers:**
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

### 6. Logging Tests

#### View Backend Logs
```bash
# Real-time logs
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail 50 backend

# Search for errors
docker-compose logs backend | grep -i error
```

#### Structured Log Format
```bash
# View JSON logs
docker-compose logs backend --tail 20 | grep "inventory_system"
```
**Expected:** JSON formatted logs with:
- timestamp
- level (INFO, WARNING, ERROR)
- message
- Additional context (tenant_id, user_id when applicable)

### 7. Container Health Tests

#### Check Service Status
```bash
docker-compose ps
```
**Expected:** All 4 services running:
- ✅ inventory_backend (Up)
- ✅ inventory_db (Up, healthy)
- ✅ inventory_redis (Up, healthy)
- ✅ inventory_frontend (Up)

#### Resource Usage
```bash
docker stats --no-stream
```
**Expected:** Reasonable resource usage:
- Backend: < 200MB RAM
- Frontend: < 100MB RAM
- PostgreSQL: < 100MB RAM
- Redis: < 50MB RAM

### 8. Error Handling Tests

#### Test 404 Not Found
```bash
curl -s http://localhost:8000/nonexistent | jq
```
**Expected:**
```json
{
  "detail": "Not Found"
}
```

#### Test Invalid Endpoint
```bash
curl -s -X POST http://localhost:8000/health | jq
```
**Expected:** 405 Method Not Allowed

### 9. Performance Tests

#### Response Time Test
```bash
# Measure backend response time
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s http://localhost:8000/health
```
**Expected:** < 0.1s (100ms)

#### Load Test (Basic)
```bash
# Install Apache Bench if needed: brew install httpd (macOS)
ab -n 1000 -c 10 http://localhost:8000/health
```
**Expected:** 
- Requests per second: > 100
- Failed requests: 0
- Mean response time: < 100ms

### 10. Database Migration Tests

#### Check Migration Status
```bash
docker-compose exec backend alembic current
```
**Expected:** Shows current revision or "head" if no migrations applied

#### View Migration History
```bash
docker-compose exec backend alembic history
```
**Expected:** List of migration revisions (may be empty if using create_all())

## Integration Testing Scenarios

### Scenario 1: Full Stack Health Check
```bash
# 1. Check all services
docker-compose ps

# 2. Test backend
curl http://localhost:8000/health

# 3. Test frontend
curl -I http://localhost:3000

# 4. Test database
docker exec inventory_db psql -U postgres -d inventory_db -c "SELECT 1"

# 5. Test Redis
docker exec inventory_redis redis-cli PING
```

### Scenario 2: Database Connectivity
```bash
# From backend container, test database connection
docker-compose exec backend python -c "
from src.db.base import engine
import asyncio

async def test_db():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database connection: OK')

asyncio.run(test_db())
"
```

### Scenario 3: Cache Functionality
```bash
# From backend container, test Redis connection
docker-compose exec backend python -c "
from src.core.cache import get_redis
import asyncio

async def test_cache():
    redis = await get_redis()
    await redis.set('test', 'value')
    result = await redis.get('test')
    print(f'Cache test: {result}')
    await redis.close()

asyncio.run(test_cache())
"
```

## Browser Testing

### Open in Browser

1. **Frontend**: http://localhost:3000
   - Check: No console errors
   - Check: Page loads correctly
   - Check: Vite HMR working (edit a file, see instant reload)

2. **Backend Swagger**: http://localhost:8000/docs
   - Check: Interactive documentation loads
   - Check: Can expand endpoints
   - Check: Schemas are visible

3. **Backend ReDoc**: http://localhost:8000/redoc
   - Check: Alternative documentation loads
   - Check: Three-column layout visible
   - Check: Navigation works

### Developer Tools Checks

1. **Network Tab**:
   - Frontend loads without CORS errors
   - All resources load (JS, CSS)
   - No 404 errors

2. **Console Tab**:
   - No JavaScript errors
   - No React warnings
   - Vite connected message visible

3. **Application Tab**:
   - localStorage has i18n settings
   - No unnecessary data stored

## Troubleshooting Tests

### If Backend Fails
```bash
# Check logs
docker-compose logs backend --tail 100

# Restart service
docker-compose restart backend

# Rebuild if needed
docker-compose build backend
docker-compose up -d backend
```

### If Database Fails
```bash
# Check if database exists
docker exec inventory_db psql -U postgres -l

# Recreate database
docker exec inventory_db psql -U postgres -c "DROP DATABASE IF EXISTS inventory_db"
docker exec inventory_db psql -U postgres -c "CREATE DATABASE inventory_db"
docker-compose restart backend
```

### If Frontend Fails
```bash
# Check logs
docker-compose logs frontend --tail 100

# Check if node_modules exist
docker-compose exec frontend ls -la node_modules

# Reinstall dependencies
docker-compose exec frontend npm install
docker-compose restart frontend
```

### If Redis Fails
```bash
# Check if Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Clear Redis data
docker exec inventory_redis redis-cli FLUSHALL
```

## Test Results Template

Use this template to document your test results:

```markdown
## Test Results - [Date]

### Automated Tests
- [ ] Phase 2 Script: __/10 passed

### Manual Tests
- [ ] Backend Health: ✅/❌
- [ ] Frontend Access: ✅/❌
- [ ] Database Tables: ✅/❌ (8 tables)
- [ ] Redis Connection: ✅/❌
- [ ] Swagger Docs: ✅/❌
- [ ] CORS Headers: ✅/❌
- [ ] Logging Format: ✅/❌

### Performance
- Backend Response Time: ____ms
- Frontend Load Time: ____ms
- Database Query Time: ____ms

### Issues Found
1. [Description]
2. [Description]

### Notes
[Any additional observations]
```

## Next Steps After Testing

If all tests pass:
✅ Commit and push changes
✅ Update project status
✅ Begin Phase 3 development

If tests fail:
1. Check logs for specific errors
2. Review recent code changes
3. Consult troubleshooting section
4. Ask for help if needed

---

**Happy Testing!** 🧪✨
