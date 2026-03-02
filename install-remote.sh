#!/bin/bash

################################################################################
# Antigravity Workspace - Remote VPS Installation Script
# Optimized for remote Ubuntu VPS deployment via SSH
# Supports: Ubuntu 20.04+, Debian 11+
#
# Usage (safer - download, inspect, then execute):
#   curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh -o install-remote.sh
#   less install-remote.sh  # review before running
#   bash install-remote.sh
#
#   With auto-SSL for seecast.cloud:
#   AUTO_SSL_DOMAIN=seecast.cloud AUTO_SSL_EMAIL=admin@seecast.cloud bash install-remote.sh
#
#   With custom domain:
#   EXTERNAL_HOST=yourdomain.com AUTO_SSL_EMAIL=you@example.com bash install-remote.sh
#
# Note: Running scripts piped directly from the internet (curl | bash) is
# discouraged. Download and inspect this script before executing it.
#
# This script will:
#   ✓ Install all system dependencies (Python, Node.js, Docker)
#   ✓ Install and configure Nginx reverse proxy
#   ✓ Setup SSL certificate with Let's Encrypt (automatic for seecast.cloud)
#   ✓ Configure firewall rules
#   ✓ Setup remote access automatically
################################################################################

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/install-remote.log"
REPO_URL="https://github.com/primoscope/antigravity-workspace-template.git"

# Auto-SSL configuration for seecast.cloud
AUTO_SSL_DOMAIN="${AUTO_SSL_DOMAIN:-}"
AUTO_SSL_EMAIL="${AUTO_SSL_EMAIL:-}"

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║     Antigravity Workspace - Remote VPS Installer          ║"
    echo "║                                                            ║"
    echo "║     Automated setup for remote Ubuntu VPS deployment      ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to print colored output with timestamps
print_status() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${BLUE}[${timestamp}] [INFO]${NC} $1"
}

print_success() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $1"
}

print_error() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${RED}[${timestamp}] [ERROR]${NC} $1"
}

print_warning() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${YELLOW}[${timestamp}] [WARNING]${NC} $1"
}

print_info() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${CYAN}[${timestamp}] [INFO]${NC} $1"
}

# Function to check if running on remote VPS
check_environment() {
    print_status "Checking environment..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. It's recommended to run as a regular user with sudo."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Get public IP
    PUBLIC_IP=$(curl -s https://api.ipify.org 2>/dev/null || echo "unknown")
    print_info "Public IP: $PUBLIC_IP"
    
    # Get hostname
    HOSTNAME=$(hostname)
    print_info "Hostname: $HOSTNAME"
    
    print_success "Environment check complete"
}

# Function to configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    if command -v ufw >/dev/null 2>&1; then
        # Allow SSH first (important!)
        sudo ufw allow ssh
        sudo ufw allow 22/tcp
        
        # Allow HTTP and HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # Allow backend port
        sudo ufw allow 8000/tcp
        
        # Allow frontend port (if separate)
        sudo ufw allow 3000/tcp
        
        # Enable firewall
        sudo ufw --force enable
        
        print_success "Firewall configured"
        print_info "Allowed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3000 (Frontend), 8000 (Backend)"
    else
        print_warning "ufw not found, skipping firewall configuration"
    fi
}

# Function to setup remote configuration
setup_remote_config() {
    print_status "Setting up remote configuration..."
    
    # Get external IP/hostname
    read -r -p "Enter your VPS IP or domain name [${PUBLIC_IP}]: " EXTERNAL_HOST
    EXTERNAL_HOST=${EXTERNAL_HOST:-$PUBLIC_IP}
    
    # Create .env file with remote configuration
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        print_warning ".env file already exists"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    cat > "${SCRIPT_DIR}/.env" << EOF
# ═══ AI Models ═══
GEMINI_API_KEY=your_gemini_api_key_here

# ═══ GitHub Integration ═══
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# ═══ Local Model Settings ═══
LOCAL_MODEL=llama3

# ═══ Server Configuration ═══
HOST=0.0.0.0
PORT=8000

# ═══ Remote Access Configuration ═══
REMOTE_ACCESS=true
EXTERNAL_HOST=${EXTERNAL_HOST}
FRONTEND_PORT=3000
BACKEND_PORT=8000

# ═══ Security Settings ═══
# Allow all origins for remote access (configure more restrictively for production)
ALLOWED_ORIGINS=http://${EXTERNAL_HOST}:3000,http://${EXTERNAL_HOST}:8000,https://${EXTERNAL_HOST}:3000,https://${EXTERNAL_HOST}:8000,http://${EXTERNAL_HOST},https://${EXTERNAL_HOST}

# ═══ Optional SSL Configuration ═══
SSL_ENABLED=false
SSL_CERT_PATH=
SSL_KEY_PATH=
EOF
    
    print_success "Remote configuration created"
    print_warning "Remember to edit .env and add your API keys!"
}

# Function to setup nginx reverse proxy
setup_nginx() {
    print_status "Setting up nginx reverse proxy..."
    
    # Check if nginx is installed
    if ! command -v nginx >/dev/null 2>&1; then
        print_status "Installing nginx..."
        sudo apt-get update -qq
        if sudo apt-get install -y nginx 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Nginx installed successfully"
        else
            print_error "Failed to install nginx"
            return 1
        fi
    else
        print_info "Nginx already installed"
    fi
    
    # Create nginx configuration
    sudo tee /etc/nginx/sites-available/antigravity > /dev/null << EOF
# Antigravity Workspace - Nginx Configuration

# Backend API (port 8000)
server {
    listen 80;
    server_name ${EXTERNAL_HOST};
    
    # Frontend location
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket location
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/antigravity /etc/nginx/sites-enabled/
    
    # Remove default site if exists
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    if sudo nginx -t; then
        sudo systemctl restart nginx
        sudo systemctl enable nginx
        print_success "Nginx configured and started"
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

# Function to setup SSL with Let's Encrypt
setup_ssl() {
    print_status "Setting up SSL with Let's Encrypt..."
    
    # Check if EXTERNAL_HOST is an IP address (SSL requires domain name)
    if [[ "${EXTERNAL_HOST}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_warning "SSL requires a domain name, not an IP address"
        print_info "Skipping SSL setup. You can set it up later with: sudo certbot --nginx"
        return
    fi
    
    # Auto-detect seecast.cloud domain or check for auto-SSL variables
    local setup_ssl=false
    local ssl_email=""
    
    if [[ "${EXTERNAL_HOST}" == *"seecast.cloud"* ]] || [[ -n "${AUTO_SSL_DOMAIN}" ]]; then
        # Automatic SSL setup for seecast.cloud or when AUTO_SSL_DOMAIN is set
        setup_ssl=true
        
        # Use AUTO_SSL_EMAIL if set, otherwise use a default
        if [[ -n "${AUTO_SSL_EMAIL}" ]]; then
            ssl_email="${AUTO_SSL_EMAIL}"
        else
            ssl_email="admin@${EXTERNAL_HOST}"
        fi
        
        print_info "Auto-SSL detected for domain: ${EXTERNAL_HOST}"
        print_info "Using email: ${ssl_email}"
    else
        # Interactive prompt for other domains
        read -r -p "Do you want to setup SSL with Let's Encrypt? (requires domain name) (y/N): " -n 1 REPLY
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            setup_ssl=true
            read -r -p "Enter your email for Let's Encrypt: " ssl_email
        else
            print_info "Skipping SSL setup"
            return
        fi
    fi
    
    if [ "$setup_ssl" = false ]; then
        return
    fi
    
    # Check if certbot is installed
    if ! command -v certbot >/dev/null 2>&1; then
        print_status "Installing certbot..."
        sudo apt-get update -qq
        if sudo apt-get install -y certbot python3-certbot-nginx 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Certbot installed successfully"
        else
            print_error "Failed to install certbot"
            return 1
        fi
    else
        print_info "Certbot already installed"
    fi
    
    # Validate email
    if [[ ! "${ssl_email}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        print_error "Invalid email address: ${ssl_email}"
        print_info "SSL setup aborted. You can run 'sudo certbot --nginx' manually later"
        return 1
    fi
    
    # Ensure nginx is running before certbot
    sudo systemctl start nginx 2>/dev/null || true
    
    # Run certbot
    print_status "Obtaining SSL certificate for ${EXTERNAL_HOST}..."
    if sudo certbot --nginx -d "${EXTERNAL_HOST}" --non-interactive --agree-tos -m "${ssl_email}" 2>&1 | tee -a "$LOG_FILE"; then
        print_success "SSL certificate installed for ${EXTERNAL_HOST}"
        
        # Update .env for SSL
        if [ -f "${SCRIPT_DIR}/.env" ]; then
            sed -i 's/SSL_ENABLED=false/SSL_ENABLED=true/' "${SCRIPT_DIR}/.env"
        fi
        
        # Setup auto-renewal check
        print_status "Setting up automatic certificate renewal..."
        if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
            (sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -
            print_success "Auto-renewal configured (daily at 12:00)"
        fi
        
        print_success "SSL setup complete!"
        print_info "Certificate will auto-renew before expiration"
        print_info "Access your site at: https://${EXTERNAL_HOST}"
    else
        print_error "SSL certificate installation failed"
        print_warning "Common causes:"
        print_info "  - Domain ${EXTERNAL_HOST} does not point to this server"
        print_info "  - Port 80 is not accessible from the internet"
        print_info "  - Firewall blocking HTTP traffic"
        print_info ""
        print_info "You can try manually: sudo certbot --nginx -d ${EXTERNAL_HOST}"
        return 1
    fi
}

# Function to display access information
display_access_info() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║          Installation Complete! 🎉                         ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Determine protocol based on SSL status
    local protocol="http"
    if [ -f "${SCRIPT_DIR}/.env" ] && grep -q "SSL_ENABLED=true" "${SCRIPT_DIR}/.env"; then
        protocol="https"
    fi
    
    echo -e "${CYAN}Access your Antigravity Workspace:${NC}"
    echo ""
    echo -e "  ${BLUE}Web Interface:${NC}  ${protocol}://${EXTERNAL_HOST}"
    echo -e "  ${BLUE}API Docs:${NC}       ${protocol}://${EXTERNAL_HOST}/docs"
    echo -e "  ${BLUE}Health Check:${NC}   ${protocol}://${EXTERNAL_HOST}/health"
    
    if [ "$protocol" = "https" ]; then
        echo ""
        echo -e "  ${GREEN}✓ SSL/HTTPS enabled${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo -e "  1. Edit .env file with your API keys:"
    echo -e "     ${BLUE}nano ${SCRIPT_DIR}/.env${NC}"
    echo ""
    echo -e "  2. Start the workspace:"
    echo -e "     ${BLUE}cd ${SCRIPT_DIR} && ./start.sh${NC}"
    echo ""
    echo -e "  3. Check service status:"
    echo -e "     ${BLUE}sudo systemctl status antigravity${NC}"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo ""
    echo -e "  ${BLUE}./start.sh${NC}       - Start the workspace"
    echo -e "  ${BLUE}./stop.sh${NC}        - Stop the workspace"
    echo -e "  ${BLUE}./validate.sh${NC}    - Validate installation"
    echo -e "  ${BLUE}./configure.sh${NC}   - Re-run configuration wizard"
    echo ""
    echo -e "${CYAN}Docker Commands:${NC}"
    echo ""
    echo -e "  ${BLUE}docker compose up -d${NC}      - Start with Docker"
    echo -e "  ${BLUE}docker compose down${NC}       - Stop Docker containers"
    echo -e "  ${BLUE}docker compose logs -f${NC}    - View Docker logs"
    echo -e "  ${BLUE}docker compose build${NC}      - Rebuild Docker image"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo -e "  • Add your API keys to .env before starting"
    echo -e "  • Port 8000 is open for backend API access"
    echo -e "  • Firewall configured for HTTP/HTTPS traffic"
    echo -e "  • Docker installed and configured"
    echo ""
}

# Main installation flow
main() {
    print_banner
    
    # Log to file
    exec 1> >(tee -a "$LOG_FILE")
    exec 2>&1
    
    print_status "Starting remote VPS installation..."
    print_info "Log file: $LOG_FILE"
    echo ""
    
    # Run checks
    check_environment
    
    # Clone or update repository
    if [ ! -d "${SCRIPT_DIR}/.git" ]; then
        print_status "Cloning repository..."
        cd "$(dirname "$SCRIPT_DIR")"
        git clone "$REPO_URL" "$(basename "$SCRIPT_DIR")"
        cd "$SCRIPT_DIR"
        print_success "Repository cloned"
    else
        print_info "Repository already exists"
    fi
    
    # Run standard installation
    print_status "Running standard installation..."
    if [ -f "${SCRIPT_DIR}/install.sh" ]; then
        # Run install.sh non-interactively where possible
        export DEBIAN_FRONTEND=noninteractive
        bash "${SCRIPT_DIR}/install.sh"
    else
        print_error "install.sh not found!"
        exit 1
    fi
    
    # Ensure Docker is accessible (handle newgrp issue)
    if command -v docker >/dev/null 2>&1; then
        if ! docker ps >/dev/null 2>&1; then
            print_warning "Docker group membership requires re-login"
            print_info "Adding workaround for current session..."
            # Create a temporary script that can access docker
            sudo setfacl -m "user:${USER}:rw" /var/run/docker.sock 2>/dev/null || true
        fi
        
        # Build Docker image for remote deployment
        print_status "Building Docker image for production..."
        if docker compose build 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Docker image built"
        else
            print_warning "Docker build failed - you can build later with: docker compose build"
        fi
    fi
    
    # Configure firewall
    configure_firewall
    
    # Setup remote configuration
    setup_remote_config
    
    # Setup nginx
    if ! setup_nginx; then
        print_error "Nginx setup failed! Check logs at $LOG_FILE"
        print_info "You can retry with: sudo apt-get install -y nginx"
        # Continue anyway, don't exit
    fi
    
    # Optional: Setup SSL
    setup_ssl
    
    # Validate installation
    print_status "Validating installation..."
    local validation_passed=true
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        print_success "Python is installed"
    else
        print_error "Python not found!"
        validation_passed=false
    fi
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        print_success "Node.js is installed"
    else
        print_warning "Node.js not found - MCP servers may not work"
    fi
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        print_success "Docker is installed"
    else
        print_warning "Docker not found - Docker deployment unavailable"
    fi
    
    # Check Nginx
    if command -v nginx >/dev/null 2>&1; then
        if sudo nginx -t 2>/dev/null; then
            print_success "Nginx is installed and configured"
        else
            print_warning "Nginx configuration has errors"
        fi
    else
        print_error "Nginx not installed!"
        validation_passed=false
    fi
    
    # Check if install.sh completed
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        print_success "Python virtual environment created"
    else
        print_warning "Python venv not found - install.sh may have failed"
    fi
    
    if [ "$validation_passed" = false ]; then
        print_warning "Some components failed to install. Check the log: $LOG_FILE"
    fi
    
    # Display access information
    display_access_info
    
    print_success "Remote VPS installation complete!"
}

# Run main function
main "$@"
