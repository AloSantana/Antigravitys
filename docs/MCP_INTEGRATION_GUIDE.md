# MCP Integration Guide — Antigravity / Gemini CLI / OpenCode
> Comprehensive guide for connecting MCP servers to AI coding tools for seamless agent-to-agent communication

---

## Overview

This guide covers the complete integration strategy for connecting MCP servers across:
- **Antigravity Workspace** (this repository)
- **Gemini CLI** (`gemini` command-line tool)
- **OpenCode / Crush** (terminal AI assistant)
- **GitHub Copilot** (via `.github/copilot/mcp.json`)
- **Multi-Agent Chat** (agent-to-agent communication patterns)

---

## Configuration File Locations

| Tool | Config File | Format |
|------|-------------|--------|
| GitHub Copilot | `.github/copilot/mcp.json` | `{ "mcpServers": { ... } }` |
| Antigravity Agents | `.agent/mcp_config.json` | `{ "mcpServers": { ... } }` |
| Gemini CLI | `~/.gemini/settings.json` | `{ "mcpServers": { ... } }` |
| OpenCode/Crush | `~/.opencode.json` or `.opencode.json` | `{ "mcpServers": { "name": { "type": "stdio", ... } } }` |
| Claude Code | `~/.claude.json` | `{ "mcpServers": { ... } }` |

---

## Transport Types

```
stdio   — subprocess via stdin/stdout (most common, most compatible)
sse     — HTTP Server-Sent Events (for remote/cloud servers)
http    — REST-based HTTP transport (newer standard)
```

**Recommendation**: Use `stdio` for local servers, `sse`/`http` for cloud-hosted servers.

---

## Architecture: Multi-Agent MCP Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    Antigravity Workspace                        │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐  │
│  │  Gemini CLI │   │  OpenCode/  │   │  GitHub Copilot     │  │
│  │  (terminal) │   │  Crush      │   │  (VS Code / Web)    │  │
│  └──────┬──────┘   └──────┬──────┘   └──────────┬──────────┘  │
│         │                 │                       │             │
│         └─────────────────┴───────────────────────┘            │
│                           │                                     │
│                    MCP Protocol (stdio/sse)                     │
│                           │                                     │
│    ┌──────────────────────┼──────────────────────────┐         │
│    │              MCP Server Layer                    │         │
│    │                                                  │         │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │         │
│    │  │filesystem│  │   git    │  │    memory    │  │         │
│    │  └──────────┘  └──────────┘  └──────────────┘  │         │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │         │
│    │  │  github  │  │  fetch   │  │  context7    │  │         │
│    │  └──────────┘  └──────────┘  └──────────────┘  │         │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │         │
│    │  │playwright│  │  brave   │  │  sequential  │  │         │
│    │  └──────────┘  └──────────┘  └──────────────┘  │         │
│    └──────────────────────────────────────────────────┘         │
│                                                                 │
│    ┌──────────────────────────────────────────────────────┐    │
│    │              Agent Swarm Layer                        │    │
│    │                                                       │    │
│    │  RouterAgent ──→ CoderAgent ──→ ReviewerAgent        │    │
│    │       │                              │                │    │
│    │       └─────────→ ResearchAgent ─────┘               │    │
│    └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start: Add a New MCP Server

### Step 1: Test the server works
```bash
npx -y <package-name> --help
# or for Python servers:
python -m <module-name> --help
```

### Step 2: Add to GitHub Copilot config
```json
// .github/copilot/mcp.json
{
  "mcpServers": {
    "new-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": { "API_KEY": "${ENV_VAR_NAME}" }
    }
  }
}
```

### Step 3: Add to agent config
```json
// .agent/mcp_config.json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": { "API_KEY": "${ENV_VAR_NAME}" }
    }
  }
}
```

### Step 4: Add to Gemini CLI config
```json
// ~/.gemini/settings.json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["-y", "package-name"]
    }
  }
}
```

### Step 5: Add to OpenCode/Crush config
```json
// ~/.opencode.json
{
  "mcpServers": {
    "new-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": []
    }
  }
}
```

---

## Multi-Agent Chat: Communication Patterns

### Pattern 1: Shared Memory Bus (via Memory MCP)

All agents communicate through the shared Memory MCP server:

```python
# Agent A writes to memory
memory.create_entities([{
    "name": "task-result-001",
    "entityType": "AgentResult",
    "observations": ["Task completed: refactored auth module", "Time: 5 minutes"]
}])

# Agent B reads from memory
results = memory.search_nodes("task-result")
```

**Config**: Both agents must share the same `@modelcontextprotocol/server-memory` instance.

### Pattern 2: File-Based Communication (via Filesystem MCP)

Agents write/read files in a shared directory:

```
/artifacts/
  agent-coder-output.md
  agent-reviewer-feedback.md
  agent-researcher-findings.md
```

```python
# Coder agent writes output
filesystem.write_file("artifacts/agent-coder-output.md", code_output)

# Reviewer agent reads and responds
output = filesystem.read_file("artifacts/agent-coder-output.md")
filesystem.write_file("artifacts/agent-reviewer-feedback.md", review)
```

### Pattern 3: Git-Based Communication (via Git MCP)

Agents communicate through git commits and branches:

```python
# Agent creates feature branch and commits
git.create_branch("feature/agent-coder-auth")
git.commit("feat: implement JWT authentication")

# Reviewer agent reviews the diff
diff = git.diff("main", "feature/agent-coder-auth")
# Then creates PR via GitHub MCP
github.create_pull_request(title="Auth implementation", head="feature/agent-coder-auth")
```

### Pattern 4: Sequential Agent Chain (via Sequential Thinking)

Pass structured thinking chains between agents:

```python
# Research agent creates thought chain
thinking = sequential_thinking.sequentialthinking(
    thought="Research phase: Found 5 relevant patterns",
    thoughtNumber=1,
    totalThoughts=3
)

# Coder agent continues the chain
thinking2 = sequential_thinking.sequentialthinking(
    thought="Implementation phase: Applying pattern #2",
    thoughtNumber=2,
    totalThoughts=3,
    # Uses previous thought context
)
```

---

## Gemini CLI Integration

### Basic Setup
```bash
# 1. Install Gemini CLI
npm install -g @google/generative-ai-cli
# or
pip install google-generativeai

# 2. Configure API key
export GEMINI_API_KEY="your-key-here"

# 3. Create settings file
mkdir -p ~/.gemini
cat > ~/.gemini/settings.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@github/mcp-server"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp", "--headless"]
    }
  }
}
EOF

# 4. Test MCP integration
gemini -p "List files using the filesystem MCP server"
```

### Gemini CLI with Agent Workflows
```bash
# Research + code in one pipeline
gemini -p "Research the latest MCP server patterns using brave-search, 
           then implement a Python example using context7 for accurate docs,
           save to artifacts/mcp-example.py using filesystem"

# Multi-step reasoning
gemini -p "Use sequential-thinking to plan a multi-agent architecture for 
           Antigravity, then create the implementation plan in memory MCP 
           for other agents to access"
```

---

## OpenCode / Crush Integration

### Configuration
```json
// ~/.opencode.json
{
  "providers": {
    "anthropic": { "apiKey": "${ANTHROPIC_API_KEY}" },
    "google": { "apiKey": "${GEMINI_API_KEY}" }
  },
  "agents": {
    "coder": { "model": "gemini-2.5-pro", "maxTokens": 8000 },
    "task": { "model": "gemini-2.5-flash", "maxTokens": 4000 },
    "title": { "model": "gemini-2.5-flash", "maxTokens": 80 }
  },
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": []
    },
    "git": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "."]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@github/mcp-server"],
      "env": [{"name": "GITHUB_TOKEN", "value": "${GITHUB_TOKEN}"}]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": [{"name": "CONTEXT7_API_KEY", "value": "${CONTEXT7_API_KEY}"}]
    },
    "brave-search": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": [{"name": "BRAVE_API_KEY", "value": "${BRAVE_API_KEY}"}]
    },
    "fetch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    }
  },
  "autoCompact": true
}
```

---

## Best Practices for Agent-to-Agent Communication

### 1. Use Memory MCP as Message Bus
```python
# All agents write to and read from the shared memory graph
# This creates a persistent, queryable communication layer

# Writing agent
memory.create_entities([{
    "name": f"msg-{timestamp}",
    "entityType": "AgentMessage",
    "observations": [
        f"from: {agent_name}",
        f"content: {message}",
        f"status: pending"
    ]
}])

# Reading agent
messages = memory.search_nodes("AgentMessage status:pending")
```

### 2. Use Filesystem for Large Payloads
```python
# For large code blocks, files, or data — use filesystem
filesystem.write_file(f"artifacts/agent-{id}-output.json", json.dumps(large_data))
# Other agents read with:
data = json.loads(filesystem.read_file(f"artifacts/agent-{id}-output.json"))
```

### 3. Version Control for Code Changes
```python
# Always use git MCP to track agent-generated code changes
git.add(".")
git.commit(f"feat: agent-{name} - {task_description}")
# Then notify via memory MCP that code is ready for review
```

### 4. Context Sharing with Context7
```python
# Before coding, always fetch current docs
docs = context7.get_docs("fastapi async endpoints")
# Pass docs as context to the coding agent
```

### 5. Parallel Agent Execution via Fetch MCP
```python
# Agents can trigger other agents via HTTP if Antigravity backend is running
result = fetch.fetch(
    url="http://localhost:8000/api/swarm/execute",
    method="POST",
    body=json.dumps({"task": "Review the auth implementation"})
)
```

---

## Troubleshooting

### Server Not Starting
```bash
# Test server manually
npx -y @modelcontextprotocol/server-filesystem . 2>&1

# Check Node.js version (needs 18+)
node --version

# Check npm version
npm --version

# Reinstall with cache clear
npm cache clean --force
npx -y @modelcontextprotocol/server-filesystem .
```

### API Key Issues
```bash
# Verify environment variables are set
echo $GITHUB_TOKEN
echo $BRAVE_API_KEY
echo $GEMINI_API_KEY

# Add to .env file in project root
cat >> .env << 'EOF'
BRAVE_API_KEY=your_key_here
CONTEXT7_API_KEY=your_key_here
EXA_API_KEY=your_key_here
EOF

# Load .env (Antigravity loads automatically)
source .env
```

### Timeout Issues
```json
// Increase timeout in config
{
  "mcpServers": {
    "slow-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "server-name"],
      "timeout": 30000
    }
  }
}
```

### Tool Not Found
```bash
# List available tools for a server
npx -y @modelcontextprotocol/server-filesystem . --list-tools

# Verify tool names match config
# Common mistake: using snake_case vs camelCase
```

---

## Environment Variables Reference

Add these to your `.env` file:

```bash
# === Required for Core Functionality ===
GITHUB_TOKEN=ghp_...                    # GitHub personal access token

# === Optional (enhances capabilities) ===
BRAVE_API_KEY=BSA...                    # Brave Search API (free: 2000/month)
CONTEXT7_API_KEY=ctx7_...              # Context7 library docs (free tier)
EXA_API_KEY=exa_...                    # Exa AI search (free credits)
AGENTOPS_API_KEY=aop_...               # AgentOps monitoring (free tier)

# === AI Model Keys (for bridges) ===
GEMINI_API_KEY=AIza...                 # Google Gemini API
ANTHROPIC_API_KEY=sk-ant-...           # Anthropic Claude API
OPENAI_API_KEY=sk-...                  # OpenAI API

# === Database ===
POSTGRES_CONNECTION_STRING=postgresql://...  # PostgreSQL connection
SUPABASE_URL=https://xxx.supabase.co        # Supabase project URL
SUPABASE_ANON_KEY=eyJ...                    # Supabase anon key

# === Cloud ===
CLOUDFLARE_API_TOKEN=...               # Cloudflare API token
CLOUDFLARE_ACCOUNT_ID=...             # Cloudflare account ID

# === Firecrawl ===
FIRECRAWL_API_KEY=fc-...              # Firecrawl scraping API
```

---

## Server Status Dashboard

Quick health check for all servers:

```bash
#!/bin/bash
# Save as scripts/check-mcp-servers.sh
# Run: bash scripts/check-mcp-servers.sh

echo "=== MCP Server Status Check ==="
echo ""

check_server() {
    local name=$1
    local cmd=$2
    if timeout 5 $cmd --version 2>/dev/null || timeout 5 $cmd --help 2>/dev/null; then
        echo "✅ $name"
    else
        echo "❌ $name"
    fi
}

echo "Checking Node.js packages..."
node_packages=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-sequential-thinking"
    "@modelcontextprotocol/server-fetch"
    "@modelcontextprotocol/server-time"
    "@github/mcp-server"
    "@playwright/mcp"
    "@upstash/context7-mcp"
)

for pkg in "${node_packages[@]}"; do
    if npm list -g "$pkg" 2>/dev/null | grep -q "$pkg"; then
        echo "✅ $pkg (installed globally)"
    elif npx -y "$pkg" --help 2>/dev/null | grep -q ""; then
        echo "⚡ $pkg (via npx)"
    else
        echo "❌ $pkg"
    fi
done

echo ""
echo "Checking environment variables..."
env_vars=("GITHUB_TOKEN" "BRAVE_API_KEY" "GEMINI_API_KEY" "CONTEXT7_API_KEY")
for var in "${env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        echo "✅ $var (set)"
    else
        echo "⚠️  $var (not set)"
    fi
done
```

---

## Related Documentation

- [`MCP_SERVERS_CATALOG.md`](./MCP_SERVERS_CATALOG.md) — Full catalog of 100+ MCP servers
- [`MCP_INSTALLATION_PROMPTS.md`](./MCP_INSTALLATION_PROMPTS.md) — Ready-to-use installation prompts
- [`GEMINI_CLI_GUIDE.md`](./GEMINI_CLI_GUIDE.md) — Gemini CLI setup and usage
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — Antigravity system architecture

---

*Last updated: March 2026 | Antigravity Workspace Template*
