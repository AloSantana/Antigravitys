# ANTIGRAVITY WORKSPACE

**Generated:** 2026-03-12 | **Commit:** 8be6068 | **Branch:** main

## OVERVIEW

AI-powered development workspace built on FastAPI + vanilla JS. Features a Gemini-based agent system with router-worker swarm orchestration, MCP tool integration, RAG-based context retrieval, model rotation across multiple providers (Gemini, Vertex, OpenAI, OpenRouter), and sandboxed code execution (local + Docker).

## PROJECT RULES (ALWAYS READ FIRST)

- **Cursor Rules**: `.cursorrules` redirects to `.antigravity/rules.md`
- **Project Directives**: `.antigravity/rules.md` contains:
  - Artifact-First protocol: create `artifacts/plan_[task_id].md` before coding
  - Type hints required (strict, using `typing` module)
  - Google-style docstrings on ALL functions/classes
  - Pydantic models for all data structures/schemas
  - YOLO mode: all terminal/file operations auto-approved

## STRUCTURE

```
Antigravitys/
├── backend/           # FastAPI server — main.py is monolith (ALL routes)
├── src/               # Agent SDK — Gemini agent, swarm, MCP client, model rotator
├── frontend/          # Vanilla JS SPA — NO build step
├── tests/             # Pytest suite (see tests/AGENTS.md)
├── .github/agents/    # 12 agent persona definitions
└── .antigravity/      # rules.md — project directives
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/main.py` | All routes in single file |
| WebSocket handling | `backend/main.py` | Search `@app.websocket` |
| Agent orchestration | `backend/agent/orchestrator.py` | Multi-model routing |
| Swarm system | `src/swarm.py` + `src/agents/` | Router-worker pattern |
| MCP integration | `src/mcp_client.py` | MCP server connections |
| Settings/config | `backend/settings_manager.py` + `src/config.py` | Pydantic Settings |
| Tests | `tests/` | See `tests/AGENTS.md` |

## COMMANDS

```bash
# Local dev
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# Docker
docker-compose up --build
docker-compose --profile with-ollama up

# Tests
pytest                              # Full suite
pytest tests/unit/                  # Unit only
pytest tests/test_foo.py::test_bar # Single test
pytest -m "not requires_ollama"    # Skip Ollama tests
pytest --cov=backend --cov=src     # With coverage

# Linting (Ruff)
ruff check . && ruff format .       # Lint + format

# Start scripts
./start.sh          # Linux/Mac
.\start.ps1          # Windows (YOLO mode)
```

## CODE STYLE

### Python
- **Type Hints**: ALL functions MUST use strict type hints (`typing` module)
- **Docstrings**: Google-style on ALL functions/classes
- **Data Models**: Pydantic `BaseModel` for all request/response schemas
- **Imports**: Absolute imports, grouped (stdlib, third-party, local)
- **Async**: Use `async/await` for I/O operations

### Ruff Config (pyproject.toml)
- Line length: 120, Indent: 4
- Ignores: E402, E701, E722, F401, F811, F841

### JavaScript/Frontend
- **ES6+**: Modern syntax, vanilla JS (no frameworks)

## TESTING

### Pytest Markers (REQUIRED)
- `unit`, `integration`, `e2e`, `slow`, `asyncio`, `requires_ollama`, `requires_gemini`
- `--strict-markers`: Undefined markers fail
- `--maxfail=5`: Stop after 5 failures
- `asyncio_mode = auto`: Async tests work without explicit fixtures

## ANTI-PATTERNS
- **DO NOT** add new route files — ALL routes in `backend/main.py`
- **DO NOT** add frontend build tools — vanilla JS only
- **NEVER** suppress type errors with `as any`, `@ts-ignore`
- **ALWAYS** run `pytest` after modifying logic

## SERVICES (docker-compose)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| backend | Custom | 8000 | FastAPI server |
| frontend | nginx:alpine | 3000/80 | Static serving |
| chromadb | chromadb/chroma | 8001 | Vector store |
| redis | redis:7-alpine | 6379 | Caching |

## NOTES
- `backend/main.py` is ~3000 lines — search by endpoint, don't scroll
- Frontend: pure HTML/CSS/JS, NO package.json
- Response caching in orchestrator (default 300s TTL)
- Signal handlers (SIGTERM/SIGINT) with 30s graceful shutdown
