# BACKEND — FastAPI Server

## OVERVIEW

FastAPI monolith serving REST API + WebSocket endpoints. All routes in `main.py` (2955 lines).

## STRUCTURE

```
backend/
├── main.py              # ALL routes, lifespan, middleware, WebSocket handlers
├── agent/               # AI model orchestration
│   ├── orchestrator.py  # Multi-model routing (Gemini → Vertex → Ollama), caching, dual-agent sessions
│   ├── gemini_client.py # Google GenAI client
│   ├── vertex_client.py # Vertex AI client
│   ├── local_client.py  # Ollama/local model client
│   └── manager.py       # Loads .agent.md persona files, queries by expertise
├── cli/
│   └── gemini_cli.py    # Terminal-based Gemini chat interface
├── rag/
│   ├── store.py         # ChromaDB vector store wrapper
│   └── ingest.py        # File ingestion pipeline (used by watcher)
├── utils/
│   ├── debug_logger.py  # Structured debug logging
│   ├── performance.py   # Performance monitoring endpoints (822 lines)
│   ├── ngrok_manager.py # Ngrok tunnel management for remote access
│   ├── platform_detect.py # OS/platform detection
│   ├── remote_config.py # Remote access configuration
│   └── file_utils.py    # File operation helpers
├── security.py          # Input validation, sanitization, rate limit helpers
├── settings_manager.py  # Runtime settings CRUD (694 lines, persists to JSON)
├── conversation_manager.py # SQLite-backed conversation history (607 lines)
├── artifact_manager.py  # Artifact storage and retrieval (494 lines)
├── watcher.py           # Watchdog file monitor on drop_zone/ → RAG ingestion
├── autopilot.py         # Autonomous agent loop
└── context_fusion.py    # Context merging from multiple sources
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add REST endpoint | `main.py` | Find similar endpoint, add nearby. Uses `@app.get/post/put/delete` |
| Add WebSocket endpoint | `main.py` | Search `@app.websocket`. Connection manager pattern |
| Change model selection | `agent/orchestrator.py` | `active_model` env var, `_select_model()` method |
| Add agent persona | `.github/agents/` (project root) | Create `name.agent.md`, auto-loaded by `manager.py` |
| Modify RAG behavior | `rag/store.py` + `rag/ingest.py` | ChromaDB operations, file chunking |
| Add performance metrics | `utils/performance.py` | `add_performance_endpoints()` called from `main.py` |
| Configure remote access | `utils/ngrok_manager.py` + `utils/remote_config.py` | Env var `REMOTE_ACCESS=true` |

## CONVENTIONS

- **All routes in main.py** — no blueprints, no separate route files
- Global instances initialized in `lifespan()` context manager, not module level
- Rate limiting via `slowapi` (disabled in test via `sys.modules` check)
- Graceful shutdown: SIGTERM/SIGINT → `shutdown_event` → 30s timeout
- Path resolution: `project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — parent of `backend/`
- Imports assume `backend/` is working dir (e.g., `from agent.orchestrator import Orchestrator`)

## ANTI-PATTERNS

- **DO NOT** create separate route files — monolith pattern is intentional
- **DO NOT** initialize services at module level — use `lifespan()` context manager
- **DO NOT** skip input validation — use `security.py` helpers for all user input
- Agent priorities in orchestrator: jules=10 (highest) → docs-master=1 (lowest)

## NOTES

- `sys.path` manipulation in `conftest.py` adds both root and `backend/` — imports work differently in test vs runtime
- `requirements.txt` is at project root, not in `backend/`
- Orchestrator cache: OrderedDict-based LRU, TTL from `CACHE_TTL_SECONDS` env (default 300s)
- `conversation_manager.py` uses SQLite (`conversations.db` at project root)
- `settings_manager.py` persists to JSON file, supports runtime reload
