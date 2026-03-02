# Remote VPS Deployment Guide

A comprehensive guide for deploying Antigravity Workspace on a remote Ubuntu VPS via SSH.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [One-Command Installation](#one-command-installation)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Accessing Your Workspace](#accessing-your-workspace)
- [Security Hardening](#security-hardening)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## Quick Start

The fastest way to deploy on a remote Ubuntu VPS:

> ⚠️ **Security Note**: Piping a remote script directly into bash executes it without inspection. Use the safer method below to download and review the script first.

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Safer: download and inspect the script before executing
curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh -o install-remote.sh
less install-remote.sh   # review before running
bash install-remote.sh
```

This will:
- ✅ Install all system dependencies
- ✅ Setup Node.js and Python environments  
- ✅ Configure firewall rules
- ✅ Setup nginx reverse proxy
- ✅ Configure remote access automatically
- ✅ Optionally setup SSL with Let's Encrypt

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 10GB free space minimum
- **CPU**: 2 cores minimum
- **Network**: Public IP address

### Required Access

- SSH access to the VPS
- sudo privileges
- Ports 80, 443, 3000, 8000 available

### Optional but Recommended

- Domain name pointing to your VPS
- SSL certificate (can be auto-generated with Let's Encrypt)

## One-Command Installation

### Step 1: Connect to Your VPS

```bash
ssh user@your-vps-ip
```

### Step 2: Run Remote Installer

```bash
# Safer: download and inspect the script before executing
curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh -o install-remote.sh
less install-remote.sh   # review before running
bash install-remote.sh
```

### Step 3: Follow Prompts

The installer will ask you:
1. **VPS IP/Domain**: Enter your public IP or domain name
2. **SSL Setup**: Whether to setup SSL with Let's Encrypt (requires domain)
3. **Email**: Your email for SSL certificate notifications

### Step 4: Configure API Keys

After installation, edit `.env`:

```bash
cd antigravity-workspace-template
nano .env
```

Add your API keys:
```bash
GEMINI_API_KEY=your_actual_key_here
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here
```

### Step 5: Start the Workspace

```bash
./start.sh
```

That's it! Your workspace is now accessible at `http://your-vps-ip`

## Manual Installation

If you prefer manual installation or the one-command installer fails:

### 1. Clone Repository

```bash
# Clone to your home directory
cd ~
git clone https://github.com/primoscope/antigravity-workspace-template.git
cd antigravity-workspace-template
```

### 2. Run Standard Install

```bash
./install.sh
```

This installs:
- Python 3.11+
- Node.js 20+
- Docker (optional)
- MCP servers
- Python dependencies

### 3. Configure for Remote Access

Edit `.env` file:

```bash
cp .env.example .env
nano .env
```

Set these variables for remote access:

```bash
# Enable remote access
REMOTE_ACCESS=true

# Your VPS IP or domain
EXTERNAL_HOST=123.456.789.0  # or yourdomain.com

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=8000

# Server binding
HOST=0.0.0.0
PORT=8000

# CORS origins (include your external host)
ALLOWED_ORIGINS=http://123.456.789.0:3000,http://123.456.789.0:8000,https://123.456.789.0
```

### 4. Configure Firewall

```bash
# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend port
sudo ufw allow 8000/tcp

# Allow frontend port (if using separate server)
sudo ufw allow 3000/tcp

# Enable firewall
sudo ufw enable
```

### 5. Setup Nginx (Optional but Recommended)

```bash
# Install nginx
sudo apt-get install -y nginx

# Copy configuration template
sudo cp nginx/antigravity.conf /etc/nginx/sites-available/antigravity

# Replace placeholder with your host
sudo sed -i 's/{{EXTERNAL_HOST}}/your-vps-ip/g' /etc/nginx/sites-available/antigravity

# Enable site
sudo ln -s /etc/nginx/sites-available/antigravity /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 6. Start the Workspace

```bash
# Start services
./start.sh

# Check status
sudo systemctl status antigravity

# View logs
sudo journalctl -u antigravity -f
```

## Configuration

### Environment Variables

Key configuration variables for remote deployment:

```bash
# === Remote Access Configuration ===
REMOTE_ACCESS=true              # Enable remote mode
EXTERNAL_HOST=your-vps-ip       # Your public IP or domain
FRONTEND_PORT=3000              # Frontend server port
BACKEND_PORT=8000               # Backend API port

# === Server Configuration ===
HOST=0.0.0.0                    # Listen on all interfaces
PORT=8000                       # Backend port

# === Security ===
ALLOWED_ORIGINS=*               # Or specific origins
MAX_FILE_SIZE=10485760          # 10MB upload limit
MAX_MESSAGE_LENGTH=10000        # Max message length

# === SSL (Optional) ===
SSL_ENABLED=false               # Enable for HTTPS
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Using Configuration Wizard

For guided configuration:

```bash
./configure.sh
```

This wizard will help you set up:
- AI model API keys
- GitHub integration
- Remote access settings
- Optional services

## Accessing Your Workspace

Once installed and running:

### Web Interface

```
http://your-vps-ip          # Main interface (via nginx)
http://your-vps-ip:8000     # Direct backend access
```

### API Documentation

```
http://your-vps-ip/docs     # Interactive API docs (Swagger)
http://your-vps-ip/health   # Health check endpoint
```

### WebSocket Connection

The frontend automatically detects and connects to:
```
ws://your-vps-ip:8000/ws    # WebSocket endpoint
```

## Security Hardening

### 1. Setup SSH Key Authentication

```bash
# On your local machine
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id user@your-vps-ip

# On VPS: Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

### 2. Change Default SSH Port

```bash
sudo nano /etc/ssh/sshd_config
# Change: Port 22 to Port 2222
sudo systemctl restart sshd

# Update firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp
```

### 3. Setup Fail2Ban

```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Restrict CORS Origins

In production, don't use wildcard. Edit `.env`:

```bash
# Instead of:
ALLOWED_ORIGINS=*

# Use specific origins:
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Enable Rate Limiting

The application includes built-in rate limiting. To adjust:

Edit `backend/main.py` and modify:
```python
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
```

## SSL/HTTPS Setup

### Automatic Setup with Let's Encrypt

If you ran the remote installer and chose SSL setup, it's already configured.

To manually setup:

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

### Manual SSL Configuration

If you have your own certificates:

1. **Update .env**:
```bash
SSL_ENABLED=true
SSL_CERT_PATH=/path/to/fullchain.pem
SSL_KEY_PATH=/path/to/privkey.pem
```

2. **Update nginx configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

3. **Restart services**:
```bash
sudo systemctl restart nginx
./stop.sh && ./start.sh
```

## Troubleshooting

### Connection Refused

**Symptom**: Cannot connect to VPS

**Solutions**:
```bash
# Check if service is running
sudo systemctl status antigravity

# Check if port is listening
sudo netstat -tlnp | grep 8000

# Check firewall
sudo ufw status

# Check nginx
sudo systemctl status nginx
sudo nginx -t
```

### CORS Errors in Browser

**Symptom**: Browser console shows CORS errors

**Solutions**:
```bash
# Check .env configuration
cat .env | grep ALLOWED_ORIGINS

# Ensure EXTERNAL_HOST matches your actual IP/domain
cat .env | grep EXTERNAL_HOST

# Restart services
./stop.sh && ./start.sh
```

### WebSocket Connection Failed

**Symptom**: Frontend shows "Offline" status

**Solutions**:
```bash
# Check backend logs
sudo journalctl -u antigravity -n 50

# Test WebSocket manually
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws

# Check nginx WebSocket configuration
sudo nginx -T | grep -A 10 "location /ws"
```

### Node.js Installation Failed

**Symptom**: MCP servers not installed

**Solutions**:
```bash
# The installer tries nvm as fallback
# Manually install with nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Install MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
# ... etc
```

### Service Won't Start

**Symptom**: `./start.sh` fails or service crashes

**Solutions**:
```bash
# Check logs
cat logs/backend.log
sudo journalctl -u antigravity -n 100

# Validate environment
./validate.sh

# Check Python dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Try running directly
cd backend
python main.py
```

### High Memory Usage

**Symptom**: VPS running out of memory

**Solutions**:
```bash
# Check memory usage
free -h
htop

# Reduce workers in backend/main.py
# Add to bottom:
# uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Performance Optimization

### 1. Enable Caching

The application has built-in caching. Tune in `.env`:

```bash
# Response cache TTL (seconds)
CACHE_TTL_SECONDS=300

# Max cached responses
CACHE_MAX_SIZE=100

# Vector query cache
VECTOR_QUERY_CACHE_TTL=60
VECTOR_QUERY_CACHE_SIZE=50
```

### 2. Setup Redis (Optional)

For better caching performance:

```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis in .env
REDIS_URL=redis://localhost:6379
```

### 3. Optimize Nginx

Edit `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Enable gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    
    # Connection pooling
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

### 4. Monitor Resources

Use the built-in performance endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/performance/metrics

# Detailed analysis
curl http://localhost:8000/performance/analysis
```

### 5. Database Optimization

If using the vector database heavily:

```bash
# In .env, tune RAG settings
RAG_MAX_CHUNK_SIZE=2000
RAG_CHUNK_OVERLAP=200
RAG_BATCH_SIZE=5
RAG_MAX_CONCURRENT_EMBEDDINGS=10
```

## Monitoring

### Setup Monitoring

1. **System Monitoring with htop**:
```bash
sudo apt-get install -y htop
htop
```

2. **Service Logs**:
```bash
# Real-time logs
sudo journalctl -u antigravity -f

# Last 100 lines
sudo journalctl -u antigravity -n 100

# Logs from today
sudo journalctl -u antigravity --since today
```

3. **Nginx Logs**:
```bash
# Access logs
sudo tail -f /var/log/nginx/antigravity_access.log

# Error logs
sudo tail -f /var/log/nginx/antigravity_error.log
```

4. **Application Logs**:
```bash
tail -f logs/backend.log
```

## Backup and Restore

### Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup important data
tar -czf ~/backups/antigravity-$(date +%Y%m%d).tar.gz \
  ~/antigravity-workspace-template/.env \
  ~/antigravity-workspace-template/drop_zone \
  ~/antigravity-workspace-template/data.db \
  ~/antigravity-workspace-template/logs

# Copy to local machine
scp user@your-vps-ip:~/backups/antigravity-*.tar.gz ./
```

### Restore

```bash
# Extract backup
tar -xzf antigravity-20240206.tar.gz -C ~/antigravity-workspace-template

# Restart services
cd ~/antigravity-workspace-template
./stop.sh && ./start.sh
```

## Updates

### Update to Latest Version

```bash
cd ~/antigravity-workspace-template

# Backup first
tar -czf ~/backup-before-update.tar.gz .env drop_zone data.db

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Update MCP servers (optional)
./install.sh --update-mcp

# Restart
./stop.sh && ./start.sh
```

## Support

### Getting Help

- **GitHub Issues**: https://github.com/primoscope/antigravity-workspace-template/issues
- **Discussions**: https://github.com/primoscope/antigravity-workspace-template/discussions
- **Documentation**: See other files in `docs/`

### Common Commands Reference

```bash
# Start
./start.sh

# Stop
./stop.sh

# Restart
./stop.sh && ./start.sh

# Status
sudo systemctl status antigravity

# Logs
sudo journalctl -u antigravity -f

# Validate
./validate.sh

# Reconfigure
./configure.sh

# Health check
./health-check.sh
```

---

## Next Steps

After successful deployment:

1. **Configure API Keys**: Add your Gemini AI and GitHub tokens
2. **Explore the Interface**: Visit http://your-vps-ip
3. **Try the Agents**: Use the specialized AI agents for your tasks
4. **Read the Examples**: Check out `docs/EXAMPLES.md`
5. **Setup SSL**: Secure your deployment with HTTPS
6. **Monitor Performance**: Use the built-in performance endpoints

Happy developing! 🚀
