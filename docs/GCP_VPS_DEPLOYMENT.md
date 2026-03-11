# ☁️ Google Cloud Compute Engine VPS Deployment Guide

Complete guide for deploying Antigravity Workspace on Google Cloud Compute Engine — covering two VM tiers, headless Docker deployment, Nginx reverse proxy for public web access, multi-project Git workflows, and AI tool installation.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [VM Tier Comparison](#vm-tier-comparison)
3. [VM Creation](#vm-creation)
4. [Firewall Rules](#firewall-rules)
5. [SSH Access](#ssh-access)
6. [Phase 1: Bootstrap the VPS](#phase-1-bootstrap-the-vps)
7. [Phase 2: Clone & Install Antigravity](#phase-2-clone--install-antigravity)
8. [Docker Headless Deployment](#docker-headless-deployment)
9. [Nginx Reverse Proxy & Public Access](#nginx-reverse-proxy--public-access)
10. [Multi-Project Git Workflow](#multi-project-git-workflow)
11. [AI Tools Installation](#ai-tools-installation)
12. [Optional Dependencies](#optional-dependencies)
13. [Monitoring & Maintenance](#monitoring--maintenance)
14. [Cost Optimization](#cost-optimization)
15. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Google Cloud account** with billing enabled
- ✅ **`gcloud` CLI** installed and authenticated ([install guide](https://cloud.google.com/sdk/docs/install))
- ✅ **Project set** in gcloud: `gcloud config set project YOUR_PROJECT_ID`
- ✅ **Compute Engine API enabled**: `gcloud services enable compute.googleapis.com`

```bash
# Verify gcloud setup
gcloud auth list
gcloud config get-value project
gcloud compute regions list | head -10
```

---

## VM Tier Comparison

| | 🟢 Standard Tier | 🟡 Production Tier ⭐ |
|---|---|---|
| **GCP Instance** | `e2-standard-4` | `n2-standard-8` |
| **vCPUs** | 4 | 8 |
| **RAM** | 16 GB | 32 GB |
| **Boot Disk** | 100 GB pd-ssd | 256 GB pd-ssd |
| **Cost (on-demand)** | ~$97/mo | ~$245/mo |
| **Cost (1yr CUD)** | ~$70/mo | ~$170/mo |
| **Docker Compose** | `docker-compose.gcp-standard.yml` | `docker-compose.gcp-production.yml` |
| **Services** | Backend + Frontend | All services + 2 replicas |
| **OpenCode** | ✅ | ✅ |
| **Moltis/OpenClaw** | ✅ | ✅ |
| **13–18 MCP Servers** | ⚠️ (tight) | ✅ |
| **ChromaDB + Redis** | ❌ (save RAM) | ✅ |
| **Local LLM (Ollama)** | ⚠️ (small models only) | ✅ (7B–13B models) |
| **Multiple repos** | ⚠️ (2–3 at once) | ✅ (many simultaneous) |
| **24/7 agent use** | ⚠️ (single agent) | ✅ |
| **Best for** | Dev/testing, single project | Multi-project, constant agents |

---

## VM Creation

### 🟢 Standard Tier — `e2-standard-4`

```bash
gcloud compute instances create antigravity-standard \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=enable-oslogin=true \
  --description="Antigravity Standard — e2-standard-4 4vCPU/16GB"
```

### 🟡 Production Tier — `n2-standard-8` (Recommended)

```bash
gcloud compute instances create antigravity-production \
  --zone=us-central1-a \
  --machine-type=n2-standard-8 \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=256GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=enable-oslogin=true \
  --description="Antigravity Production — n2-standard-8 8vCPU/32GB"
```

> 💡 **Zone selection tip**: Choose a zone close to you or your users. Common choices:
> - US: `us-central1-a`, `us-east1-b`, `us-west1-a`
> - EU: `europe-west1-b`, `europe-west4-a`
> - Asia: `asia-east1-a`, `asia-northeast1-a`

### Get your VM's external IP

```bash
gcloud compute instances describe antigravity-production \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### Reserve a static external IP (recommended for domains)

```bash
# Reserve static IP
gcloud compute addresses create antigravity-ip \
  --region=us-central1

# Assign to VM
gcloud compute instances delete-access-config antigravity-production \
  --access-config-name="External NAT" \
  --zone=us-central1-a

gcloud compute instances add-access-config antigravity-production \
  --access-config-name="External NAT" \
  --address=$(gcloud compute addresses describe antigravity-ip --region=us-central1 --format='get(address)') \
  --zone=us-central1-a
```

---

## Firewall Rules

```bash
# Allow HTTP, HTTPS, Backend API, Frontend, and Moltis Web UI
gcloud compute firewall-rules create allow-antigravity-web \
  --allow=tcp:80,tcp:443,tcp:8000,tcp:3000,tcp:13131 \
  --target-tags=http-server,https-server \
  --description="Antigravity + Moltis public web ports" \
  --direction=INGRESS \
  --priority=1000

# Verify firewall rules
gcloud compute firewall-rules list --filter="name:allow-antigravity"
```

> 🔒 **Security note**: The bootstrap script (`gcp-bootstrap.sh`) also configures UFW as a second layer of firewall protection on the VM itself.

---

## SSH Access

### Connect to your VM

```bash
# Using gcloud (recommended — handles OS Login & SSH keys automatically)
gcloud compute ssh antigravity-production --zone=us-central1-a

# Or with direct SSH (after adding your key)
ssh -i ~/.ssh/google_compute_engine YOUR_USERNAME@YOUR_VM_IP
```

### Set up SSH config for quick access

```bash
# Add to ~/.ssh/config on your LOCAL machine
cat >> ~/.ssh/config << 'EOF'
Host antigravity
    HostName YOUR_VM_IP
    User YOUR_USERNAME
    IdentityFile ~/.ssh/google_compute_engine
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

# Then connect with:
ssh antigravity
```

### Use tmux/screen to keep sessions alive

```bash
# Start a persistent session
tmux new-session -s main

# Detach: Ctrl+B, D
# Reattach: tmux attach -t main
```

---

## Phase 1: Bootstrap the VPS

> **Run this FIRST** on a fresh Ubuntu 24.04 GCP VM before cloning any repos or installing AI tools.

### Option A: Curl-pipeable (recommended for fresh VMs)

```bash
curl -fsSL https://raw.githubusercontent.com/AloSantana/Antigravitys/main/scripts/gcp-bootstrap.sh | bash
```

### Option B: Clone the helpers first, then run

```bash
# Clone just the bootstrap script
curl -fsSL https://raw.githubusercontent.com/AloSantana/Antigravitys/main/scripts/gcp-bootstrap.sh \
  -o gcp-bootstrap.sh
chmod +x gcp-bootstrap.sh
./gcp-bootstrap.sh
```

### What the bootstrap script does (10 phases)

| Phase | What it sets up |
|-------|----------------|
| **1** | System update/upgrade, UTC timezone, hostname, swap file (auto-sized: 4GB for ≤16GB RAM, 8GB for >16GB), sysctl performance tuning, ulimits |
| **2** | Essential packages: git, curl, jq, htop, tmux, vim, UFW, fail2ban, etc. |
| **3** | UFW firewall (22, 80, 443, 8000, 3000) + fail2ban SSH protection |
| **4** | Docker CE (from official Docker repo, not snap), Compose v2 plugin, daemon config with log rotation |
| **5** | Python 3.11+ (from deadsnakes PPA if needed), pip, venv |
| **6** | Node.js 20 LTS (from NodeSource) |
| **7** | Rust toolchain via rustup (for Moltis/OpenClaw) |
| **8** | Git config, GitHub CLI (`gh`), SSH key generation, `~/projects/` directory |
| **9** | Nginx + Certbot (for SSL) |
| **10** | Verification summary: all versions, system resources, next steps |

### After bootstrap — log out and back in

```bash
# Required for Docker group membership to take effect
exit
gcloud compute ssh antigravity-production --zone=us-central1-a

# Verify Docker works without sudo
docker run hello-world
```

---

## Phase 2: Clone & Install Antigravity

```bash
# 1. Go to projects directory (created by bootstrap)
cd ~/projects

# 2. Clone the repo (SSH — add key to GitHub first from bootstrap output)
git clone git@github.com:AloSantana/Antigravitys.git
cd Antigravitys

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API keys (GEMINI_API_KEY, COPILOT_MCP_GITHUB_TOKEN, etc.)

# 4. Run the Antigravity installer
chmod +x install.sh
./install.sh

# 5. (Optional) Install AI tools
./scripts/gcp-optional-deps.sh --opencode --moltis
```

---

## Docker Headless Deployment

All services run in Docker containers — no GUI required.

### Standard Tier (e2-standard-4)

```bash
cd ~/projects/Antigravitys

# Use the Standard tier compose file
cp templates/docker-compose.gcp-standard.yml docker-compose.gcp.yml

# Start headless (detached)
docker compose -f docker-compose.gcp.yml up -d

# Check status
docker compose -f docker-compose.gcp.yml ps
docker compose -f docker-compose.gcp.yml logs -f
```

### Production Tier (n2-standard-8)

```bash
cd ~/projects/Antigravitys

# Use the Production tier compose file
cp templates/docker-compose.gcp-production.yml docker-compose.gcp.yml

# Start headless with 2 backend replicas
docker compose -f docker-compose.gcp.yml up -d --scale backend=2

# Check status
docker compose -f docker-compose.gcp.yml ps
docker compose -f docker-compose.gcp.yml logs -f
```

### Or use the default docker-compose.yml

```bash
# Start core services only (no profiles)
docker compose up -d

# With ChromaDB for RAG
docker compose --profile with-chromadb up -d

# With Redis caching
docker compose --profile with-redis up -d

# With local Ollama
docker compose --profile with-ollama up -d

# Full ecosystem (OpenCode Hub, OpenClaw gateway, swarm tools)
docker compose --profile ecosystem up -d
```

### Common Docker management commands

```bash
# View running containers
docker ps

# View logs for a service
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend

# Update and rebuild
git pull
docker compose build
docker compose up -d

# Stop everything
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

---

## Nginx Reverse Proxy & Public Access

### Step 1: Configure Nginx

```bash
cd ~/projects/Antigravitys

# Copy the GCP reverse proxy template
sudo cp templates/nginx-gcp-reverse-proxy.conf /etc/nginx/sites-available/antigravity

# Replace placeholder domain with your actual domain or IP
sudo sed -i 's/your-domain.com/YOUR_DOMAIN_OR_IP/g' /etc/nginx/sites-available/antigravity

# Enable the site
sudo ln -sf /etc/nginx/sites-available/antigravity /etc/nginx/sites-enabled/antigravity
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 2: Get SSL Certificate (Let's Encrypt)

```bash
# Get certificate for your domain
sudo certbot --nginx \
  -d your-domain.com \
  -m your@email.com \
  --agree-tos \
  --non-interactive

# Verify auto-renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is handled by systemd timer (check with):
sudo systemctl status certbot.timer
```

### Step 3: Verify public access

```bash
# Test HTTP → HTTPS redirect
curl -I http://your-domain.com

# Test HTTPS
curl -I https://your-domain.com

# Test backend API
curl https://your-domain.com/health

# Test WebSocket (from browser console or wscat)
# wscat -c wss://your-domain.com/ws
```

### Using IP address (no domain)

If you don't have a domain, you can access via the VM's public IP:

```bash
# Edit Nginx config to use IP instead of domain
sudo sed -i 's/your-domain.com/YOUR_VM_IP/g' /etc/nginx/sites-available/antigravity

# Comment out SSL redirect and ssl_certificate lines (no SSL for bare IP)
sudo nano /etc/nginx/sites-available/antigravity
# Remove or comment the HTTPS server block, keep only HTTP

sudo nginx -t && sudo systemctl reload nginx

# Access at:
#   http://YOUR_VM_IP         — frontend
#   http://YOUR_VM_IP/api/    — backend API
#   ws://YOUR_VM_IP/ws        — WebSocket
```

---

## Multi-Project Git Workflow

### Directory structure

```
~/projects/
├── Antigravitys/          # Main Antigravity workspace
├── Moltis/                # OpenClaw/Moltis agent
├── oh-my-opencode/        # OpenCode plugin
├── Spotify-echo/          # Music project
├── Flowise/               # AI agent builder
└── [other repos]/
```

### Setting up SSH key for GitHub (one key for all repos)

```bash
# The bootstrap script already generated ~/.ssh/id_ed25519
# Add the public key to GitHub:
cat ~/.ssh/id_ed25519.pub
# Copy output → https://github.com/settings/keys → "New SSH key"

# Or authenticate via GitHub CLI
gh auth login
# Choose: GitHub.com → HTTPS or SSH → Login with browser (or paste token)

# Test GitHub connection
ssh -T git@github.com
```

### Clone many repos at once

```bash
cd ~/projects

# Clone all your repos
gh repo list AloSantana --limit 50 | awk '{print $1}' | while read repo; do
  echo "Cloning $repo..."
  gh repo clone "$repo" || true
done
```

### Working on multiple repos simultaneously (tmux)

```bash
# Create a tmux session with multiple windows
tmux new-session -s dev \; \
  new-window -n antigravity "cd ~/projects/Antigravitys && bash" \; \
  new-window -n moltis "cd ~/projects/Moltis && bash" \; \
  new-window -n opencode "cd ~/projects && opencode" \; \
  select-window -t antigravity

# Navigate: Ctrl+B, [window number or name]
```

### Git workflow for multiple remotes

```bash
# Keep a fork in sync with upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO.git
git fetch upstream
git merge upstream/main

# Quick status across all projects
for dir in ~/projects/*/; do
  echo "=== $(basename "$dir") ==="
  git -C "$dir" status -s 2>/dev/null || echo "(not a git repo)"
done
```

---

## AI Tools Installation

### OpenCode (Coding Agent)

```bash
# Install via the optional deps script
./scripts/gcp-optional-deps.sh --opencode

# Or manually
sudo npm install -g opencode-ai

# Configure (follow interactive setup)
opencode configure

# Run
opencode
```

### Moltis (Rust AI Agent)

> **Note:** `AloSantana/moltis` is a **fork of `moltis-org/moltis`** that is 13+ commits ahead, with a custom `gsd-opencode` / OpenCode skill adapter and `LOCAL_LINUX_INSTALL.md`. The upstream project is `moltis-org/moltis` — the binary is called **`moltis`** (not `openclaw`).

```bash
# Recommended — via the optional deps script (uses .deb package, falls back to install script)
./scripts/gcp-optional-deps.sh --moltis

# Or install directly via .deb (Ubuntu — cleanest method)
curl -LO https://github.com/moltis-org/moltis/releases/latest/download/moltis_amd64.deb
sudo dpkg -i moltis_amd64.deb

# Or official one-liner (installs to ~/.local/bin/moltis)
curl -fsSL https://www.moltis.org/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Verify
moltis --version

# Start (opens web UI at http://localhost:13131)
moltis

# Open firewall for Moltis web UI (remote access)
sudo ufw allow 13131/tcp comment 'Moltis Web UI'
```

**First run:** Moltis prints a setup code — open `http://localhost:13131` and enter it. Add your API keys (Gemini, OpenAI, Anthropic) in **Settings → Providers**.

**Install AloSantana's fork** (picks up gsd-opencode skill adapter; see [`LOCAL_LINUX_INSTALL.md`](https://github.com/AloSantana/moltis/blob/main/LOCAL_LINUX_INSTALL.md) in the fork for full details):
```bash
# Build from fork source (requires Rust from gcp-bootstrap.sh)
source ~/.cargo/env
cd ~/projects
git clone git@github.com:AloSantana/moltis.git
cd moltis
cargo install just
just build-release  # ~5-10 min
cp target/release/moltis ~/.local/bin/moltis
```

**Install as a systemd service:**
```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/moltis.service << 'EOF'
[Unit]
Description=Moltis AI Gateway
After=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/moltis
Restart=on-failure
RestartSec=5s
Environment=GEMINI_API_KEY=your-key-here

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now moltis
loginctl enable-linger "$USER"   # Keep running after logout
```

### Running agents as background services

```bash
# Create a systemd service for OpenCode
sudo tee /etc/systemd/system/opencode.service > /dev/null << 'EOF'
[Unit]
Description=OpenCode Coding Agent
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/Antigravitys
ExecStart=/usr/local/bin/opencode serve
Restart=always
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin:/home/YOUR_USERNAME/.cargo/bin

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable opencode
sudo systemctl start opencode
sudo systemctl status opencode
```

---

## Optional Dependencies

Install additional tools using the optional dependencies script:

```bash
cd ~/projects/Antigravitys

# Show available options
./scripts/gcp-optional-deps.sh --help

# Install AI tools (recommended)
./scripts/gcp-optional-deps.sh --opencode --moltis

# Install local LLM inference
./scripts/gcp-optional-deps.sh --ollama

# Install all TUI tools
./scripts/gcp-optional-deps.sh --lazydocker --lazygit

# Install monitoring stack (Prometheus + Grafana)
./scripts/gcp-optional-deps.sh --monitoring

# Install all MCP servers
./scripts/gcp-optional-deps.sh --mcp-servers

# Install everything
./scripts/gcp-optional-deps.sh --all
```

| Tool | Flag | Purpose |
|------|------|---------|
| MongoDB 7.x | `--mongodb` | Document database for Spotify-echo |
| Redis (standalone) | `--redis` | Caching outside Docker |
| Ollama | `--ollama` | Local LLM inference (llama3, mistral, etc.) |
| OpenCode | `--opencode` | Coding agent |
| Moltis/OpenClaw | `--moltis` | Rust-native AI agent |
| lazydocker | `--lazydocker` | Docker TUI (`lazydocker`) |
| lazygit | `--lazygit` | Git TUI (`lazygit`) |
| Monitoring | `--monitoring` | Prometheus + Grafana + cAdvisor |
| Caddy | `--caddy` | Alternative web server with auto-HTTPS |
| Cloudflare Tunnel | `--cloudflared` | Public tunnel without open ports |
| MCP Servers | `--mcp-servers` | All 13–18 MCP servers from the project |

---

## Monitoring & Maintenance

### Health checks

```bash
# Antigravity health
curl http://localhost:8000/health

# Use the built-in health check script
cd ~/projects/Antigravitys
chmod +x health-check.sh
./health-check.sh

# Docker container health
docker compose ps
docker stats --no-stream

# System resources
htop
df -h
free -h
```

### Auto-issue finder

```bash
cd ~/projects/Antigravitys

# Run diagnostic checks
python tools/auto_issue_finder.py --verbose

# Auto-fix common issues
python tools/auto_issue_finder.py --auto-fix
```

### Logs

```bash
# Antigravity systemd service (if using ./start.sh)
sudo journalctl -u antigravity -f

# Docker container logs
docker compose logs -f backend
docker compose logs -f --tail=100

# Nginx logs
sudo tail -f /var/log/nginx/antigravity-access.log
sudo tail -f /var/log/nginx/antigravity-error.log

# System logs
sudo journalctl -f
```

### Auto-restart on reboot

```bash
# Docker Compose services restart automatically (restart: always/unless-stopped)
# Ensure Docker starts on boot:
sudo systemctl enable docker

# Create systemd service for docker compose
sudo tee /etc/systemd/system/antigravity-docker.service > /dev/null << 'EOF'
[Unit]
Description=Antigravity Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/YOUR_USERNAME/projects/Antigravitys
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable antigravity-docker
```

### Update the workspace

```bash
cd ~/projects/Antigravitys

# Pull latest changes
git pull

# Rebuild and restart Docker services
docker compose build
docker compose up -d

# Update pip dependencies
source venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt
```

---

## Cost Optimization

### Sustained Use Discounts (automatic)

GCP automatically applies ~20% discount when a VM runs for >25% of the month — no action needed.

### Committed Use Discounts (manual)

```bash
# 1-year commitment — saves ~28–35% on n2-standard-8
gcloud compute commitments create antigravity-1yr \
  --plan=12-month \
  --region=us-central1 \
  --resources=vcpu=8,memory=32GB
```

| Instance | On-demand | 1-yr CUD | 3-yr CUD |
|----------|-----------|----------|----------|
| e2-standard-4 | ~$97/mo | ~$70/mo | ~$55/mo |
| n2-standard-8 | ~$245/mo | ~$170/mo | ~$125/mo |

### Schedule VM start/stop (if not 24/7)

```bash
# Stop VM at night (11 PM UTC) — saves ~50% if you work 12h/day
gcloud compute resource-policies create instance-schedule antigravity-schedule \
  --region=us-central1 \
  --vm-start-schedule="0 8 * * *" \
  --vm-stop-schedule="0 23 * * *" \
  --timezone=UTC

gcloud compute instances add-resource-policies antigravity-production \
  --resource-policies=antigravity-schedule \
  --zone=us-central1-a
```

### Use Spot VMs for development/testing (not production)

```bash
# Spot VM (up to 91% cheaper, can be preempted)
gcloud compute instances create antigravity-dev \
  --zone=us-central1-a \
  --machine-type=n2-standard-8 \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --tags=http-server,https-server
```

### Resize disk if running low

```bash
# Resize the disk (can be done online, no downtime)
gcloud compute disks resize DISK_NAME \
  --size=512GB \
  --zone=us-central1-a

# Then resize the filesystem
sudo resize2fs /dev/sda1
```

---

## Troubleshooting

> 🔍 See the full **[GCP VPS Issues section in TROUBLESHOOTING.md](../TROUBLESHOOTING.md#google-cloud-gcp-vps-issues)** for detailed solutions.

### Quick checks

```bash
# Check VM external IP
gcloud compute instances describe antigravity-production \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Check firewall rules
gcloud compute firewall-rules list

# Check VM status
gcloud compute instances list

# SSH debug
gcloud compute ssh antigravity-production --zone=us-central1-a -- -vvv
```

### Common issues

| Problem | Quick fix |
|---------|-----------|
| Can't SSH | Check firewall: `gcloud compute firewall-rules list` |
| Docker permission denied | Log out/in for docker group: `newgrp docker` |
| Nginx 502 | Check backend: `docker compose ps` + `docker compose logs backend` |
| SSL error | Run certbot: `sudo certbot --nginx -d your-domain.com` |
| Disk full | Check usage: `df -h`, clean Docker: `docker system prune -a` |
| VM slow | Check resources: `htop`, upgrade machine type or add swap |
| Quota exceeded | Check quotas: `gcloud compute project-info describe` |
