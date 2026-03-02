# Antigravity Workspace — Complete Setup Guide

> **Canonical reference for installing, configuring, and running the full Antigravity + OpenCode + Gemini CLI + GitHub Copilot multi-agent stack across all platforms.**

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Installation](#3-installation)
   - [Linux / macOS](#linux--macos)
   - [Windows](#windows)
   - [Docker (all platforms)](#docker-all-platforms)
4. [Environment Variables](#4-environment-variables)
5. [OpenCode Configuration](#5-opencode-configuration)
6. [Gemini CLI Configuration](#6-gemini-cli-configuration)
7. [GitHub Copilot MCP Configuration](#7-github-copilot-mcp-configuration)
8. [MCP Servers — No API Key Required](#8-mcp-servers--no-api-key-required)
9. [MCP Servers — API Key Required](#9-mcp-servers--api-key-required)
10. [Agent Configuration](#10-agent-configuration)
11. [Multi-Agent Workflow Patterns](#11-multi-agent-workflow-patterns)
12. [Antigravity Backend](#12-antigravity-backend)
13. [Health Check & Validation](#13-health-check--validation)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Overview

**Antigravity Workspace** is an AI-powered development environment that unifies:

| Component | Role |
|-----------|------|
| **FastAPI backend** (`backend/`) | REST API + WebSocket server, agent orchestration |
| **OpenCode** (`opencode.json`) | Terminal AI assistant with full MCP tool access |
| **Gemini CLI** (`~/.gemini/settings.json`) | Google Gemini in the terminal with MCP tools |
| **GitHub Copilot** (`.github/copilot/mcp.json`) | VS Code / GitHub AI with 20+ MCP tools |
| **Swarm system** (`src/`) | Router-worker multi-agent orchestration |
| **RAG pipeline** (`backend/rag/`) | ChromaDB-based vector store for context retrieval |
| **MCP servers** (18+) | Tools for search, memory, code execution, automation |

The shared MCP layer means that **every AI tool sees the same tools and memory**, enabling seamless agent-to-agent handoffs.

---

## 2. Prerequisites

### Minimum Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ | Backend server |
| Node.js | 18+ | MCP servers (npx) |
| Git | any | Version control |
| `uv` / `uvx` | any | Python-based MCP servers |

### Optional (for full stack)

| Component | Purpose |
|-----------|---------|
| Docker + Docker Compose | Containerised deployment, ChromaDB, Redis |
| Ollama | Local AI model inference |
| `opencode` CLI | Terminal AI assistant |
| `gemini` CLI | Google Gemini terminal assistant |

### Install Prerequisites

**macOS:**
```bash
brew install python node uv git
# Optional
brew install --cask docker
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install -y python3 python3-pip nodejs npm git
pip install uv
# Optional: Docker
curl -fsSL https://get.docker.com | sh
```

**Windows (PowerShell as Admin):**
```powershell
winget install Python.Python.3.12 OpenJS.NodeJS Git.Git
pip install uv
# Optional: Docker Desktop
winget install Docker.DockerDesktop
```

---

## 3. Installation

### Linux / macOS

```bash
# 1. Clone the repository
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

# 2. Run the automated installer
./install.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Section 4)

# 4. Start the workspace
./start.sh
```

The installer sets up:
- Python virtual environment + all dependencies
- Node.js MCP server packages (global or project-local)
- ChromaDB, systemd service (optional)

### Windows

```powershell
# 1. Clone the repository
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

# 2. Run the Windows installer
.\install.ps1

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env with Notepad or VS Code

# 4. Start the workspace
.\start.ps1
```

For WSL2 users, use the Linux instructions above inside the WSL2 shell.

### Docker (all platforms)

```bash
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

cp .env.example .env
# Edit .env

docker-compose up -d
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# ChromaDB: http://localhost:8001

# With local Ollama:
docker-compose --profile with-ollama up -d
```

---

## 4. Environment Variables

Copy `.env.example` to `.env` and fill in your values. The backend and all MCP tools read from `.env` automatically.

### Minimum Required

```bash
GEMINI_API_KEY=your_gemini_api_key_here   # https://aistudio.google.com/app/apikey
```

### Full Configuration

```bash
# ── AI / LLM ──────────────────────────────────────────────────────────────
GEMINI_API_KEY=                    # https://aistudio.google.com/app/apikey
GEMINI_API_KEYS=key1,key2,key3     # multiple keys for rotation (optional)
ANTHROPIC_API_KEY=                 # https://console.anthropic.com/account/keys
OPENAI_API_KEY=                    # https://platform.openai.com/api-keys
OPENROUTER_API_KEY=                # https://openrouter.ai/keys (200+ models)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # default model
ACTIVE_MODEL=auto                  # gemini | vertex | ollama | openrouter | auto

# ── Vertex AI (Google Cloud) ──────────────────────────────────────────────
VERTEX_API_KEY=
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1

# ── Search & Research ─────────────────────────────────────────────────────
TAVILY_API_KEY=                    # https://app.tavily.com
BRAVE_API_KEY=                     # https://brave.com/search/api/
EXA_API_KEY=                       # https://exa.ai/
CONTEXT7_API_KEY=                  # https://context7.com/

# ── Memory & Vector Storage ───────────────────────────────────────────────
QDRANT_URL=                        # https://cloud.qdrant.io (e.g. https://xxxx.europe-west3-0.gcp.cloud.qdrant.io)
QDRANT_API_KEY=                    # https://cloud.qdrant.io
UPSTASH_REDIS_REST_URL=            # https://console.upstash.com/redis
UPSTASH_REDIS_REST_TOKEN=          # https://console.upstash.com/redis
QSTASH_TOKEN=                      # https://console.upstash.com/qstash

# ── Automation & DevOps ───────────────────────────────────────────────────
DAYTONA_API_KEY=                   # https://app.daytona.io
DAYTONA_SERVER_URL=https://app.daytona.io/api
N8N_API_KEY=                       # https://app.n8n.cloud/
N8N_BASE_URL=                      # your n8n instance URL

# ── GitHub & Projects ─────────────────────────────────────────────────────
GITHUB_TOKEN=                      # https://github.com/settings/tokens (repo + read:org)
LINEAR_API_KEY=                    # https://linear.app/settings/api
NOTION_API_KEY=                    # https://www.notion.so/my-integrations
AGENTOPS_API_KEY=                  # https://agentops.ai/

# ── Databases ─────────────────────────────────────────────────────────────
POSTGRES_CONNECTION_STRING=        # postgresql://user:pass@host:5432/db
NEON_API_KEY=                      # https://neon.tech/

# ── Other ─────────────────────────────────────────────────────────────────
FIRECRAWL_API_KEY=                 # https://firecrawl.dev/
HOST=0.0.0.0
PORT=8000
```

---

## 5. OpenCode Configuration

OpenCode reads `opencode.json` from the project root automatically.

### Install OpenCode

```bash
# Option 1: npm
npm install -g opencode-ai

# Option 2: official install script
curl -sSfL https://opencode.ai/install | sh

# Option 3: Homebrew (macOS)
brew install sst/tap/opencode
```

### Project Config (`opencode.json`)

The `opencode.json` at the repo root is pre-configured with:

- **Providers**: Google Gemini, Anthropic, OpenAI, OpenRouter
- **Agents**: Coder (gemini-2.5-pro), Task (gemini-2.5-flash), Title (gemini-2.5-flash)
- **MCP Servers**: 30+ servers (all disabled by default — enable only what you use)
- `"permission": "allow"` — auto-approves all tool executions (YOLO mode)
- `"autoCompact": true` — automatically compacts long conversations

### Launch OpenCode

```bash
# From the project root (picks up opencode.json + .env automatically)
opencode

# Interactive commands inside OpenCode
/model gemini-2.5-pro         # switch model
/model openrouter/claude-3.5  # use OpenRouter
```

### Enabling MCP Servers in OpenCode

Edit `opencode.json`, set `"enabled": true` for the servers you want:

```json
"filesystem": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."],
  "enabled": true
}
```

**Recommended minimal set** (no API keys needed):

```json
"filesystem":          true,
"git":                 true,
"memory":              true,
"sequential-thinking": true,
"fetch":               true,
"playwright":          true
```

---

## 6. Gemini CLI Configuration

### Install Gemini CLI

```bash
npm install -g @google/generative-ai-cli
# or
npm install -g gemini-cli
```

### Configure MCP Servers

```bash
# Copy the pre-built Gemini MCP config from the repo
cp .agent/gemini_mcp_settings.json ~/.gemini/settings.json
```

Or manually create `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "enabled": true
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."],
      "enabled": true
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "enabled": true
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "enabled": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@github/mcp-server"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" },
      "enabled": true
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "@tavily/mcp"],
      "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" },
      "enabled": false
    },
    "qdrant": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "${QDRANT_URL}",
        "QDRANT_API_KEY": "${QDRANT_API_KEY}",
        "COLLECTION_NAME": "antigravity-agent-memory",
        "EMBEDDING_PROVIDER": "fastembed"
      },
      "enabled": false
    }
  }
}
```

### Launch Gemini CLI

```bash
gemini
# or use the project wrapper:
./gemini-cli.sh
```

### YOLO Mode (workspace-level)

The `.gemini/GEMINI.md` file in this repo auto-enables YOLO mode (all tool calls approved without confirmation). To use personal/global GEMINI.md:

```bash
# Copy workspace settings to global Gemini config
cp .gemini/settings.json ~/.gemini/settings.json
```

---

## 7. GitHub Copilot MCP Configuration

The `.github/copilot/mcp.json` file configures MCP tools available to GitHub Copilot in VS Code and GitHub.com.

### Current Config Location

`.github/copilot/mcp.json` — already in the repository with 20+ servers.

### Enabling Servers in Copilot

In VS Code, open the MCP configuration via Command Palette → **MCP: Configure Servers**, or directly edit `.github/copilot/mcp.json`. Set server entries to be present (Copilot reads all listed servers).

### System Prompt for Copilot

The `.github/copilot-instructions.md` file contains the Copilot system prompt. The project also has a detailed prompt in `ANTIGRAVITY_MASTER_GUIDE.md` → Section 1 that you can paste as a custom instruction in GitHub Copilot settings.

---

## 8. MCP Servers — No API Key Required

Install globally once for faster startup:

```bash
npm install -g \
  @modelcontextprotocol/server-filesystem \
  @modelcontextprotocol/server-memory \
  @modelcontextprotocol/server-sequential-thinking \
  @modelcontextprotocol/server-git \
  @modelcontextprotocol/server-github \
  @playwright/mcp \
  @narasimhaponnada/mermaid-mcp-server \
  mcp-server-docker
```

For Python-based servers:
```bash
pip install uv   # if not already installed
# uvx installs and runs Python MCP packages on-demand:
uvx mcp-server-git --help
uvx mcp-server-fetch --help
uvx mcp-server-time --help
uvx chroma-mcp --help
```

| Server | Package | What it does |
|--------|---------|-------------|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write/search workspace files |
| `git` | `uvx mcp-server-git` | Stage, commit, diff, log, branch |
| `memory` | `@modelcontextprotocol/server-memory` | In-session entity knowledge graph |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Structured multi-step reasoning |
| `fetch` | `uvx mcp-server-fetch` | HTTP GET/POST to any URL |
| `time` | `uvx mcp-server-time` | Timezone-aware timestamps |
| `sqlite` | `mcp-sqlite` | Query `data.db` directly |
| `playwright` | `@playwright/mcp` | Headless browser — scrape, test, screenshot |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | Browser automation (alternative to Playwright) |
| `mermaid` | `@narasimhaponnada/mermaid-mcp-server` | Generate architecture & flow diagrams |
| `docker` | `mcp-server-docker` | Build, run, stop containers |
| `chroma` | `uvx chroma-mcp --mode embedded` | Embedded ChromaDB vector store for local RAG |
| `python-analysis` | `uvx python-lsp-mcp` | Python code analysis and LSP features |

---

## 9. MCP Servers — API Key Required

Set the corresponding environment variables in `.env` before enabling these servers.

### Search & Research

| Server | Package | Env Var | Use case |
|--------|---------|---------|---------|
| `tavily` | `npx -y @tavily/mcp` | `TAVILY_API_KEY` | Real-time web search, news, current docs |
| `brave-search` | `npx -y @brave/brave-search-mcp-server` | `BRAVE_API_KEY` | Privacy-first web + local search |
| `exa` | `npx -y exa-mcp-server` | `EXA_API_KEY` | Neural/semantic search, full page retrieval |
| `context7` | `npx -y @upstash/context7-mcp` | `CONTEXT7_API_KEY` | Live library docs in LLM context |
| `firecrawl` | `npx -y firecrawl-mcp` | `FIRECRAWL_API_KEY` | Structured web scraping + crawling |

### Memory & Vector Storage

| Server | Package | Env Vars | Use case |
|--------|---------|---------|---------|
| `qdrant` | `uvx mcp-server-qdrant` | `QDRANT_URL`, `QDRANT_API_KEY` | Persistent semantic memory (production) |
| `upstash` | `npx -y @upstash/mcp-server` | `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `QSTASH_TOKEN` | KV state, message queues, rate limiting |

**Qdrant Setup (recommended for persistent agent memory):**
1. Create free cluster at https://cloud.qdrant.io
2. Set `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
3. Collection `antigravity-agent-memory` is auto-created on first write

### Automation & DevOps

| Server | Package | Env Vars | Use case |
|--------|---------|---------|---------|
| `daytona` | `npx -y @daytona/mcp` | `DAYTONA_API_KEY`, `DAYTONA_SERVER_URL` | Isolated dev sandbox environments |
| `n8n` | `npx -y n8n-mcp` | `N8N_API_KEY`, `N8N_BASE_URL` | Visual workflow automation |
| `agentops` | `npx -y agentops-mcp` | `AGENTOPS_API_KEY` | Agent execution tracing & observability |

### Repositories & Projects

| Server | Package | Env Var | Use case |
|--------|---------|---------|---------|
| `github` | `npx -y @modelcontextprotocol/server-github` | `GITHUB_TOKEN` | Issues, PRs, branches, file commits |
| `linear` | `npx -y linear-mcp-server` | `LINEAR_API_KEY` | Issue/project management |
| `notion` | `npx -y @notionhq/notion-mcp-server` | `NOTION_API_KEY` | Team knowledge base |
| `taskmaster-ai` | `npx -y --package=task-master-ai task-master-ai` | `GEMINI_API_KEY` | AI-driven sprint planning |

### Databases

| Server | Package | Env Var | Use case |
|--------|---------|---------|---------|
| `postgres` | `npx -y postgresql-mcp` | `POSTGRES_CONNECTION_STRING` | PostgreSQL queries |
| `neon` | `npx -y @neondatabase/mcp-server-neon` | `NEON_API_KEY` | Serverless Postgres on Neon |

### AI Model Bridges

| Server | Package | Env Var | Use case |
|--------|---------|---------|---------|
| `openrouter` | `npx -y openrouter-mcp` | `OPENROUTER_API_KEY` | Access 200+ models from one endpoint |

---

## 10. Agent Configuration

### GitHub Copilot Custom Agents (`.github/agents/`)

The workspace defines **12 specialized agents** as `.agent.md` files. Invoke them in GitHub Copilot Chat:

```
@rapid-implementer    Implement user authentication with JWT tokens
@architect            Design a microservices architecture for payments
@debug-detective      Root cause the 500 error in /api/agents/collaborate
@deep-research        Research best vector DB options for semantic search
@code-reviewer        Review the security of backend/security.py
@docs-master          Document the new /api/agents endpoints
@testing-stability-expert  Write tests for backend/agent/orchestrator.py
@performance-optimizer     Profile and optimize the RAG pipeline
@devops-infrastructure     Set up CI/CD for Docker deployment
@jules                Advanced code analysis and refactoring
```

Priority ranking: `jules` (10, highest) → `docs-master` (1, lowest)

### OpenCode Agents (in `opencode.json`)

```json
"agents": {
  "coder": { "model": "google/gemini-2.5-pro", "maxTokens": 8000 },
  "task":  { "model": "google/gemini-2.5-flash", "maxTokens": 4000 },
  "title": { "model": "google/gemini-2.5-flash", "maxTokens": 80 }
}
```

Override per-session inside OpenCode:
```
/model gemini-2.5-pro
/model openrouter/anthropic/claude-3.5-sonnet
```

### Swarm Orchestrator (Python API)

The backend exposes a swarm API for programmatic multi-agent orchestration:

```python
import asyncio
from src.swarm import SwarmOrchestrator

async def main():
    swarm = SwarmOrchestrator()
    result = await swarm.run(
        task="Implement a rate limiter for the /api/chat endpoint",
        workers=["coder", "reviewer"],
        router_model="gemini-2.5-flash"
    )
    print(result)

asyncio.run(main())
```

Or via REST API:
```bash
curl -X POST http://localhost:8000/api/agents/collaborate \
  -H "Content-Type: application/json" \
  -d '{"agents": ["coder", "reviewer"], "task": "Review security of backend/security.py"}'
```

---

## 11. Multi-Agent Workflow Patterns

### 1. Deep Research → Implement → Review (recommended for new features)

```
tavily / exa    ← research current art and libraries
context7        ← fetch live library API docs
Coder Agent     ← implement the feature
Reviewer Agent  ← security + quality audit
qdrant          ← store findings in antigravity-agent-memory
```

**OpenCode / Gemini CLI command sequence:**
```
search for best practices for implementing rate limiting in FastAPI using Tavily
use Context7 to get the latest slowapi documentation
implement the rate limiter in backend/main.py following those patterns
review the implementation for security issues
```

### 2. Multi-Session Memory Pattern

```python
# Store insight after each agent run (in any Python context)
# Requires: QDRANT_URL and QDRANT_API_KEY set in .env
from qdrant_client import QdrantClient

client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
client.upsert(
    collection_name="antigravity-agent-memory",
    points=[{
        "id": session_id,
        "vector": embed(result_text),
        "payload": {"task": task, "output": result, "timestamp": now()}
    }]
)
# Next session: retrieve relevant context
context = client.search(
    collection_name="antigravity-agent-memory",
    query_vector=embed(current_task),
    limit=5
)
```

### 3. Async Task Queue (n8n + Upstash QStash)

```
Agent → QStash.publish(task) → n8n webhook trigger → n8n workflow
      → result stored in Upstash Redis → Agent.poll_result()
```

### 4. Daytona Sandbox Pattern (risky / long-running operations)

```
1. create_sandbox(DAYTONA_API_KEY)  → sandbox_id
2. run_code(sandbox_id, command)    → stdout / stderr
3. fetch_artifacts(sandbox_id)      → result files
4. destroy_sandbox(sandbox_id)
```

### 5. Drop Zone → RAG → Chat

1. Drop any file into `drop_zone/` (the watcher auto-ingests it into ChromaDB)
2. Ask questions in the Antigravity chat interface at `http://localhost:8000`
3. The RAG pipeline retrieves relevant chunks and enriches the LLM context

---

## 12. Antigravity Backend

### Start Backend

```bash
# Development (auto-reload)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or via start script
./start.sh

# Windows
.\start.ps1
```

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend UI |
| `/health` | GET | Service health check |
| `/api/chat` | POST | Chat with AI agent |
| `/api/agents/collaborate` | POST | Multi-agent collaboration |
| `/api/agents/handoff` | POST | Record agent handoff with shared context |
| `/ws` | WS | WebSocket for real-time chat |
| `/performance/metrics` | GET | Performance metrics dashboard |
| `/performance/analysis` | GET | AI-powered performance analysis |
| `/docs` | GET | Auto-generated API docs (Swagger UI) |

### Model Selection

The backend automatically selects models via the orchestrator priority chain:
```
Gemini (GEMINI_API_KEY) → Vertex AI (VERTEX_API_KEY) → Ollama (local) → OpenRouter
```

Control via `ACTIVE_MODEL` in `.env`:
- `auto` — smart selection based on complexity
- `gemini` — force Gemini
- `vertex` — force Vertex AI
- `ollama` — local model with cloud fallback
- `openrouter` — always use OpenRouter

---

## 13. Health Check & Validation

```bash
# Full health check
./health-check.sh

# Configuration validation
./validate.sh

# Run the test suite
pytest tests/ -v

# Test specific areas
pytest tests/unit/ -v
pytest -m "not requires_ollama" -v   # skip Ollama-dependent tests

# Check API health
curl http://localhost:8000/health
```

### Manual MCP Server Test

```bash
# Test that npx-based servers work
npx -y @modelcontextprotocol/server-filesystem . --dry-run 2>&1 | head -5

# Test uvx-based servers
uvx mcp-server-fetch --help 2>&1 | head -5
uvx mcp-server-git --help 2>&1 | head -5
```

---

## 14. Troubleshooting

### OpenCode doesn't load MCP servers

1. Verify `opencode.json` is in the project root
2. Check that `"enabled": true` is set for the servers you want
3. Ensure the required npm/uvx packages are installed
4. Look at OpenCode logs: `opencode --debug`

### Windows: `uvx` not found

```powershell
pip install uv
# Restart shell, then verify:
uvx --version
```

### Git MCP server fails

```bash
# Use npx version instead of uvx
# In opencode.json / gemini settings, change:
"command": ["uvx", "mcp-server-git", ...]
# to:
"command": ["npx", "-y", "@modelcontextprotocol/server-git", ...]
```

### Qdrant connection fails

1. Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
2. Verify the cluster is running at https://cloud.qdrant.io/
3. Test manually:
```bash
uvx mcp-server-qdrant --help
curl -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections"
```

### Port 8000 already in use

```bash
lsof -i :8000          # find the process
kill <PID>             # stop it
# or change port: PORT=8001 ./start.sh
```

### Backend: Module not found

```bash
# Always run from the backend/ directory
cd backend && python main.py
# OR ensure the virtual environment is activated
source venv/bin/activate
```

### Ollama models not loading

```bash
# Check Ollama is running
ollama list
# Pull required model
ollama pull llama3
# If using Docker:
docker exec ollama ollama pull llama3
```

---

## Quick Reference

### Minimal Setup (5 minutes)

```bash
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys
cp .env.example .env
# Set GEMINI_API_KEY in .env
./start.sh
# Open: http://localhost:8000
```

### Full Stack (30 minutes)

```bash
# 1. Set all API keys in .env
# 2. Enable MCP servers in opencode.json (set "enabled": true)
# 3. Copy Gemini settings
cp .agent/gemini_mcp_settings.json ~/.gemini/settings.json
# 4. Start
docker-compose up -d
opencode   # or: gemini
```

### Config File Summary

| File | Tool | Notes |
|------|------|-------|
| `opencode.json` | OpenCode | Project-local; auto-loaded from repo root |
| `.github/copilot/mcp.json` | GitHub Copilot | MCP servers for Copilot in VS Code |
| `~/.gemini/settings.json` | Gemini CLI | User-global; copy from `.agent/gemini_mcp_settings.json` |
| `.env` | All tools | API keys; never commit this file |
| `.agent/mcp_config.json` | Antigravity agents | MCP config for backend agent system |

---

*Antigravity Workspace · Complete Setup Guide · Updated March 2026*
