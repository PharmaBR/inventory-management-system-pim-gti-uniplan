#!/bin/bash

# Test Docker Compose Stack
# Tests all services to ensure they're running correctly

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}🐳 Testing Docker Compose Stack${NC}\n"

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running. Start with: docker-compose up -d${NC}"
    exit 1
fi

echo -e "${BOLD}1. Testing PostgreSQL...${NC}"
if docker exec inventory_db psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; then
    VERSION=$(docker exec inventory_db psql -U postgres -t -c "SELECT version();" | head -n1)
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    echo -e "   Version: ${VERSION}"
else
    echo -e "${RED}❌ PostgreSQL is not responding${NC}"
    exit 1
fi

echo -e "\n${BOLD}2. Testing Redis...${NC}"
if docker exec inventory_redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not responding${NC}"
    exit 1
fi

echo -e "\n${BOLD}3. Testing Backend API...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo -e "   Response: ${HEALTH_RESPONSE}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "   Response: ${HEALTH_RESPONSE}"
    exit 1
fi

echo -e "\n${BOLD}4. Testing Frontend...${NC}"
if curl -s http://localhost:3000 | grep -q "Inventory Management System"; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
    exit 1
fi

echo -e "\n${BOLD}5. Checking Container Status...${NC}"
docker-compose ps

echo -e "\n${GREEN}${BOLD}✅ All services are healthy!${NC}\n"

echo -e "${BOLD}Service URLs:${NC}"
echo -e "  🌐 Frontend:    ${BLUE}http://localhost:3000${NC}"
echo -e "  🔧 Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs:    ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  🐘 PostgreSQL:  ${BLUE}localhost:5432${NC}"
echo -e "  🔴 Redis:       ${BLUE}localhost:6379${NC}"

echo -e "\n${BOLD}Useful commands:${NC}"
echo -e "  View logs:     ${BLUE}docker-compose logs -f${NC}"
echo -e "  Stop services: ${BLUE}docker-compose down${NC}"
echo -e "  Restart:       ${BLUE}docker-compose restart${NC}"
