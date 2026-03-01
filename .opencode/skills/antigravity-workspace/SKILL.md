---
name: antigravity-workspace
description: Use when working with the Antigravity AI Workspace - starting, configuring, debugging, or developing the FastAPI + multi-agent platform
tags:
  - antigravity
  - fastapi
  - agents
  - mcp
---

# Antigravity Workspace Skill

## Quick Start
```powershell
# Install & run
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install -r backend/requirements.txt
python backend/main.py
# Access: http://localhost:8000
```

## Key Paths
| Component | Path |
|-----------|------|
| Backend entry | `backend/main.py` |
| Agent defs | `.github/agents/*.agent.md` |
| Frontend | `frontend/index.html` |
| Settings | `backend/settings_manager.py` |
| Conversations | `backend/conversation_manager.py` |
| Swarm | `src/swarm.py` |
| Tools | `tools/auto_issue_finder.py`, `tools/health_monitor.py` |
| MCP Config | `opencode.json`, `.mcp/config.json` |
| Env Config | `.env` (from `.env.example`) |

## API Endpoints (45+)
- `GET /health` - Health check
- `POST /api/chat` - Chat with agent
- `WS /ws` - WebSocket real-time
- `GET /docs` - Swagger UI
- `GET /settings` - Get settings
- `POST /settings` - Update settings
- `GET /performance/metrics` - Performance data

## Testing
```bash
pytest tests/ -v
pytest --cov=backend tests/
```
