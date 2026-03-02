# Smart Memory System Integration for Antigravity

> **Complete multi-layer memory architecture for cross-platform agent learning and workflow optimization**

---

## Overview

The Antigravity workspace implements a 3-layer memory architecture that enables agents to learn, remember decisions, and share context across sessions and platforms:

```
┌────────────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                          │
│                                                                 │
│  Layer 1: EPHEMERAL (Session-Only)                             │
│  ├─ MCP Memory Server (in-session knowledge graph)             │
│  └─ Antigravity Backend Context (current request context)      │
│                                                                 │
│  Layer 2: PERSISTENT LOCAL (Workspace-Specific)                │
│  ├─ ChromaDB (RAG from drop_zone + codebase)                   │
│  ├─ Hivemind (.hive/ - swarm-tools semantic memory)            │
│  └─ SQLite (structured data storage)                           │
│                                                                 │
│  Layer 3: PERSISTENT CLOUD (Cross-Session, Multi-Device)       │
│  ├─ Qdrant Cloud (vector memory, architectural decisions)      │
│  └─ Upstash Redis (KV store, session handoffs, flags)          │
└────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Ephemeral Memory (In-Session)

### MCP Memory Server

**What it does**: Creates a knowledge graph during the current session. Entities and relationships persist only while the agent is running.

**When to use**:
- Track entities mentioned in the current conversation
- Build temporary relationship graphs
- Store facts needed only for the current task

**Configuration** (already enabled in `opencode.json`):
```json
{
  "mcp": {
    "memory": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
      "enabled": true
    }
  }
}
```

**Example usage** (in OpenCode or Gemini CLI):
```
"Store this fact: The auth system uses PKCE flow"
→ Agent uses memory MCP to create_entities([{
    "name": "auth-system",
    "entityType": "system",
    "observations": ["uses PKCE flow"]
  }])

Later in same session:
"What auth flow do we use?"
→ Agent queries memory, retrieves "PKCE flow"
```

---

## Layer 2: Persistent Local Memory

### 2.1 ChromaDB (Antigravity RAG)

**Location**: `backend/rag/chroma_store.py`

**What it does**: Ingests files from `drop_zone/` and codebase, creates embeddings, enables semantic search.

**Configuration** (.env):
```bash
# ChromaDB uses local embeddings — no API key needed
RAG_MAX_FILE_SIZE_MB=10
RAG_MAX_CHUNK_SIZE=2000
RAG_CHUNK_OVERLAP=200
RAG_BATCH_SIZE=5
RAG_MAX_CONCURRENT_EMBEDDINGS=10
```

**API Endpoints**:
```bash
# Ingest file
POST http://localhost:8000/api/rag/ingest
{ "file_path": "drop_zone/research.pdf", "metadata": {"source": "research"} }

# Query
POST http://localhost:8000/api/rag/query
{ "query": "authentication patterns", "top_k": 5 }
```

**Auto-Ingestion**: Files placed in `drop_zone/` are watched by `backend/watcher.py` and auto-ingested.

**MCP Integration** (optional, currently disabled):
```json
{
  "mcp": {
    "chroma": {
      "type": "local",
      "command": ["uvx", "chroma-mcp", "--mode", "embedded", "--data-dir", "./.chroma"],
      "enabled": false
    }
  }
}
```

### 2.2 Hivemind (swarm-tools Semantic Memory)

**Location**: `.hive/hivemind/`

**What it does**: Stores embeddings of successful task patterns, anti-patterns, and agent learnings. Used by swarm-tools coordinator to find similar past tasks.

**Configuration**:
```bash
# Requires Ollama for embeddings
OLLAMA_MODEL=nomic-embed-text  # or: mxbai-embed-large
OLLAMA_HOST=http://localhost:11434
```

**Setup**:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Initialize swarm-tools
npm install -g opencode-swarm-plugin
swarm setup
swarm init   # creates .hive/ directory
swarm doctor # verifies Ollama connection
```

**How it works**:
```
/swarm "Implement OAuth2 authentication"
  → Coordinator queries Hivemind: "auth patterns"
  → Retrieves: "Past auth tasks used PKCE, avoid implicit flow"
  → Applies learnings to current task
  → After completion, stores new patterns back to Hivemind
```

**Manual storage**:
```bash
# Store a learning (from OpenCode)
/hive store "Always use PKCE for OAuth2, not implicit flow. Reduces XSS risk."
```

### 2.3 SQLite (Structured Data)

**Location**: `./data.db`

**What it does**: Stores structured relational data (task history, agent metrics, configurations).

**MCP Integration** (currently disabled):
```json
{
  "mcp": {
    "sqlite": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite", "--db-path", "./data.db"],
      "enabled": false
    }
  }
}
```

**Enable for**: Multi-agent task queues, audit logs, structured settings storage.

---

## Layer 3: Persistent Cloud Memory

### 3.1 Qdrant (Vector Memory)

**What it does**: Cloud vector database for cross-session architectural decisions, design patterns, and agent discoveries.

**Why cloud?**: Shared across devices, persists indefinitely, accessible from Antigravity + OpenCode + Gemini CLI.

**Setup**:
```bash
# Get free cloud instance: https://cloud.qdrant.io
# Create collection: "antigravity-agent-memory"

# Add to .env:
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
```

**Configuration** (already enabled in `opencode.json` and `.agent/gemini_settings.json`):
```json
{
  "mcp": {
    "qdrant": {
      "command": ["uvx", "mcp-server-qdrant"],
      "enabled": true,
      "environment": {
        "QDRANT_URL": "${QDRANT_URL}",
        "QDRANT_API_KEY": "${QDRANT_API_KEY}",
        "COLLECTION_NAME": "antigravity-agent-memory",
        "EMBEDDING_PROVIDER": "fastembed"
      }
    }
  }
}
```

**Usage pattern**:
```
Session 1 (OpenCode):
  "Store this decision: Use Redis for session state, not JWT cookies"
  → Agent: qdrant-store({
       collection: "antigravity-agent-memory",
       text: "Session state: Redis preferred over JWT cookies for better invalidation control",
       metadata: { type: "architecture-decision", topic: "auth", date: "2026-03-02" }
     })

Session 2 (Gemini CLI, next day):
  "What's our session state strategy?"
  → Agent: qdrant-find({
       collection: "antigravity-agent-memory",
       query: "session state strategy",
       limit: 3
     })
  → Retrieves Session 1's decision
```

### 3.2 Upstash Redis (Cross-Session KV Store)

**What it does**: Serverless Redis for session handoffs, feature flags, cross-agent state.

**Why cloud?**: REST API = accessible from any platform, no persistent connection needed.

**Setup**:
```bash
# Get free instance: https://console.upstash.com/redis

# Add to .env:
UPSTASH_REDIS_REST_URL=https://your-db.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token
```

**Configuration** (already enabled):
```json
{
  "mcp": {
    "upstash": {
      "command": ["npx", "-y", "@upstash/mcp-server"],
      "enabled": true,
      "environment": {
        "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
        "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}"
      }
    }
  }
}
```

**Usage patterns**:

**Session handoff**:
```
Session 1 (OpenCode, Sisyphus agent):
  "I've completed the auth routes. Handoff to testing agent."
  → upstash-set("session:handoff:auth-testing", JSON.stringify({
       from: "sisyphus",
       to: "testing-stability-expert",
       context: "Auth routes implemented in backend/main.py:1234-1456",
       next_steps: ["Write pytest tests", "Test PKCE flow", "Test token refresh"]
     }))

Session 2 (Antigravity backend, testing agent):
  → upstash-get("session:handoff:auth-testing")
  → Retrieves full context, continues work
```

**Feature flags**:
```
# Enable experimental feature
upstash-set("feature:experimental-swarm-v2", "true")

# Check flag before using feature
flag = upstash-get("feature:experimental-swarm-v2")
if flag == "true": use_swarm_v2()
```

**Agent coordination**:
```
# Mark task as claimed
upstash-set("task:oauth2-impl:claimed-by", "hephaestus", { ttl: 3600 })

# Another agent checks before starting
owner = upstash-get("task:oauth2-impl:claimed-by")
if owner: skip_task()
```

---

## Automated Learning Workflows

### Workflow 1: Post-Task Pattern Storage

**Trigger**: After successful task completion

**Process**:
1. Agent identifies successful patterns (e.g., "JWT approach worked well")
2. Stores to Hivemind (swarm-tools): `/hive store "JWT approach: use RS256, store public keys in Redis"`
3. Stores to Qdrant (cross-platform): `qdrant-store({ text: "JWT implementation pattern: RS256 + Redis key store", metadata: { type: "pattern", domain: "auth" } })`
4. Stores to Upstash (metrics): `upstash-incr("success:auth-tasks")`

**Auto-trigger in OpenCode**:
Add to `.opencode/oh-my-opencode.jsonc`:
```jsonc
{
  "hooks": {
    "after_task_success": {
      "enabled": true,
      "command": "/hive store-success"
    }
  }
}
```

### Workflow 2: Pre-Task Context Retrieval

**Trigger**: Before starting new task

**Process**:
1. Query Qdrant: `qdrant-find({ query: "authentication best practices", limit: 5 })`
2. Query Hivemind: `/hive query "auth patterns"`
3. Query Upstash: `upstash-get("arch:decision:auth-strategy")`
4. Synthesize all sources → provide to agent as context

**Auto-trigger in Antigravity backend**:
```python
# In backend/agent/orchestrator.py, before task execution:
async def _enrich_context_from_memory(self, task: str) -> dict:
    """Fetch relevant memories from all layers."""
    context = {}

    # Query Qdrant via MCP (if available)
    if self.qdrant_client:
        context["vector_memories"] = await self.qdrant_client.search(task, limit=5)

    # Query ChromaDB (local RAG)
    if self.rag_store:
        context["rag_results"] = await self.rag_store.query(task, top_k=5)

    # Query Upstash (architectural decisions)
    if self.redis_client:
        context["arch_decisions"] = await self.redis_client.get(f"arch:*{task}*")

    return context
```

### Workflow 3: Anti-Pattern Detection

**Goal**: Prevent repeating mistakes

**Implementation**:
1. Store failures: `qdrant-store({ text: "Anti-pattern: implicit OAuth2 flow led to XSS vulnerability", metadata: { type: "anti-pattern", severity: "high" } })`
2. Before task: `qdrant-find({ query: task_description })`
3. If anti-pattern found: warn agent or auto-skip approach

**Example**:
```python
# In Antigravity orchestrator:
async def _check_anti_patterns(self, plan: str) -> List[str]:
    """Query for known anti-patterns related to this plan."""
    warnings = []
    results = await self.qdrant_client.search(plan, filter={"type": "anti-pattern"})
    for result in results:
        if result.score > 0.8:  # high similarity
            warnings.append(f"⚠️ Anti-pattern detected: {result.text}")
    return warnings
```

---

## Smart Workflow Automation

### Auto-Documentation from Memory

**Goal**: Generate docs from accumulated knowledge

**Implementation**:
```bash
# In OpenCode or Gemini CLI:
"Generate a document summarizing all our architectural decisions"

→ Agent queries Qdrant: filter = { type: "architecture-decision" }
→ Retrieves all decisions
→ Synthesizes into markdown
→ Writes to docs/ARCHITECTURE_DECISIONS.md
```

**Automated trigger** (cron or GitHub Actions):
```yaml
# .github/workflows/auto-docs.yml
name: Update Architecture Docs
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Call Antigravity backend to generate docs from memory
          curl -X POST http://localhost:8000/api/memory/export-docs \
            -H "Content-Type: application/json" \
            -d '{"doc_type": "architecture", "output": "docs/ARCH.md"}'
      - run: git commit -am "docs: auto-update from memory" && git push
```

### Learning from Code Reviews

**Goal**: Store reviewer feedback for future reference

**Implementation**:
```python
# In backend, after code review:
async def store_review_learnings(review_id: str, feedback: List[str]):
    """Store code review feedback to memory."""
    for item in feedback:
        # Store to Qdrant
        await qdrant_client.store({
            "text": item,
            "metadata": {
                "type": "code-review-learning",
                "review_id": review_id,
                "date": datetime.now().isoformat()
            }
        })

        # Also store to Hivemind if pattern-like
        if is_pattern(item):
            subprocess.run(["swarm", "hive", "store", item])
```

**Retrieval during code generation**:
```python
# Before generating code:
learnings = await qdrant_client.search(
    f"code review feedback for {file_type}",
    filter={"type": "code-review-learning"},
    limit=10
)
# Inject learnings into agent prompt
```

---

## Configuration Checklist

### Essential (Minimum Memory Setup)

```bash
# Layer 1 (Ephemeral) — already configured
✓ MCP Memory Server enabled in opencode.json

# Layer 2 (Local Persistent)
✓ ChromaDB configured in backend/rag/
✓ Watcher auto-ingesting drop_zone/ files
□ swarm-tools installed + Ollama running for Hivemind

# Layer 3 (Cloud Persistent)
□ Qdrant Cloud account + collection created
□ QDRANT_URL and QDRANT_API_KEY in .env
□ Upstash Redis account created
□ UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN in .env
```

### Optimal (Full Stack)

```bash
# All of Essential, plus:
□ SQLite MCP enabled for structured data
□ Chroma MCP enabled for direct vector queries from agents
□ Hivemind integrated with Antigravity backend
□ Auto-documentation workflow set up
□ Code review learning pipeline active
□ Anti-pattern detection enabled
```

---

## Quick Start: Enable Full Memory Stack

```bash
# 1. Install swarm-tools + Ollama
npm install -g opencode-swarm-plugin
swarm setup && swarm init
ollama pull nomic-embed-text

# 2. Create cloud accounts
# Qdrant: https://cloud.qdrant.io (free tier)
# Upstash: https://console.upstash.com/redis (free tier)

# 3. Update .env with credentials
echo "QDRANT_URL=https://your-cluster.cloud.qdrant.io" >> .env
echo "QDRANT_API_KEY=your_key" >> .env
echo "UPSTASH_REDIS_REST_URL=https://your-db.upstash.io" >> .env
echo "UPSTASH_REDIS_REST_TOKEN=your_token" >> .env

# 4. Restart all services
docker-compose down && docker-compose up -d
cd backend && python main.py

# 5. Test memory stack
# In OpenCode:
/swarm query "test query"  # Tests Hivemind
# In Gemini CLI:
"Use qdrant to store: This is a test memory"  # Tests Qdrant MCP
"Use upstash to set test:key to test-value"  # Tests Upstash MCP
```

---

## Memory Best Practices

1. **Layer Selection**:
   - Ephemeral (MCP Memory): Current session context only
   - Local (ChromaDB/Hivemind): Workspace-specific, fast access
   - Cloud (Qdrant/Upstash): Cross-device, persistent, slower

2. **Metadata Tagging**:
   ```json
   {
     "type": "architecture-decision" | "pattern" | "anti-pattern" | "code-review",
     "domain": "auth" | "ui" | "backend" | "devops",
     "severity": "low" | "medium" | "high" | "critical",
     "date": "2026-03-02T10:30:00Z",
     "source": "sisyphus" | "copilot-agent" | "human-review"
   }
   ```

3. **Memory Hygiene**:
   - Archive old decisions: `qdrant-update({ id, metadata: { archived: true } })`
   - Expire temporary flags: `upstash-set("temp:flag", "value", { ttl: 3600 })`
   - Periodic cleanup: `swarm hive prune --older-than=30d`

4. **Cross-Platform Syncing**:
   - Qdrant and Upstash are always in sync (cloud-hosted)
   - ChromaDB and Hivemind are local — use git LFS to version `.hive/` if needed
   - MCP Memory does NOT persist — use it only for in-session graphs

---

**Next Steps**: See `docs/MASTER_AI_AGENT_PROMPT.md` Section 11 for cross-platform model router integration.
