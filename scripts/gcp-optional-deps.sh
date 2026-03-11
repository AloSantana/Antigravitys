#!/bin/bash

################################################################################
# GCP VPS Optional Dependencies Installer
# Run AFTER gcp-bootstrap.sh and install.sh
#
# Usage:
#   ./scripts/gcp-optional-deps.sh --all
#   ./scripts/gcp-optional-deps.sh --opencode --moltis
#   ./scripts/gcp-optional-deps.sh --ollama --monitoring
#
# Flags:
#   --all          Install everything
#   --mongodb      MongoDB 7.x (standalone)
#   --redis        Redis 7.x (standalone)
#   --ollama       Ollama for local LLM inference
#   --opencode     OpenCode coding agent (latest)
#   --moltis       Moltis/OpenClaw binary (latest GitHub release)
#   --lazydocker   lazydocker TUI for Docker management
#   --lazygit      lazygit TUI for Git management
#   --monitoring   Prometheus + Grafana in Docker
#   --caddy        Caddy web server (alternative to Nginx)
#   --cloudflared  Cloudflare Tunnel
#   --mcp-servers  All MCP servers from the project
#   --help         Show this help
################################################################################

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Colors & Output
# ═══════════════════════════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

LOG_FILE="/tmp/gcp-optional-deps.log"

log() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$1] $2" >> "$LOG_FILE"
}

print_info()    { echo -e "${CYAN}[*]${NC} $1"; log "INFO" "$1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; log "SUCCESS" "$1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; log "WARNING" "$1"; }
print_error()   { echo -e "${RED}[✗]${NC} $1"; log "ERROR" "$1"; }
print_skip()    { echo -e "${BLUE}[→]${NC} $1 (already installed — skipping)"; }

print_section() {
    echo ""
    echo -e "${BOLD}${BLUE}── $1 ─────────────────────────────────────────────${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

# Fetch latest GitHub release tag for a repo (owner/repo)
get_latest_release() {
    local repo="$1"
    curl -fsSL "https://api.github.com/repos/${repo}/releases/latest" \
        | grep '"tag_name"' | head -1 | cut -d'"' -f4
}

# ═══════════════════════════════════════════════════════════════════════════════
# Installers
# ═══════════════════════════════════════════════════════════════════════════════

install_mongodb() {
    print_section "MongoDB 7.x"
    if command -v mongod &>/dev/null; then
        print_skip "MongoDB $(mongod --version | head -1)"
        return
    fi

    print_info "Installing MongoDB 7.x..."
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc \
        | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
        | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list > /dev/null
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mongodb-org
    sudo systemctl enable mongod
    sudo systemctl start mongod
    print_success "MongoDB $(mongod --version | head -1) installed and started"
}

install_redis_standalone() {
    print_section "Redis 7.x (standalone)"
    if command -v redis-server &>/dev/null; then
        print_skip "Redis $(redis-server --version | head -1)"
        return
    fi

    print_info "Installing Redis 7.x..."
    curl -fsSL https://packages.redis.io/gpg \
        | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] \
https://packages.redis.io/deb $(lsb_release -cs) main" \
        | sudo tee /etc/apt/sources.list.d/redis.list > /dev/null
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq redis
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    print_success "Redis $(redis-server --version | head -1) installed and started"
}

install_ollama() {
    print_section "Ollama (Local LLM Inference)"
    if command -v ollama &>/dev/null; then
        print_skip "Ollama $(ollama --version 2>/dev/null || echo '')"
        return
    fi

    print_info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    sudo systemctl enable ollama 2>/dev/null || true
    sudo systemctl start ollama 2>/dev/null || true
    print_success "Ollama installed"
    print_info "  Pull a model: ollama pull llama3"
    print_info "  List models:  ollama list"
    print_info "  Serve:        ollama serve  (auto-started as systemd service)"
}

install_opencode() {
    print_section "OpenCode Coding Agent"
    if command -v opencode &>/dev/null; then
        print_skip "OpenCode $(opencode --version 2>/dev/null || echo '')"
        return
    fi

    print_info "Installing OpenCode (latest)..."
    # Install via npm (official method)
    sudo npm install -g opencode-ai 2>/dev/null \
        || npm install -g opencode-ai
    print_success "OpenCode installed: $(opencode --version 2>/dev/null || echo 'run: opencode --version')"
    print_info "  Configure: opencode configure"
    print_info "  Run:       opencode"
}

install_moltis() {
    print_section "Moltis (Rust AI Agent — fork: AloSantana/moltis)"
    if command -v moltis &>/dev/null; then
        print_skip "moltis $(moltis --version 2>/dev/null || echo '')"
        return
    fi

    # Moltis upstream: https://github.com/moltis-org/moltis
    # AloSantana's fork (13+ commits ahead, with gsd-opencode & OpenCode skill adapter):
    #   https://github.com/AloSantana/moltis
    #
    # Install method priority:
    #   1. .deb package (Ubuntu — cleanest, installs to /usr/bin/moltis)
    #   2. Official install script (~/.local/bin/moltis)
    #   3. Build from AloSantana's fork (picks up custom skill adapter)

    print_info "Installing Moltis via .deb package (Ubuntu)..."
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  DEB_ARCH="amd64" ;;
        aarch64) DEB_ARCH="arm64" ;;
        *)
            print_warning "Unknown arch $ARCH — falling back to install script"
            DEB_ARCH=""
            ;;
    esac

    if [ -n "$DEB_ARCH" ]; then
        # Try .deb from upstream (moltis-org/moltis releases)
        MOLTIS_TAG=$(get_latest_release "moltis-org/moltis" 2>/dev/null || echo "")
        if [ -n "$MOLTIS_TAG" ]; then
            TAG_CLEAN="${MOLTIS_TAG#v}"
            DEB_URL="https://github.com/moltis-org/moltis/releases/download/${MOLTIS_TAG}/moltis_${TAG_CLEAN}-1_${DEB_ARCH}.deb"
            if curl -fsSL --head "$DEB_URL" 2>/dev/null | grep -qi "200"; then
                curl -fsSL "$DEB_URL" -o /tmp/moltis.deb
                sudo dpkg -i /tmp/moltis.deb
                rm -f /tmp/moltis.deb
                print_success "Moltis ${MOLTIS_TAG} installed via .deb"
                moltis --version 2>/dev/null || true
                _moltis_post_install
                return
            fi
        fi
    fi

    # Fallback: official install script (installs to ~/.local/bin/moltis)
    print_info "Falling back to official install script..."
    curl -fsSL https://www.moltis.org/install.sh | sh

    # Ensure ~/.local/bin is on PATH
    export PATH="$HOME/.local/bin:$PATH"
    for PROFILE in "$HOME/.bashrc" "$HOME/.profile"; do
        if [ -f "$PROFILE" ] && ! grep -q '\.local/bin' "$PROFILE"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        fi
    done

    if command -v moltis &>/dev/null || [ -f "$HOME/.local/bin/moltis" ]; then
        print_success "Moltis installed via install.sh"
        "$HOME/.local/bin/moltis" --version 2>/dev/null || true
        _moltis_post_install
    else
        print_warning "Install script ran but moltis binary not found."
        print_info "  Try: export PATH=\"\$HOME/.local/bin:\$PATH\" && moltis --version"
    fi
}

# Post-install: print next steps for Moltis setup
_moltis_post_install() {
    echo ""
    echo -e "${CYAN}Moltis next steps:${NC}"
    echo -e "  1. Start: ${BLUE}moltis${NC}  (web UI at http://localhost:13131)"
    echo -e "  2. Open:  ${BLUE}http://localhost:13131${NC}  (enter the setup code from the terminal)"
    echo -e "     Full install guide: ${CYAN}https://github.com/AloSantana/moltis/blob/main/LOCAL_LINUX_INSTALL.md${NC}"
    echo -e "  3. Add your API keys in Settings → Providers (Gemini, OpenAI, Anthropic, etc.)"
    echo -e "  4. Install gsd-opencode skills:"
    echo -e "     ${CYAN}moltis skills install https://github.com/AloSantana/gsd-opencode${NC}"
    echo ""
    echo -e "  ${YELLOW}Note:${NC} AloSantana's fork has custom gsd-opencode / OpenCode skill adapter."
    echo -e "  To build the fork from source (picks up those extras):"
    echo -e "    ${CYAN}cd ~/projects && git clone git@github.com:AloSantana/moltis.git${NC}"
    echo -e "    ${CYAN}cd moltis && cargo install just && just build-release${NC}"
    echo -e "    ${CYAN}cp target/release/moltis ~/.local/bin/moltis${NC}"
    echo ""
    echo -e "  Open port 13131 if you need remote access to the Moltis web UI:"
    echo -e "    ${CYAN}sudo ufw allow 13131/tcp comment 'Moltis Web UI'${NC}"
    echo ""
}

install_lazydocker() {
    print_section "lazydocker (Docker TUI)"
    if command -v lazydocker &>/dev/null; then
        print_skip "lazydocker $(lazydocker --version 2>/dev/null || echo '')"
        return
    fi

    print_info "Installing lazydocker..."
    LAZYDOCKER_TAG=$(get_latest_release "jesseduffield/lazydocker")
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  ARCH_SLUG="x86_64" ;;
        aarch64) ARCH_SLUG="arm64" ;;
        *)       ARCH_SLUG="x86_64" ;;
    esac
    URL="https://github.com/jesseduffield/lazydocker/releases/download/${LAZYDOCKER_TAG}/lazydocker_${LAZYDOCKER_TAG#v}_Linux_${ARCH_SLUG}.tar.gz"
    curl -fsSL "$URL" | tar xz -C /tmp lazydocker
    sudo mv /tmp/lazydocker /usr/local/bin/lazydocker
    print_success "lazydocker ${LAZYDOCKER_TAG} installed"
    print_info "  Run: lazydocker"
}

install_lazygit() {
    print_section "lazygit (Git TUI)"
    if command -v lazygit &>/dev/null; then
        print_skip "lazygit $(lazygit --version 2>/dev/null | head -1 || echo '')"
        return
    fi

    print_info "Installing lazygit..."
    LAZYGIT_TAG=$(get_latest_release "jesseduffield/lazygit")
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  ARCH_SLUG="x86_64" ;;
        aarch64) ARCH_SLUG="arm64" ;;
        *)       ARCH_SLUG="x86_64" ;;
    esac
    URL="https://github.com/jesseduffield/lazygit/releases/download/${LAZYGIT_TAG}/lazygit_${LAZYGIT_TAG#v}_Linux_${ARCH_SLUG}.tar.gz"
    curl -fsSL "$URL" | tar xz -C /tmp lazygit
    sudo mv /tmp/lazygit /usr/local/bin/lazygit
    print_success "lazygit ${LAZYGIT_TAG} installed"
    print_info "  Run: lazygit"
}

install_monitoring() {
    print_section "Monitoring Stack (Prometheus + Grafana)"
    if ! command -v docker &>/dev/null; then
        print_error "Docker is required for monitoring stack. Run gcp-bootstrap.sh first."
        return 1
    fi

    MONITOR_DIR="$HOME/monitoring"
    mkdir -p "$MONITOR_DIR"

    print_info "Creating monitoring Docker Compose config..."
    cat > "$MONITOR_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=antigravity
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
EOF

    cat > "$MONITOR_DIR/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'antigravity-backend'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/performance/metrics'
EOF

    cd "$MONITOR_DIR"
    docker compose up -d
    print_success "Monitoring stack started"
    print_info "  Prometheus: http://YOUR_IP:9090"
    print_info "  Grafana:    http://YOUR_IP:3001  (admin / antigravity)"
    print_info "  Directory:  $MONITOR_DIR"
}

install_caddy() {
    print_section "Caddy (Web Server — Nginx alternative)"
    if command -v caddy &>/dev/null; then
        print_skip "Caddy $(caddy version 2>/dev/null | head -1)"
        return
    fi

    print_info "Installing Caddy..."
    sudo apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        | sudo tee /etc/apt/sources.list.d/caddy-stable.list > /dev/null
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq caddy
    print_success "Caddy $(caddy version 2>/dev/null | head -1) installed"
    print_info "  Caddyfile: /etc/caddy/Caddyfile"
    print_info "  Quick HTTPS: echo 'your-domain.com { reverse_proxy localhost:8000 }' | sudo tee /etc/caddy/Caddyfile && sudo systemctl reload caddy"
}

install_cloudflared() {
    print_section "Cloudflare Tunnel (cloudflared)"
    if command -v cloudflared &>/dev/null; then
        print_skip "cloudflared $(cloudflared --version 2>/dev/null || echo '')"
        return
    fi

    print_info "Installing cloudflared..."
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  DEB_ARCH="amd64" ;;
        aarch64) DEB_ARCH="arm64" ;;
        *)       DEB_ARCH="amd64" ;;
    esac
    curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${DEB_ARCH}.deb" \
        -o /tmp/cloudflared.deb
    sudo dpkg -i /tmp/cloudflared.deb
    rm -f /tmp/cloudflared.deb
    print_success "cloudflared $(cloudflared --version 2>/dev/null) installed"
    print_info "  Create tunnel: cloudflared tunnel login"
    print_info "  Quick tunnel (no domain):  cloudflared tunnel --url http://localhost:8000"
}

install_mcp_servers() {
    print_section "MCP Servers (from project mcp.json)"
    if ! command -v node &>/dev/null; then
        print_error "Node.js is required. Run gcp-bootstrap.sh first."
        return 1
    fi

    print_info "Installing MCP servers via npm..."
    # Core MCP servers referenced in the project
    MCP_PACKAGES=(
        "@modelcontextprotocol/server-filesystem"
        "@modelcontextprotocol/server-memory"
        "@modelcontextprotocol/server-sequential-thinking"
        "@modelcontextprotocol/server-puppeteer"
        "@modelcontextprotocol/server-fetch"
        "@modelcontextprotocol/server-sqlite"
        "@modelcontextprotocol/server-git"
        "@modelcontextprotocol/server-brave-search"
        "@modelcontextprotocol/server-github"
        "mcp-server-time"
    )

    for pkg in "${MCP_PACKAGES[@]}"; do
        if npm list -g "$pkg" &>/dev/null 2>&1; then
            print_skip "$pkg"
        else
            print_info "Installing $pkg..."
            npm install -g "$pkg" --silent 2>/dev/null \
                && print_success "$pkg installed" \
                || print_warning "Failed to install $pkg (may not exist under this name)"
        fi
    done

    print_success "MCP servers installation complete"
    print_info "  Verify: npm list -g | grep modelcontext"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Help
# ═══════════════════════════════════════════════════════════════════════════════

print_help() {
    echo -e "${BOLD}GCP Optional Dependencies Installer${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all          Install all optional dependencies"
    echo "  --mongodb      MongoDB 7.x (standalone)"
    echo "  --redis        Redis 7.x (standalone, not Docker)"
    echo "  --ollama       Ollama for local LLM inference"
    echo "  --opencode     OpenCode coding agent (latest)"
    echo "  --moltis       Moltis/OpenClaw binary (latest release)"
    echo "  --lazydocker   lazydocker TUI for Docker management"
    echo "  --lazygit      lazygit TUI for Git management"
    echo "  --monitoring   Prometheus + Grafana + cAdvisor in Docker"
    echo "  --caddy        Caddy web server (Nginx alternative)"
    echo "  --cloudflared  Cloudflare Tunnel daemon"
    echo "  --mcp-servers  All MCP servers from the project"
    echo "  --help         Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --opencode --moltis"
    echo "  $0 --ollama --monitoring"
    echo "  $0 --all"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    if [ $# -eq 0 ]; then
        print_help
        exit 0
    fi

    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════╗"
    echo "  ║     GCP Optional Dependencies — Antigravity       ║"
    echo "  ╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"

    INSTALL_ALL=false
    INSTALL_MONGODB=false
    INSTALL_REDIS=false
    INSTALL_OLLAMA=false
    INSTALL_OPENCODE=false
    INSTALL_MOLTIS=false
    INSTALL_LAZYDOCKER=false
    INSTALL_LAZYGIT=false
    INSTALL_MONITORING=false
    INSTALL_CADDY=false
    INSTALL_CLOUDFLARED=false
    INSTALL_MCP=false

    for arg in "$@"; do
        case "$arg" in
            --all)          INSTALL_ALL=true ;;
            --mongodb)      INSTALL_MONGODB=true ;;
            --redis)        INSTALL_REDIS=true ;;
            --ollama)       INSTALL_OLLAMA=true ;;
            --opencode)     INSTALL_OPENCODE=true ;;
            --moltis)       INSTALL_MOLTIS=true ;;
            --lazydocker)   INSTALL_LAZYDOCKER=true ;;
            --lazygit)      INSTALL_LAZYGIT=true ;;
            --monitoring)   INSTALL_MONITORING=true ;;
            --caddy)        INSTALL_CADDY=true ;;
            --cloudflared)  INSTALL_CLOUDFLARED=true ;;
            --mcp-servers)  INSTALL_MCP=true ;;
            --help|-h)      print_help; exit 0 ;;
            *)
                print_error "Unknown option: $arg"
                print_help
                exit 1
                ;;
        esac
    done

    [ "$INSTALL_ALL" = true ] && {
        INSTALL_MONGODB=true
        INSTALL_REDIS=true
        INSTALL_OLLAMA=true
        INSTALL_OPENCODE=true
        INSTALL_MOLTIS=true
        INSTALL_LAZYDOCKER=true
        INSTALL_LAZYGIT=true
        INSTALL_MONITORING=true
        INSTALL_CADDY=true
        INSTALL_CLOUDFLARED=true
        INSTALL_MCP=true
    }

    [ "$INSTALL_MONGODB" = true ]    && install_mongodb
    [ "$INSTALL_REDIS" = true ]      && install_redis_standalone
    [ "$INSTALL_OLLAMA" = true ]     && install_ollama
    [ "$INSTALL_OPENCODE" = true ]   && install_opencode
    [ "$INSTALL_MOLTIS" = true ]     && install_moltis
    [ "$INSTALL_LAZYDOCKER" = true ] && install_lazydocker
    [ "$INSTALL_LAZYGIT" = true ]    && install_lazygit
    [ "$INSTALL_MONITORING" = true ] && install_monitoring
    [ "$INSTALL_CADDY" = true ]      && install_caddy
    [ "$INSTALL_CLOUDFLARED" = true ] && install_cloudflared
    [ "$INSTALL_MCP" = true ]        && install_mcp_servers

    echo ""
    echo -e "${GREEN}[✓]${NC} Optional dependencies installation complete!"
    echo -e "    Log: ${CYAN}$LOG_FILE${NC}"
    echo ""
}

main "$@"
