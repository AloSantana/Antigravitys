#!/bin/bash

################################################################################
# Antigravity Workspace - Quick Start Script
# Quickly start all services with one command
################################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Create required directories if they don't exist
create_required_dirs() {
    print_status "Ensuring required directories exist..."
    mkdir -p "$SCRIPT_DIR/logs"
    mkdir -p "$SCRIPT_DIR/drop_zone"
    mkdir -p "$SCRIPT_DIR/artifacts"
    print_success "Directories ready"
}

# Check if .env exists
check_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_warning ".env file not found. Running configuration wizard..."
        if [ -f "$SCRIPT_DIR/configure.sh" ]; then
            "$SCRIPT_DIR/configure.sh"
        else
            print_error "configure.sh not found!"
            print_status "Creating basic .env file..."
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env" 2>/dev/null || {
                cat > "$SCRIPT_DIR/.env" << 'EOF'
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Local Model Settings
LOCAL_MODEL=llama3

# GitHub Token
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF
                print_success ".env file created - please edit with your API keys"
            }
        fi
    fi
}

# Activate virtual environment if it exists
activate_venv() {
    if [ -d "$SCRIPT_DIR/venv" ]; then
        print_status "Activating virtual environment..."
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/venv/bin/activate"
        print_success "Virtual environment activated"
    else
        print_warning "Virtual environment not found. Run install.sh first."
        print_status "Attempting to use system Python..."
    fi
}

# Start services based on environment
start_services() {
    print_status "Starting Antigravity Workspace..."
    
    # Check if running in Docker
    if [ -f "/.dockerenv" ]; then
        print_status "Running in Docker container..."
        cd "$SCRIPT_DIR/backend"
        exec python main.py
    else
        # Check if systemd service exists
        if systemctl list-unit-files 2>/dev/null | grep -q antigravity.service; then
            print_status "Starting systemd service..."
            sudo systemctl start antigravity
            print_success "Service started!"
            echo ""
            print_status "View logs with: sudo journalctl -u antigravity -f"
        elif command -v docker &> /dev/null && docker compose version &> /dev/null && [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
            print_status "Starting with Docker Compose..."
            cd "$SCRIPT_DIR"
            docker compose up -d
            print_success "Services started!"
            echo ""
            print_status "View logs with: docker compose logs -f"
        elif command -v docker-compose &> /dev/null && [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
            print_status "Starting with Docker Compose..."
            cd "$SCRIPT_DIR"
            docker-compose up -d
            print_success "Services started!"
            echo ""
            print_status "View logs with: docker-compose logs -f"
        else
            print_status "Starting backend server directly..."
            cd "$SCRIPT_DIR/backend"
            
            # Check if already running
            if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
                OLD_PID=$(cat "$SCRIPT_DIR/.backend.pid")
                if ps -p "$OLD_PID" > /dev/null 2>&1; then
                    print_warning "Backend already running (PID: $OLD_PID)"
                    echo ""
                    print_status "View logs with: tail -f $SCRIPT_DIR/logs/backend.log"
                    exit 0
                fi
            fi
            
            # Start in background with nohup
            nohup python main.py > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
            BACKEND_PID=$!
            echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
            
            # Wait a moment and check if it started successfully
            sleep 2
            if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                print_success "Backend started (PID: $BACKEND_PID)"
            else
                print_error "Backend failed to start. Check logs at: $SCRIPT_DIR/logs/backend.log"
                exit 1
            fi
            echo ""
            print_status "View logs with: tail -f $SCRIPT_DIR/logs/backend.log"
        fi
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          Antigravity Workspace - Starting...              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    create_required_dirs
    check_env
    activate_venv
    start_services
    
    echo ""
    print_success "Antigravity Workspace is starting!"
    echo ""
    echo "Access the web interface at:"
    echo "  http://localhost:8000"
    echo ""
    echo "Stop services with:"
    echo "  ./stop.sh"
    echo ""
}

main "$@"
