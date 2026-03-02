---
name: antigravity-workspace
description: Use when working with the Antigravity AI Workspace - starting, configuring, debugging, or developing the FastAPI + multi-agent platform
tags:
  - antigravity
  - fastapi
  - agents
  - mcp
  - opencode
---

# Antigravity Workspace Skill

## Quick Start
```bash
# Linux/macOS
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install -r backend/requirements.txt
python backend/main.py
# Access: http://localhost:8000

# Windows
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install -r backend/requirements.txt
python backend/main.py
```

## Key Paths
| Component | Path |
|-----------|------|
| Backend entry | `backend/main.py` (2955-line monolith — ALL routes here) |
| Agent defs | `.github/agents/*.agent.md` |
| Frontend | `frontend/index.html` + `frontend/js/app.js` |
| Settings | `backend/settings_manager.py` |
| Conversations | `backend/conversation_manager.py` |
| Swarm | `src/swarm.py` |
| Tools | `tools/auto_issue_finder.py`, `tools/health_monitor.py` |
| MCP Config (OpenCode) | `opencode.json` |
| MCP Config (Gemini) | `.agent/gemini_mcp_settings.json` |
| OpenCode Plugin | `.opencode/oh-my-opencode.jsonc` |
| Skills | `.opencode/skills/` |
| Commands | `.opencode/command/` |
| Env Config | `.env` (from `.env.example`) |

## API Endpoints (45+)
- `GET /health` - Health check
- `POST /api/chat` - Chat with agent
- `WS /ws` - WebSocket real-time
- `GET /docs` - Swagger UI
- `GET /settings` - Get settings
- `POST /settings` - Update settings
- `GET /performance/metrics` - Performance data
- `POST /api/agents/collaborate` - Multi-agent collaboration
- `POST /api/agents/handoff` - Agent handoff

## OpenCode Integration
See `docs/OPENCODE_INTEGRATION.md` for full setup guide.

Key plugins:
- **oh-my-opencode**: Primary plugin with Sisyphus agent (`.opencode/oh-my-opencode.jsonc`)
- **gsd-opencode**: Spec-driven development (`npx gsd-opencode`)
- **swarm-tools**: Multi-agent swarm coordination

Slash commands available:
- `/start-antigravity` - Start the backend
- `/test-antigravity` - Run tests with coverage
- `/add-endpoint` - Add new API endpoint with template
- `/github-triage` - Triage GitHub issues + PRs

## Installation
```bash
# Local development
./install.sh

# Docker (full stack)
docker-compose up -d

# Remote VPS
./install-remote.sh
```

## Testing
```bash
pytest tests/ -v
pytest --cov=backend tests/
pytest tests/unit/ -v  # unit tests only
pytest -m "not requires_ollama and not requires_gemini"  # skip external services
```

## Monolith Pattern (IMPORTANT)
ALL routes live in `backend/main.py`. Do NOT create new route files.
Search for nearby endpoints: `grep -n "@app\." backend/main.py | grep -i keyword`