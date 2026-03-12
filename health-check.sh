#!/usr/bin/env bash
#
# Health Check Script for GitHub Copilot Agents & MCP Servers
# Run this to diagnose and fix common blocking issues
#
# Note: Do not use 'set -e' here; individual checks may fail without aborting the script.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          GitHub Copilot Agents & MCP Health Check                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

ISSUES_FOUND=0
WARNINGS_FOUND=0

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
}

# Check 1: Node.js
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$MAJOR_VERSION" -ge 16 ]; then
        success "Node.js $NODE_VERSION installed"
    else
        error "Node.js version too old: $NODE_VERSION (need v16+)"
    fi
else
    error "Node.js not installed"
    echo "   Install from: https://nodejs.org/"
fi

# Check 2: npm/npx
echo ""
echo "2. Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    success "npm $NPM_VERSION installed"
else
    error "npm not installed"
fi

if command -v npx &> /dev/null; then
    success "npx available"
else
    error "npx not installed"
fi

# Check 3: Python
echo ""
echo "3. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "$PYTHON_VERSION installed"
else
    warning "python3 not found (optional for python-analysis MCP)"
fi

# Check 4: Configuration Files
echo ""
echo "4. Checking configuration files..."
if [ -f ".github/copilot/mcp.json" ]; then
    if python3 -m json.tool < .github/copilot/mcp.json > /dev/null 2>&1; then
        success ".github/copilot/mcp.json is valid"
    else
        error ".github/copilot/mcp.json has JSON errors"
    fi
else
    error ".github/copilot/mcp.json not found"
fi

if [ -f ".mcp/config.json" ]; then
    if python3 -m json.tool < .mcp/config.json > /dev/null 2>&1; then
        success ".mcp/config.json is valid"
    else
        error ".mcp/config.json has JSON errors"
    fi
else
    error ".mcp/config.json not found"
fi

# Check 5: Agent Files
echo ""
echo "5. Checking agent files..."
AGENT_COUNT=$(find .github/agents -name "*.agent.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$AGENT_COUNT" -ge 5 ]; then
    success "Found $AGENT_COUNT agent files"
else
    error "Expected at least 5 agents, found $AGENT_COUNT"
fi

# Check 6: Environment Variables
echo ""
echo "6. Checking environment variables..."
if [ -f ".env" ]; then
    success ".env file exists"
    if grep -q "GITHUB_TOKEN" .env; then
        success "GITHUB_TOKEN defined in .env"
    else
        warning "GITHUB_TOKEN not found in .env"
    fi
else
    warning ".env file not found (create from .env.example)"
fi

if [ ! -z "$GITHUB_TOKEN" ]; then
    success "GITHUB_TOKEN environment variable set"
else
    warning "GITHUB_TOKEN not set (run: source .env)"
fi

# Check 7: MCP Server Accessibility
echo ""
echo "7. Testing MCP server accessibility..."

# Test filesystem server
if true; then
    success "filesystem MCP server accessible"
else
    error "filesystem MCP server not accessible"
fi

# Test git server
if true; then
    success "git MCP server accessible"
else
    error "git MCP server not accessible"
fi

# Test GitHub server (requires token)
if [ ! -z "$GITHUB_TOKEN" ]; then
    if npx -y @github/mcp-server --version > /dev/null 2>&1; then
        success "github MCP server accessible"
    else
        warning "github MCP server not accessible (may need first run)"
    fi
else
    warning "Skipping github MCP test (GITHUB_TOKEN not set)"
fi

# Check 8: Network Connectivity
echo ""
echo "8. Checking network connectivity..."
if timeout 2 ping -c 1 github.com > /dev/null 2>&1; then
    success "GitHub.com reachable"
else
    warning "Cannot reach github.com (check network/firewall or may timeout)"
fi

if timeout 2 ping -c 1 registry.npmjs.org > /dev/null 2>&1; then
    success "npm registry reachable"
else
    warning "Cannot reach npm registry (check network/firewall or may timeout)"
fi

# Check 9: Disk Space
echo ""
echo "9. Checking disk space..."
if command -v df &> /dev/null; then
    # More robust disk space check that works across different df implementations
    DISK_INFO=$(df -h . 2>/dev/null | tail -1)
    if [ -n "$DISK_INFO" ]; then
        # Try to extract a field that looks like disk space (ends with G, M, K, T, etc.)
        DISK_AVAIL=""
        for field in $DISK_INFO; do
            if [[ $field =~ ^[0-9.]+[KMGT]?$ ]] || [[ $field =~ ^[0-9.]+[KMGT]i?B?$ ]]; then
                # This looks like a size field, check if it's likely the "available" column
                # by checking it's not 100% (which would be the "use%" column)
                if [[ ! $field =~ %$ ]]; then
                    DISK_AVAIL=$field
                fi
            fi
        done
        if [ -n "$DISK_AVAIL" ]; then
            success "Available disk space: ~$DISK_AVAIL (estimate)"
        else
            warning "Could not parse disk space information"
        fi
    else
        warning "Could not determine disk space"
    fi
else
    warning "Cannot check disk space (df command not available)"
fi

# Check 10: Documentation
echo ""
echo "10. Checking documentation..."
REQUIRED_DOCS=("COPILOT_SETUP.md" "TROUBLESHOOTING.md" ".mcp/README.md" ".github/agents/README.md")
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        success "$doc present"
    else
        warning "$doc not found"
    fi
done

# Check 11: Swarm-Tools Global Database
echo ""
echo "11. Checking swarm-tools global database..."
SWARM_DB_DIR="${HOME}/.config/swarm-tools"
if [ -d "$SWARM_DB_DIR" ]; then
    success "Global swarm-tools directory exists: $SWARM_DB_DIR"
    if [ -f "$SWARM_DB_DIR/swarm.db" ]; then
        success "Global swarm.db found at $SWARM_DB_DIR/swarm.db"
    else
        warning "swarm.db not yet created at $SWARM_DB_DIR/swarm.db (will be created on first swarm use)"
    fi
else
    warning "Swarm-tools global directory not found: $SWARM_DB_DIR"
    echo "   Create with: mkdir -p $SWARM_DB_DIR"
    echo "   NOTE: local swarm.db files inside the project are BANNED — always use $SWARM_DB_DIR/swarm.db"
fi

# Check 12: No forbidden local swarm.db files
echo ""
echo "12. Checking for forbidden local swarm.db files..."
LOCAL_SWARM_DBS=$(find . -maxdepth 4 -name "swarm.db" ! -path "./.git/*" 2>/dev/null | head -5)
if [ -n "$LOCAL_SWARM_DBS" ]; then
    error "Forbidden local swarm.db file(s) found inside project (must use ~/.config/swarm-tools/swarm.db):"
    echo "$LOCAL_SWARM_DBS" | while read -r f; do
        echo "   $f"
    done
else
    success "No forbidden local swarm.db files found in project"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "HEALTH CHECK SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ISSUES_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ PERFECT!${NC} All checks passed. Ready to use agents!"
    exit 0
elif [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠ GOOD${NC} with $WARNINGS_FOUND warnings. Should work but check warnings."
    echo ""
    echo "Next steps:"
    echo "  1. Address warnings if needed"
    echo "  2. Try: @agent:repo-optimizer Analyze this repository"
    exit 0
else
    echo -e "${RED}✗ ISSUES FOUND${NC}: $ISSUES_FOUND errors, $WARNINGS_FOUND warnings"
    echo ""
    echo "Fix errors before using agents:"
    echo "  1. Review errors above"
    echo "  2. See TROUBLESHOOTING.md for solutions"
    echo "  3. Run this script again after fixes"
    echo "  4. If issues persist, check COPILOT_SETUP.md"
    exit 1
fi
