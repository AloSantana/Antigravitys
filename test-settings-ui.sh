#!/bin/bash
# Settings UI Enhancement Test Script
# Tests all new endpoints and UI functionality

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "============================================"
echo "Settings UI Enhancement - Test Suite"
echo "============================================"
echo ""
echo "API Base: $API_BASE"
echo "Frontend: $FRONTEND_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    echo -n "Testing: $description... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        echo "  Response: $(echo "$body" | jq -c '.' 2>/dev/null || echo "$body")"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "  Response: $body"
        return 1
    fi
}

# Test counter
total_tests=0
passed_tests=0

# Test 1: Backend Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "GET" "/health" "Backend health endpoint"; then
    ((passed_tests++))
fi
echo ""

# Test 2: Get Available Models
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Get Available Models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "GET" "/settings/models" "Get available AI models"; then
    ((passed_tests++))
fi
echo ""

# Test 3: Set Active Model (Gemini)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Set Active Model to Gemini"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "POST" "/settings/models?model_id=gemini" "Set active model to Gemini"; then
    ((passed_tests++))
fi
echo ""

# Test 4: Set Active Model (Auto)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Set Active Model to Auto"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "POST" "/settings/models?model_id=auto" "Set active model to Auto"; then
    ((passed_tests++))
fi
echo ""

# Test 5: Reload Environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Reload Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "POST" "/settings/reload-env" "Reload environment variables"; then
    ((passed_tests++))
fi
echo ""

# Test 6: Ngrok Status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6: Ngrok Tunnel Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))
if test_endpoint "GET" "/ngrok/status" "Get ngrok tunnel status"; then
    ((passed_tests++))
fi
echo ""

# Test 7: Frontend HTML Contains New Elements
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 7: Frontend HTML Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total_tests++))

html_file="./frontend/index.html"
if [ ! -f "$html_file" ]; then
    echo -e "${RED}✗ FAIL${NC} - frontend/index.html not found"
else
    checks=0
    total_checks=8
    
    # Check for key elements
    echo -n "  Checking for live status banner... "
    if grep -q "live-status-banner" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for model selection UI... "
    if grep -q "model-selection-group" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for reload environment button... "
    if grep -q "reloadEnvironment()" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for ngrok section... "
    if grep -q "ngrokStatusContainer" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for selectModel function... "
    if grep -q "function selectModel" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for updateLiveStatusBanner function... "
    if grep -q "function updateLiveStatusBanner" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for copyToClipboard function... "
    if grep -q "function copyToClipboard" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "  Checking for CSS styles... "
    if grep -q ".live-status-banner" "$html_file" && grep -q ".model-radio-option" "$html_file"; then
        echo -e "${GREEN}✓${NC}"
        ((checks++))
    else
        echo -e "${RED}✗${NC}"
    fi
    
    if [ $checks -eq $total_checks ]; then
        echo -e "  ${GREEN}✓ PASS${NC} - All HTML elements present ($checks/$total_checks)"
        ((passed_tests++))
    else
        echo -e "  ${YELLOW}⚠ PARTIAL${NC} - Some elements missing ($checks/$total_checks)"
    fi
fi
echo ""

# Summary
echo "============================================"
echo "Test Summary"
echo "============================================"
echo "Total Tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"
echo ""

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Open browser to $FRONTEND_URL"
    echo "2. Navigate to Settings tab"
    echo "3. Test UI interactions:"
    echo "   - Select different models"
    echo "   - Click reload environment"
    echo "   - Check ngrok status"
    echo "   - Verify live status banner updates"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please check:"
    echo "1. Backend is running on $API_BASE"
    echo "2. All endpoints are properly configured"
    echo "3. Frontend files are in place"
    exit 1
fi
