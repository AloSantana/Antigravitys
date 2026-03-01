#!/bin/bash

################################################################################
# Antigravity Workspace - Linux/macOS Installation Script
# Automated installer that checks dependencies, creates venv, installs packages,
# sets up MCP servers, creates directories, and verifies the installation.
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
#   ./install.sh --skip-mcp       # Skip MCP server installation
#   ./install.sh --skip-docker    # Skip Docker-related checks
#   ./install.sh --auto-fix       # Automatically fix common issues
#   ./install.sh --help           # Show help
#
# Compatible with:
#   - Ubuntu 20.04+ / Debian 11+
#   - macOS 12+ (Monterey and later)
#   - Windows (Git Bash, WSL2)
#
# Requirements:
#   - Python 3.11+
#   - pip
#   - Node.js 18+ (optional, for MCP servers)
################################################################################

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/install.log"
REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=11
REQUIRED_NODE_MAJOR=18
SKIP_MCP=false
SKIP_DOCKER=false
AUTO_FIX=false
HAS_NODE=false
ERRORS=0
WARNINGS=0

# ═══════════════════════════════════════════════════════════════════════════════
# Colors & Output
# ═══════════════════════════════════════════════════════════════════════════════

# Detect color support
if [ -t 1 ] && command -v tput &>/dev/null && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' NC=''
fi

log() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$1] $2" >> "$LOG_FILE"
}

print_info() {
    echo -e "${CYAN}[*]${NC} $1"
    log "INFO" "$1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    log "SUCCESS" "$1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    log "WARNING" "$1"
    WARNINGS=$((WARNINGS + 1))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    log "ERROR" "$1"
    ERRORS=$((ERRORS + 1))
}

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Antigravity Workspace - Linux/macOS Installation      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}═══ $1 ═══${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Argument Parsing
# ═══════════════════════════════════════════════════════════════════════════════

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-mcp       Skip MCP server installation"
    echo "  --skip-docker    Skip Docker-related checks and setup"
    echo "  --auto-fix       Automatically fix common issues"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Full installation"
    echo "  $0 --skip-mcp          # Skip MCP servers"
    echo "  $0 --auto-fix          # Auto-fix issues"
    echo ""
}

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --skip-mcp)    SKIP_MCP=true ;;
            --skip-docker) SKIP_DOCKER=true ;;
            --auto-fix)    AUTO_FIX=true ;;
            --help|-h)     show_help; exit 0 ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
}

# ═══════════════════════════════════════════════════════════════════════════════
# System Information
# ═══════════════════════════════════════════════════════════════════════════════

show_system_info() {
    print_section "System Information"

    # Detect OS
    local os_name="Unknown"
    if [ -f /etc/os-release ]; then
        os_name="$(. /etc/os-release && echo "$PRETTY_NAME")"
    elif [ "$(uname -s)" = "Darwin" ]; then
        os_name="macOS $(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
    elif [ "$(uname -s)" = "MINGW64_NT"* ] || [ "$(uname -s)" = "MSYS_NT"* ]; then
        os_name="Windows (Git Bash / MSYS2)"
    fi
    echo -e "  OS: ${os_name}"

    # CPU
    if command -v nproc &>/dev/null; then
        echo -e "  CPU Cores: $(nproc)"
    elif command -v sysctl &>/dev/null; then
        echo -e "  CPU Cores: $(sysctl -n hw.ncpu 2>/dev/null || echo 'unknown')"
    fi

    # Memory
    if command -v free &>/dev/null; then
        local mem_gb
        mem_gb="$(free -g 2>/dev/null | awk '/^Mem:/{print $2}')"
        echo -e "  RAM: ${mem_gb} GB"
        if [ "${mem_gb:-0}" -lt 2 ]; then
            print_warning "Less than 2GB RAM available"
        fi
    elif command -v sysctl &>/dev/null; then
        local mem_bytes
        mem_bytes="$(sysctl -n hw.memsize 2>/dev/null || echo 0)"
        local mem_gb=$((mem_bytes / 1073741824))
        echo -e "  RAM: ${mem_gb} GB"
    fi

    # Disk space
    local free_gb
    free_gb="$(df -BG "$SCRIPT_DIR" 2>/dev/null | awk 'NR==2{gsub("G","",$4); print $4}' || echo 'unknown')"
    if [ "$free_gb" != "unknown" ]; then
        echo -e "  Free Disk Space: ${free_gb} GB"
        if [ "${free_gb:-0}" -lt 5 ]; then
            print_warning "Less than 5GB disk space available"
        fi
    fi

    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Prerequisite Checks
# ═══════════════════════════════════════════════════════════════════════════════

# Find the best python command (python3 preferred, then python)
find_python() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null; then
        echo "python"
    else
        echo ""
    fi
}

check_python() {
    print_section "Checking Python Installation"

    local python_cmd
    python_cmd="$(find_python)"

    if [ -z "$python_cmd" ]; then
        print_error "Python not found"
        print_info "Install Python 3.11+ from: https://www.python.org/downloads/"
        if [ "$(uname -s)" = "Linux" ]; then
            print_info "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
            print_info "  Fedora/RHEL:   sudo dnf install python3 python3-pip"
            print_info "  Arch:          sudo pacman -S python python-pip"
        elif [ "$(uname -s)" = "Darwin" ]; then
            print_info "  macOS: brew install python@3.12"
        fi
        return 1
    fi

    local version_output
    version_output="$($python_cmd --version 2>&1)"

    if [[ "$version_output" =~ Python\ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
        local major="${BASH_REMATCH[1]}"
        local minor="${BASH_REMATCH[2]}"
        local patch="${BASH_REMATCH[3]}"

        if [ "$major" -gt "$REQUIRED_PYTHON_MAJOR" ] || \
           { [ "$major" -eq "$REQUIRED_PYTHON_MAJOR" ] && [ "$minor" -ge "$REQUIRED_PYTHON_MINOR" ]; }; then
            print_success "Python ${major}.${minor}.${patch} found (using: $python_cmd)"
            return 0
        else
            print_error "Python ${major}.${minor}.${patch} found, but ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}+ required"
            print_info "Install Python 3.11+ from: https://www.python.org/downloads/"
            return 1
        fi
    else
        print_error "Could not determine Python version from: $version_output"
        return 1
    fi
}

check_pip() {
    print_info "Checking pip..."

    local python_cmd
    python_cmd="$(find_python)"

    if $python_cmd -m pip --version &>/dev/null; then
        print_success "pip is available"
        return 0
    fi

    print_warning "pip not found — attempting to install..."

    if $python_cmd -m ensurepip --upgrade &>/dev/null 2>&1; then
        print_success "pip installed via ensurepip"
        return 0
    fi

    # Try system package manager
    if [ "$AUTO_FIX" = true ]; then
        if command -v apt-get &>/dev/null; then
            print_info "Installing pip via apt..."
            sudo apt-get update -qq && sudo apt-get install -y python3-pip &>/dev/null
            if $python_cmd -m pip --version &>/dev/null; then
                print_success "pip installed via apt"
                return 0
            fi
        elif command -v brew &>/dev/null; then
            print_info "pip should come with Homebrew Python"
        fi
    fi

    print_error "Failed to install pip"
    return 1
}

check_node() {
    print_section "Checking Node.js Installation"

    if ! command -v node &>/dev/null; then
        print_warning "Node.js not found"
        print_info "Node.js is optional but recommended for MCP servers"
        print_info "Install from: https://nodejs.org/"
        if [ "$(uname -s)" = "Linux" ]; then
            print_info "  Or: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs"
        elif [ "$(uname -s)" = "Darwin" ]; then
            print_info "  Or: brew install node"
        fi
        HAS_NODE=false
        return 0  # Don't fail — Node is optional
    fi

    local node_version
    node_version="$(node --version 2>&1)"

    if [[ "$node_version" =~ v([0-9]+) ]]; then
        local major="${BASH_REMATCH[1]}"

        if [ "$major" -ge "$REQUIRED_NODE_MAJOR" ]; then
            print_success "Node.js ${node_version} found"

            # Check npm
            if command -v npm &>/dev/null; then
                local npm_version
                npm_version="$(npm --version 2>&1)"
                print_success "npm ${npm_version} found"
            else
                print_warning "npm not found"
            fi

            HAS_NODE=true
        else
            print_warning "Node.js ${node_version} found, but v${REQUIRED_NODE_MAJOR}+ recommended"
            print_info "Download from: https://nodejs.org/"
            HAS_NODE=true  # Don't fail, just warn
        fi
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Virtual Environment
# ═══════════════════════════════════════════════════════════════════════════════

setup_venv() {
    print_section "Setting up Python Virtual Environment"

    local venv_path="${SCRIPT_DIR}/venv"
    local python_cmd
    python_cmd="$(find_python)"

    if [ -d "$venv_path" ]; then
        print_success "Virtual environment already exists"

        # Verify it works
        if [ -f "$venv_path/bin/activate" ]; then
            print_success "venv/bin/activate found"
        else
            print_warning "venv exists but activate script missing — recreating..."
            rm -rf "$venv_path"
        fi
    fi

    if [ ! -d "$venv_path" ]; then
        print_info "Creating virtual environment..."

        # Ensure python3-venv is installed on Debian/Ubuntu
        if [ "$(uname -s)" = "Linux" ] && command -v apt-get &>/dev/null; then
            if ! $python_cmd -m venv --help &>/dev/null 2>&1; then
                print_info "Installing python3-venv package..."
                sudo apt-get install -y python3-venv &>/dev/null 2>&1 || true
            fi
        fi

        if $python_cmd -m venv "$venv_path"; then
            print_success "Virtual environment created"
        else
            print_error "Failed to create virtual environment"
            return 1
        fi
    fi

    return 0
}

activate_venv() {
    local activate_script="${SCRIPT_DIR}/venv/bin/activate"

    if [ -f "$activate_script" ]; then
        print_info "Activating virtual environment..."
        # shellcheck source=/dev/null
        source "$activate_script"
        print_success "Virtual environment activated"
        return 0
    else
        print_warning "Could not activate virtual environment — using system Python"
        return 0  # Don't fail
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Python Dependencies
# ═══════════════════════════════════════════════════════════════════════════════

install_python_deps() {
    print_section "Installing Python Dependencies"

    local python_cmd
    python_cmd="$(find_python)"

    # Upgrade pip
    print_info "Upgrading pip..."
    if $python_cmd -m pip install --upgrade pip --quiet 2>/dev/null; then
        print_success "pip upgraded"
    else
        print_warning "Failed to upgrade pip (continuing anyway)"
    fi

    # Install root requirements
    local root_reqs="${SCRIPT_DIR}/requirements.txt"
    if [ -f "$root_reqs" ]; then
        print_info "Installing root requirements..."
        if $python_cmd -m pip install -r "$root_reqs" 2>&1 | tail -5; then
            print_success "Root requirements installed"
        else
            print_error "Failed to install root requirements"
            return 1
        fi
    else
        print_warning "requirements.txt not found"
    fi

    # Install backend requirements
    local backend_reqs="${SCRIPT_DIR}/backend/requirements.txt"
    if [ -f "$backend_reqs" ]; then
        print_info "Installing backend requirements..."
        if $python_cmd -m pip install -r "$backend_reqs" 2>&1 | tail -5; then
            print_success "Backend requirements installed"
        else
            print_error "Failed to install backend requirements"
            return 1
        fi
    else
        print_warning "backend/requirements.txt not found"
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# MCP Servers
# ═══════════════════════════════════════════════════════════════════════════════

install_mcp_servers() {
    if [ "$SKIP_MCP" = true ]; then
        print_info "Skipping MCP server installation (--skip-mcp flag)"
        return 0
    fi

    print_section "Installing MCP Servers"

    if ! command -v npm &>/dev/null; then
        print_warning "npm not found — skipping MCP server installation"
        print_info "Install Node.js from https://nodejs.org/ to enable MCP servers"
        return 0
    fi

    # Core MCP servers
    local core_servers=(
        "@modelcontextprotocol/server-filesystem"
        "@modelcontextprotocol/server-memory"
        "@modelcontextprotocol/server-sequential-thinking"
    )

    # Optional MCP servers
    local optional_servers=(
        "mcp-server-docker"
    )

    print_info "Installing core MCP servers..."
    for server in "${core_servers[@]}"; do
        print_info "  Installing ${server}..."
        if npm install -g "$server" &>/dev/null 2>&1; then
            print_success "  ${server} installed"
        else
            print_warning "  Failed to install ${server} (continuing...)"
        fi
    done

    print_info "Installing optional MCP servers..."
    for server in "${optional_servers[@]}"; do
        print_info "  Installing ${server}..."
        if npm install -g "$server" &>/dev/null 2>&1; then
            print_success "  ${server} installed"
        else
            print_info "  Optional ${server} not installed (this is okay)"
        fi
    done

    # Python MCP server
    local python_cmd
    python_cmd="$(find_python)"
    print_info "Installing Python MCP server..."
    if $python_cmd -m pip install mcp-server-python-analysis --quiet 2>/dev/null; then
        print_success "Python MCP server installed"
    else
        print_info "Python MCP server not installed (optional)"
    fi

    print_success "MCP server installation completed"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Required Directories
# ═══════════════════════════════════════════════════════════════════════════════

create_directories() {
    print_section "Creating Required Directories"

    local directories=(
        "drop_zone"
        "artifacts"
        "logs"
        "data"
        "frontend/static"
    )

    for dir in "${directories[@]}"; do
        local path="${SCRIPT_DIR}/${dir}"
        if [ ! -d "$path" ]; then
            mkdir -p "$path"
            print_info "Created: ${dir}"
        fi
    done

    print_success "All directories ready"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration Setup
# ═══════════════════════════════════════════════════════════════════════════════

setup_configuration() {
    print_section "Setting up Configuration"

    local env_path="${SCRIPT_DIR}/.env"
    local env_example="${SCRIPT_DIR}/.env.example"

    if [ -f "$env_path" ]; then
        print_success ".env file already exists"
        return 0
    fi

    if [ -f "$env_example" ]; then
        cp "$env_example" "$env_path"
        print_success "Created .env from .env.example"
    else
        print_info "Creating minimal .env file..."
        cat > "$env_path" << 'ENVEOF'
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=

# OpenRouter API Key (access 100+ models from https://openrouter.ai/keys)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Local Model Settings
LOCAL_MODEL=llama3

# Active AI Model Selection
# Options: 'gemini', 'vertex', 'ollama', 'openrouter', 'auto'
ACTIVE_MODEL=auto

# Model Rotator (Multi-Key Support)
MODEL_ROTATOR_ENABLED=true
SWARM_AUTO_ROTATE_KEYS=true
SMART_RATE_LIMIT_HANDOFF=true

# Multiple keys (comma-separated for rotation)
GEMINI_API_KEYS=
OPENROUTER_API_KEYS=
OPENAI_API_KEYS=

# GitHub Token (get from https://github.com/settings/tokens)
# Required scopes: repo, read:org
COPILOT_MCP_GITHUB_TOKEN=

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# Advanced Settings
DEBUG_MODE=false
LOG_LEVEL=INFO

# ⚠ IMPORTANT: Fill in your actual API keys above
# Run ./configure.sh for interactive configuration wizard
ENVEOF
        print_success ".env file created"
    fi

    print_warning "Please edit .env with your API keys"
    print_info "  Or run: ./configure.sh"

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Auto-Fix Common Issues
# ═══════════════════════════════════════════════════════════════════════════════

auto_fix_issues() {
    if [ "$AUTO_FIX" != true ]; then
        return 0
    fi

    print_section "Auto-Fix: Scanning for Common Issues"

    local python_cmd
    python_cmd="$(find_python)"

    # Fix 1: Ensure scripts are executable
    print_info "Ensuring scripts are executable..."
    local scripts=(start.sh configure.sh stop.sh validate.sh health-check.sh)
    for script in "${scripts[@]}"; do
        if [ -f "${SCRIPT_DIR}/${script}" ] && [ ! -x "${SCRIPT_DIR}/${script}" ]; then
            chmod +x "${SCRIPT_DIR}/${script}"
            print_success "  Fixed permissions: ${script}"
        fi
    done

    # Fix 2: Fix line endings (CRLF → LF) for shell scripts
    if command -v sed &>/dev/null; then
        print_info "Fixing line endings..."
        for script in "${SCRIPT_DIR}"/*.sh; do
            if [ -f "$script" ] && file "$script" 2>/dev/null | grep -q "CRLF"; then
                sed -i 's/\r$//' "$script" 2>/dev/null || true
                print_success "  Fixed line endings: $(basename "$script")"
            fi
        done
    fi

    # Fix 3: Ensure __init__.py exists in key directories
    print_info "Checking Python package markers..."
    local python_dirs=(backend backend/agent backend/rag backend/utils src src/agents src/tools src/sandbox)
    for dir in "${python_dirs[@]}"; do
        local init_file="${SCRIPT_DIR}/${dir}/__init__.py"
        if [ -d "${SCRIPT_DIR}/${dir}" ] && [ ! -f "$init_file" ]; then
            touch "$init_file"
            print_success "  Created: ${dir}/__init__.py"
        fi
    done

    # Fix 4: Ensure .gitkeep in empty directories
    print_info "Ensuring placeholder files in empty directories..."
    local keep_dirs=(drop_zone artifacts logs data)
    for dir in "${keep_dirs[@]}"; do
        local dir_path="${SCRIPT_DIR}/${dir}"
        if [ -d "$dir_path" ] && [ -z "$(ls -A "$dir_path" 2>/dev/null)" ]; then
            touch "${dir_path}/.gitkeep"
            print_info "  Added .gitkeep to: ${dir}"
        fi
    done

    print_success "Auto-fix completed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Verification
# ═══════════════════════════════════════════════════════════════════════════════

verify_installation() {
    print_section "Verifying Installation"

    local python_cmd
    python_cmd="$(find_python)"

    # Test critical Python imports
    print_info "Testing Python imports..."
    local test_result
    test_result="$($python_cmd -c "
import sys
import logging
logging.getLogger('chromadb').setLevel(logging.ERROR)

errors = []

# Critical
try:
    import fastapi
    import uvicorn
except ImportError as e:
    print(f'CRITICAL_FAIL: {e}')
    sys.exit(1)

# Optional
try:
    import chromadb
except Exception as e:
    print(f'OPTIONAL_WARNING: chromadb: {e}')

print('OK')
" 2>&1)" || true

    if echo "$test_result" | grep -q "OK"; then
        if echo "$test_result" | grep -q "OPTIONAL_WARNING"; then
            print_warning "Python dependencies verified (with warnings for optional components)"
            echo "$test_result" | grep "OPTIONAL_WARNING" | while read -r line; do
                print_info "  $line"
            done
        else
            print_success "Python dependencies verified"
        fi
    else
        print_error "Python dependency verification failed: $test_result"
    fi

    # Test backend module
    print_info "Testing backend module..."
    local backend_result
    backend_result="$(cd "${SCRIPT_DIR}/backend" && $python_cmd -c "
try:
    from main import app
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1)" || true

    if echo "$backend_result" | grep -q "OK"; then
        print_success "Backend module loads successfully"
    else
        print_warning "Backend module has issues: $backend_result"
    fi

    # Check if backend can bind to port
    print_info "Checking port 8000 availability..."
    if command -v ss &>/dev/null; then
        if ss -tlnp 2>/dev/null | grep -q ":8000 "; then
            print_warning "Port 8000 is already in use — stop existing service before starting"
        else
            print_success "Port 8000 is available"
        fi
    elif command -v lsof &>/dev/null; then
        if lsof -i :8000 &>/dev/null; then
            print_warning "Port 8000 is already in use — stop existing service before starting"
        else
            print_success "Port 8000 is available"
        fi
    fi

    print_success "Installation verification completed"
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Completion Message
# ═══════════════════════════════════════════════════════════════════════════════

show_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║        Installation Complete! 🎉                          ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ "$ERRORS" -gt 0 ]; then
        print_warning "Completed with ${ERRORS} error(s) and ${WARNINGS} warning(s)"
        print_info "Check the log file for details: ${LOG_FILE}"
        echo ""
    elif [ "$WARNINGS" -gt 0 ]; then
        print_info "Completed with ${WARNINGS} warning(s) — these are non-critical"
        echo ""
    fi

    print_success "Next Steps:"
    echo ""
    echo -e "  1. Edit configuration:"
    echo -e "     ${CYAN}nano .env${NC}"
    echo ""
    echo -e "  2. Or run configuration wizard:"
    echo -e "     ${CYAN}./configure.sh${NC}"
    echo ""
    echo -e "  3. Start the workspace:"
    echo -e "     ${CYAN}./start.sh${NC}"
    echo ""
    echo -e "  4. Access web interface:"
    echo -e "     ${CYAN}http://localhost:8000${NC}"
    echo ""
    echo -e "  For detailed help, see:"
    echo -e "     ${CYAN}docs/REMOTE_DEPLOYMENT.md${NC}"
    echo ""
    print_info "Installation log saved to: ${LOG_FILE}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    parse_args "$@"

    # Initialize log
    echo "Installation started at $(date)" > "$LOG_FILE"

    print_header
    show_system_info

    # ─── Prerequisites ───
    if ! check_python; then
        echo ""
        print_error "Python ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}+ is required. Please install it first."
        exit 1
    fi

    if ! check_pip; then
        echo ""
        print_error "pip is required but couldn't be installed"
        exit 1
    fi

    # Node.js is optional
    check_node
    if [ "$HAS_NODE" = false ]; then
        print_info "Node.js is recommended but not required"
        print_info "You can install it later from: https://nodejs.org/"
    fi

    # ─── Virtual Environment ───
    if ! setup_venv; then
        echo ""
        print_error "Failed to create virtual environment"
        exit 1
    fi

    activate_venv

    # ─── Python Dependencies ───
    if ! install_python_deps; then
        echo ""
        print_error "Failed to install Python dependencies"
        exit 1
    fi

    # ─── MCP Servers ───
    if [ "$HAS_NODE" = true ]; then
        install_mcp_servers
    else
        print_info "Skipping MCP servers (Node.js not available)"
    fi

    # ─── Directories ───
    create_directories

    # ─── Configuration ───
    setup_configuration

    # ─── Auto-Fix ───
    auto_fix_issues

    # ─── Verify ───
    verify_installation

    # ─── Done ───
    show_completion
}

main "$@"
