# Antigravity Workspace — Master Guide & LLM System Prompt

> **All-in-one reference for setting up, configuring, and prompting the full
> Antigravity / OpenCode multi-agent stack with every integrated service.**

---

## Table of Contents

1. [LLM System Prompt](#1-llm-system-prompt)
2. [Environment Variables — Quick Reference](#2-environment-variables--quick-reference)
3. [MCP Servers — No API Key Required](#3-mcp-servers--no-api-key-required)
4. [MCP Servers — API Key Required](#4-mcp-servers--api-key-required)
5. [OpenCode Configuration](#5-opencode-configuration)
6. [Gemini CLI Configuration](#6-gemini-cli-configuration)
7. [Service Setup Checklists](#7-service-setup-checklists)
8. [Agent Workflow Patterns](#8-agent-workflow-patterns)

---

## 1. LLM System Prompt

> Paste the block below as the **System Prompt** in OpenCode, Gemini CLI, or any
> agent framework to activate the full Antigravity capability set.

```
You are the Antigravity AI Agent — an autonomous, multi-agent coding assistant
operating inside the Antigravity Workspace.

══════════════════════════════════════════════════════════════════
 IDENTITY & MISSION
══════════════════════════════════════════════════════════════════
You are an elite software engineer with deep expertise in:
• Python (FastAPI, async, Pydantic, pytest)
• JavaScript / TypeScript (ES2022+, Node.js, vanilla DOM)
• AI/ML pipelines (Langchain, ChromaDB, Qdrant, Gemini, Ollama)
• DevOps (Docker, GitHub Actions, Daytona sandboxes)
• Multi-agent orchestration and swarm patterns

Your mission: deliver production-quality code, infrastructure, and
documentation with minimal user friction. Execute first, report after.

══════════════════════════════════════════════════════════════════
 AVAILABLE SERVICES & TOOLS
══════════════════════════════════════════════════════════════════

AI Models
  • Google Gemini 2.5 Pro/Flash  — primary reasoning & code generation
  • Gemini 2.5 Flash             — fast summaries, titles, routing tasks
  • OpenRouter                   — fallback + 200+ model access

Search & Research
  • Tavily          — AI-optimised web search; use for current events/docs
  • Brave Search    — privacy-first web search
  • Exa.ai          — neural semantic search + full-page content retrieval

Memory & Vector Storage
  • Qdrant (cloud)  — production vector DB; collection: antigravity-agent-memory
  • Upstash Redis   — serverless Redis for cross-session agent state & caching
  • Chroma (local)  — embedded vector store for dev/test RAG pipelines
  • MCP Memory      — in-session entity graph (ephemeral)

Automation & Workflow
  • n8n             — visual workflow automation; trigger builds, notify teams
  • Daytona         — persistent sandboxed dev environments per task/session
  • GitHub MCP      — full repo control (issues, PRs, branches, file edits)
  • Taskmaster-AI   — AI-driven sprint/task management for complex projects

Documentation & Knowledge
  • Context7        — fetch up-to-date library docs at inference time
  • Notion          — persistent team knowledge base
  • Mermaid         — generate architecture and flow diagrams inline

Dev Utilities (no auth required)
  • Filesystem      — read/write/search files in the workspace
  • Git             — stage, commit, diff, log, branch operations
  • Fetch           — make HTTP requests to any URL
  • Playwright      — headless browser automation and E2E testing
  • Docker          — build/run containers without leaving the chat
  • SQLite          — query the local data.db directly
  • Time            — timezone-aware timestamps for scheduling
  • Sequential-Thinking — structured multi-step reasoning chains

══════════════════════════════════════════════════════════════════
 BEHAVIOUR RULES
══════════════════════════════════════════════════════════════════
1. EXECUTE without asking for permission. Apply YOLO mode.
2. Use type hints in all Python code; async/await for all I/O.
3. Follow PEP 8, Google-style docstrings, and existing code patterns.
4. Never hardcode secrets — always read from environment variables.
5. After every significant change: lint → test → commit via report_progress.
6. Use Tavily or Exa for real-time information before answering knowledge
   questions that may be out of date.
7. Store agent memory in Qdrant (semantic) and Upstash Redis (state/KV).
8. Spawn Daytona sandboxes for risky or long-running operations.
9. Coordinate multi-agent tasks using the Swarm Orchestrator pattern:
   Router → Workers (Coder / Reviewer / Researcher) → Synthesis.
10. When uncertain about library APIs, call Context7 first.

══════════════════════════════════════════════════════════════════
 PROJECT LAYOUT (key paths)
══════════════════════════════════════════════════════════════════
backend/          FastAPI app, agent manager, RAG, orchestrator
frontend/         Pure HTML/CSS/JS + CodeMirror web UI
.agent/           Agent definitions, MCP config templates, skills
.github/          Copilot instructions, custom agent prompts, workflows
src/              Swarm system (MessageBus, RouterAgent, workers)
tests/            pytest test suite
opencode.json     OpenCode / Crush MCP server config (project-local)
.env              Environment variables (gitignored — NEVER commit)

══════════════════════════════════════════════════════════════════
 RESPONSE FORMAT
══════════════════════════════════════════════════════════════════
• Keep prose concise; let code speak.
• Use fenced code blocks with language tags.
• For multi-file changes, list every affected file before the diffs.
• End every task with a one-line status: ✅ Done | ⚠️ Partial | ❌ Failed
```

---

## 2. Environment Variables — Quick Reference

> Copy `.env.example` → `.env`, then fill in the values below.
> **Never commit `.env` to version control.**

### AI & LLM Providers

| Variable | Service | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini | https://aistudio.google.com/app/apikey |
| `ANTHROPIC_API_KEY` | Claude / Taskmaster-AI | https://console.anthropic.com/account/keys |
| `OPENAI_API_KEY` | OpenAI | https://platform.openai.com/api-keys |
| `OPENROUTER_API_KEY` | OpenRouter (200+ models) | https://openrouter.ai/keys |

### Search & Research

| Variable | Service | Where to get it |
|---|---|---|
| `TAVILY_API_KEY` | Tavily AI Search | https://app.tavily.com |
| `BRAVE_API_KEY` | Brave Search | https://brave.com/search/api/ |
| `EXA_API_KEY` | Exa.ai Neural Search | https://exa.ai/ |
| `CONTEXT7_API_KEY` | Context7 Library Docs | https://context7.com/ |

### Memory & Vector Storage

| Variable | Service | Where to get it |
|---|---|---|
| `QDRANT_URL` | Qdrant Vector DB | https://cloud.qdrant.io |
| `QDRANT_API_KEY` | Qdrant Cloud Auth | https://cloud.qdrant.io |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis | https://console.upstash.com/redis |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis Auth | https://console.upstash.com/redis |
| `QSTASH_TOKEN` | Upstash QStash | https://console.upstash.com/qstash |

### Automation & DevOps

| Variable | Service | Where to get it |
|---|---|---|
| `DAYTONA_API_KEY` | Daytona Sandboxes | https://app.daytona.io |
| `DAYTONA_SERVER_URL` | Daytona API base URL | `https://app.daytona.io/api` |
| `N8N_API_KEY` | n8n Workflow Automation | https://app.n8n.cloud/ |
| `N8N_BASE_URL` | n8n instance URL | your n8n cloud/self-hosted URL |

### GitHub & Project Management

| Variable | Service | Where to get it |
|---|---|---|
| `GITHUB_TOKEN` | GitHub API | https://github.com/settings/tokens |
| `LINEAR_API_KEY` | Linear Issues | https://linear.app/settings/api |
| `NOTION_API_KEY` | Notion Knowledge Base | https://www.notion.so/my-integrations |

---

## 3. MCP Servers — No API Key Required

These servers are **always available** and require zero credentials.
Install once globally for faster startup:

```bash
npm install -g \
  @modelcontextprotocol/server-filesystem \
  @modelcontextprotocol/server-git \
  @modelcontextprotocol/server-memory \
  @modelcontextprotocol/server-sequential-thinking \
  @modelcontextprotocol/server-fetch \
  @modelcontextprotocol/server-time \
  @modelcontextprotocol/server-sqlite \
  @playwright/mcp \
  @narasimhaponnada/mermaid-mcp-server \
  mcp-server-docker
```

| Server | Package | What it does |
|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write/search workspace files |
| `git` | `@modelcontextprotocol/server-git` | Stage, commit, diff, log, branch |
| `memory` | `@modelcontextprotocol/server-memory` | In-session entity graph (ephemeral KG) |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Structured multi-step reasoning |
| `fetch` | `@modelcontextprotocol/server-fetch` | HTTP GET/POST to any URL |
| `time` | `@modelcontextprotocol/server-time` | Timezone-aware timestamps |
| `sqlite` | `@modelcontextprotocol/server-sqlite` | Query `data.db` directly |
| `playwright` | `@playwright/mcp` | Headless browser — scrape, test, screenshot |
| `mermaid` | `@narasimhaponnada/mermaid-mcp-server` | Generate architecture / flow diagrams |
| `docker` | `mcp-server-docker` | Build, run, stop containers |
| `chroma` | `chroma-mcp` (via `uvx`) | Embedded vector store for local RAG |

---

## 4. MCP Servers — API Key Required

These servers unlock premium capabilities. Set the corresponding environment
variables in your `.env` file before use.

### 🔍 Search & Research

#### Tavily
```jsonc
// opencode.json
"tavily": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@tavily/mcp"],
  "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
}
```
**Use for:** real-time web search, news, current documentation, agent RAG  
**Env var:** `TAVILY_API_KEY`

---

#### Brave Search
```jsonc
"brave-search": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@brave/brave-search-mcp"],
  "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
}
```
**Use for:** web & local search without tracking  
**Env var:** `BRAVE_API_KEY`

---

#### Exa.ai
```jsonc
"exa": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "exa-mcp-server"],
  "env": { "EXA_API_KEY": "${EXA_API_KEY}" }
}
```
**Use for:** semantic/neural search, full-page content retrieval, finding similar docs  
**Env var:** `EXA_API_KEY`

---

#### Context7
```jsonc
"context7": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"],
  "env": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
}
```
**Use for:** fetching up-to-date library docs at inference time; eliminates hallucinated APIs  
**Env var:** `CONTEXT7_API_KEY`

---

### 🧠 Memory & Vector Storage

#### Qdrant
```jsonc
"qdrant": {
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-server-qdrant"],
  "env": {
    "QDRANT_URL":         "${QDRANT_URL}",
    "QDRANT_API_KEY":     "${QDRANT_API_KEY}",
    "COLLECTION_NAME":    "antigravity-agent-memory",
    "EMBEDDING_PROVIDER": "fastembed"
  }
}
```
**Use for:** persistent semantic memory across sessions, vector similarity search  
**Env vars:** `QDRANT_URL`, `QDRANT_API_KEY`  
**Default collection:** `antigravity-agent-memory`

---

#### Upstash Redis + QStash
```jsonc
"upstash": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@upstash/mcp-server"],
  "env": {
    "UPSTASH_REDIS_REST_URL":   "${UPSTASH_REDIS_REST_URL}",
    "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}",
    "QSTASH_TOKEN":             "${QSTASH_TOKEN}"
  }
}
```
**Use for:** KV state across agent sessions, rate limiting, async message queues  
**Env vars:** `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `QSTASH_TOKEN`

---

### ⚙️ Automation & DevOps

#### Daytona
```jsonc
"daytona": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@daytona/mcp"],
  "env": {
    "DAYTONA_API_KEY":    "${DAYTONA_API_KEY}",
    "DAYTONA_SERVER_URL": "${DAYTONA_SERVER_URL}"
  }
}
```
**Use for:** spin up isolated dev sandbox environments, long-running builds  
**Env vars:** `DAYTONA_API_KEY`, `DAYTONA_SERVER_URL` (`https://app.daytona.io/api`)

---

#### n8n
```jsonc
"n8n": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@n8n/mcp-server"],
  "env": {
    "N8N_API_KEY":  "${N8N_API_KEY}",
    "N8N_BASE_URL": "${N8N_BASE_URL}"
  }
}
```
**Use for:** trigger automated workflows, connect agents to external services  
**Env vars:** `N8N_API_KEY`, `N8N_BASE_URL`

---

#### GitHub
```jsonc
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@github/mcp-server"],
  "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
}
```
**Use for:** issue management, PRs, branch creation, file commits from agent  
**Env var:** `GITHUB_TOKEN`

---

## 5. OpenCode Configuration

The `opencode.json` at the repo root is the project-local config for OpenCode/Crush.
It includes **all** MCP servers above. To activate:

```bash
# 1. Install OpenCode
npm install -g opencode-ai   # or: curl -sSfL https://opencode.ai/install | sh

# 2. Copy .env.example → .env and fill in your keys
cp .env.example .env
# edit .env with your actual API key values

# 3. Launch (picks up opencode.json + .env automatically)
opencode
```

### Agent Model Configuration

| Role | Model | Max Tokens |
|---|---|---|
| `coder` | `gemini-2.5-pro` | 8 000 |
| `task` | `gemini-2.5-flash` | 4 000 |
| `title` | `gemini-2.5-flash` | 80 |

Override per-session with:
```
/model gemini-2.5-pro
```

---

## 6. Gemini CLI Configuration

Copy `.agent/gemini_mcp_settings.json` to `~/.gemini/settings.json` to enable
all MCP servers in the Gemini CLI:

```bash
cp .agent/gemini_mcp_settings.json ~/.gemini/settings.json
```

Then launch:
```bash
gemini
# or: ./gemini-cli.sh
```

---

## 7. Service Setup Checklists

### Quick Start (5 minutes)

- [ ] `cp .env.example .env`
- [ ] Set `GEMINI_API_KEY` in `.env`
- [ ] `npm install -g npx` (if not already present)
- [ ] `opencode` or `./start.sh`

### Full Stack Activation

- [ ] **Gemini** — `GEMINI_API_KEY` in `.env`
- [ ] **Tavily** — `TAVILY_API_KEY` → real-time search enabled
- [ ] **Brave Search** — `BRAVE_API_KEY` → privacy-first web search
- [ ] **Exa.ai** — `EXA_API_KEY` → semantic neural search
- [ ] **Context7** — `CONTEXT7_API_KEY` → live library docs
- [ ] **Qdrant** — `QDRANT_URL` + `QDRANT_API_KEY` → persistent vector memory
- [ ] **Upstash Redis** — `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` → agent state
- [ ] **Upstash QStash** — `QSTASH_TOKEN` → async message queues
- [ ] **Daytona** — `DAYTONA_API_KEY` + `DAYTONA_SERVER_URL` → isolated sandboxes
- [ ] **n8n** — `N8N_API_KEY` + `N8N_BASE_URL` → workflow automation
- [ ] **GitHub** — `GITHUB_TOKEN` → full repo integration
- [ ] **Anthropic** — `ANTHROPIC_API_KEY` → Taskmaster-AI + Claude fallback

### Validate Your Setup

```bash
./health-check.sh      # full service check
./validate.sh          # config + dependency validation
```

---

## 8. Agent Workflow Patterns

### Deep Research → Implement → Review

```
1. Tavily / Exa      ← research current state of the art
2. Context7          ← fetch library APIs
3. Coder Agent       ← implement the feature
4. Reviewer Agent    ← security + quality audit
5. Qdrant            ← store findings in semantic memory
```

### Multi-Session Memory Pattern

```python
# Store insight after each agent run
qdrant.upsert(collection="antigravity-agent-memory", points=[{
    "id": session_id,
    "vector": embed(result),
    "payload": {"task": task, "output": result, "timestamp": now()}
}])

# Retrieve relevant context at session start
context = qdrant.search(collection="antigravity-agent-memory",
                        query_vector=embed(current_task), limit=5)
```

### Async Task Queue (n8n + Upstash QStash)

```
Agent → QStash.publish(task) → n8n webhook trigger → n8n workflow
→ result stored in Upstash Redis → Agent.poll_result()
```

### Daytona Sandbox Pattern

```
1. Agent.create_sandbox(DAYTONA_API_KEY) → sandbox_id
2. Agent.run_in_sandbox(sandbox_id, command)
3. Agent.fetch_artifacts(sandbox_id) → result files
4. Agent.destroy_sandbox(sandbox_id)
```

---

## Environment Variable Summary (all-in-one `.env` snippet)

```bash
# ── AI / LLM ──────────────────────────────────────────────────────
GEMINI_API_KEY=<your-gemini-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
OPENAI_API_KEY=<your-openai-key>
OPENROUTER_API_KEY=<your-openrouter-key>

# ── Search & Research ─────────────────────────────────────────────
TAVILY_API_KEY=<your-tavily-key>
BRAVE_API_KEY=<your-brave-key>
EXA_API_KEY=<your-exa-key>
CONTEXT7_API_KEY=<your-context7-key>

# ── Memory & Vector Storage ───────────────────────────────────────
QDRANT_URL=<your-qdrant-cloud-url>
QDRANT_API_KEY=<your-qdrant-key>
UPSTASH_REDIS_REST_URL=<your-upstash-redis-url>
UPSTASH_REDIS_REST_TOKEN=<your-upstash-token>
QSTASH_TOKEN=<your-qstash-token>

# ── Automation & DevOps ───────────────────────────────────────────
DAYTONA_API_KEY=<your-daytona-key>
DAYTONA_SERVER_URL=https://app.daytona.io/api
N8N_API_KEY=<your-n8n-key>
N8N_BASE_URL=<your-n8n-instance-url>

# ── GitHub & Projects ─────────────────────────────────────────────
GITHUB_TOKEN=<your-github-token>
LINEAR_API_KEY=<your-linear-key>
NOTION_API_KEY=<your-notion-key>

# ── Server ────────────────────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
```

---

*Antigravity Workspace · Master Guide v2.0 · Updated March 2026*
