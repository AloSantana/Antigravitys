#!/bin/bash

################################################################################
# Antigravity Workspace - Setup Test Script
# Tests the complete installation and configuration
################################################################################

set +e  # Don't exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSED=0
FAILED=0

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║     Antigravity Workspace - Setup Test Suite              ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}═══ $1 ═══${NC}"
    echo ""
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Test 1: Backend Import
test_backend_import() {
    print_section "Test 1: Backend Module Import"
    
    cd "$SCRIPT_DIR/backend"
    if python3 -c "from main import app" 2>/dev/null; then
        check_pass "Backend imports successfully"
    else
        check_fail "Backend import failed"
        echo "    Run: pip3 install -r backend/requirements.txt"
    fi
}

# Test 2: Check Routes
test_backend_routes() {
    print_section "Test 2: Backend Routes"
    
    cd "$SCRIPT_DIR/backend"
    ROUTES=$(python3 -c "from main import app; routes = [r.path for r in app.routes]; print('\n'.join(routes))" 2>/dev/null)
    
    if echo "$ROUTES" | grep -q "/files"; then
        check_pass "Route /files exists"
    else
        check_fail "Route /files missing"
    fi
    
    if echo "$ROUTES" | grep -q "/upload"; then
        check_pass "Route /upload exists"
    else
        check_fail "Route /upload missing"
    fi
    
    if echo "$ROUTES" | grep -q "/ws"; then
        check_pass "WebSocket route /ws exists"
    else
        check_fail "WebSocket route /ws missing"
    fi
}

# Test 3: Frontend Files
test_frontend() {
    print_section "Test 3: Frontend Files"
    
    if [ -f "$SCRIPT_DIR/frontend/index.html" ]; then
        check_pass "Frontend index.html exists"
        
        # Check for dynamic URLs
        if grep -q "API_BASE" "$SCRIPT_DIR/frontend/index.html"; then
            check_pass "Frontend uses dynamic API URLs"
        else
            check_fail "Frontend has hardcoded URLs"
        fi
        
        # Check for WebSocket reconnection
        if grep -q "connectWebSocket" "$SCRIPT_DIR/frontend/index.html"; then
            check_pass "Frontend has WebSocket reconnection"
        else
            check_fail "Frontend missing WebSocket reconnection"
        fi
    else
        check_fail "Frontend index.html missing"
    fi
}

# Test 4: Configuration
test_configuration() {
    print_section "Test 4: Configuration Files"
    
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        check_pass ".env.example exists"
        
        # Check it doesn't have real API keys
        if grep -q "your_.*_here" "$SCRIPT_DIR/.env.example"; then
            check_pass ".env.example has placeholder values"
        else
            check_fail ".env.example may contain real API keys"
        fi
    else
        check_fail ".env.example missing"
    fi
    
    if [ -f "$SCRIPT_DIR/.gitignore" ]; then
        check_pass ".gitignore exists"
        
        if grep -q "^\.env$" "$SCRIPT_DIR/.gitignore"; then
            check_pass ".env is in .gitignore"
        else
            check_fail ".env not in .gitignore (security risk)"
        fi
    else
        check_fail ".gitignore missing"
    fi
}

# Test 5: Scripts
test_scripts() {
    print_section "Test 5: Helper Scripts"
    
    SCRIPTS=("install.sh" "configure.sh" "start.sh" "stop.sh" "validate.sh" "health-check.sh")
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$SCRIPT_DIR/$script" ]; then
            if [ -x "$SCRIPT_DIR/$script" ]; then
                check_pass "$script is executable"
            else
                check_fail "$script exists but not executable"
            fi
        else
            check_fail "$script missing"
        fi
    done
}

# Test 6: Directory Structure
test_directories() {
    print_section "Test 6: Directory Structure"
    
    DIRS=("backend" "frontend" "drop_zone" ".github/agents" ".mcp")
    
    for dir in "${DIRS[@]}"; do
        if [ -d "$SCRIPT_DIR/$dir" ]; then
            check_pass "Directory $dir exists"
        else
            check_fail "Directory $dir missing"
        fi
    done
}

# Test 7: Agent Files
test_agents() {
    print_section "Test 7: Custom Agents"
    
    AGENT_COUNT=$(find "$SCRIPT_DIR/.github/agents" -name "*.agent.md" 2>/dev/null | wc -l)
    
    if [ "$AGENT_COUNT" -ge 5 ]; then
        check_pass "Found $AGENT_COUNT agent files"
    else
        check_fail "Only $AGENT_COUNT agents found (expected at least 5)"
    fi
    
    # Check for specific agents
    EXPECTED_AGENTS=("full-stack-developer" "devops-infrastructure" "testing-stability-expert" "performance-optimizer" "docs-master")
    
    for agent in "${EXPECTED_AGENTS[@]}"; do
        if [ -f "$SCRIPT_DIR/.github/agents/${agent}.agent.md" ]; then
            check_pass "Agent $agent exists"
        else
            check_fail "Agent $agent missing"
        fi
    done
}

# Test 8: No Duplicate Routes
test_no_duplicates() {
    print_section "Test 8: No Duplicate Routes"
    
    cd "$SCRIPT_DIR/backend"
    ROUTE_COUNT=$(python3 -c "from main import app; routes = [r.path for r in app.routes]; print(len(routes))" 2>/dev/null)
    UNIQUE_ROUTE_COUNT=$(python3 -c "from main import app; routes = set([r.path for r in app.routes]); print(len(routes))" 2>/dev/null)
    
    if [ "$ROUTE_COUNT" = "$UNIQUE_ROUTE_COUNT" ]; then
        check_pass "No duplicate routes ($ROUTE_COUNT routes)"
    else
        check_fail "Found duplicate routes (total: $ROUTE_COUNT, unique: $UNIQUE_ROUTE_COUNT)"
    fi
}

# Print Summary
print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                      TEST SUMMARY                         ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Passed:${NC} $PASSED tests"
    echo -e "  ${RED}Failed:${NC} $FAILED tests"
    echo ""
    
    TOTAL=$((PASSED + FAILED))
    if [ $TOTAL -gt 0 ]; then
        SUCCESS_RATE=$((PASSED * 100 / TOTAL))
        echo -e "  Success Rate: $SUCCESS_RATE%"
    fi
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Run: ./configure.sh (if not done)"
        echo "  2. Run: ./start.sh"
        echo "  3. Open: http://localhost:8000"
    else
        echo -e "${RED}✗ Some tests failed.${NC}"
        echo ""
        echo "Please fix the issues above before proceeding."
    fi
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Main execution
main() {
    print_header
    
    test_backend_import
    test_backend_routes
    test_frontend
    test_configuration
    test_scripts
    test_directories
    test_agents
    test_no_duplicates
    
    print_summary
    
    if [ $FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

main "$@"
