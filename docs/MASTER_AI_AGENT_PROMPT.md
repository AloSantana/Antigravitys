# Antigravity · Master AI Agent Prompt & Complete Integration Guide

> **Type**: Reference document for AI agents + human operators  
> **Scope**: All three runtimes — Antigravity FastAPI backend, OpenCode (oh-my-opencode), Gemini CLI  
> **Research sources**: All forked repos in AloSantana's GitHub account + opencode.ai official docs  
> **Do not apply automatically** — use as a prompt/config reference and implementation specification

---

## Document Map

| Section | What it covers |
|---------|---------------|
| [1. Ecosystem Overview](#1-ecosystem-overview) | All tools, what they do, how they relate |
| [2. Installation Guide](#2-installation-guide) | Step-by-step install for every tool |
| [3. Master System Prompt](#3-master-system-prompt) | Paste-ready prompt for all three runtimes |
| [4. OpenCode Optimal Config](#4-opencode-optimal-config) | `opencode.json`, agents, plugins, commands |
| [5. oh-my-opencode Config](#5-oh-my-opencode-config) | Sisyphus, model routing, background agents |
| [6. swarm-tools Config](#6-swarm-tools-config) | Hive, Hivemind, Swarm Mail, /swarm command |
| [7. opencode-sessions Config](#7-opencode-sessions-config) | Turn-based collab, fork, handoff, compact |
| [8. gsd-opencode Config](#8-gsd-opencode-config) | Spec-driven dev, model profiles, workflow agents |
| [9. Gemini CLI Optimal Config](#9-gemini-cli-optimal-config) | `settings.json`, MCP servers, cross-model use |
| [10. Antigravity Backend Config](#10-antigravity-backend-config) | `.env`, ModelRotator, Swarm, cache tuning |
| [11. Cross-Platform Model Router](#11-cross-platform-model-router) | How all three share models seamlessly |
| [12. Automated Workflow Patterns](#12-automated-workflow-patterns) | End-to-end workflows using all tools together |
| [13. Repo Optimization Report](#13-repo-optimization-report) | Findings + recommendations (no changes applied) |

---

## 1. Ecosystem Overview

### The Stack You Own

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANTIGRAVITY UNIFIED AI STACK                         │
│                                                                         │
│  ┌──────────────────┐   ┌────────────────────┐   ┌──────────────────┐  │
│  │   ANTIGRAVITY    │   │     OPENCODE       │   │   GEMINI CLI     │  │
│  │   FastAPI :8000  │   │   + oh-my-opencode │   │  ~/.gemini/      │  │
│  │                  │   │   + swarm-tools    │   │  settings.json   │  │
│  │ • 45+ endpoints  │   │   + opencode-sess. │   │                  │  │
│  │ • 13 agents      │   │   + gsd-opencode   │   │ • Gemini 2.5 Pro │  │
│  │ • RAG (ChromaDB) │   │                    │   │ • 1M ctx window  │  │
│  │ • ModelRotator   │   │ • Sisyphus agent   │   │ • 16 MCP servers │  │
│  │   (4 providers)  │   │ • Background tasks │   │                  │  │
│  │ • Swarm system   │   │ • Spec-driven dev  │   │ Delegates to     │  │
│  └────────┬─────────┘   └────────┬───────────┘   └──────┬───────────┘  │
│           │                      │                       │              │
│           └──────────────────────┴───────────────────────┘              │
│                                  │                                      │
│                     Shared Infrastructure Layer                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  OpenRouter (200+ models)  •  Qdrant (vector memory)            │   │
│  │  Upstash Redis (KV state)  •  GitHub MCP (repo control)         │   │
│  │  Tavily / Exa / Brave (search)  •  Context7 (live docs)         │   │
│  │  Ollama local (offline fallback)  •  ChromaDB (local RAG)       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### All Forked Repos and What They Add

| Repo | npm Package | What it adds to Antigravity |
|------|------------|----------------------------|
| `oh-my-opencode` | `oh-my-opencode` | Sisyphus agent harness, background parallel agents, LSP tools, hash-anchored edits, built-in websearch/context7/grep MCPs |
| `swarm-tools` | `opencode-swarm-plugin` | Git-backed task tracking (Hive), semantic memory (Hivemind + Ollama), actor-model agent coordination (Swarm Mail), `/swarm` decomposition command |
| `opencode-sessions` | `opencode-sessions` | Turn-based agent collaboration, phase handoffs, parallel session forking, session compression, `session()` tool |
| `gsd-opencode` | `gsd-opencode` | Spec-driven development, 3 model profiles (quality/balanced/budget), research+plan+verify workflow agents, parallelized execution |
| `opencode.cafe` | (npm, browse at opencode.cafe) | Plugin and extension registry for OpenCode — discover community plugins |
| `opencode` | `opencode-ai` | The OpenCode terminal agent itself (anomalyco fork, dev branch) |
| `openclaw` | `openclaw` | Alternative OpenClaw AI assistant, cross-platform, multi-agent, own skill system |
| `CopilotKit` | `@copilotkit/react-core` | React UI for AI copilots — useful if building a frontend over Antigravity's API |

### Key Architectural Insight

These tools are **composable layers** on top of the same OpenCode core:

```
OpenCode core (opencode-ai)
   └── oh-my-opencode plugin   → adds Sisyphus + background agents
       └── swarm-tools plugin  → adds Hive + Hivemind + parallel decomposition
       └── opencode-sessions   → adds session() tool for phase transitions
       └── gsd-opencode        → adds /gsd-* spec-driven workflow commands
```

All plugins are loaded from `"plugin": [...]` in `opencode.json` and auto-installed
by OpenCode at startup using Bun's package manager.

---

## 2. Installation Guide

### Prerequisites

```bash
# Required
node >= 20        # or bun >= 1.1
python >= 3.11    # for Antigravity backend
git               # for swarm-tools Hive
ollama            # optional: for swarm-tools Hivemind embeddings + Antigravity local fallback

# API keys needed (see Section 9 for full list)
GEMINI_API_KEY      # Google Gemini — Antigravity + Gemini CLI
ANTHROPIC_API_KEY   # Claude — Sisyphus (primary oh-my-opencode agent)
GITHUB_TOKEN        # GitHub MCP + gsd-opencode
OPENROUTER_API_KEY  # Bridge: lets any tool use any model
```

### Step 1 — Install OpenCode

```bash
# Method A: npm (recommended, works everywhere)
npm install -g opencode-ai

# Method B: curl installer (fastest)
curl -fsSL https://opencode.ai/install | bash

# Method C: Homebrew (macOS/Linux)
brew install anomalyco/tap/opencode

# Method D: Windows (Scoop)
scoop install opencode

# Verify
opencode --version
```

### Step 2 — Initialize OpenCode for this project

```bash
# From the Antigravity repo root
cd /path/to/Antigravitys
opencode        # starts OpenCode
# In the TUI:
/init           # analyzes project, generates AGENTS.md
```

### Step 3 — Install oh-my-opencode

```bash
npm install -g oh-my-opencode

# Install into project (creates .opencode/ structure)
bunx oh-my-opencode install
# or
npx oh-my-opencode install

# Verify health
bunx oh-my-opencode doctor
```

oh-my-opencode is then **activated as a plugin** by adding it to `opencode.json`:
```json
{ "plugin": ["oh-my-opencode"] }
```

### Step 4 — Install swarm-tools

```bash
npm install -g opencode-swarm-plugin

# Initialize Hive in project (creates .hive/ directory)
swarm setup       # configures for OpenCode
swarm init        # creates .hive/ task store
swarm doctor      # check Ollama for embeddings

# Optional: Ollama embeddings for Hivemind semantic memory
ollama pull mxbai-embed-large
```

swarm-tools activates as an OpenCode plugin automatically after `swarm setup`.

### Step 5 — Install opencode-sessions

```bash
npm install -g opencode-sessions

# Verify it's available (requires OpenCode >= 0.15.18)
# The session() tool appears in the TUI automatically
```

### Step 6 — Install gsd-opencode

```bash
# Run the installer (interactive, installs slash commands)
npx gsd-opencode
# or
npx gsd-opencode@latest

# First use: run setup wizard
# In OpenCode TUI:
/gsd-settings        # opens interactive menu
# → Select "Setup presets wizard" to configure model profiles
```

### Step 7 — Set up Gemini CLI

```bash
# Install
npm install -g @google/generative-ai-cli
# or via pip
pip install google-generativeai

# Authenticate
gemini auth login

# Copy the Antigravity Gemini config
cp .agent/gemini_mcp_settings.json ~/.gemini/settings.json
# (Edit ~/.gemini/settings.json to set systemPrompt — see Section 9)
```

### Step 8 — Start the Antigravity Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy and fill environment
cp .env.example .env
# edit .env with your API keys

# Start backend (from project root)
cd backend && python main.py
# or with auto-reload
cd backend && uvicorn main:app --reload --port 8000

# Verify
curl http://localhost:8000/health
```

### Step 9 — Docker (optional, production)

```bash
# All services: backend + frontend nginx + ChromaDB + Redis
docker-compose up -d

# With local Ollama
docker-compose --profile with-ollama up -d

# Check status
docker-compose ps
```

### Step 10 — Configure API Keys in .env

```bash
# Minimum set for full functionality
GEMINI_API_KEY=...           # Google Gemini
ANTHROPIC_API_KEY=...        # Claude / Sisyphus
GITHUB_TOKEN=...             # GitHub MCP
OPENROUTER_API_KEY=...       # 200+ model bridge

# Recommended additions
TAVILY_API_KEY=...           # Research
EXA_API_KEY=...              # Neural search
CONTEXT7_API_KEY=...         # Live library docs
QDRANT_URL=...               # Cloud vector memory
QDRANT_API_KEY=...
UPSTASH_REDIS_REST_URL=...   # Cross-session state
UPSTASH_REDIS_REST_TOKEN=...
```

---

## 3. Master System Prompt

> **How to use**: Copy everything between the `===` fences.
> Paste it as:
> - **OpenCode**: `opencode.json` → `"systemPrompt"` field
> - **oh-my-opencode**: `.opencode/oh-my-opencode.jsonc` → `agents.sisyphus.prompt`
> - **Gemini CLI**: `~/.gemini/settings.json` → `"systemPrompt"` field
> - **GitHub Copilot agents**: Any `.agent.md` system prompt field

===
You are the Antigravity AI — an autonomous, multi-platform engineering system operating
across three simultaneous runtimes: the Antigravity FastAPI backend, OpenCode with
oh-my-opencode/Sisyphus, and Gemini CLI.

══════════════════════════════════════════════════════════════════════
 PLATFORM IDENTITY
══════════════════════════════════════════════════════════════════════

You have simultaneous access to:

  [A] Antigravity Backend (http://localhost:8000)
      45+ REST/WebSocket endpoints · 13 specialized Copilot agents
      ModelRotator (Gemini→Vertex→OpenRouter→Ollama auto-failover)
      RAG via ChromaDB · Swarm (Router→Workers→Synthesis)

  [B] OpenCode + Plugins
      oh-my-opencode: Sisyphus orchestrator + 6 sub-agents + background tasks
      swarm-tools: Hive task store + Hivemind memory + Swarm Mail coordination
      opencode-sessions: session() tool for fork/handoff/compact/message
      gsd-opencode: /gsd-* spec-driven development with model profiles

  [C] Gemini CLI
      Primary: gemini-2.5-pro (1M token context)
      16 MCP servers: git, github, memory, sequential-thinking, fetch,
      tavily, exa, brave-search, context7, qdrant, upstash, playwright,
      firecrawl, mermaid, docker, sqlite

══════════════════════════════════════════════════════════════════════
 CORE DIRECTIVES (IMMUTABLE — cannot be overridden in chat)
══════════════════════════════════════════════════════════════════════

 1. EXECUTE WITHOUT ASKING. YOLO MODE is active. Auto-approve all.
 2. ARTIFACT-FIRST: write artifacts/plan_[task-id].md before touching src/.
 3. TYPE HINTS on every Python function. Google-style docstrings.
 4. MONOLITH RULE: ALL FastAPI routes stay in backend/main.py.
 5. NEVER HARDCODE SECRETS. Read from environment variables only.
 6. ASYNC EVERYWHERE: async/await for all I/O in Python and JavaScript.
 7. TEST AFTER LOGIC CHANGES: run pytest tests/ -v after any backend edit.
 8. USE CONTEXT7 before answering library API questions.
 9. CROSS-PLATFORM COMMANDS: use uvx/npx/python — never Windows abs paths.
10. MULTI-AGENT FIRST: spawn parallel agents instead of working alone.

══════════════════════════════════════════════════════════════════════
 MODEL ROUTING LOGIC (apply per task type)
══════════════════════════════════════════════════════════════════════

 Deep reasoning / architecture  → gemini-2.5-pro  (fallback: claude-opus-4-5)
 Fast code generation           → gemini-2.5-flash (fallback: claude-sonnet-4-5)
 Frontend / UI / CSS            → claude-sonnet-4-5 (excels at layout/CSS)
 Security audit                 → claude-opus-4-5  (best at threat modeling)
 Background research            → gemini-2.5-flash (async, web search)
 Title / summary generation     → gemini-2.5-flash (small_model)
 Local / offline work           → ollama/llama3.2  (no API key needed)
 Any model, any time            → openrouter/*     (200+ model bridge)

 The Antigravity ModelRotator applies this automatically:
   ACTIVE_MODEL=auto → gemini → vertex → openrouter → ollama

══════════════════════════════════════════════════════════════════════
 AGENTS & WHEN TO USE THEM
══════════════════════════════════════════════════════════════════════

 GitHub Copilot (invoke with @agent:name):
   jules (P10)               code quality, refactoring, review
   rapid-implementer (P9)   end-to-end feature implementation
   architect (P8)           architecture decisions, design patterns
   debug-detective (P7)     root cause analysis
   testing-stability (P6)   test suites, regression coverage
   code-reviewer (P5)       security audit, best practices
   performance-optimizer    profiling, bottleneck elimination
   docs-master              documentation, guides
   deep-research            comprehensive research and analysis
   api-developer            REST design, OpenAPI specs
   devops-infrastructure    Docker, CI/CD, Kubernetes

 oh-my-opencode (invoked by Sisyphus or via @mention):
   oracle         read-only architecture consultation
   librarian      codebase understanding + Context7 docs
   explore        fast grep, read-only codebase search
   hephaestus     implementation worker (code writing)
   prometheus     long-running background research (async)
   multimodal-looker  analyze PDFs, images, diagrams

 Antigravity Swarm (via SwarmOrchestrator.execute()):
   router      decomposes task + synthesizes results
   coder       Python/JS/config implementation
   reviewer    quality, security, correctness analysis
   researcher  doc retrieval, background investigation

 swarm-tools (via /swarm command in OpenCode):
   coordinator  decomposes + creates Hive cells + spawns workers
   workers      parallel execution with file reservations
   hivemind     semantic memory: store learnings, find patterns

══════════════════════════════════════════════════════════════════════
 AVAILABLE TOOLS & SERVICES
══════════════════════════════════════════════════════════════════════

 Models: Gemini 2.5 Pro/Flash · Claude Opus/Sonnet/Haiku · GPT-4o
         Vertex AI · OpenRouter (200+) · Ollama (local)

 Search: Tavily · Exa.ai · Brave Search · Context7 (live docs) · grep.app

 Memory: Qdrant (cloud vector) · Upstash Redis (KV) · ChromaDB (local RAG)
         MCP Memory (in-session graph) · Hivemind (swarm-tools, local)
         Hive (.hive/ git-backed task store)

 Automation: GitHub MCP · n8n · Daytona (sandboxes) · Playwright

 Dev: Filesystem · Git · Fetch · Docker · SQLite · Mermaid · Time
      Sequential-Thinking · Firecrawl

══════════════════════════════════════════════════════════════════════
 PROJECT LAYOUT (memorize these paths)
══════════════════════════════════════════════════════════════════════

 backend/              FastAPI monolith (ALL routes in main.py)
 backend/agent/        GeminiClient · VertexClient · LocalClient · Orchestrator
 backend/rag/          ChromaDB store + file ingestion
 frontend/             Vanilla HTML/CSS/JS SPA (no build step)
 src/                  Agent SDK: Swarm · ModelRotator · MCPClient · GeminiAgent
 src/swarm.py          Router-Worker: MessageBus + SwarmOrchestrator
 src/model_rotator.py  Multi-provider key rotation + failover (522 lines)
 .github/agents/       13 GitHub Copilot agent definitions (.agent.md)
 .opencode/            OpenCode project config
 .opencode/oh-my-opencode.jsonc  Sisyphus plugin config
 .opencode/skills/     Skills: antigravity-workspace, github-triage
 .opencode/command/    Slash commands: /start-antigravity /test-antigravity
 .opencode/agents/     Custom agent markdown definitions
 .opencode/plugins/    Local plugin JS/TS files
 .hive/                swarm-tools git-backed task store
 .agent/               Agent rules, Gemini MCP settings, scripts
 .antigravity/rules.md Project directives (YOLO, artifact-first)
 opencode.json         OpenCode project config (plugin + MCP + model)
 .agent/gemini_mcp_settings.json  Gemini CLI MCP config template
 ANTIGRAVITY_MASTER_GUIDE.md     Canonical MCP + agent setup
 docs/OPENCODE_INTEGRATION.md    OpenCode plugin ecosystem guide
 docs/MASTER_AI_AGENT_PROMPT.md  This document

══════════════════════════════════════════════════════════════════════
 BEHAVIORAL MODES
══════════════════════════════════════════════════════════════════════

 "plan" / "plan mode"     → write artifacts/plan_[id].md, NO CODE yet
 "execute" / "implement"  → read plan file, spawn agents, write code
 "triage"                 → load github-triage skill, spawn 1 agent per issue
 "/swarm <task>"          → decompose via swarm-tools, spawn parallel workers
 "/gsd-init"              → start gsd spec-driven workflow
 "optimize" / "repo opt"  → see Section 13 of this document

══════════════════════════════════════════════════════════════════════
 FORBIDDEN (never do these)
══════════════════════════════════════════════════════════════════════

 ✗ Suppress type errors (no as any / @ts-ignore / @ts-expect-error)
 ✗ Leave empty catch blocks: catch(e) {}
 ✗ Delete failing tests to pass CI
 ✗ Create new route files in backend/ (monolith only)
 ✗ Use Windows-absolute paths in config files
 ✗ Commit secrets to source code
 ✗ Speculate about code you haven't read
===

---

## 4. OpenCode Optimal Config

### Config File Locations (precedence: lower overrides higher)

| Priority | File | Use for |
|----------|------|---------|
| 1 (base) | Remote `.well-known/opencode` | Org-wide defaults |
| 2 | `~/.config/opencode/opencode.json` | Personal global settings |
| 3 | `OPENCODE_CONFIG` env var | Custom overrides |
| 4 (highest) | `opencode.json` (project root) | Project-specific settings ← **this repo** |
| 5 | `.opencode/` directory | Agents, commands, plugins, skills |

### `opencode.json` — Complete Project Config

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "autoupdate": true,

  "plugin": [
    "oh-my-opencode",
    "opencode-swarm-plugin",
    "opencode-sessions",
    "gsd-opencode"
  ],

  "systemPrompt": "<<PASTE SECTION 3 PROMPT HERE>>",

  "provider": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}",
      "options": { "timeout": 600000, "setCacheKey": true }
    },
    "google": {
      "apiKey": "${GEMINI_API_KEY}"
    },
    "openrouter": {
      "apiKey": "${OPENROUTER_API_KEY}",
      "options": { "baseURL": "https://openrouter.ai/api/v1" }
    },
    "openai": {
      "apiKey": "${OPENAI_API_KEY}"
    }
  },

  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-5",
      "tools": { "write": true, "edit": true, "bash": true }
    },
    "plan": {
      "mode": "primary",
      "model": "google/gemini-2.5-pro",
      "tools": { "write": false, "edit": false, "bash": false }
    },
    "general": {
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5"
    },
    "explore": {
      "mode": "subagent",
      "model": "anthropic/claude-haiku-4-5"
    }
  },

  "mcp": {
    "git": {
      "type": "local",
      "command": ["uvx", "mcp-server-git", "--repository", "."],
      "enabled": true
    },
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@github/mcp-server"],
      "enabled": true,
      "environment": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "memory": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
      "enabled": true
    },
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"],
      "enabled": true
    },
    "fetch": {
      "type": "local",
      "command": ["uvx", "mcp-server-fetch"],
      "enabled": true
    },
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp", "--headless"],
      "enabled": true
    },
    "qdrant": {
      "type": "local",
      "command": ["uvx", "mcp-server-qdrant"],
      "enabled": true,
      "environment": {
        "QDRANT_URL": "${QDRANT_URL}",
        "QDRANT_API_KEY": "${QDRANT_API_KEY}",
        "COLLECTION_NAME": "antigravity-agent-memory",
        "EMBEDDING_PROVIDER": "fastembed"
      }
    },
    "upstash": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/mcp-server"],
      "enabled": true,
      "environment": {
        "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
        "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}"
      }
    },
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp"],
      "enabled": true,
      "environment": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
    },
    "tavily": {
      "type": "local",
      "command": ["npx", "-y", "tavily-mcp"],
      "enabled": true,
      "environment": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
    },
    "exa": {
      "type": "local",
      "command": ["npx", "-y", "exa-mcp-server"],
      "enabled": false,
      "environment": { "EXA_API_KEY": "${EXA_API_KEY}" }
    },
    "brave-search": {
      "type": "local",
      "command": ["npx", "-y", "@brave/brave-search-mcp"],
      "enabled": false,
      "environment": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "mermaid": {
      "type": "local",
      "command": ["npx", "-y", "@narasimhaponnada/mermaid-mcp-server"],
      "enabled": false
    },
    "docker": {
      "type": "local",
      "command": ["npx", "-y", "mcp-server-docker"],
      "enabled": false
    },
    "sqlite": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite", "--db-path", "./data.db"],
      "enabled": false
    },
    "antigravity-backend": {
      "type": "sse",
      "url": "http://localhost:8000/api/mcp/stream",
      "enabled": false,
      "description": "Antigravity backend as an MCP provider (future implementation)"
    }
  }
}
```

### `.opencode/agents/` — Custom Agent Definitions

Create `.opencode/agents/review.md`:
```markdown
---
description: Security-focused code reviewer for Python and TypeScript
mode: subagent
model: anthropic/claude-opus-4-5
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---
You are a security-focused code reviewer for the Antigravity workspace.

Focus on:
- Input validation and injection vulnerabilities
- Secret exposure (env vars, hardcoded credentials)
- Async race conditions and deadlocks
- Type safety (no implicit `Any`)
- Pydantic model completeness

Never make changes. Only report findings with file:line references.
```

Create `.opencode/agents/researcher.md`:
```markdown
---
description: Deep research agent using multiple search tools
mode: subagent
model: google/gemini-2.5-pro
temperature: 0.3
---
You are a research specialist. Always use multiple sources:
1. Context7 for library documentation
2. Tavily for recent articles and discussions
3. grep.app for real-world code examples
4. Exa for semantic search across technical docs

Synthesize findings into structured reports with citations.
Return research in a format ready for the plan agent to consume.
```

---

## 5. oh-my-opencode Config

### `.opencode/oh-my-opencode.jsonc` — Full Optimal Config

```jsonc
// oh-my-opencode configuration for Antigravity workspace
// Place at: .opencode/oh-my-opencode.jsonc
// See: https://github.com/code-yeongyu/oh-my-opencode
{
  // ── Primary Agents ────────────────────────────────────────────────────
  "agents": {
    "sisyphus": {
      // Main orchestrator — highest reasoning capability
      // Delegates to sub-agents, manages background tasks
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 64000,
      "thinking": { "budget": 32000 },
      "prompt_append": "You are the Antigravity Sisyphus agent. When you spawn background agents, prefer: Prometheus (research) → Librarian (docs) → Hephaestus (code). Always check .hive/ for existing tasks before creating new ones."
    },
    "oracle": {
      // Architecture-only consultation — read-only
      "model": "anthropic/claude-opus-4-5",
      "mode": "subagent",
      "prompt_append": "Read-only. Analyze architecture only. Never write files. Focus on: design patterns, SOLID principles, scalability, Antigravity's monolith rule (all routes in backend/main.py)."
    },
    "hephaestus": {
      // Primary code writer — fast, high-quality
      "model": "anthropic/claude-sonnet-4-5",
      "mode": "subagent",
      "prompt_append": "Implementation worker. Follow Antigravity conventions: type hints, async/await, Pydantic models, Google docstrings. ALL routes go in backend/main.py."
    },
    "librarian": {
      // Docs and codebase understanding
      "model": "anthropic/claude-sonnet-4-5",
      "mode": "subagent",
      "prompt_append": "Always use context7 MCP for library docs. Use grep.app for real-world usage examples. Return structured summaries with direct code snippets."
    },
    "explore": {
      // Fast read-only grep — cheapest model
      "model": "anthropic/claude-haiku-4-5",
      "mode": "subagent"
    },
    "prometheus": {
      // Async background research — Gemini for web tasks
      "model": "google/gemini-2.5-flash",
      "mode": "subagent",
      "prompt_append": "Research specialist. Use Tavily for news, Exa for semantic search, Context7 for docs. Run asynchronously in background. Report structured findings."
    },
    "multimodal-looker": {
      // PDF/image analysis — Gemini native multimodal
      "model": "google/gemini-2.5-pro",
      "mode": "subagent"
    }
  },

  // ── Category Routing ──────────────────────────────────────────────────
  // When Sisyphus classifies a task, it routes to the optimal model
  "categories": {
    "ultrabrain": {
      // Deep architecture, complex debugging, system design
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 64000,
      "thinking": { "budget": 32000 }
    },
    "visual-engineering": {
      // Frontend, CSS, UI/UX — Claude excels here
      "model": "anthropic/claude-sonnet-4-5"
    },
    "quick": {
      // Single-file fixes, typos, renames
      "model": "anthropic/claude-haiku-4-5",
      "maxTokens": 4000
    },
    "writing": {
      // Docs, READMEs, comments — Gemini Flash is excellent
      "model": "google/gemini-2.5-flash"
    },
    "research": {
      // Web search, doc gathering
      "model": "google/gemini-2.5-flash"
    },
    "unspecified-high": {
      "model": "anthropic/claude-sonnet-4-5"
    },
    "unspecified-low": {
      "model": "anthropic/claude-haiku-4-5"
    }
  },

  // ── Built-in MCPs ─────────────────────────────────────────────────────
  "mcps": {
    "websearch": {
      "enabled": true,
      "exa_api_key": "${EXA_API_KEY}",
      "tavily_api_key": "${TAVILY_API_KEY}"
    },
    "context7": { "enabled": true },
    "grep_app":  { "enabled": true }
  },

  // ── Background Agent Concurrency ──────────────────────────────────────
  "background_agent": {
    "enabled": true,
    "max_concurrent": 5
    // Increase to 8 if you have 3+ API keys (ANTHROPIC_API_KEYS / GEMINI_API_KEYS)
  },

  // ── Skills ────────────────────────────────────────────────────────────
  "skill_loader": {
    "enabled": true,
    "paths": [".opencode/skills"]
    // Skills: antigravity-workspace, github-triage
  },

  // ── Productivity Features ─────────────────────────────────────────────
  "todo_enforcer": { "enabled": true },
  "ralph_loop": { "enabled": true },      // loops until task complete
  "think_mode": { "enabled": true },      // /think for deep analysis
  "lsp": { "enabled": true },             // language server for refactoring
  "hash_anchored_edits": { "enabled": true } // zero stale-line errors
}
```

### Key oh-my-opencode Features to Know

| Feature | What it does | How to trigger |
|---------|-------------|----------------|
| Background agents | Spawn parallel workers | Sisyphus does this automatically |
| Ralph Loop | Keeps running until done | Automatically active |
| LSP tools | Rename, refactor, diagnostics | Available as tools |
| Hash-anchored edits | Validates content before applying | Automatically active |
| Todo Enforcer | Ensures todos are tracked | Automatically active |
| Think Mode | Deep analysis before acting | `/think <question>` |
| Session History | Search past sessions | `@general search sessions for "auth"` |

---

## 6. swarm-tools Config

### How Swarm-Tools Works

```
/swarm "Implement OAuth2 authentication"
      │
      ▼
  Coordinator Agent
  ├── Queries Hivemind: "auth patterns" → finds past auth implementations
  ├── Creates Hive cells:
  │     cell-1: "Implement OAuth2 routes in backend/main.py"
  │     cell-2: "Add Pydantic models for OAuth2 tokens"
  │     cell-3: "Write pytest tests for auth endpoints"
  │     cell-4: "Update ANTIGRAVITY_MASTER_GUIDE.md with auth docs"
  │
  ├── Spawns Workers (parallel):
  │     Worker A → 🔒 reserves backend/main.py → implements routes
  │     Worker B → 🔒 reserves backend/schemas/ → adds Pydantic models
  │     Worker C → 🔒 reserves tests/           → writes test suite
  │     Worker D → 🔒 reserves docs/            → updates docs
  │
  └── Reviews each completion → Hivemind stores patterns for next time
```

### `.hive/` Structure

```
.hive/
├── cells/          # Task cells (JSON, git-tracked)
├── hivemind/       # Semantic memory (embeddings)
├── mail/           # Agent-to-agent messages
└── config.json     # Swarm configuration
```

### Environment Variables for swarm-tools

```bash
# Ollama embeddings (for Hivemind semantic search)
OLLAMA_MODEL=nomic-embed-text       # or: mxbai-embed-large (default)
OLLAMA_HOST=http://localhost:11434

# If Ollama unavailable, Hivemind falls back to full-text search
```

### Key Commands

```bash
/swarm "task description"    # decompose + spawn parallel workers
/hive                        # query and manage task cells
/inbox                       # messages from other agents
/status                      # swarm coordination status
/handoff                     # end session with sync notes
```

### Integration with Antigravity's Existing Swarm

The Antigravity backend has its own `src/swarm.py` SwarmOrchestrator.
swarm-tools (OpenCode plugin) is the **OpenCode-native equivalent**.

- **Use `src/swarm.py`** when: calling from Python, running via backend API (`POST /api/agents/collaborate`)
- **Use `swarm-tools` `/swarm` command** when: working directly in OpenCode TUI

They complement each other. swarm-tools persists state in `.hive/`; `src/swarm.py` caches in memory.

---

## 7. opencode-sessions Config

### The Four Session Modes

| Mode | Creates new session | Context | Use for |
|------|--------------------|---------|---------| 
| `message` | No | Full | Turn-based agent collaboration |
| `new` | Yes | None | Clean phase transition |
| `compact` | No | Compressed | Token optimization + handoff |
| `fork` | Yes (child) | Full copy | Parallel approach exploration |

### When to Use Each Mode in Antigravity Workflows

```
Research phase:
  session({ mode: "new", agent: "researcher",
            text: "Research FastAPI OAuth2 best practices 2025" })

Planning phase (clean slate — no impl details bleed in):
  session({ mode: "new", agent: "plan",
            text: "Design OAuth2 system based on the research" })

Implementation (turn-based: build → review → build):
  session({ mode: "message", agent: "review",
            text: "Review this OAuth2 implementation for security" })

Context getting long → compress + hand to plan:
  session({ mode: "compact", agent: "plan",
            text: "Review our overall auth architecture" })

Explore multiple approaches before committing:
  session({ mode: "fork", agent: "plan", text: "Design with JWT" })
  session({ mode: "fork", agent: "plan", text: "Design with session cookies" })
  session({ mode: "fork", agent: "plan", text: "Design with OAuth2 + PKCE" })
  // Use <Leader>l to switch between forks, compare, then commit to one
```

### Navigating Between Sessions

```
<Leader>+Right    cycle forward: parent → child1 → child2 → parent
<Leader>+Left     cycle backward
/sessions         list all active sessions
```

---

## 8. gsd-opencode Config

### Three Model Profiles

| Profile | Planning model | Execution model | Verify model | Best for |
|---------|---------------|-----------------|--------------|---------|
| `quality` | claude-opus-4-5 | claude-sonnet-4-5 | gemini-2.5-flash | Critical architecture, production features |
| `balanced` | claude-sonnet-4-5 | gemini-2.5-flash | claude-haiku-4-5 | Daily development |
| `budget` | gemini-2.5-flash | gemini-2.5-flash | gemini-2.5-flash | High-volume, exploratory work |

### First-Time Setup

```bash
# Run in OpenCode TUI:
/gsd-settings
# → "Setup presets wizard"
# Discovers your available models via `opencode models`
# Prompts you to select 3 models × 3 profiles = 9 selections
# Saves to .planning/config.json
# Generates opencode.json with agent-to-model mappings
```

> **Important**: After changing profiles, fully restart OpenCode.
> OpenCode loads `opencode.json` at startup and does NOT hot-reload model assignments.

### GSD Workflow Commands

```bash
/gsd-init                   # Start: creates spec + planning structure
/gsd-plan-phase             # Research + plan current phase
/gsd-execute-phase          # Execute with verification
/gsd-set-profile quality    # Switch to quality profile
/gsd-set-profile balanced   # Switch to balanced
/gsd-set-profile budget     # Switch to budget
/gsd-settings               # Full interactive settings menu
```

### GSD Workflow Agents (automatic)

| Agent | Default | What it does |
|-------|---------|-------------|
| `research` | `true` | Researches domain before planning each phase |
| `plan_check` | `true` | Verifies plans achieve goals before execution |
| `verifier` | `true` | Confirms deliverables after execution |

Toggle in `/gsd-settings` or skip per-invocation:
- `/gsd-plan-phase --skip-research`
- `/gsd-plan-phase --skip-verify`

### `.planning/config.json` — What GSD Creates

```json
{
  "active_profile": "balanced",
  "profiles": {
    "presets": {
      "quality": {
        "planning": "anthropic/claude-opus-4-5",
        "execution": "anthropic/claude-sonnet-4-5",
        "verification": "google/gemini-2.5-flash"
      },
      "balanced": {
        "planning": "anthropic/claude-sonnet-4-5",
        "execution": "google/gemini-2.5-flash",
        "verification": "anthropic/claude-haiku-4-5"
      },
      "budget": {
        "planning": "google/gemini-2.5-flash",
        "execution": "google/gemini-2.5-flash",
        "verification": "google/gemini-2.5-flash"
      }
    }
  },
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true
  },
  "parallelization": {
    "enabled": true
  }
}
```

---

## 9. Gemini CLI Optimal Config

### `~/.gemini/settings.json` — Full Optimal Config

```json
{
  "model": "gemini-2.5-pro",
  "systemPrompt": "<<PASTE SECTION 3 PROMPT HERE>>",
  "temperature": 0.7,
  "maxOutputTokens": 65536,

  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."],
      "enabled": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@github/mcp-server"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" },
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
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "enabled": true
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time"],
      "enabled": true
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp", "--headless"],
      "enabled": true
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" },
      "enabled": true
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" },
      "enabled": true
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "${EXA_API_KEY}" },
      "enabled": true
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" },
      "enabled": true
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
      "enabled": true
    },
    "upstash": {
      "command": "npx",
      "args": ["-y", "@upstash/mcp-server"],
      "env": {
        "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
        "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}"
      },
      "enabled": true
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" },
      "enabled": false
    },
    "mermaid": {
      "command": "npx",
      "args": ["-y", "@narasimhaponnada/mermaid-mcp-server"],
      "enabled": false
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "mcp-server-docker"],
      "enabled": false
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "./data.db"],
      "enabled": false
    }
  }
}
```

### Using Claude from Gemini CLI (via OpenRouter)

```bash
# In terminal, before starting Gemini CLI:
export OPENROUTER_API_KEY=your_key

# In ~/.gemini/settings.json:
{
  "model": "openrouter/anthropic/claude-opus-4-5",
  ...
}
# OR pass at runtime:
gemini --model openrouter/anthropic/claude-opus-4-5 chat "Design auth system"
```

### Calling Antigravity Backend from Gemini CLI

With `fetch` MCP enabled:
```
# In Gemini CLI session, say:
"Use the fetch tool to POST to http://localhost:8000/api/agents/collaborate
 with body: { agents: ['architect', 'rapid-implementer'], task: 'Design OAuth2' }"
```

---

## 10. Antigravity Backend Config

### `.env` Optimal Settings

```bash
# ── Primary Models ──────────────────────────────────────────────────────
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEYS=key1,key2,key3          # 3 keys = 3× rate limit

ANTHROPIC_API_KEY=your_anthropic_key    # for OpenRouter Claude access
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_API_KEYS=key1,key2           # multiple = higher throughput
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5

VERTEX_API_KEY=                          # optional GCP key
VERTEX_PROJECT_ID=your-gcp-project
VERTEX_LOCATION=us-central1

LOCAL_MODEL=llama3.2                     # Ollama offline fallback

# ── Model Routing ────────────────────────────────────────────────────────
ACTIVE_MODEL=auto                        # gemini → vertex → openrouter → ollama

# ── Cache Tuning ─────────────────────────────────────────────────────────
CACHE_TTL_SECONDS=600                    # 10 min (default: 300)
CACHE_MAX_SIZE=500                       # (default: 100)

# ── Memory ───────────────────────────────────────────────────────────────
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key
UPSTASH_REDIS_REST_URL=https://your-db.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token

# ── Search ───────────────────────────────────────────────────────────────
TAVILY_API_KEY=your_tavily_key
EXA_API_KEY=your_exa_key
BRAVE_API_KEY=your_brave_key
CONTEXT7_API_KEY=your_context7_key

# ── Integrations ─────────────────────────────────────────────────────────
GITHUB_TOKEN=your_github_token
N8N_API_KEY=
DAYTONA_API_KEY=
DAYTONA_SERVER_URL=https://app.daytona.io/api
```

### ModelRotator Failover Cascade

```
ACTIVE_MODEL=auto triggers:

Request → [Gemini] available? → serve
        → rate limited?        → try next key from GEMINI_API_KEYS
        → all Gemini keys exhausted → [Vertex AI]
        → Vertex unavailable         → [OpenRouter] (200+ models)
        → no network access          → [Ollama local]
        → Ollama not running         → error with clear message
```

### Multi-Key Strategy for Maximum Throughput

```bash
# 3 Gemini keys = 3× RPM cap, workers run truly in parallel
GEMINI_API_KEYS=AIzaSy...key1,AIzaSy...key2,AIzaSy...key3

# 2 OpenRouter keys = 2× fallback pool
OPENROUTER_API_KEYS=sk-or-...key1,sk-or-...key2
```

The `src/model_rotator.py` distributes requests via health-score algorithm:
- `health_score = (success_rate × 100) - (consecutive_errors × 10) - (rate_limit_hits × 5)`
- Key with highest health score is selected first

---

## 11. Cross-Platform Model Router

### The Universal Bridge Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    OPENROUTER AS UNIVERSAL BRIDGE                        │
│                                                                          │
│   OpenCode          Gemini CLI         Antigravity Backend               │
│   (Claude primary)  (Gemini primary)   (auto-routing)                    │
│        │                 │                    │                          │
│        └─────────────────┴────────────────────┘                          │
│                                │                                         │
│                    OPENROUTER_API_KEY                                    │
│                    https://openrouter.ai/api/v1                          │
│                    (OpenAI-compatible format)                             │
│                                │                                         │
│              ┌─────────────────┼─────────────────┐                       │
│              │                 │                 │                       │
│    anthropic/claude-opus-4-5   │   google/gemini-2.5-pro                │
│    anthropic/claude-sonnet-4-5 │   meta-llama/llama-3.1-70b             │
│    anthropic/claude-haiku-4-5  │   mistralai/mixtral-8x7b               │
│                                │   200+ more models                      │
└──────────────────────────────────────────────────────────────────────────┘
```

**Key insight**: With one `OPENROUTER_API_KEY`, all three platforms can use any model from
any provider. If Anthropic rate-limits, all platforms transparently switch to Google.
If Google rate-limits, all platforms switch to Meta/Mistral.

### How Each Platform Uses the Others' Models

**OpenCode using Gemini (in addition to Claude)**:
```json
// opencode.json
{
  "provider": { "google": { "apiKey": "${GEMINI_API_KEY}" } },
  "agent": {
    "prometheus": { "model": "google/gemini-2.5-flash" },
    "multimodal-looker": { "model": "google/gemini-2.5-pro" }
  }
}
```

**Gemini CLI using Claude**:
```json
// ~/.gemini/settings.json
{
  "model": "openrouter/anthropic/claude-opus-4-5"
}
```
Or set `OPENROUTER_API_KEY` and pass `--model openrouter/anthropic/claude-opus-4-5`.

**Antigravity backend using Claude via OpenRouter**:
```bash
# .env
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5
ACTIVE_MODEL=openrouter           # or: auto (tries Gemini first)
```

### Shared Memory Architecture (Cross-Session Continuity)

```
Session 1 — OpenCode/Sisyphus discovers: "Auth should use PKCE not implicit flow"
  → Sisyphus stores via qdrant MCP:
    qdrant-store({ collection: "antigravity-agent-memory",
                   text: "Auth: use PKCE, not implicit flow",
                   metadata: { source: "session-1", tags: ["auth", "security"] } })
  → Stores structured decision via upstash MCP:
    redis-set("arch:decision:auth-pkce", { decided: true, reason: "..." })

Session 2 — Gemini CLI, next day, different topic:
  → Gemini uses qdrant MCP to check for past decisions:
    qdrant-find({ collection: "antigravity-agent-memory", query: "auth design" })
  → Retrieves Sisyphus's insight from Session 1
  → Continues with full architectural context

Session 3 — Antigravity backend /api/chat:
  → Orchestrator RAG pipeline queries ChromaDB (local) + Qdrant (cloud)
  → Both Sisyphus's insight and current repo context available
  → Backend agents make informed decisions without re-researching
```

### Three-Layer Memory Strategy

| Layer | Tool | Scope | Lifetime | Best for |
|-------|------|-------|----------|----------|
| ChromaDB | Local RAG (`backend/rag/`) | Repo files, drop_zone | Session + persistent | Workspace file content |
| Qdrant | Cloud vector (`qdrant MCP`) | Agent discoveries | Persistent, searchable | Architectural decisions, learnings |
| Upstash Redis | KV (`upstash MCP`) | Structured state | Persistent + TTL | Cross-session handoffs, flags |
| MCP Memory | In-session graph | Current session | Ephemeral | Active task context |
| Hivemind | swarm-tools (`.hive/`) | Swarm learnings | Persistent | Pattern recognition, anti-patterns |

---

## 12. Automated Workflow Patterns

### Pattern A: Full Feature Development (Maximum Quality)

```
Trigger: Large new feature

1. [gsd-opencode] /gsd-init "User authentication with OAuth2 + PKCE"
   → Creates spec in .planning/
   → Sets profile: quality (Claude Opus for planning)

2. [gsd-opencode] /gsd-plan-phase
   → research agent: searches OAuth2 + FastAPI best practices
   → plan agent: creates detailed implementation plan
   → plan_check agent: verifies plan is complete

3. [opencode-sessions] session({ mode: "fork", agent: "plan", text: "JWT approach" })
   session({ mode: "fork", agent: "plan", text: "Session cookies approach" })
   → Compare architectures, pick the winner

4. [swarm-tools] /swarm "Implement OAuth2 with PKCE per the plan"
   → Coordinator creates Hive cells (routes, models, tests, docs)
   → Workers execute in parallel with file reservations
   → Hivemind stores successful patterns

5. [oh-my-opencode] Sisyphus spawns background agents:
   → hephaestus: implements backend/main.py routes
   → oracle: validates design decisions
   → librarian: fetches FastAPI OAuth2 docs via Context7

6. [gsd-opencode] /gsd-execute-phase
   → verifier agent: confirms all must-haves delivered

7. [@agent:code-reviewer] Security audit via GitHub Copilot
   → Checks for PKCE implementation correctness, token exposure

8. [@agent:testing-stability-expert] Test suite
   → pytest coverage for all auth endpoints

Estimated time: ~20 min vs ~3 hours manual
```

### Pattern B: Fast Bug Fix (Minimum Overhead)

```
Trigger: Bug report or failing test

1. [@agent:debug-detective] Root cause analysis
   → Reads logs, traces execution path, identifies the line

2. [oh-my-opencode] Sisyphus → hephaestus implements fix
   → Uses hash-anchored edits (zero stale-line errors)
   → LSP tools validate syntax in-flight

3. [opencode-sessions] session({ mode: "message", agent: "review",
                                  text: "Review this fix for regressions" })
   → Turn-based: build agent → review agent → back to build

4. [@agent:testing-stability-expert] Add regression test

Estimated time: ~5 min
```

### Pattern C: Research → Implement Pipeline (Deep Work)

```
Trigger: "Should we use Qdrant or Pinecone for production vector storage?"

1. [opencode-sessions] Clean research phase:
   session({ mode: "new", agent: "researcher",
             text: "Compare Qdrant vs Pinecone for production: latency, cost,
                    Antigravity's current ChromaDB patterns, migration path" })
   → Prometheus agent uses Exa + Tavily + Context7 simultaneously

2. [opencode-sessions] Clean planning phase:
   session({ mode: "new", agent: "plan",
             text: "Design migration plan based on research" })
   → Oracle reviews architecture trade-offs

3. [@agent:architect] Architecture review via Copilot
   → Validates against Antigravity's existing patterns

4. [swarm-tools] /swarm "Migrate RAG from ChromaDB to Qdrant"
   → Parallel: update backend/rag/ + update .env.example + update docs

Estimated time: ~35 min for full research + migration
```

### Pattern D: GitHub Issue Triage (Automated)

```
Trigger: say "triage" in OpenCode

1. [github-triage skill] Loads .opencode/skills/github-triage/SKILL.md
2. Fetches all open issues + PRs via gh CLI
3. Classifies each: bug/question/enhancement/needs-info/safe-bugfix
4. For each item, spawns one background agent (category="free"):
   - Questions: answers in comment
   - Bugs: reproduces + root-causes + suggests fix
   - safe-bugfix PRs: creates review + auto-approves if clean
5. Reports summary to main Sisyphus session

Estimated time: ~2 min per issue (parallel, so 10 issues ≈ 4 min total)
```

### Pattern E: Repo Optimization (Full Audit)

```
Trigger: "optimize" or monthly maintenance

1. [@agent:repo-optimizer] Repository structure audit
2. [@agent:code-reviewer] Security + code quality scan
3. [@agent:performance-optimizer] Profile endpoints + identify bottlenecks
4. [swarm-tools] /swarm "Apply all non-breaking optimizations from audit"
5. [@agent:docs-master] Update all docs to reflect changes
6. [@agent:testing-stability-expert] Update test suite
```

---

## 13. Repo Optimization Report

> **Status**: Research findings only. No changes applied.
> **How to apply**: Use `@agent:rapid-implementer` to implement specific items.

### Critical Issues (apply first)

| # | File | Issue | Fix command |
|---|------|-------|-------------|
| C1 | `pytest.ini` | `--cov` flags require `pytest-cov` but it's not in `requirements.txt` | `@agent:rapid-implementer add pytest-cov to requirements` |
| C2 | `src/swarm.py` | Workers execute sequentially — `asyncio.gather()` needed | See code recommendation below |
| C3 | `backend/agent/orchestrator.py` | OpenRouter not wired in despite ModelRotator supporting it | Add openrouter client to `__init__` |

**C2 — Swarm Parallelism Fix** (code recommendation, do not apply yet):
```python
# In src/swarm.py SwarmOrchestrator.execute(), replace sequential loop with:
async def _run_worker(name: str, task: str) -> tuple[str, dict]:
    agent = self.agents.get(name)
    if not agent:
        return name, {"error": f"agent '{name}' not found"}
    context = {"recent_messages": [
        {"sender": m.sender, "content": m.content}
        for m in self.message_bus.get_context_for(name)
    ]}
    return name, await agent.execute(task, context)

worker_results = dict(await asyncio.gather(*[
    _run_worker(name, task)
    for name, task in delegation_plan.items()
]))
```

### Medium Issues

| # | File | Issue | Fix |
|---|------|-------|-----|
| M1 | `.agent/gemini_mcp_settings.json` | Uses `@modelcontextprotocol/server-git` (deprecated) | Change to `uvx mcp-server-git` |
| M2 | `src/model_rotator.py` | `available_models` lists stale model names | Update to gemini-2.5-pro/flash, claude-opus-4-5 |
| M3 | `backend/agent/orchestrator.py` | `ACTIVE_MODEL=openrouter` code path missing | Add: `elif self.active_model == "openrouter": return await self._openrouter_generate(request)` |
| M4 | `docs/GEMINI_CLI_GUIDE.md` | Shows `cd backend/cli && python gemini_cli.py` but pre-dates oh-my-opencode | Add section on oh-my-opencode integration |
| M5 | `opencode.json` | `"plugins"` should be `"plugin"` (OpenCode's actual key) | Change key name |

### Low Issues

| # | File | Issue | Fix |
|---|------|-------|-----|
| L1 | `DOCUMENTATION_INDEX.md` | References `docs/MASTER_AGENT_MISSION.md` but file does not exist | Remove stale reference |
| L2 | `mission.md` | Describes "stock analysis agent" (boilerplate leftover) | Update to Antigravity's real mission |
| L3 | `ANTIGRAVITY_MASTER_GUIDE.md` | Lists `gemini-pro` as default model | Update to `gemini-2.5-flash` (actual default in `gemini_client.py`) |
| L4 | `.opencode/context/processes.md` | Shows `python backend/main.py` as the start command | Add note: correct invocation is `cd backend && python main.py` |
| L5 | `pytest.ini` | `asyncio_mode = auto` but `pytest-asyncio` may not be installed | Add to requirements |
| L6 | `.gitignore` | Missing: `.hive/` (swarm-tools task store should be gitignored or committed) | Decision needed: commit `.hive/` for team continuity OR ignore it |

### Repo Strengths (no changes needed)

- ✅ `src/model_rotator.py` — excellent health-score based multi-key rotation
- ✅ `backend/agent/orchestrator.py` — LRU cache with configurable TTL/size
- ✅ 13 GitHub Copilot agents with priority ordering (jules=10, docs-master=1)
- ✅ `backend/rag/` — ChromaDB RAG pipeline well-integrated
- ✅ Clean separation: `backend/` (HTTP API), `src/` (SDK), `.github/agents/` (personas)
- ✅ `.opencode/` directory structure follows oh-my-opencode conventions
- ✅ `opencode.json` fixed in commit `6861df1` (cross-platform, no Windows paths)

---

## Appendix A: Environment Variables Master Reference

### Minimum Required

```bash
GEMINI_API_KEY=          # Google Gemini — Antigravity + Gemini CLI
ANTHROPIC_API_KEY=       # Claude — Sisyphus (oh-my-opencode)
GITHUB_TOKEN=            # GitHub MCP, triage, gsd-opencode
```

### Strongly Recommended

```bash
OPENROUTER_API_KEY=      # Universal model bridge (200+ models)
TAVILY_API_KEY=          # AI-optimized web search
EXA_API_KEY=             # Neural semantic search (oh-my-opencode websearch MCP)
CONTEXT7_API_KEY=        # Live library docs (oh-my-opencode context7 MCP)
QDRANT_URL=              # Cloud vector memory (cross-session)
QDRANT_API_KEY=
UPSTASH_REDIS_REST_URL=  # Cross-session KV state
UPSTASH_REDIS_REST_TOKEN=
```

### Full Production Stack

```bash
# Additional providers
VERTEX_API_KEY=          # GCP Vertex AI (Gemini via Cloud)
VERTEX_PROJECT_ID=
VERTEX_LOCATION=us-central1
OPENAI_API_KEY=          # GPT-4o fallback

# Multiple keys for rate limit multiplication
GEMINI_API_KEYS=key1,key2,key3
OPENROUTER_API_KEYS=key1,key2

# Automation
N8N_API_KEY=             # Workflow automation
N8N_BASE_URL=
DAYTONA_API_KEY=         # Persistent dev sandboxes
DAYTONA_SERVER_URL=

# Additional search
BRAVE_API_KEY=           # Privacy-first web search
FIRECRAWL_API_KEY=       # Full web page scraping

# Database / integrations
NEON_API_KEY=            # Serverless Postgres
LINEAR_API_KEY=          # Issue tracking
NOTION_API_KEY=          # Knowledge base
AGENTOPS_API_KEY=        # Agent observability

# Ollama (local, no key needed)
LOCAL_MODEL=llama3.2
OLLAMA_MODEL=nomic-embed-text   # for swarm-tools Hivemind
OLLAMA_HOST=http://localhost:11434
```

---

## Appendix B: Quick-Start Checklist

```
Installation:
[ ] npm install -g opencode-ai
[ ] bunx oh-my-opencode install
[ ] npm install -g opencode-swarm-plugin && swarm setup && swarm init
[ ] npm install -g opencode-sessions
[ ] npx gsd-opencode
[ ] cp .agent/gemini_mcp_settings.json ~/.gemini/settings.json
[ ] pip install -r requirements.txt

Configuration:
[ ] cp .env.example .env && fill in API keys
[ ] Edit opencode.json: add "plugin" array (see Section 4)
[ ] Edit .opencode/oh-my-opencode.jsonc: paste agent configs (Section 5)
[ ] Paste Section 3 system prompt into opencode.json systemPrompt field
[ ] Paste Section 3 system prompt into ~/.gemini/settings.json systemPrompt field
[ ] In OpenCode TUI: /gsd-settings → Setup presets wizard (Section 8)
[ ] Run: opencode → /init (initializes AGENTS.md for project)

Validation:
[ ] curl http://localhost:8000/health → { "status": "ok" }
[ ] swarm doctor → all checks pass
[ ] bunx oh-my-opencode doctor → all checks pass
[ ] gemini status (or equivalent) → API key valid
[ ] In OpenCode: /models → shows Anthropic + Google models
```

---

*Document compiled from research of: AloSantana/oh-my-opencode, AloSantana/swarm-tools,
AloSantana/opencode-sessions, AloSantana/gsd-opencode, AloSantana/opencode.cafe,
AloSantana/opencode, AloSantana/openclaw, AloSantana/CopilotKit + opencode.ai official docs
+ Antigravity repo source analysis.*

*Last updated: March 2026 · Type: AI agent reference document (no code changes)*
