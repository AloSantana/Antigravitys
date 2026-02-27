#!/bin/bash

################################################################################
# Test Script for Installation Script Fixes
# Validates all critical fixes have been applied
################################################################################

set -eo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Installation Script Fixes - Verification Tests        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Check for rollback mechanism
echo -e "${BLUE}Test 1: Rollback Mechanism${NC}"
if grep -q "cleanup_on_error()" install.sh && grep -q "trap cleanup_on_error ERR" install.sh; then
    test_pass "Rollback mechanism exists in install.sh"
else
    test_fail "Rollback mechanism missing in install.sh"
fi

if grep -q "VENV_CREATED" install.sh && grep -q "CONFIG_BACKED_UP" install.sh; then
    test_pass "Tracking variables present"
else
    test_fail "Tracking variables missing"
fi

# Test 2: Check for sudo validation
echo ""
echo -e "${BLUE}Test 2: Sudo Validation${NC}"
if grep -q "sudo -n true 2>/dev/null" install.sh; then
    test_pass "Sudo validation check exists"
else
    test_fail "Sudo validation check missing"
fi

if grep -q "Sudo access verified" install.sh; then
    test_pass "Sudo success message exists"
else
    test_fail "Sudo success message missing"
fi

# Test 3: Check for hardcoded paths removal
echo ""
echo -e "${BLUE}Test 3: Hardcoded Paths Removed${NC}"
if grep -q "/home/runner/work/antigravity-workspace-template" install.sh install-remote.sh 2>/dev/null; then
    test_fail "Hardcoded paths still present!"
else
    test_pass "No hardcoded paths in install.sh"
    test_pass "No hardcoded paths in install-remote.sh"
fi

if grep -q 'root ${SCRIPT_DIR}/frontend' install.sh; then
    test_pass "Nginx config uses SCRIPT_DIR"
else
    test_fail "Nginx config doesn't use SCRIPT_DIR"
fi

# Test 4: Check shellcheck compliance
echo ""
echo -e "${BLUE}Test 4: ShellCheck Compliance${NC}"

check_shellcheck() {
    local script=$1
    local errors
    errors=$(shellcheck "$script" 2>&1 | grep -c "error" || true)
    local warnings
    warnings=$(shellcheck "$script" 2>&1 | grep -c "warning" || true)
    
    if [ "$errors" -eq 0 ]; then
        test_pass "$script has no errors"
    else
        test_fail "$script has $errors error(s)"
    fi
}

for script in install.sh install-remote.sh start.sh stop.sh configure.sh validate.sh; do
    if [ -f "$script" ]; then
        check_shellcheck "$script"
    fi
done

# Test 5: Check timestamp logging
echo ""
echo -e "${BLUE}Test 5: Timestamp Logging${NC}"

check_timestamps() {
    local script=$1
    if grep -q 'timestamp="$(date' "$script"; then
        test_pass "$script has timestamp logging"
    else
        test_fail "$script missing timestamp logging"
    fi
}

for script in install.sh install-remote.sh; do
    check_timestamps "$script"
done

# Test 6: Check error handling improvements
echo ""
echo -e "${BLUE}Test 6: Error Handling${NC}"

for script in install.sh install-remote.sh start.sh configure.sh validate.sh; do
    if grep -q "set -euo pipefail" "$script"; then
        test_pass "$script uses strict error handling"
    else
        test_fail "$script missing strict error handling"
    fi
done

# Test 7: Check quoting fixes
echo ""
echo -e "${BLUE}Test 7: Variable Quoting${NC}"

if grep -q 'cd "$SCRIPT_DIR" || exit' install.sh; then
    test_pass "cd commands have proper error handling"
else
    test_fail "cd commands missing error handling"
fi

if grep -q 'usermod -aG docker "$USER"' install.sh; then
    test_pass "Variables properly quoted"
else
    test_fail "Variables not properly quoted"
fi

# Test 8: Check shellcheck annotations
echo ""
echo -e "${BLUE}Test 8: ShellCheck Annotations${NC}"

if grep -q "# shellcheck source=/dev/null" install.sh; then
    test_pass "ShellCheck source annotations present"
else
    test_fail "ShellCheck source annotations missing"
fi

# Test 9: Check configuration backup
echo ""
echo -e "${BLUE}Test 9: Configuration Backup${NC}"

if grep -q 'BACKUP_DIR="${SCRIPT_DIR}/.backup_' install.sh; then
    test_pass "Configuration backup mechanism exists"
else
    test_fail "Configuration backup mechanism missing"
fi

# Test 10: Check read command fixes
echo ""
echo -e "${BLUE}Test 10: Read Command Fixes${NC}"

if grep -q 'read -r -p' install.sh configure.sh 2>/dev/null; then
    test_pass "Read commands use -r flag"
else
    test_fail "Read commands missing -r flag"
fi

# Summary
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
    echo -e "${GREEN}✓ All tests passed! Installation scripts are ready.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the fixes.${NC}"
    exit 1
fi
