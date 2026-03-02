# Antigravity — Master Agent Mission Prompt

> **Purpose**: Optimized, multi-phase prompt for AI coding agents (Gemini CLI, GitHub Copilot, OpenCode/Crush, Jules) to fully configure and extend the Antigravity workspace.
>
> **How to use**: Paste the relevant phase block(s) as a task prompt or system addition. Each phase is self-contained and references concrete repo paths and agents.
>
> **Last updated**: March 2026 | Repo: `AloSantana/Antigravitys`

---

## Table of Contents

1. [Full Mission Prompt (Single-Block)](#1-full-mission-prompt-single-block)
2. [Phase 1 — Repo Analysis & Pattern Discovery](#2-phase-1--repo-analysis--pattern-discovery)
3. [Phase 2 — Deep GitHub Search (Forked Skill Repos)](#3-phase-2--deep-github-search-forked-skill-repos)
4. [Phase 3 — Documentation Audit & Consolidation](#4-phase-3--documentation-audit--consolidation)
5. [Phase 4 — Tool & Config Optimal Integration](#5-phase-4--tool--config-optimal-integration)
6. [Phase 5 — MCP Server Discovery & Installation](#6-phase-5--mcp-server-discovery--installation)
7. [Phase 6 — Multi-Agent Orchestration](#7-phase-6--multi-agent-orchestration)
8. [Phase 7 — Smart Memory & Automated Learning](#8-phase-7--smart-memory--automated-learning)
9. [Phase 8 — Repo Optimization & Final Config](#9-phase-8--repo-optimization--final-config)
10. [Agent Quick-Reference](#10-agent-quick-reference)
11. [Key Repo Paths](#11-key-repo-paths)

---

## 1. Full Mission Prompt (Single-Block)

> Paste this entire block as a task prompt for a long-running AI agent session (Gemini CLI `--yolo`, Jules, or Copilot Agent).

```
MISSION: Complete Antigravity Multi-Agent Platform Configuration

You are operating inside the Antigravity Workspace (AloSantana/Antigravitys).
Your mission is to configure Antigravity, OpenCode/Crush, Gemini CLI, and all
installed agents to work completely seamlessly — with shared routing, model
switching, cross-tool memory, and fully automated workflows.

Execute every phase below in order. Use YOLO mode (no confirmations needed).
After each phase, commit progress via report_progress or git commit with a
descriptive message.

═══════════════════════════════════════════════════════════════
PHASE 1: REPO ANALYSIS & PATTERN DISCOVERY
═══════════════════════════════════════════════════════════════
1. Read .antigravity/rules.md, GEMINI.md, mission.md, and ANTIGRAVITY_MASTER_GUIDE.md
2. Map the full codebase: backend/ (FastAPI), src/ (Agent SDK), frontend/ (Vanilla JS)
3. Identify the current model routing logic in:
   - backend/agent/orchestrator.py (Gemini → Vertex → Ollama fallback chain)
   - src/model_rotator.py (API key rotation, rate-limit handling)
   - src/swarm.py (Router → Coder/Reviewer/Researcher workers)
4. List all active MCP server configs across:
   - .github/copilot/mcp.json (Copilot)
   - .agent/mcp_config.json (SDK)
   - .agent/gemini_mcp_settings.json (Gemini CLI)
   - .agent/opencode_mcp_config.json (OpenCode)
   - opencode.json (OpenCode local)
   - mcp.json (root)
5. Identify gaps: servers enabled in one config but missing from others.
   Produce artifacts/plan_phase1_analysis.md with all findings.

═══════════════════════════════════════════════════════════════
PHASE 2: DEEP GITHUB SEARCH (FORKED SKILL REPOS)
═══════════════════════════════════════════════════════════════
Use @agent:deep-research and the GitHub MCP tool for this phase.

1. Search GitHub account AloSantana for all forked/owned repos containing:
   - "skills", "mcp", "agent", "integration", "tools", "knowledge"
   in their name, description, or topics.
2. For each discovered repo, extract:
   - MCP server definitions (mcp.json / mcpServers blocks)
   - Agent persona files (*.agent.md, *.md in agents/ dirs)
   - Skill definitions (.agent/skills/ directories)
   - Configuration templates (.env.example, settings.json)
3. Merge all unique, high-quality items into the main repo:
   - New skills → .agent/skills/
   - New agent personas → .github/agents/
   - New MCP server entries → .agent/mcp_config.json (deduped)
4. Document every source in artifacts/plan_phase2_discovery.md.

═══════════════════════════════════════════════════════════════
PHASE 3: DOCUMENTATION AUDIT & CONSOLIDATION
═══════════════════════════════════════════════════════════════
Use @agent:docs-master for this phase.

1. Read ALL docs in docs/ (26 files) and root-level *.md files.
2. Identify:
   - Duplicate content across files
   - Outdated instructions (old package names, deprecated configs)
   - Missing topics (no docs for src/swarm.py, model_rotator.py, sandbox system)
3. Actions:
   a. Update ANTIGRAVITY_MASTER_GUIDE.md to be the single canonical reference.
   b. Add a "Swarm Orchestration" section covering src/swarm.py patterns.
   c. Add a "Model Rotation & Fallback" section covering src/model_rotator.py.
   d. Add a "Sandbox Execution" section covering src/sandbox/.
   e. Mark/remove duplicate docs; update DOCUMENTATION_INDEX.md.
4. Regenerate README.md highlights based on current actual feature set.

═══════════════════════════════════════════════════════════════
PHASE 4: SEAMLESS TOOL INTEGRATION
═══════════════════════════════════════════════════════════════
Use @agent:architect for workflow design; @agent:rapid-implementer to code.

Goal: Antigravity, OpenCode/Crush, and Gemini CLI must share ONE unified
MCP server list and ONE model routing config.

1. Create .agent/unified_mcp.json — the master MCP config used by ALL tools.
   Format must be compatible with all three (Gemini CLI settings.json format).
2. Create scripts/sync_mcp_configs.py — reads unified_mcp.json and writes
   the correct format to:
   - ~/.gemini/settings.json (Gemini CLI)
   - ~/.opencode.json (OpenCode/Crush global)
   - .github/copilot/mcp.json (GitHub Copilot)
3. Add a "Model Router" config in .agent/model_router.json that defines:
   - Primary: Gemini 2.5 Pro (via GEMINI_API_KEY)
   - Secondary: Vertex AI Gemini (via VERTEX_API_KEY / Google Cloud)
   - Tertiary: OpenRouter (via OPENROUTER_API_KEY, 200+ models)
   - Local: Ollama (http://localhost:11434, model: OLLAMA_MODEL)
   - Fallback order: primary → secondary → tertiary → local
4. Update backend/agent/orchestrator.py to read model_router.json so the
   fallback chain is config-driven (not hardcoded).
5. Verify by running: pytest tests/test_orchestrator.py -v

═══════════════════════════════════════════════════════════════
PHASE 5: MCP SERVER DISCOVERY & INSTALLATION
═══════════════════════════════════════════════════════════════
Use @agent:performance-optimizer to evaluate; @agent:rapid-implementer to install.

1. Review docs/MCP_SERVERS_CATALOG.md for the curated server list.
2. Select TOP-PRIORITY servers for immediate installation (no API key needed):
   - @modelcontextprotocol/server-filesystem
   - @modelcontextprotocol/server-git
   - @modelcontextprotocol/server-memory
   - @modelcontextprotocol/server-sequential-thinking
   - @modelcontextprotocol/server-fetch
   - @modelcontextprotocol/server-time
   - @modelcontextprotocol/server-sqlite
   - @playwright/mcp
   - @github/mcp-server
3. Select API-KEY servers to configure (keys read from .env):
   - @upstash/context7-mcp (CONTEXT7_API_KEY) — live library docs
   - exa-mcp-server (EXA_API_KEY) — semantic search
   - firecrawl-mcp (FIRECRAWL_API_KEY) — web scraping
   - @qdrant/mcp-server (QDRANT_URL + QDRANT_API_KEY) — vector memory
   - taskmaster-ai (ANTHROPIC_API_KEY or OPENAI_API_KEY) — task management
4. Run: npm install -g <each package> for global install.
5. Add/enable each in .agent/unified_mcp.json.
6. Run scripts/sync_mcp_configs.py to propagate to all tool configs.
7. Test each connection with: npx <package> --help (verify no startup errors).

═══════════════════════════════════════════════════════════════
PHASE 6: MULTI-AGENT ORCHESTRATION
═══════════════════════════════════════════════════════════════
Use @agent:architect for design; @agent:rapid-implementer to implement.

Current state: src/swarm.py implements Router → Coder/Reviewer/Researcher.
                backend/agent/orchestrator.py handles HTTP API multi-agent.

1. Extend SwarmOrchestrator (src/swarm.py) to support:
   a. Dynamic worker registration (load .github/agents/*.agent.md at runtime)
   b. Parallel worker execution (asyncio.gather for independent sub-tasks)
   c. Shared context via Qdrant MCP (persist swarm state between sessions)
2. Add new FastAPI endpoints in backend/main.py:
   - POST /api/swarm/execute   — run SwarmOrchestrator.execute() via HTTP
   - GET  /api/swarm/status    — return current swarm agent status
   - POST /api/swarm/register  — dynamically register a new agent persona
3. Update .github/agents/ to include swarm-aware agents:
   - Each agent.md should declare its role: router | coder | reviewer | researcher | specialist
4. Add a skill: .agent/skills/multi-agent/swarm-orchestration.md documenting
   how to compose agents, including example prompts.
5. Run: pytest tests/test_swarm.py tests/test_orchestrator.py -v

═══════════════════════════════════════════════════════════════
PHASE 7: SMART MEMORY & AUTOMATED LEARNING
═══════════════════════════════════════════════════════════════
Use @agent:architect for design; @agent:rapid-implementer for implementation.

1. Implement a unified memory layer in src/memory/ (or extend existing):
   - Short-term: MCP Memory server (in-session knowledge graph)
   - Mid-term: Upstash Redis (cross-session KV, TTL-based)
   - Long-term: Qdrant vector store (semantic retrieval, never expires)
2. Create backend/memory_router.py — a FastAPI router with:
   - POST /api/memory/store   — store a fact/code snippet/decision
   - GET  /api/memory/recall  — semantic search across all memory layers
   - DELETE /api/memory/forget — remove by ID or pattern
3. Add auto-learning hooks in backend/agent/orchestrator.py:
   - After each successful agent response → extract key facts → store in Qdrant
   - After each failed response → store error + context as a "lesson" in Redis
4. Add a .agent/skills/memory/ skill set:
   - memory-store.md  — how and when to store memories
   - memory-recall.md — query patterns for effective retrieval
   - memory-prune.md  — TTL policies and cleanup strategies
5. Update GEMINI.md and .antigravity/rules.md with:
   - "Always recall from Qdrant before starting a complex task"
   - "Always store key decisions and code patterns after completing a task"
6. Run: pytest tests/test_memory.py -v

═══════════════════════════════════════════════════════════════
PHASE 8: REPO OPTIMIZATION & FINAL CONFIGURATION
═══════════════════════════════════════════════════════════════
Use @agent:repo-optimizer for cleanup; @agent:docs-master for final docs.

1. Run the existing repo analysis: python tools/auto_issue_finder.py
2. Fix all reported issues (prioritise P0/P1 severity).
3. Run full test suite: pytest tests/ -v --tb=short -x
4. Fix any test failures introduced by phases 1-7.
5. Update the following files:
   - README.md — reflect new capabilities (swarm API, memory router, unified MCP)
   - ANTIGRAVITY_MASTER_GUIDE.md — add Phase 4-7 sections
   - QUICKSTART.md — update setup steps for unified_mcp.json + sync script
   - .env.example — add all new env vars (QDRANT_URL, QDRANT_API_KEY,
     UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN, CONTEXT7_API_KEY, EXA_API_KEY,
     FIRECRAWL_API_KEY, OPENROUTER_API_KEY, TASKMASTER_API_KEY)
6. Run: python scripts/sync_mcp_configs.py to ensure all tool configs are current.
7. Commit all changes with message: "feat: complete multi-agent platform config"

═══════════════════════════════════════════════════════════════
COMPLETION CRITERIA
═══════════════════════════════════════════════════════════════
✓ All 8 phases completed and documented in artifacts/
✓ pytest passes with ≥ 90% of tests green
✓ .agent/unified_mcp.json exists and is valid JSON
✓ scripts/sync_mcp_configs.py runs without errors
✓ backend starts: cd backend && uvicorn main:app --port 8000 (no import errors)
✓ /api/swarm/execute returns a valid response for a simple task
✓ /api/memory/recall returns results for a test query
✓ README.md and ANTIGRAVITY_MASTER_GUIDE.md reflect the complete feature set
```

---

## 2. Phase 1 — Repo Analysis & Pattern Discovery

**Agent**: Any (Copilot, Gemini CLI, Jules)
**Est. time**: 15-20 min

```
TASK: Analyse the Antigravity repository structure and produce a comprehensive
      system map.

Steps:
1. Read these files first (in order):
   - mission.md
   - .antigravity/rules.md
   - GEMINI.md
   - ANTIGRAVITY_MASTER_GUIDE.md
   - DOCUMENTATION_INDEX.md

2. Map the dual-layer architecture:
   BACKEND LAYER (HTTP API):
     backend/main.py            — All FastAPI routes (~2955 lines)
     backend/agent/orchestrator.py — Multi-model routing + caching
     backend/agent/gemini_client.py
     backend/agent/local_client.py
     backend/agent/vertex_client.py
     backend/rag/               — ChromaDB RAG pipeline
     backend/settings_manager.py
     backend/security.py

   SDK LAYER (standalone):
     src/agent.py               — GeminiAgent (Think-Act-Reflect loop)
     src/swarm.py               — SwarmOrchestrator (Router-Worker pattern)
     src/model_rotator.py       — Multi-provider API key rotation
     src/mcp_client.py          — MCP server connection manager
     src/memory.py              — MemoryManager
     src/config.py              — Pydantic Settings
     src/agents/                — RouterAgent, CoderAgent, ReviewerAgent, ResearcherAgent
     src/sandbox/               — Local + Docker code execution
     src/tools/                 — Tool registry (execution, MCP proxy, OpenAI proxy)

   FRONTEND:
     frontend/index.html + frontend/js/app.js — 1222+2914 line vanilla SPA

3. Identify current MCP server configurations:
   Run: python -c "
   import json, glob, os
   configs = glob.glob('**/*.json', recursive=True)
   for c in configs:
       try:
           d = json.load(open(c))
           if 'mcpServers' in d or ('servers' in d and isinstance(d['servers'], dict)):
               print(c, list((d.get('mcpServers') or d.get('servers', {})).keys())[:5])
       except: pass
   "

4. Produce: artifacts/plan_phase1_analysis.md with:
   - Architecture diagram (Mermaid)
   - MCP config matrix (which server is in which config file)
   - Model routing chain diagram
   - List of agents defined in .github/agents/
   - List of skills in .agent/skills/
   - Identified gaps and inconsistencies
```

---

## 3. Phase 2 — Deep GitHub Search (Forked Skill Repos)

**Agent**: `@agent:deep-research`
**Tools**: GitHub MCP (`@github/mcp-server`), Fetch MCP

```
TASK: Search AloSantana's GitHub account for forked/owned repositories
      containing useful skills, MCP configs, and agent definitions.

Steps:
1. Use GitHub MCP tools to list all repos for user AloSantana:
   - Filter for repos with topics: mcp, agent, skills, ai, tools, integration
   - Include forks (many useful configs come from forked repos)

2. For each candidate repo, check for these files/dirs:
   - mcp.json, mcp_config.json, .mcp.json, opencode.json, settings.json
   - agents/, .github/agents/, .agent/agents/
   - skills/, .agent/skills/
   - GEMINI.md, .cursorrules, CLAUDE.md, AGENTS.md (system prompts)
   - requirements.txt, package.json (dependency clues)

3. Extract and categorise findings:
   MCP_SERVERS = {}   # unique server entries not already in .agent/unified_mcp.json
   AGENT_PERSONAS = []  # new agent.md files
   SKILLS = []          # new skill markdown files
   SYSTEM_PROMPTS = []  # new GEMINI.md / CLAUDE.md content worth merging
   CONFIG_TEMPLATES = []  # .env.example entries

4. Merge into main repo:
   - MCP servers → append to .agent/unified_mcp.json (dedup by package name)
   - Agent personas → .github/agents/<name>.agent.md (no overwrite of existing)
   - Skills → .agent/skills/<category>/<name>.md
   - Env vars → append to .env.example (with comments marking source repo)

5. Document all sources in artifacts/plan_phase2_discovery.md:
   Table: | Repo | File | What was merged | Reason |
```

---

## 4. Phase 3 — Documentation Audit & Consolidation

**Agent**: `@agent:docs-master`

```
TASK: Audit all documentation, remove duplication, and update to reflect
      the current codebase.

Current doc inventory (docs/):
  API_QUICK_REFERENCE.md, ARCHITECTURE.md, ARCHITECTURE_ANALYSIS_SUMMARY.md,
  ARCHITECTURE_QUICK_REFERENCE.md, AUTO_ISSUE_FINDER.md, CLOUD_DEPLOY.md,
  DESIGN_SYSTEM.md, GEMINI_CLI_GUIDE.md, JULES_INTEGRATION.md,
  MCP_INSTALLATION_PROMPTS.md, MCP_INTEGRATION_GUIDE.md, MCP_SERVERS_CATALOG.md,
  MCP_STATUS.md, PERFORMANCE_QUICK_REFERENCE.md, PERFORMANCE_REPORT.md,
  PLAN.md, PROGRESS_REPORT.md, README.md, REMOTE_DEPLOYMENT.md, SECURITY.md,
  SETTINGS_GUI.md, SSL_SETUP_GUIDE.md, VERTEX_AI_SETUP.md,
  WINDOWS_QUICK_REFERENCE.md, WINDOWS_SETUP.md, mcp-gateway-setup-guide.md

Steps:
1. Read each doc; flag:
   [DUPLICATE] — same content covered in ANTIGRAVITY_MASTER_GUIDE.md
   [OUTDATED]  — references old package names or deprecated endpoints
   [MISSING]   — topics not covered by any doc

2. Expected MISSING topics to add sections for:
   - Swarm Orchestration (src/swarm.py)
   - Model Rotation (src/model_rotator.py)
   - Sandbox Execution (src/sandbox/)
   - Memory Router API (/api/memory/*)
   - Swarm API (/api/swarm/*)
   - Unified MCP Config (.agent/unified_mcp.json)
   - Model Router Config (.agent/model_router.json)

3. Update ANTIGRAVITY_MASTER_GUIDE.md to include all MISSING sections.

4. For each [DUPLICATE] doc: add a deprecation notice at the top pointing to
   ANTIGRAVITY_MASTER_GUIDE.md. Do NOT delete — preserve history.

5. Update DOCUMENTATION_INDEX.md to reflect changes.

6. Update README.md:
   - Features section must reflect: swarm API, memory router, unified MCP,
     model rotation, 20+ MCP servers, sandbox execution
   - Quick-start must match current start.sh behaviour
   - Architecture diagram must match actual dual-layer design
```

---

## 5. Phase 4 — Tool & Config Optimal Integration

**Agent**: `@agent:architect` (design) + `@agent:rapid-implementer` (code)

```
TASK: Create a unified configuration layer so Antigravity, OpenCode/Crush,
      and Gemini CLI share the same MCP servers and model routing.

Deliverables:

A. .agent/unified_mcp.json
   ─────────────────────────
   Single source of truth for all MCP servers.
   Format: Gemini CLI mcpServers schema (command/args/env/enabled).
   Must include all servers from:
     .agent/mcp_config.json
     .agent/gemini_mcp_settings.json
     .agent/opencode_mcp_config.json
     opencode.json → mcpServers
     .github/copilot/mcp.json → servers
   Dedup by package name. Set enabled=true for no-auth servers.

B. .agent/model_router.json
   ──────────────────────────
   {
     "primary":   {"provider": "gemini",   "model": "gemini-2.5-pro",  "env": "GEMINI_API_KEY"},
     "secondary": {"provider": "vertex",   "model": "gemini-2.5-pro",  "env": "VERTEX_API_KEY"},
     "tertiary":  {"provider": "openrouter","model": "auto",           "env": "OPENROUTER_API_KEY"},
     "local":     {"provider": "ollama",   "model": "${OLLAMA_MODEL}", "url": "http://localhost:11434"}
   }

C. scripts/sync_mcp_configs.py
   ───────────────────────────
   Reads .agent/unified_mcp.json and writes:
   1. ~/.gemini/settings.json  (Gemini CLI format)
   2. ~/.opencode.json         (OpenCode global, merges mcpServers)
   3. .github/copilot/mcp.json (GitHub Copilot format, translates schema)
   Run this script as part of install.sh and configure.sh.

D. Update backend/agent/orchestrator.py
   ───────────────────────────────────
   Load .agent/model_router.json on startup.
   Replace hardcoded provider checks with config-driven routing.
   Preserve existing fallback logic; just make it config-driven.

E. Update install.sh / configure.sh
   ──────────────────────────────────
   Add step: python scripts/sync_mcp_configs.py after dependency install.

Verification:
  pytest tests/test_orchestrator.py -v
  python scripts/sync_mcp_configs.py && echo "Sync OK"
  python -c "import json; json.load(open('.agent/unified_mcp.json')); print('unified_mcp valid')"
```

---

## 6. Phase 5 — MCP Server Discovery & Installation

**Agent**: `@agent:performance-optimizer` (evaluate) + `@agent:rapid-implementer` (install)

```
TASK: Install the highest-value MCP servers and integrate them into
      .agent/unified_mcp.json.

TIER 1 — No API Key (install immediately):
  npm install -g @modelcontextprotocol/server-filesystem
  npm install -g @modelcontextprotocol/server-git
  npm install -g @modelcontextprotocol/server-memory
  npm install -g @modelcontextprotocol/server-sequential-thinking
  npm install -g @modelcontextprotocol/server-fetch
  npm install -g @modelcontextprotocol/server-time
  npm install -g @modelcontextprotocol/server-sqlite
  npm install -g @playwright/mcp
  npm install -g @github/mcp-server
  npm install -g mermaid-mcp-server
  npm install -g @narasimhaponnada/mermaid-mcp-server

TIER 2 — API Key Required (add to unified_mcp.json as enabled=false):
  npm install -g @upstash/context7-mcp          # CONTEXT7_API_KEY
  npm install -g exa-mcp-server                 # EXA_API_KEY
  npm install -g firecrawl-mcp                  # FIRECRAWL_API_KEY
  npm install -g @qdrant/mcp-server             # QDRANT_URL + QDRANT_API_KEY
  npm install -g taskmaster-ai                  # OPENAI_API_KEY or ANTHROPIC_API_KEY
  npm install -g agentops-mcp                   # AGENTOPS_API_KEY

TIER 3 — Advanced (add to unified_mcp.json as enabled=false):
  npm install -g mcp-server-docker              # Docker Desktop required
  npm install -g @notionhq/notion-mcp-server    # NOTION_API_KEY
  npm install -g linear-mcp-server              # LINEAR_API_KEY

After installing each tier:
1. Update .agent/unified_mcp.json with the new entries.
2. Run: python scripts/sync_mcp_configs.py
3. Test: npx <package> --version (verify binary is available)
4. For Tier 1 servers: set enabled=true in unified_mcp.json.

Add all new env vars to .env.example with helpful comments.
```

---

## 7. Phase 6 — Multi-Agent Orchestration

**Agent**: `@agent:architect` (design) + `@agent:rapid-implementer` (implement)

```
TASK: Extend the existing swarm system to support dynamic agents, parallel
      execution, and persistent cross-session state.

Current swarm:
  src/swarm.py → SwarmOrchestrator → [RouterAgent, CoderAgent, ReviewerAgent, ResearcherAgent]
  src/agents/  → 4 agent classes

Required extensions:

A. Dynamic Agent Loading (src/swarm.py)
   ─────────────────────────────────────
   Add SwarmOrchestrator.load_personas(personas_dir=".github/agents/"):
     - Parse *.agent.md frontmatter for: name, role, description, skills
     - Register as dynamic workers alongside the built-in 4
   Add SwarmOrchestrator.execute_parallel(tasks: dict):
     - Run independent worker tasks concurrently using asyncio.gather()

B. New API Endpoints (backend/main.py)
   ────────────────────────────────────
   POST /api/swarm/execute
     Body: {"task": str, "agents": list[str] | null, "parallel": bool}
     Returns: {"result": str, "agents_used": list, "steps": list, "duration_ms": int}

   GET /api/swarm/status
     Returns: {"agents": [{"name", "role", "available"}], "active_tasks": int}

   POST /api/swarm/register
     Body: {"name": str, "role": str, "system_prompt": str, "skills": list}
     Returns: {"registered": bool, "agent_id": str}

C. Persistent Swarm Memory
   ─────────────────────────
   After each SwarmOrchestrator.execute() call:
     - Store task + result summary in Qdrant (collection: "swarm-history")
     - Store agent performance metrics in Redis (key: "swarm:metrics:<agent_name>")
   On execute() start:
     - Recall top-3 similar past tasks from Qdrant to pre-load context

D. Skill-Aware Routing
   ──────────────────
   Update RouterAgent (src/agents/__init__.py) to:
     - Read available skills from .agent/skills/
     - Match task keywords to skill categories
     - Include relevant skill docs in worker system prompts

Verification:
  pytest tests/test_swarm.py -v
  curl -X POST http://localhost:8000/api/swarm/execute \
       -H "Content-Type: application/json" \
       -d '{"task": "Write a hello world FastAPI endpoint"}'
```

---

## 8. Phase 7 — Smart Memory & Automated Learning

**Agent**: `@agent:architect` (design) + `@agent:rapid-implementer` (implement)

```
TASK: Build a three-tier memory system with automated capture and recall.

Architecture:
  ┌─────────────────────────────────────────────────────┐
  │              MEMORY ROUTER                          │
  │  /api/memory/store → routes to appropriate tier     │
  │  /api/memory/recall → queries all tiers, ranks     │
  └─────────┬───────────────┬───────────────────────────┘
            ↓               ↓               ↓
      SHORT-TERM       MID-TERM         LONG-TERM
      MCP Memory       Redis KV         Qdrant Vector
      (in-session)     (30d TTL)        (permanent)
      entity graph     code patterns    semantic search

Implementation steps:

1. Create backend/memory_router.py:
   - FastAPI APIRouter with prefix /api/memory
   - MemoryRouter class with store(), recall(), forget() methods
   - Tier routing logic:
       code/patterns → mid-term (Redis) + long-term (Qdrant)
       facts/decisions → long-term (Qdrant)
       session context → short-term (MCP Memory)

2. Register in backend/main.py:
   from memory_router import memory_router
   app.include_router(memory_router)

3. Auto-capture hooks in backend/agent/orchestrator.py:
   After process_request() success:
     → extract_key_facts(response) → store in memory
   After process_request() failure:
     → store_lesson(error, context, agent) in Redis with key "lessons:<hash>"

4. Smart context injection in orchestrator.py:
   Before every agent call:
     → relevant_memories = await memory.recall(task, top_k=5)
     → prepend to system prompt as "## Relevant Past Context\n..."

5. Skill files:
   .agent/skills/memory/store-patterns.md   — when and what to store
   .agent/skills/memory/recall-patterns.md  — how to query effectively
   .agent/skills/memory/memory-hygiene.md   — TTL policies, dedup

6. Update GEMINI.md and .antigravity/rules.md:
   Add rule: "Before any complex task → recall from memory"
   Add rule: "After any task completion → store key facts and code patterns"

Verification:
  pytest tests/test_memory.py -v
  curl -X POST http://localhost:8000/api/memory/store \
       -d '{"content": "FastAPI routes use async def", "type": "pattern"}'
  curl "http://localhost:8000/api/memory/recall?q=FastAPI+patterns"
```

---

## 9. Phase 8 — Repo Optimization & Final Config

**Agent**: `@agent:repo-optimizer` (cleanup) + `@agent:docs-master` (final docs)

```
TASK: Clean the repo, fix all issues, run tests, and update all documentation
      to reflect the complete, configured system.

Steps:
1. Run issue finder: python tools/auto_issue_finder.py > artifacts/logs/issues.txt
2. Fix all P0 and P1 issues found.
3. Run full test suite: pytest tests/ -v --tb=short --maxfail=10 -q
4. Fix any test failures (DO NOT delete tests to make them pass).
5. Run: python scripts/sync_mcp_configs.py (final sync)

Documentation updates:

README.md:
  - Features: add Swarm API, Memory Router, Unified MCP, Model Rotation
  - Architecture section: update diagram with new components
  - Quickstart: reference .agent/unified_mcp.json and sync script

ANTIGRAVITY_MASTER_GUIDE.md:
  - Sections 9-16 for all new phases
  - Updated system prompt with new capabilities

QUICKSTART.md:
  - Step 4: python scripts/sync_mcp_configs.py
  - Step 5: test with /api/swarm/execute

.env.example:
  Add all new variables:
    QDRANT_URL=https://your-cluster.qdrant.tech
    QDRANT_API_KEY=
    UPSTASH_REDIS_URL=https://your-db.upstash.io
    UPSTASH_REDIS_TOKEN=
    CONTEXT7_API_KEY=
    EXA_API_KEY=
    FIRECRAWL_API_KEY=
    OPENROUTER_API_KEY=
    AGENTOPS_API_KEY=
    TASKMASTER_API_KEY=
    OLLAMA_MODEL=llama3

Final commit message:
  "feat: complete multi-agent platform — swarm API, memory router, unified MCP, model rotation"
```

---

## 10. Agent Quick-Reference

| When you need to... | Use agent |
|---|---|
| Research repos, technologies, or problems deeply | `@agent:deep-research` |
| Design architecture or system structure | `@agent:architect` |
| Implement code quickly end-to-end | `@agent:rapid-implementer` |
| Create or update documentation | `@agent:docs-master` |
| Review code for quality and security | `@agent:code-reviewer` |
| Debug an issue or trace a root cause | `@agent:debug-detective` |
| Optimize performance or memory usage | `@agent:performance-optimizer` |
| Set up repo tooling or fix CI/config | `@agent:repo-optimizer` |
| Create or fix tests | `@agent:testing-stability-expert` |
| Design DevOps / Docker / CI/CD | `@agent:devops-infrastructure` |

---

## 11. Key Repo Paths

| Path | Purpose |
|---|---|
| `backend/main.py` | All FastAPI routes (~2955 lines) |
| `backend/agent/orchestrator.py` | Multi-model routing + cache |
| `src/swarm.py` | SwarmOrchestrator (Router-Worker) |
| `src/model_rotator.py` | API key rotation + rate-limit handling |
| `src/mcp_client.py` | MCP server connection manager |
| `src/config.py` | Pydantic settings |
| `src/agent.py` | GeminiAgent (Think-Act-Reflect) |
| `.agent/unified_mcp.json` | **NEW** — single source of truth for MCP |
| `.agent/model_router.json` | **NEW** — model fallback chain config |
| `scripts/sync_mcp_configs.py` | **NEW** — sync unified config to all tools |
| `backend/memory_router.py` | **NEW** — three-tier memory API |
| `.github/agents/` | 12 agent persona definitions |
| `.agent/skills/` | Skill knowledge base |
| `.agent/mcp_config.json` | Current MCP config (SDK) |
| `.agent/gemini_mcp_settings.json` | Gemini CLI MCP config |
| `.agent/opencode_mcp_config.json` | OpenCode MCP config |
| `opencode.json` | OpenCode local config |
| `.github/copilot/mcp.json` | GitHub Copilot MCP config |
| `ANTIGRAVITY_MASTER_GUIDE.md` | Canonical reference document |
| `docs/MCP_SERVERS_CATALOG.md` | Curated MCP server list |
| `.antigravity/rules.md` | Project coding standards |
| `GEMINI.md` | YOLO mode + workspace directives |
| `artifacts/` | Plans, logs, and agent outputs |
