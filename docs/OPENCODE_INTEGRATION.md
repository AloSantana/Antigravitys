# OpenCode Integration Guide — Antigravity Workspace

> **Complete guide for setting up OpenCode, oh-my-opencode, swarm-tools, and all related plugins with the Antigravity platform.**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start (5 minutes)](#quick-start)
3. [Core Tools](#core-tools)
4. [oh-my-opencode — Primary Plugin](#oh-my-opencode)
5. [swarm-tools — Multi-Agent Coordination](#swarm-tools)
6. [opencode-sessions — Session Management](#opencode-sessions)
7. [opencode.cafe — Plugin Discovery](#opencodecafe)
8. [MCP Server Configuration](#mcp-server-configuration)
9. [Optimal Configuration](#optimal-configuration)
10. [Agent Workflows](#agent-workflows)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Antigravity workspace integrates with a rich ecosystem of OpenCode plugins and tools. These repos are all forked under **AloSantana**:

| Repo | Purpose | Install |
|------|---------|---------|
| [oh-my-opencode](https://github.com/AloSantana/oh-my-opencode) | Multi-agent orchestration harness with 11 agents, 46 hooks, 26 tools | `npm i -g oh-my-opencode` |
| [swarm-tools](https://github.com/AloSantana/swarm-tools) | Multi-agent swarm coordination with learning | `npm i -g swarm-tools` |
| [opencode-sessions](https://github.com/AloSantana/opencode-sessions) | Session management with multi-agent collaboration | `npm i opencode-sessions` |
| [opencode.cafe](https://github.com/AloSantana/opencode.cafe) | Plugin & extension discovery hub | Web app |
| [opencode](https://github.com/AloSantana/opencode) | OpenCode fork (Claude Code alternative) | See below |

---

## Quick Start

### Prerequisites

```bash
# Required: Node.js 20+ and npm/bun
node --version   # >= 20.0.0
bun --version    # >= 1.0.0 (recommended)

# Required: Python 3.8+ with uv or uvx
python --version  # >= 3.8
uvx --version    # for Python MCP servers

# Required: OpenCode (the AI coding agent)
npm install -g opencode-ai
opencode --version
```

### 1. Install OpenCode

```bash
# Install via npm
npm install -g opencode-ai

# Or via bun (faster)
bun add -g opencode-ai

# Verify
opencode --version
```

### 2. Install oh-my-opencode Plugin

```bash
# Install globally
npm install -g oh-my-opencode

# Or via npx (no install needed)
npx oh-my-opencode install

# Interactive setup wizard
bunx oh-my-opencode install

# Verify installation
bunx oh-my-opencode doctor
```

### 3. Install swarm-tools

```bash
npm install -g opencode-swarm-plugin
```

### 4. Configure the Workspace

The `opencode.json` in this repo is pre-configured. Copy it to your home config:

```bash
# Option A: Use project-level config (recommended — already in repo root)
# opencode.json is already here, just run opencode from repo root

# Option B: Copy to user config
cp opencode.json ~/.config/opencode/config.json
# Then set your API keys in .env

# Option C: Symlink
ln -sf $(pwd)/opencode.json ~/.config/opencode/config.json
```

### 5. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your API keys (minimum required)
# GEMINI_API_KEY=your-key         # for Gemini models
# ANTHROPIC_API_KEY=your-key     # for Claude models (oh-my-opencode)
# GITHUB_TOKEN=your-token        # for GitHub MCP
```

### 6. Start Using

```bash
# From the repo root
opencode

# OpenCode will load:
# - opencode.json (MCP servers + plugin config)
# - .opencode/oh-my-opencode.jsonc (Sisyphus agent config)
# - .opencode/skills/ (available skills)
# - .opencode/command/ (slash commands)
# - .opencode/context/ (project context)
```

---

## Core Tools

### OpenCode

OpenCode is the open-source AI coding agent (Claude Code alternative). It uses `opencode.json` for configuration.

```json
// opencode.json structure
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow",          // auto-approve all tool calls
  "plugins": ["oh-my-opencode"],  // loaded plugins
  "mcp": { ... }                  // MCP servers
}
```

**Key commands:**
```bash
opencode                # Start interactive session
opencode --help        # Help
opencode models        # List available models
```

### The .opencode/ Directory

OpenCode looks for project context in `.opencode/`:

```
.opencode/
├── oh-my-opencode.jsonc    # Plugin configuration
├── context/
│   ├── standards.md        # Coding standards (loaded into every session)
│   ├── processes.md        # Development processes
│   └── domain.md           # Project domain knowledge
├── skills/
│   ├── antigravity-workspace/SKILL.md   # Workspace skill
│   └── github-triage/SKILL.md          # GitHub triage skill
└── command/
    ├── start-antigravity.md   # /start-antigravity slash command
    ├── test-antigravity.md    # /test-antigravity slash command
    └── add-endpoint.md        # /add-endpoint slash command
```

---

## oh-my-opencode

The primary plugin that transforms OpenCode into a multi-agent development team.

### What It Provides

- **11 Agents**: Sisyphus (primary), Oracle, Librarian, Explore, Hephaestus, Atlas, Prometheus, Metis, Momus, Multimodal-Looker, Sisyphus-Junior
- **26 Tools**: LSP hover/goto/refs, AST-grep, delegate-task, background agents, etc.
- **46 Lifecycle Hooks**: Pre/post-tool guards, context injection, output truncation
- **3 Built-in MCPs**: Context7 (docs), Exa/Tavily (web search), grep.app (code search)
- **Skills System**: Modular skill loading via SKILL.md files
- **Background Agents**: Run multiple agents in parallel (like a dev team)

### Configuration

The plugin is configured via `.opencode/oh-my-opencode.jsonc` (project-level) or `~/.config/opencode/oh-my-opencode.jsonc` (user-level).

Key configuration:
```jsonc
{
  "agents": {
    "sisyphus": {
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 64000,
      "thinking": { "budget": 32000 }
    }
  },
  "categories": {
    "ultrabrain": { "model": "anthropic/claude-opus-4-5" },
    "quick": { "model": "anthropic/claude-haiku-4-5" }
  }
}
```

### Sisyphus Agent

Sisyphus is the primary orchestration agent — a "SF Bay Area senior engineer" persona that:
- Never works alone when specialists are available
- Delegates frontend work, research, deep analysis to sub-agents
- Uses todos for progress tracking
- Runs background agents in parallel

**How it works:**
1. You send a message
2. Sisyphus classifies the request (Trivial / Explicit / Exploratory / Open-ended / GitHub Work)
3. If a skill matches → invokes skill immediately
4. Spawns background agents for parallel research/implementation
5. Delegates to specialist agents (Oracle for architecture, Explore for codebase grep, Hephaestus for coding)
6. Synthesizes results

### Available Skills

Skills are loaded when their trigger phrases match:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `antigravity-workspace` | "antigravity", "start server", "backend" | Antigravity workspace operations |
| `github-triage` | "triage", "triage issues", "triage PRs" | Automated GitHub issue/PR triage |
| `git-master` | "commit", "rebase", "squash", "who wrote" | Advanced git operations |
| `playwright` | Any browser-related task | Browser automation |
| `frontend-ui-ux` | "UI", "design", "style" | Frontend design patterns |

### Slash Commands

Available in this workspace:

| Command | Purpose |
|---------|---------|
| `/start-antigravity` | Start the FastAPI backend server |
| `/test-antigravity` | Run the test suite with coverage |
| `/add-endpoint` | Add a new API endpoint (with template) |
| `/github-triage` | Triage open issues and PRs |

### Installing Additional oh-my-opencode Skills

```bash
# From oh-my-opencode source
# Skills can be added to .opencode/skills/{skill-name}/SKILL.md

# Structure:
# ---
# name: skill-name
# description: "When to use this skill"
# ---
# # Skill content
```

---

## swarm-tools

Multi-agent swarm coordination for OpenCode with learning capabilities.

### What It Provides

- **Swarm orchestration**: Queen (coordinator) → Workers (specialized agents)
- **Learning system**: Agents track what worked and improve over time
- **Issue tracking**: Per-agent issue tracking and resolution
- **Parallel execution**: Multiple agents work simultaneously

### Structure

```
.opencode/          # OpenCode plugin configs
.hive/              # Hive state (queen config, worker definitions)
packages/
  swarm-core/       # Core swarm coordination
  agent-memory/     # Agent learning and memory
  issue-tracker/    # Per-agent issue tracking
```

### Integration with Antigravity

The Antigravity swarm system in `src/swarm.py` uses a similar pattern. To use swarm-tools with OpenCode:

```bash
# Install
npm install -g swarm-tools

# Configure in .opencode/oh-my-opencode.jsonc
# Background agents with category="free" provide swarm-like parallelism
```

---

## opencode-sessions

Session management plugin for OpenCode with multi-agent collaboration.

### What It Provides

- **Session persistence**: Save and restore agent sessions
- **Multi-agent collaboration**: Share context between agents in a session
- **Session history**: Browse and replay past sessions
- **Export**: Export sessions to markdown/JSON

### Installation

```bash
npm install opencode-sessions

# Or add to opencode plugins
# In opencode.json: "plugins": ["opencode-sessions"]
```

### Key Features

```typescript
// Create a session
const session = await SessionManager.create({
  name: "feature-xyz",
  agents: ["sisyphus", "hephaestus"]
});

// Share context
await session.broadcast({ type: "context", data: { ... } });

// List sessions
await SessionManager.list();

// Restore session
await SessionManager.restore("session-id");
```

---

## opencode.cafe

Plugin and extension discovery hub for the OpenCode ecosystem.

- **URL**: https://opencode.cafe (web app)
- **Purpose**: Browse and install OpenCode plugins
- **Relevant plugins for Antigravity**:
  - oh-my-opencode (agent harness)
  - swarm-tools (multi-agent coordination)
  - opencode-sessions (session management)

---

## MCP Server Configuration

The `opencode.json` in this repo configures all MCP servers. All servers are `enabled: false` by default — enable them as needed.

### No API Key Required (enable freely)

```json
"filesystem": { "enabled": true },
"git": { "enabled": true },
"memory": { "enabled": true },
"sequential-thinking": { "enabled": true },
"fetch": { "enabled": true },
"time": { "enabled": true },
"sqlite": { "enabled": true },
"playwright": { "enabled": true },
"docker": { "enabled": true },
"mermaid": { "enabled": true }
```

### API Key Required

| Server | Key Variable | Purpose |
|--------|-------------|---------|
| `github` | `GITHUB_TOKEN` | GitHub repo operations |
| `brave-search` | `BRAVE_API_KEY` | Privacy-first web search |
| `exa` | `EXA_API_KEY` | Semantic neural search |
| `tavily` | `TAVILY_API_KEY` | AI-optimized web search |
| `context7` | `CONTEXT7_API_KEY` | Live library documentation |
| `qdrant` | `QDRANT_API_KEY` | Vector memory (cloud) |
| `upstash` | `UPSTASH_EMAIL` + `UPSTASH_API_KEY` | Redis/QStash |
| `daytona` | `DAYTONA_API_KEY` | Sandboxed environments |
| `n8n` | `N8N_API_KEY` + `N8N_BASE_URL` | Workflow automation |
| `firecrawl` | `FIRECRAWL_API_KEY` | Web scraping |
| `linear` | `LINEAR_API_KEY` | Issue tracking |
| `notion` | `NOTION_API_KEY` | Knowledge base |
| `openrouter` | `OPENROUTER_API_KEY` | 200+ model access |

### Recommended Minimal Setup

For daily Antigravity development, enable these MCP servers:

```json
"git": { "enabled": true },
"memory": { "enabled": true },
"sequential-thinking": { "enabled": true },
"fetch": { "enabled": true },
"github": { "enabled": true, "environment": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" } },
"playwright": { "enabled": true }
```

### uvx Servers (Python-based)

These servers require `uv`/`uvx` installed:

```bash
# Install uv (cross-platform)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Available uvx servers
uvx mcp-server-git          # git operations
uvx mcp-server-fetch        # HTTP fetch
uvx mcp-server-time         # timestamps
uvx mcp-server-qdrant       # Qdrant vector DB
uvx chroma-mcp              # ChromaDB
uvx python-lsp-mcp          # Python LSP
```

---

## Optimal Configuration

### Recommended opencode.json Setup

For the best Antigravity + OpenCode experience:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow",
  "plugins": ["oh-my-opencode"],
  "mcp": {
    "git": { "type": "local", "command": ["uvx", "mcp-server-git", "--repository", "."], "enabled": true },
    "memory": { "type": "local", "command": ["npx", "-y", "@modelcontextprotocol/server-memory"], "enabled": true },
    "sequential-thinking": { "type": "local", "command": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"], "enabled": true },
    "fetch": { "type": "local", "command": ["uvx", "mcp-server-fetch"], "enabled": true },
    "github": { "type": "local", "command": ["npx", "-y", "@github/mcp-server"], "enabled": true, "environment": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" } },
    "playwright": { "type": "local", "command": ["npx", "-y", "@playwright/mcp"], "enabled": true }
  }
}
```

### Recommended oh-my-opencode.jsonc

```jsonc
{
  "agents": {
    "sisyphus": {
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 64000,
      "thinking": { "budget": 32000 }
    }
  },
  "categories": {
    "ultrabrain": { "model": "anthropic/claude-opus-4-5" },
    "quick": { "model": "anthropic/claude-haiku-4-5" }
  },
  "mcps": {
    "websearch": { "enabled": true },
    "context7": { "enabled": true },
    "grep_app": { "enabled": true }
  },
  "background_agent": { "enabled": true, "max_concurrent": 5 }
}
```

### Multi-Stack Setup (Maximum Power)

Use all tools together:

```
OpenCode session
  │
  ├── oh-my-opencode plugin (auto-loaded)
  │     ├── Sisyphus (primary agent)
  │     ├── Background agents (5 concurrent)
  │     └── Built-in MCPs (Context7, Exa, grep.app)
  │
  └── MCP Servers (from opencode.json)
        ├── git, memory, sequential-thinking
        ├── github (for triage + PR automation)
        └── playwright (for E2E testing)
```

---

## Agent Workflows

### Feature Development (Full Stack)

```bash
# 1. Plan with GSD
/gsd-init
# Describe: "Add Qdrant-based persistent memory to replace ChromaDB"

# 2. Research phase (oh-my-opencode does this automatically via background agents)
# Sisyphus fires Prometheus for background research on Qdrant Python client

# 3. Execute phase
/gsd-execute-phase
# Sisyphus delegates to Hephaestus for implementation
# Oracle is consulted for architecture decisions

# 4. Run tests
/test-antigravity

# 5. Commit (Sisyphus uses git-master skill if available)
# Say: "commit with message: feat: add Qdrant persistent memory"
```

### GitHub Triage

```bash
# Triage all open issues and PRs in parallel
# Trigger phrase: "triage" or "github triage"

# Sisyphus detects the trigger, loads github-triage skill
# Spawns 1 background agent per issue/PR
# Each agent: analyzes → comments → closes/merges if safe
# Final report: all items with actions taken
```

### Deep Research

```bash
# Research + implement pattern
# Say: "research the best way to add streaming SSE to the FastAPI backend,
#       then implement it with proper backpressure handling"

# Sisyphus:
# 1. Fires Prometheus (background) for research
# 2. Fires Librarian (background) to fetch FastAPI SSE docs via Context7
# 3. Fires Explore to search current codebase for existing SSE patterns
# 4. Synthesizes findings → asks you to confirm approach
# 5. Delegates to Hephaestus for implementation
```

### Debugging

```bash
# Systematic debugging with codebase evidence
# Say: "The /api/agents/collaborate endpoint returns 500 when
#       two agents are called simultaneously. Debug this."

# Sisyphus:
# 1. Fires Explore to search for the endpoint
# 2. Fires Explore to find async patterns and potential race conditions
# 3. Reads the code (never speculates)
# 4. Identifies root cause with file:line evidence
# 5. Delegates fix to Hephaestus
# 6. Requests test to verify fix
```

---

## Troubleshooting

### "Plugin not found: oh-my-opencode"

```bash
# Install the plugin
npm install -g oh-my-opencode

# Verify it's in PATH
which oh-my-opencode
bunx oh-my-opencode doctor

# Check plugin load in OpenCode
# Start OpenCode, check for "Loaded plugin: oh-my-opencode" in logs
```

### "Command not found: uvx"

```bash
# Install uv (includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"  # or wherever uv installs

# Verify
uvx --version
```

### "MCP server failed to start"

```bash
# Test the server directly
npx -y @modelcontextprotocol/server-memory
# If it starts, the issue is with OpenCode connecting

# Check for port conflicts
lsof -i :3000  # docker-agent-gateway port

# Enable verbose logging in opencode
OPENCODE_LOG_LEVEL=debug opencode
```

### "Sisyphus not responding / using wrong model"

```bash
# Validate .opencode/oh-my-opencode.jsonc (strip comments then parse)
node -e "
const fs = require('fs');
const text = fs.readFileSync('.opencode/oh-my-opencode.jsonc','utf8')
  .replace(/\/\/[^\n]*/g,'')   // strip // comments
  .replace(/\/\*[\s\S]*?\*\//g,'');  // strip /* */ comments
try { JSON.parse(text); console.log('JSONC valid'); }
catch(e) { console.error('JSONC invalid:', e.message); }
"

# Verify ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY

# Check plugin doctor
bunx oh-my-opencode doctor
```

### Background agents not running

```bash
# Verify tmux is installed (required for background agents)
tmux --version

# Install if missing
sudo apt-get install tmux  # Linux
brew install tmux           # macOS
```

---

## Forked Repos Reference

All forked repos with relevant links:

| Repo | Original | Our Fork | Key Files |
|------|---------|----------|-----------|
| oh-my-opencode | [code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) | [AloSantana/oh-my-opencode](https://github.com/AloSantana/oh-my-opencode) | `.opencode/`, `sisyphus-prompt.md` |
| swarm-tools | [opencode-ai/swarm-tools](https://github.com/opencode-ai/swarm-tools) | [AloSantana/swarm-tools](https://github.com/AloSantana/swarm-tools) | `.hive/`, `.opencode/`, `packages/` |
| opencode-sessions | [opencode-ai/opencode-sessions](https://github.com/opencode-ai/opencode-sessions) | [AloSantana/opencode-sessions](https://github.com/AloSantana/opencode-sessions) | `index.ts` |
| opencode.cafe | [opencode-ai/opencode.cafe](https://github.com/opencode-ai/opencode.cafe) | [AloSantana/opencode.cafe](https://github.com/AloSantana/opencode.cafe) | `app/` (Next.js) |
| opencode | [opencode-ai/opencode](https://github.com/opencode-ai/opencode) | [AloSantana/opencode](https://github.com/AloSantana/opencode) | Core agent |

---

*Antigravity Workspace · OpenCode Integration Guide · March 2026*
