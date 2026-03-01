# Antigravity Workspace - Development Processes

## Starting the App
1. Activate venv: `.\venv\Scripts\Activate.ps1` (Windows)
2. Install deps: `pip install -r requirements.txt && pip install -r backend/requirements.txt`
3. Run: `python backend/main.py` or `.\start.ps1`
4. Access: http://localhost:8000

## Testing
- Run all tests: `pytest tests/ -v`
- With coverage: `pytest --cov=backend --cov-report=html tests/`
- Quick system test: `python test_phase4_systems.py`

## Code Style
- Python: PEP 8, strict type hints, Google-style docstrings
- Pydantic models for all data structures
- Tools in `tools/` directory with fail-graceful patterns
- Ruff linter config in `pyproject.toml`

## Agent Development
- Agents defined in `.github/agents/*.agent.md`
- Swarm orchestration via `src/swarm.py`
- Router-worker pattern: Router -> Coder/Reviewer/Researcher -> Synthesis

## MCP Server Management
- Core servers configured in `opencode.json`
- Additional configs in `.mcp/config.json` and `.agent/mcp_config.json`
- Servers use stdio transport with npx
