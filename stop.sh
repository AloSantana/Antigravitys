#!/bin/bash

################################################################################
# Antigravity Workspace - Stop Script
# Stops all running services
################################################################################

# Don't exit on error - we want to try all stop methods
set +e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Antigravity Workspace - Stopping...              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

STOPPED_SOMETHING=false

# Stop systemd service if running
if systemctl list-unit-files 2>/dev/null | grep -q antigravity.service; then
    if systemctl is-active --quiet antigravity 2>/dev/null; then
        print_status "Stopping systemd service..."
        sudo systemctl stop antigravity
        print_success "Service stopped"
        STOPPED_SOMETHING=true
    fi
fi

# Stop Docker Compose if running
if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        cd "$SCRIPT_DIR" || exit 1
        if docker compose ps -q 2>/dev/null | grep -q .; then
            print_status "Stopping Docker Compose services..."
            docker compose down
            print_success "Docker services stopped"
            STOPPED_SOMETHING=true
        fi
    elif command -v docker-compose &> /dev/null; then
        cd "$SCRIPT_DIR" || exit 1
        if docker-compose ps -q 2>/dev/null | grep -q .; then
            print_status "Stopping Docker Compose services..."
            docker-compose down
            print_success "Docker services stopped"
            STOPPED_SOMETHING=true
        fi
    fi
fi

# Stop backend process if running
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    PID=$(cat "$SCRIPT_DIR/.backend.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        print_status "Stopping backend process (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm "$SCRIPT_DIR/.backend.pid"
        print_success "Backend stopped"
        STOPPED_SOMETHING=true
    else
        rm "$SCRIPT_DIR/.backend.pid"
        print_warning "Backend PID file exists but process not running"
    fi
fi

# Find and stop any remaining Python processes running main.py
# Using pgrep instead of ps aux | grep
if command -v pgrep &> /dev/null; then
    MAIN_PIDS=$(pgrep -f "python.*main.py" || true)
else
    # Fallback to grep method if pgrep not available
    MAIN_PIDS=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')
fi

if [ -n "$MAIN_PIDS" ]; then
    print_status "Stopping remaining main.py processes..."
    for pid in $MAIN_PIDS; do
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
    # Force kill if still running
    for pid in $MAIN_PIDS; do
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
    print_success "Remaining processes stopped"
    STOPPED_SOMETHING=true
fi

echo ""
if [ "$STOPPED_SOMETHING" = true ]; then
    print_success "All services stopped successfully"
else
    print_warning "No running services found"
fi
echo ""
