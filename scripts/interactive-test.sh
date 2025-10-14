#!/bin/bash

# Interactive Testing Menu for Phase 2
# Run: bash scripts/interactive-test.sh

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

function wait_for_enter() {
    echo ""
    read -p "Press ENTER to continue..."
}

function test_backend_health() {
    print_header "Testing Backend Health"
    
    echo "Calling: GET http://localhost:8000/health"
    RESPONSE=$(curl -s http://localhost:8000/health)
    
    echo -e "\nResponse:"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    
    if echo "$RESPONSE" | grep -q '"status": "ok"'; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi
    
    wait_for_enter
}

function test_swagger_docs() {
    print_header "Testing Swagger Documentation"
    
    echo "Calling: GET http://localhost:8000/docs"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
    
    if [ "$STATUS" = "200" ]; then
        print_success "Swagger docs accessible (HTTP $STATUS)"
        print_info "Open in browser: http://localhost:8000/docs"
    else
        print_error "Swagger docs failed (HTTP $STATUS)"
    fi
    
    wait_for_enter
}

function test_database_tables() {
    print_header "Testing Database Tables"
    
    echo "Querying PostgreSQL for tables..."
    docker exec inventory_db psql -U postgres -d inventory_db -c "\dt" 2>/dev/null
    
    TABLE_COUNT=$(docker exec inventory_db psql -U postgres -d inventory_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | tr -d ' ')
    
    if [ "$TABLE_COUNT" = "8" ]; then
        print_success "All 8 tables found"
    else
        print_error "Expected 8 tables, found $TABLE_COUNT"
    fi
    
    wait_for_enter
}

function test_redis() {
    print_header "Testing Redis Connection"
    
    echo "Sending PING to Redis..."
    RESPONSE=$(docker exec inventory_redis redis-cli PING 2>/dev/null)
    
    if [ "$RESPONSE" = "PONG" ]; then
        print_success "Redis responding: $RESPONSE"
    else
        print_error "Redis not responding"
    fi
    
    echo -e "\nTesting SET/GET operations..."
    docker exec inventory_redis redis-cli SET test:interactive "Hello from test" >/dev/null 2>&1
    VALUE=$(docker exec inventory_redis redis-cli GET test:interactive 2>/dev/null)
    docker exec inventory_redis redis-cli DEL test:interactive >/dev/null 2>&1
    
    if [ "$VALUE" = "Hello from test" ]; then
        print_success "Redis SET/GET working"
    else
        print_error "Redis SET/GET failed"
    fi
    
    wait_for_enter
}

function test_frontend() {
    print_header "Testing Frontend"
    
    echo "Calling: GET http://localhost:3000"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    
    if [ "$STATUS" = "200" ]; then
        print_success "Frontend accessible (HTTP $STATUS)"
        print_info "Open in browser: http://localhost:3000"
    else
        print_error "Frontend failed (HTTP $STATUS)"
    fi
    
    wait_for_enter
}

function test_docker_services() {
    print_header "Testing Docker Services Status"
    
    echo "Checking all services..."
    docker-compose ps
    
    RUNNING=$(docker-compose ps --filter "status=running" --format json 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$RUNNING" = "4" ]; then
        print_success "All 4 services running"
    else
        print_error "Expected 4 services, found $RUNNING running"
    fi
    
    wait_for_enter
}

function test_database_indexes() {
    print_header "Testing Database Indexes"
    
    echo "Counting indexes in database..."
    INDEX_COUNT=$(docker exec inventory_db psql -U postgres -d inventory_db -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'" 2>/dev/null | tr -d ' ')
    
    echo "Found $INDEX_COUNT indexes"
    
    if [ "$INDEX_COUNT" -gt "50" ]; then
        print_success "Database has $INDEX_COUNT indexes (expected ~55)"
    else
        print_error "Expected ~55 indexes, found only $INDEX_COUNT"
    fi
    
    wait_for_enter
}

function test_logs() {
    print_header "Checking Backend Logs for Errors"
    
    echo "Analyzing last 100 log lines..."
    ERROR_COUNT=$(docker-compose logs backend --tail 100 | grep -i "error\|exception\|traceback" | wc -l | tr -d ' ')
    
    if [ "$ERROR_COUNT" = "0" ]; then
        print_success "No errors found in logs"
    else
        print_info "Found $ERROR_COUNT error-related messages (review logs to confirm if critical)"
    fi
    
    wait_for_enter
}

function view_backend_logs() {
    print_header "Backend Logs (Last 30 Lines)"
    
    docker-compose logs backend --tail 30
    
    wait_for_enter
}

function view_database_schema() {
    print_header "Database Schema - Tenants Table"
    
    docker exec inventory_db psql -U postgres -d inventory_db -c "\d tenants" 2>/dev/null
    
    wait_for_enter
}

function run_full_suite() {
    print_header "Running Full Test Suite"
    
    bash scripts/test-phase2.sh
    
    wait_for_enter
}

function open_urls() {
    print_header "Opening URLs in Browser"
    
    print_info "Opening Frontend (http://localhost:3000)..."
    open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Please open manually: http://localhost:3000"
    
    sleep 1
    
    print_info "Opening Swagger Docs (http://localhost:8000/docs)..."
    open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || echo "Please open manually: http://localhost:8000/docs"
    
    wait_for_enter
}

function show_menu() {
    clear
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║     Interactive Testing Menu - Phase 2               ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Quick Tests:"
    echo "  1) Backend Health Check"
    echo "  2) Swagger Documentation"
    echo "  3) Database Tables"
    echo "  4) Redis Connection"
    echo "  5) Frontend Accessibility"
    echo ""
    echo "Detailed Tests:"
    echo "  6) Docker Services Status"
    echo "  7) Database Indexes"
    echo "  8) Backend Logs (errors)"
    echo ""
    echo "Information:"
    echo "  9) View Backend Logs"
    echo " 10) View Database Schema"
    echo ""
    echo "Actions:"
    echo " 11) Run Full Automated Suite"
    echo " 12) Open URLs in Browser"
    echo ""
    echo "  0) Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Select option: " choice
    
    case $choice in
        1) test_backend_health ;;
        2) test_swagger_docs ;;
        3) test_database_tables ;;
        4) test_redis ;;
        5) test_frontend ;;
        6) test_docker_services ;;
        7) test_database_indexes ;;
        8) test_logs ;;
        9) view_backend_logs ;;
        10) view_database_schema ;;
        11) run_full_suite ;;
        12) open_urls ;;
        0) 
            echo -e "\n${GREEN}Thanks for testing! 🧪✨${NC}\n"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            sleep 2
            ;;
    esac
done
