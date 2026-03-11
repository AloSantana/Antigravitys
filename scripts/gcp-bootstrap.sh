#!/bin/bash

################################################################################
# GCP VPS Bootstrap Script — Run this FIRST on a fresh Ubuntu 24.04 VM
# Sets up base system BEFORE cloning any repos or installing AI tools.
#
# Usage (curl-pipeable):
#   curl -fsSL https://raw.githubusercontent.com/AloSantana/Antigravitys/main/scripts/gcp-bootstrap.sh | bash
#
# Or clone and run:
#   chmod +x scripts/gcp-bootstrap.sh
#   ./scripts/gcp-bootstrap.sh
#
# After this script completes, proceed with:
#   git clone https://github.com/AloSantana/Antigravitys.git
#   cd Antigravitys && ./install.sh
#   ./scripts/gcp-optional-deps.sh --opencode --moltis
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

LOG_FILE="/tmp/gcp-bootstrap.log"

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
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    log "ERROR" "$1"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}══════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}══════════════════════════════════════════════${NC}"
    log "STEP" "$1"
}

# Error trap
trap 'print_error "Bootstrap failed at line $LINENO. Check $LOG_FILE for details."; exit 1' ERR

# ═══════════════════════════════════════════════════════════════════════════════
# Banner
# ═══════════════════════════════════════════════════════════════════════════════

print_banner() {
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════╗"
    echo "  ║         GCP VPS Bootstrap — Antigravity           ║"
    echo "  ║   Phase 1: Fresh Ubuntu 24.04 LTS Setup           ║"
    echo "  ╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${YELLOW}Log file: $LOG_FILE${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: System Hardening & Base Setup
# ═══════════════════════════════════════════════════════════════════════════════

phase1_system_setup() {
    print_step "Phase 1: System Hardening & Base Setup"

    # Update & upgrade
    print_info "Updating system packages..."
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
    print_success "System packages updated"

    # Set timezone to UTC
    if [ "$(timedatectl show -p Timezone --value 2>/dev/null)" != "UTC" ]; then
        sudo timedatectl set-timezone UTC
        print_success "Timezone set to UTC"
    else
        print_info "Timezone already UTC"
    fi

    # Set hostname if on GCP (metadata server available)
    if curl -sf -H "Metadata-Flavor: Google" \
            "http://metadata.google.internal/computeMetadata/v1/instance/name" \
            --connect-timeout 2 > /tmp/_gcp_name 2>/dev/null; then
        GCP_NAME=$(cat /tmp/_gcp_name)
        sudo hostnamectl set-hostname "$GCP_NAME" 2>/dev/null || true
        print_success "Hostname set to: $GCP_NAME"
        rm -f /tmp/_gcp_name
    fi

    # Detect RAM and auto-size swap
    TOTAL_RAM_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
    if [ "$TOTAL_RAM_GB" -le 16 ]; then
        SWAP_SIZE="4G"
    else
        SWAP_SIZE="8G"
    fi

    # Create swap file (idempotent)
    if ! swapon --show | grep -q /swapfile; then
        print_info "Creating ${SWAP_SIZE} swap file..."
        sudo fallocate -l "$SWAP_SIZE" /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        # Persist across reboots
        if ! grep -q '/swapfile' /etc/fstab; then
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
        fi
        print_success "Swap file created: ${SWAP_SIZE}"
    else
        print_info "Swap already configured"
    fi

    # Sysctl performance tuning (idempotent)
    SYSCTL_CONF="/etc/sysctl.d/99-antigravity.conf"
    if [ ! -f "$SYSCTL_CONF" ]; then
        sudo tee "$SYSCTL_CONF" > /dev/null << 'EOF'
# Antigravity GCP Performance Tuning
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5
fs.file-max=500000
fs.inotify.max_user_watches=524288
net.core.somaxconn=65535
net.core.netdev_max_backlog=5000
net.ipv4.tcp_max_syn_backlog=8096
net.ipv4.tcp_slow_start_after_idle=0
EOF
        sudo sysctl -p "$SYSCTL_CONF" > /dev/null
        print_success "Sysctl performance tuning applied"
    else
        print_info "Sysctl tuning already configured"
    fi

    # Configure ulimits (idempotent)
    LIMITS_CONF="/etc/security/limits.d/99-antigravity.conf"
    if [ ! -f "$LIMITS_CONF" ]; then
        sudo tee "$LIMITS_CONF" > /dev/null << 'EOF'
# Antigravity GCP ulimits
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
root soft nofile 65535
root hard nofile 65535
EOF
        print_success "ulimits configured"
    else
        print_info "ulimits already configured"
    fi

    print_success "Phase 1 complete"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Essential Packages
# ═══════════════════════════════════════════════════════════════════════════════

phase2_essential_packages() {
    print_step "Phase 2: Essential Packages"

    print_info "Installing essential packages..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        build-essential curl git wget unzip jq \
        htop tmux screen nano vim tree ncdu \
        software-properties-common apt-transport-https \
        ca-certificates gnupg lsb-release \
        ufw fail2ban \
        acl \
        2>&1 | grep -v "^$" | head -20 || true

    print_success "Essential packages installed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Firewall (UFW)
# ═══════════════════════════════════════════════════════════════════════════════

phase3_firewall() {
    print_step "Phase 3: Firewall (UFW) & fail2ban"

    # Configure UFW (idempotent)
    print_info "Configuring UFW firewall..."
    sudo ufw --force reset > /dev/null 2>&1
    sudo ufw default deny incoming > /dev/null
    sudo ufw default allow outgoing > /dev/null
    sudo ufw allow 22/tcp comment 'SSH' > /dev/null
    sudo ufw allow 80/tcp comment 'HTTP' > /dev/null
    sudo ufw allow 443/tcp comment 'HTTPS' > /dev/null
    sudo ufw allow 8000/tcp comment 'Backend API' > /dev/null
    sudo ufw allow 3000/tcp comment 'Frontend' > /dev/null
    # Port 13131 is used by Moltis web UI.
    # Moltis upstream: moltis-org/moltis — AloSantana/moltis is a fork 13+ commits ahead.
    # Both use the same port (13131). Safe to open here; remove if not using Moltis.
    sudo ufw allow 13131/tcp comment 'Moltis Web UI' > /dev/null
    sudo ufw --force enable > /dev/null
    print_success "UFW firewall enabled (22, 80, 443, 8000, 3000, 13131)"

    # Configure fail2ban for SSH protection
    if [ ! -f /etc/fail2ban/jail.local ]; then
        sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(syslog_backend)s
EOF
        sudo systemctl enable fail2ban > /dev/null 2>&1 || true
        sudo systemctl restart fail2ban > /dev/null 2>&1 || true
        print_success "fail2ban configured for SSH protection"
    else
        print_info "fail2ban already configured"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: Docker Engine (Headless)
# ═══════════════════════════════════════════════════════════════════════════════

phase4_docker() {
    print_step "Phase 4: Docker Engine (Headless)"

    if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
        print_info "Docker + Compose plugin already installed"
        docker --version
        docker compose version
        return
    fi

    print_info "Installing Docker CE from official repository..."

    # Remove old conflicting packages
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Add Docker GPG key
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repo
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin

    # Enable & start Docker
    sudo systemctl enable docker
    sudo systemctl start docker

    # Add current user to docker group
    sudo usermod -aG docker "$USER" 2>/dev/null || true

    # Configure Docker daemon (log rotation + overlay2)
    sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-address-pools": [
    {"base": "172.17.0.0/12", "size": 24}
  ],
  "live-restore": true
}
EOF
    sudo systemctl reload docker 2>/dev/null || sudo systemctl restart docker

    print_success "Docker CE + Compose plugin installed"
    docker --version
    docker compose version

    print_warning "NOTE: You must log out and back in (or run 'newgrp docker') for docker group to take effect"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: Python 3.11+
# ═══════════════════════════════════════════════════════════════════════════════

phase5_python() {
    print_step "Phase 5: Python 3.11+"

    # Check if Python 3.11+ is already installed
    if command -v python3 &>/dev/null; then
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
            print_info "Python $PY_VERSION already installed"
            python3 --version
        else
            print_info "Python $PY_VERSION found, upgrading to 3.11+ via deadsnakes PPA..."
            sudo add-apt-repository -y ppa:deadsnakes/ppa > /dev/null 2>&1
            sudo apt-get update -qq
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
            sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 11
            print_success "Python 3.11 installed via deadsnakes PPA"
        fi
    else
        print_info "Python not found, installing 3.11..."
        sudo add-apt-repository -y ppa:deadsnakes/ppa > /dev/null 2>&1
        sudo apt-get update -qq
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 11
        print_success "Python 3.11 installed"
    fi

    # Install pip and venv
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-pip python3-venv 2>/dev/null || true

    # Create python → python3 symlink if missing
    if ! command -v python &>/dev/null; then
        sudo ln -sf /usr/bin/python3 /usr/local/bin/python
        print_success "Created python → python3 symlink"
    fi

    python3 --version
    pip3 --version 2>/dev/null || python3 -m pip --version
    print_success "Phase 5 complete"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 6: Node.js 20 LTS
# ═══════════════════════════════════════════════════════════════════════════════

phase6_nodejs() {
    print_step "Phase 6: Node.js 20 LTS"

    if command -v node &>/dev/null; then
        NODE_VER=$(node --version | tr -d 'v' | cut -d. -f1)
        if [ "$NODE_VER" -ge 20 ]; then
            print_info "Node.js $(node --version) already installed"
            return
        fi
    fi

    print_info "Installing Node.js 20 LTS via NodeSource..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nodejs

    print_success "Node.js $(node --version) installed"
    print_success "npm $(npm --version) available"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 7: Rust Toolchain
# ═══════════════════════════════════════════════════════════════════════════════

phase7_rust() {
    print_step "Phase 7: Rust Toolchain (for Moltis/OpenClaw)"

    if command -v rustc &>/dev/null; then
        print_info "Rust $(rustc --version) already installed"
        return
    fi

    print_info "Installing Rust toolchain via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --no-modify-path --default-toolchain stable

    # Add to PATH for current session
    # shellcheck source=/dev/null
    source "$HOME/.cargo/env" 2>/dev/null || true

    # Add to shell profile (idempotent)
    for PROFILE in "$HOME/.bashrc" "$HOME/.profile"; do
        if [ -f "$PROFILE" ] && ! grep -q 'cargo/env' "$PROFILE"; then
            echo '' >> "$PROFILE"
            echo '# Rust toolchain' >> "$PROFILE"
            echo '. "$HOME/.cargo/env"' >> "$PROFILE"
        fi
    done

    print_success "Rust $(rustc --version 2>/dev/null || echo 'installed') — reload shell or run: source ~/.cargo/env"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 8: Git & GitHub Setup
# ═══════════════════════════════════════════════════════════════════════════════

phase8_git_github() {
    print_step "Phase 8: Git & GitHub Setup"

    # Git is already installed in Phase 2 — configure it
    GIT_NAME="${GIT_NAME:-GCP Agent}"
    GIT_EMAIL="${GIT_EMAIL:-agent@localhost}"

    git config --global user.name "$GIT_NAME"
    git config --global user.email "$GIT_EMAIL"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    git config --global core.editor nano
    print_success "Git configured (name: $GIT_NAME, email: $GIT_EMAIL)"
    print_info "  To change: git config --global user.name 'Your Name'"

    # Install GitHub CLI (idempotent)
    if ! command -v gh &>/dev/null; then
        print_info "Installing GitHub CLI..."
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
            | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
https://cli.github.com/packages stable main" \
            | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt-get update -qq
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gh
        print_success "GitHub CLI installed: $(gh --version | head -1)"
    else
        print_info "GitHub CLI already installed: $(gh --version | head -1)"
    fi

    # Generate SSH key for GitHub (ed25519) if not exists
    SSH_KEY="$HOME/.ssh/id_ed25519"
    if [ ! -f "$SSH_KEY" ]; then
        mkdir -p "$HOME/.ssh"
        chmod 700 "$HOME/.ssh"
        ssh-keygen -t ed25519 -C "$GIT_EMAIL" -f "$SSH_KEY" -N ""
        print_success "SSH key generated: $SSH_KEY"
    else
        print_info "SSH key already exists: $SSH_KEY"
    fi

    # Add GitHub to known_hosts (prevent first-connect prompt)
    if ! grep -q "github.com" "$HOME/.ssh/known_hosts" 2>/dev/null; then
        ssh-keyscan github.com >> "$HOME/.ssh/known_hosts" 2>/dev/null
        print_success "github.com added to known_hosts"
    fi

    # Create projects directory structure
    mkdir -p "$HOME/projects"
    print_success "Created $HOME/projects/ directory"

    # Print SSH key for user to add to GitHub
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}📋 ADD THIS SSH KEY TO GITHUB:${NC}"
    echo -e "${YELLOW}   https://github.com/settings/keys${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat "$SSH_KEY.pub"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  Or use: ${CYAN}gh auth login${NC}  (interactive GitHub auth)"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 9: Nginx + Certbot
# ═══════════════════════════════════════════════════════════════════════════════

phase9_nginx() {
    print_step "Phase 9: Nginx + Certbot (SSL)"

    if ! command -v nginx &>/dev/null; then
        print_info "Installing Nginx..."
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx
        sudo systemctl enable nginx
        sudo systemctl start nginx
        print_success "Nginx installed and started"
    else
        print_info "Nginx already installed: $(nginx -v 2>&1)"
    fi

    # Install certbot (idempotent)
    if ! command -v certbot &>/dev/null; then
        print_info "Installing Certbot for SSL..."
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
            certbot python3-certbot-nginx
        print_success "Certbot installed"
    else
        print_info "Certbot already installed: $(certbot --version 2>&1)"
    fi

    print_info "  To get SSL cert: sudo certbot --nginx -d your-domain.com -m you@email.com --agree-tos"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 10: Verification & Summary
# ═══════════════════════════════════════════════════════════════════════════════

phase10_verify() {
    print_step "Phase 10: Verification & Summary"

    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║        Bootstrap Complete! Installed versions:   ║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""

    # Versions
    echo -e "${CYAN}System:${NC}"
    echo -e "  OS:       $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY | cut -d= -f2 | tr -d '"')"
    echo -e "  Hostname: $(hostname)"
    echo -e "  Timezone: $(timedatectl show -p Timezone --value 2>/dev/null || echo 'UTC')"
    echo ""
    echo -e "${CYAN}Runtime:${NC}"
    echo -e "  Python:   $(python3 --version 2>&1 | grep -oP 'Python \S+')"
    echo -e "  Node.js:  $(node --version 2>/dev/null || echo 'not found')"
    echo -e "  npm:      $(npm --version 2>/dev/null || echo 'not found')"
    echo -e "  Rust:     $(rustc --version 2>/dev/null || source "$HOME/.cargo/env" 2>/dev/null && rustc --version 2>/dev/null || echo 'installed — reload shell')"
    echo -e "  Docker:   $(docker --version 2>/dev/null || echo 'not found')"
    echo -e "  Compose:  $(docker compose version 2>/dev/null || echo 'not found')"
    echo -e "  Git:      $(git --version)"
    echo -e "  gh CLI:   $(gh --version 2>/dev/null | head -1 || echo 'not found')"
    echo -e "  Nginx:    $(nginx -v 2>&1 | grep -oP 'nginx/\S+')"
    echo ""

    # Resources
    echo -e "${CYAN}System Resources:${NC}"
    echo -e "  RAM:      $(free -h | awk '/Mem:/{print $2}') total / $(free -h | awk '/Mem:/{print $7}') available"
    echo -e "  Swap:     $(free -h | awk '/Swap:/{print $2}')"
    echo -e "  Disk:     $(df -h / | awk 'NR==2{print $4}') free / $(df -h / | awk 'NR==2{print $2}') total"
    echo -e "  CPUs:     $(nproc)"
    echo ""

    # Next steps
    echo -e "${BOLD}${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}🚀 Next Steps:${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BLUE}1.${NC} Add your SSH key to GitHub: https://github.com/settings/keys"
    echo -e "  ${BLUE}2.${NC} Authenticate GitHub CLI:  ${CYAN}gh auth login${NC}"
    echo -e "  ${BLUE}3.${NC} Clone Antigravity repo:"
    echo -e "       ${CYAN}cd ~/projects && git clone git@github.com:AloSantana/Antigravitys.git${NC}"
    echo -e "  ${BLUE}4.${NC} Run Antigravity installer: ${CYAN}cd Antigravitys && ./install.sh${NC}"
    echo -e "  ${BLUE}5.${NC} (Optional) Install AI tools:"
    echo -e "       ${CYAN}./scripts/gcp-optional-deps.sh --opencode --moltis${NC}"
    echo -e "  ${BLUE}6.${NC} Deploy with Docker:        ${CYAN}docker compose up -d${NC}"
    echo -e "  ${BLUE}7.${NC} Set up Nginx reverse proxy:"
    echo -e "       ${CYAN}sudo cp templates/nginx-gcp-reverse-proxy.conf /etc/nginx/sites-available/antigravity${NC}"
    echo -e "       ${CYAN}sudo sed -i 's/your-domain.com/YOUR_DOMAIN/' /etc/nginx/sites-available/antigravity${NC}"
    echo -e "       ${CYAN}sudo ln -s /etc/nginx/sites-available/antigravity /etc/nginx/sites-enabled/${NC}"
    echo -e "       ${CYAN}sudo nginx -t && sudo systemctl reload nginx${NC}"
    echo -e "  ${BLUE}8.${NC} Get SSL certificate:       ${CYAN}sudo certbot --nginx -d your-domain.com${NC}"
    echo ""
    echo -e "  ${YELLOW}⚠${NC}  Log out and back in for docker group permissions to take effect."
    echo ""
    echo -e "  Log file: ${CYAN}$LOG_FILE${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_banner

    # Must be run as non-root (but with sudo access)
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root. Run as a normal user with sudo access."
        print_info "On GCP: the default user is 'ubuntu' or your username — it already has sudo."
        exit 1
    fi

    # Check sudo access
    if ! sudo -n true 2>/dev/null && ! sudo -v 2>/dev/null; then
        print_error "This script requires sudo access. Please ensure your user has sudo privileges."
        exit 1
    fi

    phase1_system_setup
    phase2_essential_packages
    phase3_firewall
    phase4_docker
    phase5_python
    phase6_nodejs
    phase7_rust
    phase8_git_github
    phase9_nginx
    phase10_verify
}

main "$@"
