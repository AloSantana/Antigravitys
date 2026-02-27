#!/bin/bash
#
# Phase 3 Verification Script
# Verifies all components are working correctly
#

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}Phase 3 Verification Script${NC}\n"

PASS=0
FAIL=0

check() {
    local name="$1"
    shift
    
    echo -n "Checking $name... "
    if "$@" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAIL++))
        return 1
    fi
}

# Check files exist
echo -e "${BOLD}File Existence:${NC}"
check "auto_issue_finder.py" test -f tools/auto_issue_finder.py
check "health_monitor.py" test -f tools/health_monitor.py
check "test_auto_issue_finder.py" test -f tests/test_auto_issue_finder.py
check "test_health_monitor.py" test -f tests/test_health_monitor.py
check "PHASE3_COMPLETE.md" test -f PHASE3_COMPLETE.md
check "demo-phase3.sh" test -f demo-phase3.sh

# Check executability
echo -e "\n${BOLD}File Permissions:${NC}"
check "auto_issue_finder.py executable" test -x tools/auto_issue_finder.py
check "health_monitor.py executable" test -x tools/health_monitor.py
check "demo-phase3.sh executable" test -x demo-phase3.sh

# Check CLI help
echo -e "\n${BOLD}CLI Interface:${NC}"
check "auto_issue_finder --help" python tools/auto_issue_finder.py --help
check "health_monitor --help" python tools/health_monitor.py --help

# Check basic functionality
echo -e "\n${BOLD}Basic Functionality:${NC}"
check "auto_issue_finder runs" timeout 10 python tools/auto_issue_finder.py --checks config --no-color
check "health_monitor status" python tools/health_monitor.py --status

# Check Python imports
echo -e "\n${BOLD}Python Imports:${NC}"
check "auto_issue_finder imports" python -c "import sys; sys.path.insert(0, 'tools'); import auto_issue_finder"
check "health_monitor imports" python -c "import sys; sys.path.insert(0, 'tools'); import health_monitor"

# Summary
echo -e "\n${BOLD}═══════════════════════════════════════${NC}"
echo -e "${BOLD}Verification Summary:${NC}"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo -e "${BOLD}═══════════════════════════════════════${NC}\n"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ All checks passed!${NC}"
    echo -e "${GREEN}Phase 3 is ready for use! 🎉${NC}\n"
    exit 0
else
    echo -e "${RED}${BOLD}✗ Some checks failed!${NC}"
    echo -e "${YELLOW}Please review the failures above.${NC}\n"
    exit 1
fi
