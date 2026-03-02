#!/bin/bash

################################################################################
# Antigravity Workspace - Quick Start Script
# Quickly start all services with one command
#
# Flags:
#   --ecosystem   Also start ecosystem daemons (OpenCode Agent Hub, OpenClaw
#                 gateway, Swarm-Tools SQLite interface, oh-my-opencode harness)
################################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECOSYSTEM_MODE=false

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

# ── Ecosystem daemons ────────────────────────────────────────────────────────

# Start a single ecosystem component in the background if its entry-point exists.
# Arguments: <name> <pid_file> <log_file> <working_dir> <command...>
start_ecosystem_component() {
    local name="$1"
    local pid_file="$2"
    local log_file="$3"
    local work_dir="$4"
    shift 4  # remaining args are the command

    if [ ! -d "$work_dir" ]; then
        print_warning "Ecosystem component '$name' not found at $work_dir – skipping"
        return 0
    fi

    # Already running?
    if [ -f "$pid_file" ]; then
        local old_pid
        old_pid=$(cat "$pid_file")
        if ps -p "$old_pid" > /dev/null 2>&1; then
            print_warning "$name already running (PID: $old_pid)"
            return 0
        fi
    fi

    print_status "Starting $name…"
    mkdir -p "$(dirname "$log_file")"
    (cd "$work_dir" && nohup "$@" >> "$log_file" 2>&1 &
     echo $! > "$pid_file")

    sleep 1
    local new_pid
    new_pid=$(cat "$pid_file" 2>/dev/null || echo "")
    if [ -n "$new_pid" ] && ps -p "$new_pid" > /dev/null 2>&1; then
        print_success "$name started (PID: $new_pid)"
    else
        print_warning "$name may not have started – check $log_file"
    fi
}

start_ecosystem() {
    print_status "Starting Antigravity Ecosystem components…"
    echo ""

    # Load ecosystem environment overrides if present
    local eco_env="$SCRIPT_DIR/ecosystem/.env.ecosystem"
    if [ -f "$eco_env" ]; then
        # shellcheck source=/dev/null
        set -a; source "$eco_env"; set +a
    fi

    OPENCODE_HUB_PORT="${OPENCODE_HUB_PORT:-9100}"
    OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-9200}"
    OH_MY_OPENCODE_PORT="${OH_MY_OPENCODE_PORT:-9300}"
    SWARM_DB_PATH="${SWARM_DB_PATH:-$HOME/.config/swarm-tools/swarm.db}"

    # ── oh-my-opencode (Sisyphus agent harness) ──────────────────────────────
    local omc_dir="$SCRIPT_DIR/ecosystem/oh-my-opencode"
    if [ -d "$omc_dir" ]; then
        if [ -f "$omc_dir/package.json" ]; then
            start_ecosystem_component \
                "oh-my-opencode" \
                "$SCRIPT_DIR/.oh-my-opencode.pid" \
                "$SCRIPT_DIR/logs/oh-my-opencode.log" \
                "$omc_dir" \
                npx oh-my-opencode --port "$OH_MY_OPENCODE_PORT"
        elif [ -f "$omc_dir/main.py" ]; then
            start_ecosystem_component \
                "oh-my-opencode" \
                "$SCRIPT_DIR/.oh-my-opencode.pid" \
                "$SCRIPT_DIR/logs/oh-my-opencode.log" \
                "$omc_dir" \
                python main.py --port "$OH_MY_OPENCODE_PORT"
        fi
    fi

    # ── OpenCode Agent Hub ───────────────────────────────────────────────────
    local opencode_dir="$SCRIPT_DIR/ecosystem/opencode"
    if [ -d "$opencode_dir" ]; then
        if [ -f "$opencode_dir/package.json" ]; then
            start_ecosystem_component \
                "opencode-hub" \
                "$SCRIPT_DIR/.opencode-hub.pid" \
                "$SCRIPT_DIR/logs/opencode-hub.log" \
                "$opencode_dir" \
                npx opencode serve --port "$OPENCODE_HUB_PORT"
        fi
    fi

    # ── OpenClaw message-routing gateway ────────────────────────────────────
    local openclaw_dir="$SCRIPT_DIR/ecosystem/openclaw"
    if [ -d "$openclaw_dir" ]; then
        if [ -f "$openclaw_dir/package.json" ]; then
            start_ecosystem_component \
                "openclaw-gateway" \
                "$SCRIPT_DIR/.openclaw.pid" \
                "$SCRIPT_DIR/logs/openclaw.log" \
                "$openclaw_dir" \
                npx openclaw --port "$OPENCLAW_GATEWAY_PORT"
        elif [ -f "$openclaw_dir/main.py" ]; then
            start_ecosystem_component \
                "openclaw-gateway" \
                "$SCRIPT_DIR/.openclaw.pid" \
                "$SCRIPT_DIR/logs/openclaw.log" \
                "$openclaw_dir" \
                python main.py --port "$OPENCLAW_GATEWAY_PORT"
        fi
    fi

    # ── Swarm-Tools SQLite interface ─────────────────────────────────────────
    local swarm_dir="$SCRIPT_DIR/ecosystem/swarm-tools"
    if [ -d "$swarm_dir" ]; then
        mkdir -p "$(dirname "$SWARM_DB_PATH")"
        if [ -f "$swarm_dir/serve.py" ]; then
            start_ecosystem_component \
                "swarm-tools" \
                "$SCRIPT_DIR/.swarm-tools.pid" \
                "$SCRIPT_DIR/logs/swarm-tools.log" \
                "$swarm_dir" \
                python serve.py --db "$SWARM_DB_PATH"
        elif [ -f "$swarm_dir/package.json" ]; then
            start_ecosystem_component \
                "swarm-tools" \
                "$SCRIPT_DIR/.swarm-tools.pid" \
                "$SCRIPT_DIR/logs/swarm-tools.log" \
                "$swarm_dir" \
                npx swarm-tools serve --db "$SWARM_DB_PATH"
        fi
    fi

    echo ""
    print_success "Ecosystem components launched"
    echo ""
    echo "  oh-my-opencode harness → port $OH_MY_OPENCODE_PORT"
    echo "  OpenCode Agent Hub     → port $OPENCODE_HUB_PORT"
    echo "  OpenClaw gateway       → port $OPENCLAW_GATEWAY_PORT"
    echo "  Swarm-Tools DB         → $SWARM_DB_PATH"
    echo ""
    echo "Ecosystem logs: $SCRIPT_DIR/logs/"
    echo ""
}

# Main execution
main() {
    # Parse flags
    for arg in "$@"; do
        case "$arg" in
            --ecosystem)
                ECOSYSTEM_MODE=true
                ;;
        esac
    done

    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          Antigravity Workspace - Starting...              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    create_required_dirs
    check_env
    activate_venv
    start_services

    if [ "$ECOSYSTEM_MODE" = "true" ]; then
        start_ecosystem
    fi

    echo ""
    print_success "Antigravity Workspace is starting!"
    echo ""
    echo "Access the web interface at:"
    echo "  http://localhost:8000"
    echo ""
    if [ "$ECOSYSTEM_MODE" = "true" ]; then
        echo "Ecosystem mode active – see port assignments above."
        echo ""
    fi
    echo "Stop services with:"
    echo "  ./stop.sh"
    echo ""
}

main "$@"
