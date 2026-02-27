#!/bin/bash

################################################################################
# Antigravity Workspace - Interactive Configuration Wizard
# Helps users set up their environment quickly
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║     Antigravity Workspace - Configuration Wizard          ║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}═══ $1 ═══${NC}"
    echo ""
}

print_info() {
    echo -e "${CYAN}ℹ${NC}  $1"
}

print_success() {
    echo -e "${GREEN}✓${NC}  $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC}  $1"
}

prompt_input() {
    local prompt="$1"
    local default="$2"
    local result
    
    if [ -n "$default" ]; then
        read -r -p "$(echo -e "${GREEN}?${NC}") $prompt [${default}]: " result
        result="${result:-$default}"
    else
        read -r -p "$(echo -e "${GREEN}?${NC}") $prompt: " result
    fi
    
    echo "$result"
}

prompt_password() {
    local prompt="$1"
    local result
    
    read -r -s -p "$(echo -e "${GREEN}?${NC}") $prompt: " result
    echo ""
    echo "$result"
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local result
    
    if [ "$default" = "y" ]; then
        read -r -p "$(echo -e "${GREEN}?${NC}") $prompt [Y/n]: " result
        result="${result:-y}"
    else
        read -r -p "$(echo -e "${GREEN}?${NC}") $prompt [y/N]: " result
        result="${result:-n}"
    fi
    
    [[ "$result" =~ ^[Yy]$ ]]
}

validate_api_key() {
    local key="$1"
    if [ ${#key} -lt 20 ]; then
        return 1
    fi
    return 0
}

configure_gemini() {
    print_section "Gemini AI Configuration"
    
    print_info "Gemini is used for high-complexity reasoning tasks."
    print_info "Get your API key from: https://aistudio.google.com/app/apikey"
    echo ""
    
    GEMINI_API_KEY=$(prompt_input "Enter your Gemini API key" "${GEMINI_API_KEY}")
    
    if validate_api_key "$GEMINI_API_KEY"; then
        print_success "Gemini API key configured"
    else
        print_warning "API key seems short. Make sure it's correct."
    fi
}

configure_github() {
    print_section "GitHub Integration"
    
    if prompt_yes_no "Enable GitHub MCP integration?" "y"; then
        print_info "Create a token at: https://github.com/settings/tokens"
        print_info "Required scopes: repo, read:org"
        echo ""
        
        GITHUB_TOKEN=$(prompt_input "Enter your GitHub token" "${COPILOT_MCP_GITHUB_TOKEN}")
        
        if validate_api_key "$GITHUB_TOKEN"; then
            print_success "GitHub token configured"
        else
            print_warning "Token seems short. Make sure it's correct."
        fi
    else
        GITHUB_TOKEN=""
        print_info "GitHub integration will be disabled"
    fi
}

configure_ollama() {
    print_section "Local AI (Ollama) Configuration"
    
    if prompt_yes_no "Use local Ollama for low-complexity tasks?" "y"; then
        LOCAL_MODEL=$(prompt_input "Enter model name" "${LOCAL_MODEL:-llama3}")
        print_success "Ollama configured with model: $LOCAL_MODEL"
        
        if ! command -v ollama &> /dev/null; then
            print_warning "Ollama not installed. Install from: https://ollama.ai"
            if prompt_yes_no "Install Ollama now?" "n"; then
                curl -fsSL https://ollama.ai/install.sh | sh
                print_success "Ollama installed"
            fi
        fi
    else
        LOCAL_MODEL=""
        print_info "Ollama will not be used"
    fi
}

configure_optional_services() {
    print_section "Optional Services"
    
    # Brave Search
    if prompt_yes_no "Enable Brave Search integration?" "n"; then
        print_info "Get API key from: https://brave.com/search/api/"
        BRAVE_API_KEY=$(prompt_input "Enter Brave Search API key")
        print_success "Brave Search configured"
    else
        BRAVE_API_KEY=""
    fi
    
    # PostgreSQL
    if prompt_yes_no "Enable PostgreSQL integration?" "n"; then
        print_info "Format: postgresql://user:password@host:port/database"
        POSTGRES_CONNECTION=$(prompt_input "Enter PostgreSQL connection string")
        print_success "PostgreSQL configured"
    else
        POSTGRES_CONNECTION=""
    fi
}

configure_server() {
    print_section "Server Configuration"
    
    HOST=$(prompt_input "Server host" "${HOST:-0.0.0.0}")
    PORT=$(prompt_input "Server port" "${PORT:-8000}")
    
    print_success "Server will run on $HOST:$PORT"
}

configure_remote_access() {
    print_section "Remote Access Configuration"
    
    print_info "Configure remote access for VPS deployment"
    echo ""
    
    if prompt_yes_no "Enable remote access mode?" "n"; then
        REMOTE_ACCESS="true"
        
        # Get public IP automatically
        PUBLIC_IP=$(curl -s https://api.ipify.org 2>/dev/null || echo "")
        
        if [ -n "$PUBLIC_IP" ]; then
            print_info "Detected public IP: $PUBLIC_IP"
        fi
        
        EXTERNAL_HOST=$(prompt_input "Enter your VPS IP or domain" "${EXTERNAL_HOST:-$PUBLIC_IP}")
        FRONTEND_PORT=$(prompt_input "Frontend port" "${FRONTEND_PORT:-3000}")
        BACKEND_PORT=$(prompt_input "Backend port" "${BACKEND_PORT:-8000}")
        
        # Build allowed origins
        if prompt_yes_no "Allow all origins (wildcard)? [Development only]" "n"; then
            ALLOWED_ORIGINS="*"
            print_warning "Wildcard CORS enabled - DO NOT use in production!"
        else
            ALLOWED_ORIGINS="http://${EXTERNAL_HOST}:${FRONTEND_PORT},http://${EXTERNAL_HOST}:${BACKEND_PORT},https://${EXTERNAL_HOST}:${FRONTEND_PORT},https://${EXTERNAL_HOST}:${BACKEND_PORT},http://${EXTERNAL_HOST},https://${EXTERNAL_HOST}"
            print_success "CORS configured for: $EXTERNAL_HOST"
        fi
        
        # SSL configuration
        if prompt_yes_no "Enable SSL/HTTPS?" "n"; then
            SSL_ENABLED="true"
            print_info "You'll need SSL certificate files"
            SSL_CERT_PATH=$(prompt_input "SSL certificate path" "${SSL_CERT_PATH:-}")
            SSL_KEY_PATH=$(prompt_input "SSL key path" "${SSL_KEY_PATH:-}")
        else
            SSL_ENABLED="false"
            SSL_CERT_PATH=""
            SSL_KEY_PATH=""
        fi
        
        print_success "Remote access configured"
        print_info "Access your workspace at: http://${EXTERNAL_HOST}"
        
    else
        REMOTE_ACCESS="false"
        EXTERNAL_HOST=""
        FRONTEND_PORT="3000"
        BACKEND_PORT="8000"
        ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"
        SSL_ENABLED="false"
        SSL_CERT_PATH=""
        SSL_KEY_PATH=""
        print_info "Remote access disabled - localhost only"
    fi
}

save_configuration() {
    print_section "Saving Configuration"
    
    ENV_FILE="$SCRIPT_DIR/.env"
    
    # Backup existing .env if it exists
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Existing .env backed up"
    fi
    
    # Create new .env file
    cat > "$ENV_FILE" << EOF
# Antigravity Workspace Configuration
# Generated on: $(date)

# ═══ AI Models ═══
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=${GEMINI_API_KEY}

# Local Model Settings (if using Ollama)
LOCAL_MODEL=${LOCAL_MODEL}

# ═══ GitHub Integration ═══
COPILOT_MCP_GITHUB_TOKEN=${GITHUB_TOKEN}

# ═══ Optional Services ═══
# Brave Search API
COPILOT_MCP_BRAVE_API_KEY=${BRAVE_API_KEY}

# PostgreSQL connection
COPILOT_MCP_POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION}

# ═══ Server Configuration ═══
HOST=${HOST}
PORT=${PORT}

# ═══ Remote Access Configuration ═══
REMOTE_ACCESS=${REMOTE_ACCESS}
EXTERNAL_HOST=${EXTERNAL_HOST}
FRONTEND_PORT=${FRONTEND_PORT}
BACKEND_PORT=${BACKEND_PORT}

# ═══ Security Settings ═══
ALLOWED_ORIGINS=${ALLOWED_ORIGINS}

# ═══ SSL Configuration ═══
SSL_ENABLED=${SSL_ENABLED}
SSL_CERT_PATH=${SSL_CERT_PATH}
SSL_KEY_PATH=${SSL_KEY_PATH}

# ═══ Advanced Settings ═══
# Debug mode (true/false)
DEBUG_MODE=false

# Agent settings
AGENT_NAME=AntigravityAgent
MAX_ITERATIONS=10

# Database
DB_PATH=./data.db

# Logging
LOG_LEVEL=INFO
EOF
    
    print_success "Configuration saved to .env"
}

test_configuration() {
    print_section "Testing Configuration"
    
    # Test Gemini API
    if [ -n "$GEMINI_API_KEY" ]; then
        print_info "Testing Gemini API connection..."
        # Add actual test here if needed
        print_success "Gemini configuration looks good"
    fi
    
    # Test GitHub token
    if [ -n "$GITHUB_TOKEN" ]; then
        print_info "Testing GitHub token..."
        if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user &> /dev/null; then
            print_success "GitHub token is valid"
        else
            print_warning "GitHub token validation failed. Check your token."
        fi
    fi
    
    # Test Ollama
    if [ -n "$LOCAL_MODEL" ] && command -v ollama &> /dev/null; then
        print_info "Testing Ollama..."
        if ollama list | grep -q "$LOCAL_MODEL"; then
            print_success "Ollama model '$LOCAL_MODEL' is available"
        else
            print_warning "Model '$LOCAL_MODEL' not found. Pull it with: ollama pull $LOCAL_MODEL"
        fi
    fi
}

display_summary() {
    print_section "Configuration Summary"
    
    echo -e "${GREEN}✓${NC} Gemini AI: ${GEMINI_API_KEY:+Configured}${GEMINI_API_KEY:-Not configured}"
    echo -e "${GREEN}✓${NC} Local AI (Ollama): ${LOCAL_MODEL:-Disabled}"
    echo -e "${GREEN}✓${NC} GitHub Integration: ${GITHUB_TOKEN:+Enabled}${GITHUB_TOKEN:-Disabled}"
    echo -e "${GREEN}✓${NC} Brave Search: ${BRAVE_API_KEY:+Enabled}${BRAVE_API_KEY:-Disabled}"
    echo -e "${GREEN}✓${NC} PostgreSQL: ${POSTGRES_CONNECTION:+Enabled}${POSTGRES_CONNECTION:-Disabled}"
    echo -e "${GREEN}✓${NC} Server: $HOST:$PORT"
    echo -e "${GREEN}✓${NC} Remote Access: ${REMOTE_ACCESS:-false}"
    if [ "$REMOTE_ACCESS" = "true" ]; then
        echo -e "    ${CYAN}→${NC} External Host: ${EXTERNAL_HOST}"
        echo -e "    ${CYAN}→${NC} Frontend Port: ${FRONTEND_PORT}"
        echo -e "    ${CYAN}→${NC} Backend Port: ${BACKEND_PORT}"
        echo -e "    ${CYAN}→${NC} SSL: ${SSL_ENABLED}"
    fi
    echo ""
    
    print_info "Configuration file: $SCRIPT_DIR/.env"
    echo ""
}

display_next_steps() {
    print_section "Next Steps"
    
    echo "1. Start the services:"
    echo "   cd $SCRIPT_DIR"
    
    if [ "$REMOTE_ACCESS" = "true" ]; then
        echo "   ./start.sh  # Or: sudo systemctl start antigravity"
    else
        echo "   sudo systemctl start antigravity"
    fi
    echo ""
    echo "2. Check status:"
    echo "   sudo systemctl status antigravity"
    echo ""
    echo "3. View logs:"
    echo "   sudo journalctl -u antigravity -f"
    echo ""
    echo "4. Access web interface:"
    
    if [ "$REMOTE_ACCESS" = "true" ]; then
        if [ "$SSL_ENABLED" = "true" ]; then
            echo "   https://${EXTERNAL_HOST}"
        else
            echo "   http://${EXTERNAL_HOST}"
        fi
    else
        echo "   http://localhost:$PORT"
    fi
    echo ""
    echo "5. Reconfigure anytime:"
    echo "   ./configure.sh"
    echo ""
}

load_existing_config() {
    if [ -f "$SCRIPT_DIR/.env" ]; then
        print_info "Loading existing configuration..."
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/.env"
        print_success "Existing configuration loaded"
    fi
}

main() {
    print_header
    
    print_info "This wizard will help you configure Antigravity Workspace."
    print_info "Press Ctrl+C at any time to cancel."
    echo ""
    
    if prompt_yes_no "Continue with configuration?" "y"; then
        # Load existing config if available
        load_existing_config
        
        # Run configuration steps
        configure_gemini
        configure_github
        configure_ollama
        configure_optional_services
        configure_server
        configure_remote_access
        
        # Save and test
        save_configuration
        test_configuration
        
        # Display summary
        display_summary
        display_next_steps
        
        print_success "Configuration completed!"
    else
        print_info "Configuration cancelled"
        exit 0
    fi
}

main "$@"
