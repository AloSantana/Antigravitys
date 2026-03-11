# 🔄 Antigravity — Complete Reinstall Guide (GCP Production VM)

> **Use this guide when rebuilding from scratch or reinstalling on a fresh VM.**
> Follow each step in order. Do not skip the bootstrap phase.

---

## Table of Contents

1. [Before You Start — Checklist](#1-before-you-start--checklist)
2. [Create the GCP VM](#2-create-the-gcp-vm)
3. [Open Firewall Ports](#3-open-firewall-ports)
4. [Connect via SSH](#4-connect-via-ssh)
5. [Phase 1 — Bootstrap the VM](#5-phase-1--bootstrap-the-vm)
6. [Phase 2 — Clone & Install Antigravity](#6-phase-2--clone--install-antigravity)
7. [Phase 3 — Configure Environment Variables](#7-phase-3--configure-environment-variables)
8. [Phase 4 — Start Services with Docker](#8-phase-4--start-services-with-docker)
9. [Phase 5 — Install AI Tools (OpenCode + Moltis)](#9-phase-5--install-ai-tools-opencode--moltis)
10. [Phase 6 — Install OpenCode Plugins](#10-phase-6--install-opencode-plugins)
11. [Verify Everything Works](#11-verify-everything-works)
12. [Set Up SSH Quick Access from Your Local Machine](#12-set-up-ssh-quick-access-from-your-local-machine)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Before You Start — Checklist

Before you run a single command, make sure you have all of these:

- [ ] Google Cloud account with **billing enabled**
- [ ] `gcloud` CLI installed on your **local machine** — [install guide](https://cloud.google.com/sdk/docs/install)
- [ ] Logged in: `gcloud auth login`
- [ ] Project set: `gcloud config set project YOUR_PROJECT_ID`
- [ ] Compute Engine API enabled: `gcloud services enable compute.googleapis.com`
- [ ] Your API keys ready (at minimum: `GEMINI_API_KEY`, `GITHUB_TOKEN`)

```bash
# Verify gcloud is ready
gcloud auth list
gcloud config get-value project
```

---

## 2. Create the GCP VM

Run this **on your local machine** (not on the VM):

```bash
gcloud compute instances create antigravity-production \
  --zone=us-central1-a \
  --machine-type=n2-standard-8 \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=enable-oslogin=true \
  --description="Antigravity Production — n2-standard-8 8vCPU/32GB"
```

> ⚠️ **Disk size notes:**
> - **Always specify `--boot-disk-size`** — GCP defaults to 10 GB which is far too small.
>   Docker images, AI models, and logs will fill 10 GB within hours.
> - **200 GB** is the recommended size. If you get a quota error with 256 GB, 200 GB works.
> - To check your SSD quota:
>   ```bash
>   gcloud compute project-info describe \
>     --format="table(quotas[].metric,quotas[].limit,quotas[].usage)" \
>     | grep -i ssd
>   ```
> - To request more quota: GCP Console → IAM & Admin → Quotas.

### Get the external IP (save this — you'll need it)

```bash
gcloud compute instances list
# Look for the EXTERNAL_IP column next to antigravity-production
# It will be a numeric IP like: 104.131.108.55
```

---

## 3. Open Firewall Ports

```bash
gcloud compute firewall-rules create allow-antigravity \
  --allow=tcp:80,tcp:443,tcp:8000,tcp:3000,tcp:13131 \
  --target-tags=http-server,https-server \
  --description="Antigravity + Moltis public web ports" \
  --direction=INGRESS \
  --priority=1000

# Verify
gcloud compute firewall-rules list --filter="name:allow-antigravity"
```

---

## 4. Connect via SSH

### Option A — gcloud (recommended, handles keys automatically)

```bash
gcloud compute ssh antigravity-production --zone=us-central1-a
```

### Option B — direct SSH

```bash
# Replace EXTERNAL_IP with the numeric IP from step 2
ssh -i ~/.ssh/google_compute_engine YOUR_USERNAME@EXTERNAL_IP
```

> ❌ **"Could not resolve hostname" error?**
> This means you used a placeholder instead of the real IP.
> Replace `EXTERNAL_IP` with the actual number from `gcloud compute instances list`.

---

## 5. Phase 1 — Bootstrap the VM

> Run the following **inside the VM** (after SSH-ing in). This sets up Docker,
> Node.js, Python, Rust, Nginx, and all system dependencies.

```bash
curl -fsSL https://raw.githubusercontent.com/AloSantana/Antigravitys/main/scripts/gcp-bootstrap.sh | bash
```

The bootstrap script runs 10 phases automatically:

| Phase | What it installs |
|-------|-----------------|
| 1 | System update, timezone (UTC), swap file, sysctl tuning |
| 2 | git, curl, jq, htop, tmux, vim, fail2ban, etc. |
| 3 | UFW firewall (ports 22, 80, 443, 8000, 3000) + fail2ban |
| 4 | Docker CE + Compose v2 + log rotation |
| 5 | Python 3.11+, pip, venv |
| 6 | Node.js 20 LTS |
| 7 | Rust toolchain (for Moltis) |
| 8 | Git config, GitHub CLI, SSH key, `~/projects/` directory |
| 9 | Nginx + Certbot |
| 10 | Verification summary |

> ⏱️ This takes about 5–10 minutes.

### After bootstrap — log out and back in

Docker group membership only takes effect after a fresh login:

```bash
exit
gcloud compute ssh antigravity-production --zone=us-central1-a

# Verify Docker works without sudo
docker run hello-world
```

---

## 6. Phase 2 — Clone & Install Antigravity

```bash
# 1. Go to the projects directory (created by bootstrap)
cd ~/projects

# 2. Clone the repo via HTTPS (or SSH if you added the key to GitHub)
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

# 3. Run the Antigravity installer
chmod +x install.sh
./install.sh
```

The installer sets up the Python virtual environment and all dependencies.

---

## 7. Phase 3 — Configure Environment Variables

```bash
cd ~/projects/Antigravitys

# Copy the example env file
cp .env.example .env

# Edit it (add your API keys)
nano .env
```

### Minimum required keys

```bash
GEMINI_API_KEY=your_gemini_api_key_here       # https://aistudio.google.com/app/apikey
GITHUB_TOKEN=your_github_token_here            # https://github.com/settings/tokens
```

### Recommended additional keys

```bash
ANTHROPIC_API_KEY=                  # https://console.anthropic.com/account/keys
OPENAI_API_KEY=                     # https://platform.openai.com/api-keys
OPENROUTER_API_KEY=                 # https://openrouter.ai/keys (200+ models)
TAVILY_API_KEY=                     # https://app.tavily.com (web search for agents)
CONTEXT7_API_KEY=                   # https://context7.com (live library docs)

# Server settings for production
HOST=0.0.0.0
PORT=8000
REMOTE_ACCESS=true
EXTERNAL_HOST=YOUR_EXTERNAL_IP      # replace with the numeric IP from step 2
```

> 💾 Save with `Ctrl+O`, exit with `Ctrl+X`.

---

## 8. Phase 4 — Start Services with Docker

```bash
cd ~/projects/Antigravitys
```

### Pre-create bind-mount directories

Docker creates missing bind-mount directories as **root**, which prevents the
container's non-root `appuser` from writing to them.  Create them yourself first
so they are owned by your login account (the container's entrypoint script will
then take over ownership):

```bash
mkdir -p logs artifacts drop_zone
```

### Start core services

```bash
# Start backend + frontend (ChromaDB and Redis are optional profiles)
docker compose up -d

# Check all containers are running
docker compose ps

# Follow logs — watch for any startup errors (Ctrl+C to stop)
docker compose logs -f backend
```

> ✅ **What to expect:** The backend entrypoint script (`scripts/docker-entrypoint.sh`)
> runs briefly as root to fix ownership on the bind-mounted volumes (`logs/`,
> `artifacts/`, `drop_zone/`) and then drops to `appuser` before starting Python.
> You should **not** see any `PermissionError` lines in the logs.
> If you do, see the [Troubleshooting](#13-troubleshooting) section.

### Verify the backend is up

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

### Access from the internet

```
http://YOUR_EXTERNAL_IP:3000    — Frontend web UI
http://YOUR_EXTERNAL_IP:8000    — Backend API
http://YOUR_EXTERNAL_IP:8000/docs — API documentation
```

---

## 9. Phase 5 — Install AI Tools (OpenCode + Moltis)

Run the optional deps script to install both at once:

```bash
cd ~/projects/Antigravitys
./scripts/gcp-optional-deps.sh --opencode --moltis
```

Or install them individually:

### OpenCode

```bash
sudo npm install -g opencode-ai

# Verify
opencode --version

# Run (from the repo root so it picks up opencode.json + .env)
cd ~/projects/Antigravitys
opencode
```

### Moltis (optional Rust AI agent)

```bash
# Install via the script (tries .deb first, falls back to install script)
./scripts/gcp-optional-deps.sh --moltis

# Or manually via .deb (Ubuntu)
curl -LO https://github.com/moltis-org/moltis/releases/latest/download/moltis_amd64.deb
sudo dpkg -i moltis_amd64.deb

# Start Moltis (opens web UI at http://localhost:13131)
moltis
```

> On first launch, Moltis prints a setup code in the terminal.
> Open `http://YOUR_EXTERNAL_IP:13131` and enter the code.
> Then go to **Settings → Providers** and add your API keys.

---

## 10. Phase 6 — Install OpenCode Plugins

These plugins add multi-agent orchestration and session management to OpenCode.

```bash
# Install oh-my-opencode (Sisyphus multi-agent harness)
npm install -g oh-my-opencode
bunx oh-my-opencode install    # sets up .opencode/ directory
bunx oh-my-opencode doctor     # verify health

# Install swarm-tools (parallel agent coordination)
npm install -g opencode-swarm-plugin
swarm setup
swarm init

# Install opencode-sessions (session fork/handoff/compact)
npm install -g opencode-sessions
```

The `opencode.json` in the repo root is already pre-configured with all three plugins:

```json
"plugin": [
  "oh-my-opencode",
  "opencode-swarm-plugin",
  "opencode-sessions"
]
```

> ℹ️ **Note:** `gsd-opencode` is intentionally **not** included — it conflicts with the
> oh-my-opencode plugin when both are active at the same time.

### Launch OpenCode with all plugins

```bash
cd ~/projects/Antigravitys
opencode
# Sisyphus agent activates automatically
```

---

## 11. Verify Everything Works

Run through this checklist after completing all phases:

```bash
# 1. Backend health
curl http://localhost:8000/health

# 2. Docker containers
docker compose ps

# 3. OpenCode version
opencode --version

# 4. oh-my-opencode health
bunx oh-my-opencode doctor

# 5. Node.js + npm
node --version   # should be 20+
npm --version

# 6. Python
python3 --version   # should be 3.11+

# 7. Disk space (must not be near 100%)
df -h /
```

**Expected output summary:**

| Check | Expected |
|-------|---------|
| `curl /health` | `{"status":"healthy"}` |
| `docker compose ps` | all services `Up` |
| `opencode --version` | any version string |
| `df -h /` | less than 80% used |

---

## 12. Set Up SSH Quick Access from Your Local Machine

Do this **on your local machine** (not the VM) for convenient one-command access.

### Step 1 — Find your external IP

```bash
# From your LOCAL machine
gcloud compute instances list
# Note the EXTERNAL_IP for antigravity-production
```

### Step 2 — Add an entry to your SSH config

Open `~/.ssh/config` in a text editor and **add these lines** (replace the two
placeholder values with real ones):

```
Host antigravity
    HostName 104.131.108.55
    User YOUR_USERNAME
    IdentityFile ~/.ssh/google_compute_engine
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

> Replace `104.131.108.55` with your actual external IP.
> Replace `YOUR_USERNAME` with the username you use to SSH into GCP
> (shown in `gcloud compute instances list` or your OS Login profile).

Or use this one-liner (**replace both placeholders first**):

```bash
cat >> ~/.ssh/config << 'EOF'
Host antigravity
    HostName 104.131.108.55
    User YOUR_USERNAME
    IdentityFile ~/.ssh/google_compute_engine
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
```

### Step 3 — Connect

```bash
ssh antigravity
```

---

## 13. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `Could not resolve hostname` in SSH | Placeholder IP left in `~/.ssh/config` | Open `~/.ssh/config`, replace `HostName` value with the real numeric IP from `gcloud compute instances list` |
| `No space left on device` | Boot disk was 10 GB (GCP default) | Resize: `gcloud compute disks resize antigravity-production --size=200GB --zone=us-central1-a` then `sudo resize2fs /dev/sda1` |
| `SSD quota exceeded` when creating VM | Project quota < 256 GB | Use `--boot-disk-size=200GB` (already in the command above), or request quota increase in GCP Console → IAM → Quotas |
| `docker: Permission denied` | User not in docker group | Run `newgrp docker` or log out and back in |
| Backend returns 502 | Container not started | Run `docker compose up -d` then check `docker compose logs backend` |
| OpenCode plugins not loading | Plugin not installed or path issue | Re-run `bunx oh-my-opencode install` from the repo root |
| Moltis web UI not reachable | Port 13131 not open | `sudo ufw allow 13131/tcp` and check GCP firewall rules |
| VM slow / OOM | Not enough RAM for all services | Check `htop`, reduce services: `docker compose stop chromadb redis` |
| `PermissionError: [Errno 13] Permission denied: '/app/artifacts/code'` | `logs/` or `artifacts/` was created by root before `docker compose up` | Run `mkdir -p logs artifacts drop_zone` **before** `docker compose up` (see Phase 4). The entrypoint script auto-fixes ownership on startup. |
| `PermissionError: [Errno 13] Permission denied: 'backend'` | VectorStore path bug (fixed) — old image still running | Rebuild: `docker compose build --no-cache backend && docker compose up -d` |
| `PermissionError: [Errno 13] Permission denied: 'logs/debug.jsonl'` | DebugLogger path bug (fixed) — old image still running | Rebuild: `docker compose build --no-cache backend && docker compose up -d` |
| `artifact_manager - ERROR - Failed to initialize artifact storage` in logs | Permission denied on `/app/artifacts` subdirectories | Backend continues in degraded mode — artifact endpoints return 500. Fix: `mkdir -p logs artifacts drop_zone`, then restart: `docker compose restart backend` |

### Resize a disk that was created too small

If your VM was accidentally created with the GCP default 10 GB disk:

```bash
# On your LOCAL machine — resize the disk (no downtime)
gcloud compute disks resize antigravity-production \
  --size=200GB \
  --zone=us-central1-a

# Then inside the VM — expand the filesystem
sudo resize2fs /dev/sda1

# Verify
df -h /
```

### Full reinstall — delete and recreate the VM

If you need to start completely from scratch:

```bash
# Delete the old VM (from your local machine)
gcloud compute instances delete antigravity-production --zone=us-central1-a

# Then go back to Step 2 of this guide
```

---

*Antigravity Workspace · Reinstall Guide · Production VM*
