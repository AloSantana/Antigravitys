#!/bin/bash

################################################################################
# Antigravity Workspace - Automated Installation Script
# Optimized for Ubuntu VPS deployment
# Supports: Ubuntu 20.04+, Debian 11+
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
LOG_FILE="${SCRIPT_DIR}/install.log"
NODE_VERSION="20"
PYTHON_VERSION="3.11"

# Cleanup tracking
VENV_CREATED=false
CONFIG_BACKED_UP=false
BACKUP_DIR=""

# Rollback and cleanup function
cleanup_on_error() {
    local exit_code=$?
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    echo ""
    print_error "Installation failed at ${timestamp} (exit code: ${exit_code})"
    print_status "Performing cleanup..."
    
    # Remove partial venv if created
    if [ "$VENV_CREATED" = true ] && [ -d "${SCRIPT_DIR}/venv" ]; then
        print_status "Removing partial virtual environment..."
        rm -rf "${SCRIPT_DIR}/venv"
        print_success "Virtual environment cleaned up"
    fi
    
    # Restore backed up configs
    if [ "$CONFIG_BACKED_UP" = true ] && [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
        print_status "Restoring backed up configurations..."
        if [ -f "${BACKUP_DIR}/.env" ]; then
            cp "${BACKUP_DIR}/.env" "${SCRIPT_DIR}/.env"
            print_success "Restored .env file"
        fi
    fi
    
    # Log failure point
    echo "[${timestamp}] Installation failed at line ${BASH_LINENO[0]} with exit code $exit_code" >> "${LOG_FILE}"
    
    print_error "Installation incomplete. Check logs at: ${LOG_FILE}"
    print_info "You can try running the installer again or fix issues manually."
    
    exit "$exit_code"
}

# Register cleanup function
trap cleanup_on_error ERR

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt yes/no question
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

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS. This script requires Ubuntu 20.04+ or Debian 11+"
        exit 1
    fi
    
    print_status "Detected OS: $OS $VER"
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check sudo access BEFORE any sudo command is executed
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges. Please run with sudo or ensure your user is in sudoers."
        print_info "You can configure passwordless sudo or run: sudo ./install.sh"
        exit 1
    fi
    print_success "Sudo access verified"
    
    # Check RAM
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -lt 2048 ]; then
        print_warning "Recommended RAM: 2GB+. Current: ${TOTAL_RAM}MB"
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df -BG "$SCRIPT_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 5 ]; then
        print_warning "Recommended disk space: 5GB+. Available: ${AVAILABLE_SPACE}GB"
    fi
    
    print_success "System requirements check completed"
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    sudo apt-get update -qq
    sudo apt-get install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        ca-certificates \
        gnupg \
        lsb-release \
        python3-pip \
        python3-venv \
        python3-dev \
        nginx \
        supervisor \
        jq \
        unzip
    
    print_success "System dependencies installed"
}

# Function to install Node.js
install_nodejs() {
    if command_exists node; then
        CURRENT_NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$CURRENT_NODE_VERSION" -ge "$NODE_VERSION" ]; then
            print_success "Node.js $(node -v) already installed"
            return
        fi
    fi
    
    print_status "Installing Node.js ${NODE_VERSION}..."
    
    # Method 1: Try NodeSource repository
    if ! install_nodejs_nodesource; then
        print_warning "NodeSource installation failed, trying nvm..."
        
        # Method 2: Try nvm as fallback
        if ! install_nodejs_nvm; then
            print_error "All Node.js installation methods failed"
            print_info "You can manually install Node.js ${NODE_VERSION}+ from https://nodejs.org/"
            return 1
        fi
    fi
    
    # Verify installation
    if command_exists node; then
        print_success "Node.js $(node -v) installed successfully"
    else
        print_error "Node.js installation verification failed"
        return 1
    fi
}

# Function to install Node.js via NodeSource
install_nodejs_nodesource() {
    print_status "Attempting NodeSource installation..."
    
    # Clean up any existing NodeSource configuration
    sudo rm -f /etc/apt/sources.list.d/nodesource.list 2>/dev/null || true
    
    # Try to download and run setup script
    if curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x -o /tmp/nodesource_setup.sh 2>/dev/null; then
        if sudo -E bash /tmp/nodesource_setup.sh 2>&1 | tee -a "$LOG_FILE"; then
            if sudo apt-get install -y nodejs 2>&1 | tee -a "$LOG_FILE"; then
                rm -f /tmp/nodesource_setup.sh
                return 0
            fi
        fi
    fi
    
    rm -f /tmp/nodesource_setup.sh
    return 1
}

# Function to install Node.js via nvm
install_nodejs_nvm() {
    print_status "Installing Node.js via nvm..."
    
    # Download and install nvm
    export NVM_DIR="$HOME/.nvm"
    
    if [ ! -d "$NVM_DIR" ]; then
        if curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash 2>&1 | tee -a "$LOG_FILE"; then
            print_success "nvm installed"
        else
            return 1
        fi
    fi
    
    # Load nvm
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    
    # Install Node.js
    if nvm install ${NODE_VERSION} 2>&1 | tee -a "$LOG_FILE"; then
        nvm use ${NODE_VERSION}
        nvm alias default ${NODE_VERSION}
        
        # Add nvm to shell profile for future sessions
        if ! grep -q 'NVM_DIR' ~/.bashrc 2>/dev/null; then
            {
                echo 'export NVM_DIR="$HOME/.nvm"'
                echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"'
            } >> ~/.bashrc
        fi
        
        return 0
    fi
    
    return 1
}

# Function to install Python
install_python() {
    if command_exists python3; then
        print_success "Python $(python3 --version) already installed"
    else
        print_status "Installing Python..."
        sudo apt-get install -y python3 python3-pip python3-venv
        print_success "Python installed"
    fi
}

# Function to install Docker
install_docker() {
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        print_success "Docker ${DOCKER_VERSION} already installed"
        
        # Verify Docker is working
        if docker ps >/dev/null 2>&1; then
            print_success "Docker daemon is running"
        else
            print_warning "Docker installed but daemon not accessible"
            print_info "You may need to start Docker or add your user to docker group"
        fi
        return
    fi
    
    print_status "Installing Docker..."
    
    # Detect OS for correct repository
    if [ -f /etc/os-release ]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        OS_ID=$ID
    else
        OS_ID="ubuntu"
    fi
    
    # Remove old Docker versions if they exist
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    
    if [ "$OS_ID" = "debian" ]; then
        curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    else
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    fi
    
    # Set proper permissions on GPG key
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Install Docker
    sudo apt-get update -qq
    if sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>&1 | tee -a "$LOG_FILE"; then
        print_success "Docker packages installed"
    else
        print_error "Docker installation failed"
        return 1
    fi
    
    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker "$USER"
    
    # Create docker group if it doesn't exist
    if ! getent group docker > /dev/null 2>&1; then
        sudo groupadd docker
    fi
    
    print_success "Docker installed successfully"
    print_warning "You may need to log out and back in for docker group membership to take effect"
    print_info "Or run: newgrp docker"
    
    # Verify installation
    if sudo docker run hello-world >/dev/null 2>&1; then
        print_success "Docker is working correctly"
    else
        print_warning "Docker installed but test container failed"
    fi
}

# Function to setup npm prefix for non-sudo installs
setup_npm_prefix() {
    # Check if nvm is being used
    if [ -d "$HOME/.nvm" ]; then
        # nvm handles its own prefix, no setup needed
        return 0
    fi
    
    # Setup npm prefix to avoid sudo for global packages
    NPM_PREFIX="$HOME/.npm-global"
    
    if [ ! -d "$NPM_PREFIX" ]; then
        print_status "Setting up npm global prefix..."
        mkdir -p "$NPM_PREFIX"
        npm config set prefix "$NPM_PREFIX"
        
        # Add to PATH if not already there
        if ! echo "$PATH" | grep -q "$NPM_PREFIX/bin"; then
            echo "export PATH=$NPM_PREFIX/bin:\$PATH" >> ~/.bashrc
            export PATH="$NPM_PREFIX/bin:$PATH"
        fi
        
        print_success "npm prefix configured to $NPM_PREFIX"
    fi
}

# Function to install npm package with fallback methods
install_npm_package() {
    local package="$1"
    
    # Try without sudo first (if nvm or prefix is set)
    if npm install -g "$package" 2>&1 | tee -a "$LOG_FILE"; then
        return 0
    fi
    
    # If that failed, try with sudo
    print_status "Retrying with sudo..."
    if sudo npm install -g "$package" 2>&1 | tee -a "$LOG_FILE"; then
        return 0
    fi
    
    return 1
}

# Function to install MCP servers
install_mcp_servers() {
    print_status "Installing MCP servers..."
    
    # Check npm prefix and setup if needed
    setup_npm_prefix
    
    # Define MCP servers to install
    MCP_SERVERS=(
        "@modelcontextprotocol/server-filesystem"
        "@modelcontextprotocol/server-memory"
        "@modelcontextprotocol/server-sequential-thinking"
    )
    
    # Optional MCP servers (may fail, but that's okay)
    OPTIONAL_SERVERS=(
        "mcp-server-docker"
    )
    
    # Install core MCP servers one by one with error handling
    for server in "${MCP_SERVERS[@]}"; do
        print_status "Installing $server..."
        if install_npm_package "$server"; then
            print_success "$server installed"
        else
            print_error "Failed to install $server"
            # Continue anyway for now
        fi
    done
    
    # Install optional MCP servers (don't fail if these don't work)
    for server in "${OPTIONAL_SERVERS[@]}"; do
        print_status "Installing optional $server..."
        if install_npm_package "$server"; then
            print_success "$server installed"
        else
            print_warning "Optional $server not installed (this is okay)"
        fi
    done
    
    # Install Python based MCP server
    print_status "Installing Python MCP server..."
    
    # Try to install in venv if available
    if [ -d "$SCRIPT_DIR/venv" ]; then
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/venv/bin/activate"
        if pip install mcp-server-python-analysis 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Python MCP server installed in venv"
        else
            print_warning "Python MCP server not installed (optional)"
        fi
        deactivate
    else
        # Fallback: try user install if venv not available
        if pip3 install --user mcp-server-python-analysis 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Python MCP server installed (user)"
        elif command_exists pipx; then
            if pipx install mcp-server-python-analysis 2>&1 | tee -a "$LOG_FILE"; then
                print_success "Python MCP server installed via pipx"
            else
                print_warning "Python MCP server not installed (optional)"
            fi
        else
            print_warning "Python MCP server not installed (optional) - venv not available"
        fi
    fi
    
    print_success "MCP server installation completed"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    cd "$SCRIPT_DIR" || exit 1
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        VENV_CREATED=true
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install backend requirements
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
    fi
    
    # Install root requirements if exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    print_success "Python environment setup completed"
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image..."
    
    if ! command_exists docker; then
        print_warning "Docker not installed, skipping image build"
        return 0
    fi
    
    # Check if we can run docker without sudo
    if ! docker ps >/dev/null 2>&1; then
        print_warning "Cannot access Docker daemon. You may need to:"
        print_info "  1. Log out and back in (for docker group)"
        print_info "  2. Or run: newgrp docker"
        print_info "  3. Or run with sudo: sudo docker compose build"
        return 0
    fi
    
    # Build using docker compose
    if command_exists docker && docker compose version >/dev/null 2>&1; then
        print_status "Building with docker compose..."
        if docker compose build 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Docker image built successfully"
        else
            print_warning "Docker image build failed (you can build later with: docker compose build)"
        fi
    elif command_exists docker-compose; then
        print_status "Building with docker-compose..."
        if docker-compose build 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Docker image built successfully"
        else
            print_warning "Docker image build failed (you can build later with: docker-compose build)"
        fi
    else
        print_status "Building with docker build..."
        if docker build -t antigravity-workspace:latest . 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Docker image built successfully"
        else
            print_warning "Docker image build failed"
        fi
    fi
}

# Function to test Docker setup
test_docker_setup() {
    print_status "Testing Docker setup..."
    
    if ! command_exists docker; then
        print_info "Docker not installed, skipping test"
        return 0
    fi
    
    # Test docker command
    if docker --version >/dev/null 2>&1; then
        print_success "Docker command available: $(docker --version | cut -d' ' -f3 | tr -d ',')"
    else
        print_error "Docker command failed"
        return 1
    fi
    
    # Test docker compose
    if docker compose version >/dev/null 2>&1; then
        print_success "Docker Compose available: $(docker compose version | cut -d' ' -f4)"
    elif command_exists docker-compose; then
        print_success "Docker Compose (standalone) available: $(docker-compose --version | cut -d' ' -f4 | tr -d ',')"
    else
        print_warning "Docker Compose not available"
    fi
    
    # Test docker daemon access
    if docker ps >/dev/null 2>&1; then
        print_success "Docker daemon accessible"
    else
        print_warning "Docker daemon not accessible (may need to relogin or use: newgrp docker)"
    fi
    
    # Test if image exists
    if docker images | grep -q antigravity; then
        print_success "Antigravity Docker image found"
    else
        print_info "Antigravity Docker image not built yet (run: docker compose build)"
    fi
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    cd "$SCRIPT_DIR" || exit 1
    
    # Backup existing .env if present
    if [ -f ".env" ]; then
        BACKUP_DIR="${SCRIPT_DIR}/.backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp ".env" "$BACKUP_DIR/.env"
        CONFIG_BACKED_UP=true
        print_info "Backed up existing .env to $BACKUP_DIR"
    fi
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Created .env from .env.example. Please edit .env with your API keys."
        else
            cat > .env << 'EOF'
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Local Model Settings (if using Ollama)
LOCAL_MODEL=llama3

# GitHub Token for MCP integration
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# Optional: Brave Search API
COPILOT_MCP_BRAVE_API_KEY=

# Optional: PostgreSQL connection
COPILOT_MCP_POSTGRES_CONNECTION_STRING=

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF
            print_warning "Created .env file. Please edit it with your API keys."
        fi
    else
        print_success ".env file already exists"
    fi
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/antigravity.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Antigravity Workspace Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR/backend
Environment="PATH=$SCRIPT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$SCRIPT_DIR/.env
ExecStart=$SCRIPT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable antigravity.service
    
    print_success "Systemd service created"
}

# Function to setup nginx reverse proxy
setup_nginx() {
    print_status "Setting up Nginx reverse proxy..."
    
    NGINX_CONF="/etc/nginx/sites-available/antigravity"
    
    # Use SCRIPT_DIR instead of hardcoded paths
    sudo tee "$NGINX_CONF" > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root ${SCRIPT_DIR}/frontend;
        index index.html;
        try_files \$uri \$uri/ =404;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    # Static files
    location /static/ {
        alias ${SCRIPT_DIR}/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    sudo nginx -t
    
    # Restart nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_success "Nginx reverse proxy configured"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    if command_exists ufw; then
        sudo ufw --force enable
        sudo ufw allow 22/tcp
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 8000/tcp
        print_success "Firewall configured"
    else
        print_warning "UFW not installed, skipping firewall setup"
    fi
}

# Function to create directories
create_directories() {
    print_status "Creating required directories..."
    
    cd "$SCRIPT_DIR" || exit 1
    
    mkdir -p drop_zone
    mkdir -p artifacts
    mkdir -p logs
    mkdir -p frontend/static
    mkdir -p data
    
    print_success "Directories created"
}

# Function to run health check
run_health_check() {
    print_status "Running health check..."
    
    cd "$SCRIPT_DIR" || exit 1
    
    if [ -f "health-check.sh" ]; then
        chmod +x health-check.sh
        ./health-check.sh || true
    fi
    
    print_success "Health check completed"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    cd "$SCRIPT_DIR" || exit 1
    
    # Test critical Python imports
    print_status "Testing Python imports..."
    if [ -d "venv" ]; then
        # shellcheck source=/dev/null
        source venv/bin/activate
        
        # Robust verification script
        python3 - << 'EOF'
import sys
try:
    import fastapi
    import uvicorn
    # Use the new genai package
    from google import genai
    print("Core modules: OK")
except Exception as e:
    print(f"CRITICAL_FAIL: {e}")
    sys.exit(1)

try:
    import chromadb
    print("chromadb: OK")
except Exception as e:
    print(f"OPTIONAL_WARNING: chromadb failed to load: {e}")
    # We don't exit with 1 for chromadb to allow resilience mode
EOF
        
        if [ $? -eq 0 ]; then
            print_success "Python dependencies verified"
        else
            print_error "Python dependency verification failed"
            print_info "Try running: source venv/bin/activate && pip install -r backend/requirements.txt"
        fi
        
        # Test if backend can at least parse
        print_status "Testing backend startup..."
        if python3 -c "import sys; sys.path.insert(0, 'backend'); from main import app; print('Backend OK')" 2>&1 | tee -a "$LOG_FILE"; then
            print_success "Backend module loads successfully"
        else
            print_warning "Backend module has issues - check logs"
        fi
        
        deactivate
    else
        print_warning "Virtual environment not found - skipping Python verification"
    fi
    
    print_success "Installation verification completed"
}

# Function to display completion message
display_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║        Antigravity Workspace Installation Complete!       ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Edit .env file with your API keys:"
    echo "     nano $SCRIPT_DIR/.env"
    echo ""
    echo "  2. Start the service:"
    echo "     sudo systemctl start antigravity"
    echo ""
    echo "  3. Check service status:"
    echo "     sudo systemctl status antigravity"
    echo ""
    echo "  4. View logs:"
    echo "     sudo journalctl -u antigravity -f"
    echo ""
    echo "  5. Access the web interface:"
    echo "     http://$(hostname -I | awk '{print $1}')"
    echo ""
    print_warning "Important: After editing .env, restart the service:"
    echo "     sudo systemctl restart antigravity"
    echo ""
    echo "  Documentation: $SCRIPT_DIR/README.md"
    echo "  Log file: $LOG_FILE"
    echo ""
}

# Main installation flow
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║     Antigravity Workspace - Automated Installation        ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root. It will use sudo when needed."
        exit 1
    fi
    
    # Start logging
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    print_status "Installation started at $(date)"
    echo ""
    
    # Run installation steps
    detect_os
    check_requirements
    install_system_dependencies
    install_nodejs
    install_python
    install_docker
    create_directories
    install_mcp_servers
    setup_python_env
    setup_environment
    
    # Test Docker setup
    test_docker_setup
    
    # Build Docker image (optional, can be done later)
    if prompt_yes_no "Build Docker image now? (optional, takes a few minutes)" "n"; then
        build_docker_image
    else
        print_info "Skipping Docker image build. You can build later with: docker compose build"
    fi
    
    create_systemd_service
    
    # Optional: Setup nginx (comment out if not needed)
    if command_exists nginx; then
        setup_nginx
    else
        print_warning "Nginx not installed, skipping reverse proxy setup"
    fi
    
    # Optional: Setup firewall
    setup_firewall
    
    # Run health check
    run_health_check
    
    # Verify installation
    verify_installation
    
    # Display completion message
    display_completion
    
    print_status "Installation log saved to: $LOG_FILE"
}

# Run main installation
main "$@"
