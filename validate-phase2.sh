#!/bin/bash

# Phase 2 Settings Implementation Validation Script
# Validates that all components are properly implemented

echo "🔍 Validating Phase 2 - Settings GUI & Auth Dashboard Implementation"
echo "================================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT FOUND"
        ((FAILED++))
        return 1
    fi
}

# Function to check for specific content
check_content() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
        return 1
    fi
}

echo "📁 Checking Backend Files..."
echo "----------------------------"
check_file "backend/settings_manager.py"
check_file "backend/main.py"
check_file "backend/requirements.txt"
echo ""

echo "🎨 Checking Frontend Files..."
echo "----------------------------"
check_file "frontend/index.html"
echo ""

echo "🧪 Checking Test Files..."
echo "----------------------------"
check_file "tests/test_settings_api.py"
echo ""

echo "📚 Checking Documentation..."
echo "----------------------------"
check_file "PHASE2_SETTINGS_COMPLETE.md"
echo ""

echo "🔍 Checking Backend Implementation..."
echo "----------------------------"
check_content "backend/settings_manager.py" "class SettingsManager" "SettingsManager class defined"
check_content "backend/settings_manager.py" "def get_settings" "get_settings() method"
check_content "backend/settings_manager.py" "def update_settings" "update_settings() method"
check_content "backend/settings_manager.py" "def get_mcp_servers_status" "get_mcp_servers_status() method"
check_content "backend/settings_manager.py" "def validate_api_key" "validate_api_key() method"
check_content "backend/settings_manager.py" "SENSITIVE_VARS" "Sensitive variables protection"
check_content "backend/settings_manager.py" "Fernet" "Encryption implementation"
echo ""

echo "🔍 Checking API Endpoints..."
echo "----------------------------"
check_content "backend/main.py" "GET /settings" "GET /settings endpoint"
check_content "backend/main.py" "POST /settings" "POST /settings endpoint"
check_content "backend/main.py" "GET /settings/models" "GET /settings/models endpoint"
check_content "backend/main.py" "POST /settings/models" "POST /settings/models endpoint"
check_content "backend/main.py" "GET /settings/mcp" "GET /settings/mcp endpoint"
check_content "backend/main.py" "POST /settings/mcp" "POST /settings/mcp/{server} endpoint"
check_content "backend/main.py" "POST /settings/validate" "POST /settings/validate endpoint"
check_content "backend/main.py" "POST /settings/api-keys" "POST /settings/api-keys endpoint"
check_content "backend/main.py" "GET /settings/env" "GET /settings/env endpoint"
check_content "backend/main.py" "POST /settings/env" "POST /settings/env endpoint"
check_content "backend/main.py" "GET /settings/export" "GET /settings/export endpoint"
check_content "backend/main.py" "POST /settings/test-connection" "POST /settings/test-connection endpoint"
check_content "backend/main.py" "settings_manager = SettingsManager()" "SettingsManager initialization"
echo ""

echo "🔍 Checking Frontend Implementation..."
echo "----------------------------"
check_content "frontend/index.html" "⚙️ Settings" "Settings tab"
check_content "frontend/index.html" "settings-panel" "Settings panel"
check_content "frontend/index.html" "AI Model Configuration" "AI Model Configuration section"
check_content "frontend/index.html" "API Keys Management" "API Keys Management section"
check_content "frontend/index.html" "MCP Server Manager" "MCP Server Manager section"
check_content "frontend/index.html" "Server Configuration" "Server Configuration section"
check_content "frontend/index.html" "Environment Variables" "Environment Variables section"
check_content "frontend/index.html" "Configuration Export" "Configuration Export section"
check_content "frontend/index.html" "loadSettings()" "loadSettings() function"
check_content "frontend/index.html" "loadModels()" "loadModels() function"
check_content "frontend/index.html" "loadMCPServers()" "loadMCPServers() function"
check_content "frontend/index.html" "updateApiKey()" "updateApiKey() function"
check_content "frontend/index.html" "testConnection()" "testConnection() function"
check_content "frontend/index.html" "exportConfiguration()" "exportConfiguration() function"
echo ""

echo "🔍 Checking CSS Styling..."
echo "----------------------------"
check_content "frontend/index.html" ".settings-container" "Settings container CSS"
check_content "frontend/index.html" ".settings-section" "Settings section CSS"
check_content "frontend/index.html" ".mcp-server-item" "MCP server item CSS"
check_content "frontend/index.html" ".model-card" "Model card CSS"
check_content "frontend/index.html" ".toggle-switch" "Toggle switch CSS"
check_content "frontend/index.html" ".env-var-table" "Environment variable table CSS"
check_content "frontend/index.html" "@media (max-width: 1024px)" "Responsive design"
echo ""

echo "🔍 Checking Test Coverage..."
echo "----------------------------"
check_content "tests/test_settings_api.py" "class TestSettingsEndpoints" "Settings endpoint tests"
check_content "tests/test_settings_api.py" "class TestAIModelsEndpoints" "AI models endpoint tests"
check_content "tests/test_settings_api.py" "class TestMCPServerEndpoints" "MCP server endpoint tests"
check_content "tests/test_settings_api.py" "class TestAPIKeyEndpoints" "API key endpoint tests"
check_content "tests/test_settings_api.py" "class TestEnvironmentVariablesEndpoints" "Environment variables tests"
check_content "tests/test_settings_api.py" "class TestConnectionTestEndpoints" "Connection test tests"
check_content "tests/test_settings_api.py" "class TestConfigurationExport" "Configuration export tests"
check_content "tests/test_settings_api.py" "class TestSettingsManager" "SettingsManager tests"
check_content "tests/test_settings_api.py" "class TestErrorHandling" "Error handling tests"
check_content "tests/test_settings_api.py" "class TestSecurityMeasures" "Security tests"
echo ""

echo "🔍 Checking Dependencies..."
echo "----------------------------"
check_content "backend/requirements.txt" "cryptography" "cryptography dependency"
check_content "backend/requirements.txt" "pydantic-settings" "pydantic-settings dependency"
check_content "backend/requirements.txt" "python-dotenv" "python-dotenv dependency"
echo ""

echo "🔍 Checking Documentation..."
echo "----------------------------"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Overview" "Documentation overview"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Features Implemented" "Features section"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## API Endpoints" "API documentation"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Frontend Components" "Frontend documentation"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Security Features" "Security documentation"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Testing" "Testing documentation"
check_content "PHASE2_SETTINGS_COMPLETE.md" "## Usage Guide" "Usage guide"
echo ""

# Line counts
echo "📊 Implementation Statistics"
echo "----------------------------"
if [ -f "backend/settings_manager.py" ]; then
    LINES=$(wc -l < backend/settings_manager.py)
    echo -e "settings_manager.py: ${YELLOW}${LINES}${NC} lines"
fi

if [ -f "backend/main.py" ]; then
    SETTINGS_LINES=$(grep -A 500 "Settings & Configuration API" backend/main.py | grep -B 500 "End Settings API" | wc -l)
    echo -e "main.py (settings endpoints): ${YELLOW}${SETTINGS_LINES}${NC} lines"
fi

if [ -f "tests/test_settings_api.py" ]; then
    TEST_LINES=$(wc -l < tests/test_settings_api.py)
    echo -e "test_settings_api.py: ${YELLOW}${TEST_LINES}${NC} lines"
fi

if [ -f "frontend/index.html" ]; then
    SETTINGS_HTML=$(grep -A 200 "Settings Panel" frontend/index.html | wc -l)
    SETTINGS_CSS=$(grep -A 200 "Settings Panel Styles" frontend/index.html | wc -l)
    SETTINGS_JS=$(grep -A 300 "Settings Panel Functions" frontend/index.html | wc -l)
    echo -e "index.html (settings HTML): ${YELLOW}${SETTINGS_HTML}${NC} lines"
    echo -e "index.html (settings CSS): ${YELLOW}${SETTINGS_CSS}${NC} lines"
    echo -e "index.html (settings JS): ${YELLOW}${SETTINGS_JS}${NC} lines"
fi

echo ""

# Count test methods
if [ -f "tests/test_settings_api.py" ]; then
    TEST_COUNT=$(grep -c "def test_" tests/test_settings_api.py)
    echo -e "Total test methods: ${YELLOW}${TEST_COUNT}${NC}"
fi

# Count API endpoints
if [ -f "backend/main.py" ]; then
    ENDPOINT_COUNT=$(grep -c "@app\.\(get\|post\)\(\"/settings" backend/main.py)
    echo -e "Total settings endpoints: ${YELLOW}${ENDPOINT_COUNT}${NC}"
fi

echo ""
echo "================================================================="
echo -e "📋 Validation Summary"
echo "================================================================="
echo -e "${GREEN}✓ Passed:${NC} $PASSED"
echo -e "${RED}✗ Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All validations passed! Implementation is complete.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some validations failed. Please review the output above.${NC}"
    exit 1
fi
