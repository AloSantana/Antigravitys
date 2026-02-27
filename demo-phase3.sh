#!/bin/bash
#
# Phase 3 Demo Script
# Demonstrates the Smart Auto-Issue Finder and Health Monitor capabilities
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   Phase 3: Smart Auto-Issue Finder & Health Monitor   ║${NC}"
echo -e "${BOLD}${CYAN}║                    Demo Script                         ║${NC}"
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to print section header
print_header() {
    echo -e "\n${BOLD}${BLUE}▶ $1${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print info
print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to run command with header
run_demo() {
    local title="$1"
    shift
    print_header "$title"
    print_info "Command: $*"
    echo ""
    "$@" || true
    echo ""
}

# Check dependencies
print_header "Checking Dependencies"
if ! python -c "import psutil, requests" 2>/dev/null; then
    print_warning "Installing required dependencies..."
    pip install -q psutil requests pyyaml
    print_success "Dependencies installed"
else
    print_success "All dependencies available"
fi

# Demo 1: Auto-Issue Finder - Help
run_demo "Auto-Issue Finder: Help & Options" \
    python tools/auto_issue_finder.py --help

# Demo 2: Quick Configuration Check
run_demo "Configuration Validation Check" \
    python tools/auto_issue_finder.py --checks config --no-color

# Demo 3: Docker Validation
run_demo "Docker Configuration Check" \
    python tools/auto_issue_finder.py --checks docker --no-color

# Demo 4: Shell Script Linting
print_header "Shell Script Linting (if any .sh files exist)"
if ls *.sh 1> /dev/null 2>&1; then
    python tools/auto_issue_finder.py --checks shell --no-color | head -30
else
    print_info "No shell scripts found in root directory"
fi
echo ""

# Demo 5: JSON Output
run_demo "JSON Output Format (first 30 lines)" \
    bash -c "python tools/auto_issue_finder.py --checks config --output json | head -30"

# Demo 6: Auto-Fix Demo
print_header "Auto-Fix Capabilities Demo"
print_info "Creating test script without shebang..."
echo 'echo "test script"' > /tmp/test_script.sh
print_info "Command: python tools/auto_issue_finder.py --checks shell --project-root /tmp --auto-fix"
echo ""
python tools/auto_issue_finder.py --checks shell --project-root /tmp --auto-fix --no-color || true
if head -1 /tmp/test_script.sh | grep -q "#!/"; then
    print_success "Shebang was automatically added!"
    echo "Content:"
    cat /tmp/test_script.sh
fi
rm -f /tmp/test_script.sh
echo ""

# Demo 7: Health Monitor Help
run_demo "Health Monitor: Help & Options" \
    python tools/health_monitor.py --help

# Demo 8: Health Monitor Status
run_demo "Health Monitor: Current Status" \
    python tools/health_monitor.py --status

# Demo 9: Static Analysis Sample
print_header "Static Analysis Sample (first 40 lines)"
print_info "Running static analysis on Python files..."
echo ""
python tools/auto_issue_finder.py --checks static --no-color | head -40
echo ""

# Demo 10: All Checks Summary
run_demo "Complete Diagnostic Summary" \
    bash -c "python tools/auto_issue_finder.py --no-color | grep -A 10 'Summary:'"

# Demo 11: File Structure
print_header "Phase 3 File Structure"
echo "Tools:"
ls -lh tools/*.py 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Tests:"
ls -lh tests/test_auto_issue_finder.py tests/test_health_monitor.py 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Documentation:"
ls -lh PHASE3*.md 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# Demo 12: Quick Test Run
print_header "Running Quick Test Sample"
print_info "Running a subset of tests..."
echo ""
if command -v pytest &> /dev/null; then
    pytest tests/test_auto_issue_finder.py::TestStaticAnalyzer::test_find_syntax_error \
           tests/test_health_monitor.py::TestSystemMonitor::test_get_metrics \
           -v --tb=short || true
else
    print_warning "pytest not installed. Install with: pip install pytest"
fi
echo ""

# Summary
print_header "Demo Summary"
echo -e "${BOLD}Phase 3 Components:${NC}"
echo ""
echo -e "${GREEN}✓${NC} Auto-Issue Finder (tools/auto_issue_finder.py)"
echo "  - Static code analysis"
echo "  - Shell script linting"
echo "  - Configuration validation"
echo "  - Dependency checking"
echo "  - Runtime health checks"
echo "  - Docker validation"
echo "  - Auto-fix capabilities"
echo ""
echo -e "${GREEN}✓${NC} Health Monitor (tools/health_monitor.py)"
echo "  - System resource monitoring"
echo "  - Service availability checking"
echo "  - Alert management"
echo "  - Auto-restart functionality"
echo "  - Metrics export"
echo "  - Daemon mode"
echo ""
echo -e "${GREEN}✓${NC} Comprehensive Tests"
echo "  - 75+ test cases"
echo "  - Unit and integration tests"
echo "  - Mock-based testing"
echo ""
echo -e "${GREEN}✓${NC} Complete Documentation"
echo "  - PHASE3_COMPLETE.md (full guide)"
echo "  - PHASE3_QUICK_REFERENCE.md (commands)"
echo "  - PHASE3_IMPLEMENTATION_SUMMARY.md (overview)"
echo ""

print_header "Quick Start Commands"
echo -e "${CYAN}# Run full diagnostic${NC}"
echo "python tools/auto_issue_finder.py --verbose"
echo ""
echo -e "${CYAN}# Auto-fix issues${NC}"
echo "python tools/auto_issue_finder.py --auto-fix"
echo ""
echo -e "${CYAN}# Start health monitoring${NC}"
echo "python tools/health_monitor.py --daemon --verbose"
echo ""
echo -e "${CYAN}# Check monitor status${NC}"
echo "python tools/health_monitor.py --status"
echo ""
echo -e "${CYAN}# Run tests${NC}"
echo "pytest tests/test_auto_issue_finder.py tests/test_health_monitor.py -v"
echo ""

echo -e "${BOLD}${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║          Phase 3 Demo Complete! 🎉                     ║${NC}"
echo -e "${BOLD}${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
