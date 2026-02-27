#!/bin/bash

################################################################################
# Antigravity Workspace - Setup Validation Script
# Validates installation and configuration
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSED=0
FAILED=0
WARNINGS=0

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║     Antigravity Workspace - Setup Validation              ║${NC}"
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

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate Python installation
validate_python() {
    print_section "Python Environment"
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        check_pass "Python installed: $PYTHON_VERSION"
        
        # Check version
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            check_pass "Python version is 3.8+ ✓"
        else
            check_fail "Python version should be 3.8+, got $PYTHON_VERSION"
        fi
    else
        check_fail "Python 3 is not installed"
    fi
    
    # Check pip
    if command_exists pip3; then
        check_pass "pip installed: $(pip3 --version | cut -d' ' -f2)"
    else
        check_fail "pip is not installed"
    fi
    
    # Check virtual environment
    if [ -d "$SCRIPT_DIR/venv" ]; then
        check_pass "Virtual environment exists"
        
        # Try to activate and check packages
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/venv/bin/activate" 2>/dev/null || true
        if [ -n "$VIRTUAL_ENV" ]; then
            check_pass "Virtual environment can be activated"
            
            # Check key packages
            PACKAGES=("fastapi" "uvicorn" "chromadb" "langchain" "pydantic" "google.genai")
            for pkg in "${PACKAGES[@]}"; do
                # Use a more robust check that catches any exception during import
                if python -c "import $pkg" 2>/dev/null; then
                    check_pass "Package '$pkg' is installed and loadable"
                elif [ "$pkg" == "chromadb" ]; then
                    # Special handling for chromadb which might fail on Python 3.14 but still be "installed"
                    if pip show chromadb >/dev/null 2>&1; then
                        check_warn "Package 'chromadb' is installed but failed to load (common on Python 3.14+). Vector features will be limited."
                    else
                        check_warn "Package 'chromadb' is NOT installed"
                    fi
                else
                    check_warn "Package '$pkg' is not installed or failed to load"
                fi
            done
        else
            check_warn "Could not activate virtual environment"
        fi
    else
        check_warn "Virtual environment not found at $SCRIPT_DIR/venv"
    fi
}

# Validate Node.js and npm
validate_nodejs() {
    print_section "Node.js Environment"
    
    if command_exists node; then
        NODE_VERSION=$(node -v)
        check_pass "Node.js installed: $NODE_VERSION"
        
        MAJOR=$(echo "$NODE_VERSION" | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$MAJOR" -ge 18 ]; then
            check_pass "Node.js version is 18+ ✓"
        else
            check_warn "Node.js version should be 18+, got $NODE_VERSION"
        fi
    else
        check_warn "Node.js is not installed (required for MCP servers)"
    fi
    
    if command_exists npm; then
        NPM_VERSION=$(npm -v)
        check_pass "npm installed: $NPM_VERSION"
    else
        check_warn "npm is not installed"
    fi
    
    if command_exists npx; then
        check_pass "npx is available"
    else
        check_warn "npx is not available"
    fi
}

# Validate configuration files
validate_configuration() {
    print_section "Configuration Files"
    
    # Check .env file
    if [ -f "$SCRIPT_DIR/.env" ]; then
        check_pass ".env file exists"
        
        # Check for required variables
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/.env" 2>/dev/null || true
        
        if [ -n "$GEMINI_API_KEY" ]; then
            if [ "$GEMINI_API_KEY" != "your_gemini_api_key_here" ]; then
                check_pass "GEMINI_API_KEY is configured"
            else
                check_warn "GEMINI_API_KEY is not set (using default)"
            fi
        else
            check_warn "GEMINI_API_KEY is not set"
        fi
        
        if [ -n "$COPILOT_MCP_GITHUB_TOKEN" ]; then
            if [ "$COPILOT_MCP_GITHUB_TOKEN" != "your_github_token_here" ]; then
                check_pass "GitHub token is configured"
            else
                check_warn "GitHub token is not set (using default)"
            fi
        else
            check_warn "GitHub token is not configured (optional)"
        fi
    else
        check_fail ".env file not found"
        echo "    Run: ./configure.sh to create it"
    fi
    
    # Check MCP configuration
    if [ -f "$SCRIPT_DIR/.mcp/config.json" ]; then
        check_pass "MCP config exists (.mcp/config.json)"
    else
        check_warn "MCP config not found"
    fi
    
    if [ -f "$SCRIPT_DIR/.github/copilot/mcp.json" ]; then
        check_pass "GitHub Copilot MCP config exists"
    else
        check_warn "GitHub Copilot MCP config not found"
    fi
}

# Validate directory structure
validate_directories() {
    print_section "Directory Structure"
    
    REQUIRED_DIRS=(
        "backend"
        "frontend"
        "drop_zone"
        "artifacts"
        "logs"
        ".mcp"
        ".github/agents"
        ".github/copilot"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$SCRIPT_DIR/$dir" ]; then
            check_pass "Directory exists: $dir"
        else
            check_warn "Directory missing: $dir"
            mkdir -p "$SCRIPT_DIR/$dir" 2>/dev/null || true
        fi
    done
}

# Validate agents
validate_agents() {
    print_section "Custom Agents"
    
    AGENTS_DIR="$SCRIPT_DIR/.github/agents"
    
    if [ -d "$AGENTS_DIR" ]; then
        AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.agent.md" | wc -l)
        check_pass "Found $AGENT_COUNT custom agents"
        
        # List agents
        for agent in "$AGENTS_DIR"/*.agent.md; do
            if [ -f "$agent" ]; then
                AGENT_NAME=$(basename "$agent" .agent.md)
                check_pass "  - $AGENT_NAME"
            fi
        done
    else
        check_warn "Agents directory not found"
    fi
}

# Validate Docker setup
validate_docker() {
    print_section "Docker Environment"
    
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        check_pass "Docker installed: $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker info >/dev/null 2>&1; then
            check_pass "Docker daemon is running"
        else
            check_warn "Docker daemon is not running"
        fi
    else
        check_warn "Docker is not installed (optional)"
    fi
    
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        check_pass "Docker Compose is available"
    else
        check_warn "Docker Compose is not available (optional)"
    fi
    
    # Check docker-compose.yml
    if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
        check_pass "docker-compose.yml exists"
    else
        check_warn "docker-compose.yml not found"
    fi
}

# Validate services
validate_services() {
    print_section "Services Status"
    
    # Check systemd service
    if systemctl list-unit-files | grep -q antigravity.service; then
        check_pass "Systemd service is installed"
        
        if systemctl is-enabled antigravity.service >/dev/null 2>&1; then
            check_pass "Service is enabled"
        else
            check_warn "Service is not enabled"
        fi
        
        if systemctl is-active antigravity.service >/dev/null 2>&1; then
            check_pass "Service is running"
        else
            check_warn "Service is not running"
        fi
    else
        check_warn "Systemd service not installed (optional)"
    fi
    
    # Check if backend port is open
    if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
        check_pass "Backend port (8000) is open"
    else
        check_warn "Backend port (8000) is not open"
    fi
}

# Validate web interface
validate_web_interface() {
    print_section "Web Interface"
    
    if [ -f "$SCRIPT_DIR/frontend/index.html" ]; then
        check_pass "Frontend HTML exists"
    else
        check_fail "Frontend HTML not found"
    fi
    
    # Try to connect to backend
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        check_pass "Backend API is accessible"
    else
        check_warn "Backend API is not accessible (service may not be running)"
    fi
}

# Validate scripts
validate_scripts() {
    print_section "Helper Scripts"
    
    SCRIPTS=(
        "install.sh"
        "configure.sh"
        "start.sh"
        "stop.sh"
        "health-check.sh"
    )
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$SCRIPT_DIR/$script" ]; then
            if [ -x "$SCRIPT_DIR/$script" ]; then
                check_pass "Script is executable: $script"
            else
                check_warn "Script exists but not executable: $script"
            fi
        else
            check_warn "Script not found: $script"
        fi
    done
}

# Print summary
print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                      VALIDATION SUMMARY                    ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}   $PASSED checks"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS checks"
    echo -e "  ${RED}Failed:${NC}   $FAILED checks"
    echo ""
    
    TOTAL=$((PASSED + WARNINGS + FAILED))
    if [ $TOTAL -gt 0 ]; then
        SUCCESS_RATE=$((PASSED * 100 / TOTAL))
        echo -e "  Success Rate: $SUCCESS_RATE%"
    fi
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ Validation completed successfully!${NC}"
        if [ $WARNINGS -gt 0 ]; then
            echo -e "${YELLOW}  Note: There are $WARNINGS warnings that should be addressed.${NC}"
        fi
    else
        echo -e "${RED}✗ Validation failed with $FAILED error(s).${NC}"
        echo -e "  Please fix the errors and run validation again."
    fi
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ $FAILED -gt 0 ]; then
        exit 1
    fi
}

# Main validation flow
main() {
    print_header
    
    validate_python
    validate_nodejs
    validate_configuration
    validate_directories
    validate_agents
    validate_docker
    validate_services
    validate_web_interface
    validate_scripts
    
    print_summary
}

main "$@"
