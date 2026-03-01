# Antigravity Workspace - Domain Context

## Overview
Antigravity Workspace is a production-ready, enterprise-grade AI-powered development workspace with:
- 13 Specialized AI Agents + Dual-Agent Mode
- 24+ MCP Servers for tool integration
- FastAPI backend (Python 3.11+) running on port 8000
- Single-page HTML frontend with multi-tab dashboard
- SQLite-backed conversation history
- Artifact management system
- Real-time performance monitoring
- WebSocket-based real-time communication

## Architecture
- **Backend**: `backend/main.py` - FastAPI with 45+ REST endpoints + WebSocket
- **Frontend**: `frontend/index.html` - Single HTML SPA with Chat, Editor, Settings, Performance, Terminal, Debug tabs
- **Agents**: `.github/agents/` - 13 specialized agent definitions
- **Swarm System**: `src/swarm.py` - Router-worker pattern for multi-agent orchestration
- **MCP Servers**: Configured in `opencode.json`, `.mcp/config.json`
- **Tools**: `tools/auto_issue_finder.py`, `tools/health_monitor.py`

## Key Technologies
- Python: FastAPI, Uvicorn, LangChain, ChromaDB, Pydantic
- AI: Google Gemini, Vertex AI, Ollama, OpenRouter
- Frontend: Vanilla HTML/JS, Chart.js, CodeMirror
- Data: SQLite, ChromaDB (vector DB), Redis
- Protocol: MCP (Model Context Protocol)

## Configuration
- Environment: `.env` (from `.env.example`)
- OpenCode MCP: `opencode.json` (root)
- Backend port: 8000
- CORS origins: localhost:3000, localhost:8000
