# ANTIGRAVITY WORKSPACE

**Generated:** 2026-03-01 | **Commit:** 8be6068 | **Branch:** main

## OVERVIEW

AI-powered development workspace built on FastAPI + vanilla JS. Features a Gemini-based agent system with router-worker swarm orchestration, MCP tool integration, RAG-based context retrieval, model rotation across multiple providers (Gemini, Vertex, OpenAI, OpenRouter), and sandboxed code execution (local + Docker).

## STRUCTURE

```
Antigravitys/
├── backend/           # FastAPI server — main.py is 2955-line monolith (ALL routes here)
│   ├── agent/         # Multi-client orchestrator (Gemini, Vertex, local/Ollama)
│   ├── cli/           # Gemini CLI interface
│   ├── rag/           # ChromaDB-based vector store + ingestion
│   └── utils/         # Performance, debug logging, ngrok, platform detection
├── src/               # Agent SDK — Gemini agent, swarm system, MCP client, model rotator
│   ├── agents/        # Swarm workers (coder, reviewer, researcher, router)
│   ├── sandbox/       # Code execution (local + Docker, factory pattern)
│   └── tools/         # Tool registry (MCP tools, OpenAI proxy, execution tool)
├── frontend/          # Vanilla JS SPA — NO framework, NO build step
│   ├── js/app.js      # Single 2914-line file — entire frontend logic
│   └── css/           # style.css + legacy.css
├── tests/             # Pytest — unit/integration/e2e/performance, 430-line conftest.py
├── tools/             # Dev utilities (auto_issue_finder, health_monitor, split_monolith)
├── .github/agents/    # 12 agent persona definitions (.agent.md files)
├── .antigravity/      # rules.md — project directives and coding standards
├── nginx/             # Reverse proxy config for Docker deployment
├── drop_zone/         # File watcher directory — auto-ingests into RAG
├── artifacts/         # Agent output artifacts (plans, logs)
└── docs/              # 26 markdown files — architecture, security, deployment guides
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/main.py` | All routes in single file. Search for `@app.` decorators |
| WebSocket handling | `backend/main.py` | Search `@app.websocket`. Reconnection with exponential backoff |
| Agent orchestration | `backend/agent/orchestrator.py` | Multi-model routing (Gemini/Vertex/local), caching, dual-agent sessions |
| Swarm system | `src/swarm.py` + `src/agents/` | Router-worker pattern. `MessageBus` + `SwarmOrchestrator` |
| Model rotation | `src/model_rotator.py` | API key rotation, rate limit detection, health monitoring (522 lines) |
| MCP integration | `src/mcp_client.py` | MCP server connections, tool discovery |
| Settings/config | `backend/settings_manager.py` + `src/config.py` | Pydantic Settings, env-based config |
| Security | `backend/security.py` | Input validation, file sanitization, rate limiting |
| RAG pipeline | `backend/rag/` | ChromaDB store + file ingestion pipeline |
| File watcher | `backend/watcher.py` | Watchdog-based, monitors `drop_zone/`, debounced |
| Frontend UI | `frontend/index.html` + `frontend/js/app.js` | 1222-line HTML + 2914-line JS |
| Agent personas | `.github/agents/*.agent.md` | 12 agent definitions loaded by `backend/agent/manager.py` |
| Project rules | `.antigravity/rules.md` | Coding standards, artifact protocol, YOLO mode |
| Tests | `tests/` | See `tests/AGENTS.md` |
| Docker deploy | `docker-compose.yml` | 4 services: backend, frontend(nginx), chromadb, redis |
| CI/CD | `.github/workflows/` | 7 workflows: ci, test, security, deploy (GCP, DigitalOcean) |

## CONVENTIONS

- **Type hints**: ALL Python functions MUST use strict type hints (`typing` module)
- **Docstrings**: Google-style docstrings on all functions/classes
- **Data models**: Pydantic `BaseModel` for all request/response schemas
- **Tools**: External API calls MUST be wrapped in dedicated functions in `tools/` or `src/tools/`
- **Linter**: Ruff — line-length 120, indent 4. Ignores: E402, E701, E722, F401, F811, F841
- **Tests**: Pytest with markers (`unit`, `integration`, `e2e`, `slow`, `asyncio`, `requires_ollama`, `requires_gemini`). Coverage on `backend/` + `src/`. Max 5 failures then stop.
- **Async**: `asyncio_mode = auto` in pytest. FastAPI async endpoints throughout.
- **Artifact protocol**: Complex tasks → create `artifacts/plan_[task_id].md` first, test logs → `artifacts/logs/`

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** add new route files — ALL routes live in `backend/main.py` (monolith pattern)
- **DO NOT** add frontend build tools — vanilla JS, served statically via nginx
- **DO NOT** summarize excessively — project uses large context windows (1M+ tokens)
- **NEVER** suppress type errors with `as any`, `@ts-ignore`, `@ts-expect-error`
- **ALWAYS** run `pytest` after modifying logic
- **ALWAYS** read `mission.md` before architectural decisions
- **ALWAYS** read `.antigravity/rules.md` for project directives
- Rate limiter is auto-disabled during pytest (`if "pytest" in sys.modules`)

## UNIQUE STYLES

- **Dual-layer architecture**: `backend/` = FastAPI HTTP server; `src/` = Agent SDK (can run independently)
- **Agent personas**: 12 `.agent.md` files in `.github/agents/` define specialized agents with priority rankings (jules=10 highest → docs-master=1 lowest)
- **Multi-provider model routing**: Orchestrator tries Gemini → Vertex → local(Ollama) with caching and handoff
- **Drop zone pattern**: Files placed in `drop_zone/` are auto-ingested into ChromaDB via watchdog
- **.cursorrules**: Redirects to `.antigravity/rules.md` for agent instructions
- **YOLO mode**: All terminal/file operations auto-approved, no confirmation prompts

## COMMANDS

```bash
# Local dev
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# Full stack (Docker)
docker-compose up --build                     # All services
docker-compose --profile with-ollama up       # Include local Ollama

# Tests
pytest                                        # Full suite (coverage on backend/ + src/)
pytest tests/unit/                            # Unit only
pytest -m "not requires_ollama"               # Skip Ollama-dependent tests

# Start scripts
./start.sh                                    # Linux/Mac
.\start.ps1                                   # Windows (sets YOLO mode)

# Swarm demo
python src/swarm_demo.py
```

## SERVICES (docker-compose)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| backend | Custom (Python 3.11) | 8000 | FastAPI server |
| frontend | nginx:alpine | 3000/80 | Static file serving |
| chromadb | chromadb/chroma | 8001 | Vector store for RAG |
| redis | redis:7-alpine | 6379 | Caching (password: `antigravity`) |
| ollama | ollama/ollama | 11434 | Local AI (optional profile) |

## NOTES

- `backend/main.py` is 2955 lines — search by endpoint path, not scrolling
- Frontend has NO package.json, NO node_modules — it's pure HTML/CSS/JS served by nginx
- `src/config.py` uses `pydantic-settings` with `.env` file — check `.env.example` for all vars
- `backend/agent/orchestrator.py` has response caching with TTL (default 300s, configurable via `CACHE_TTL_SECONDS`)
- Signal handlers (SIGTERM/SIGINT) for graceful shutdown with 30s timeout
- `tests/conftest.py` adds both project root AND `backend/` to `sys.path`
- The `data/` directory exists but is empty — used for runtime data storage
