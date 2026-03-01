# Antigravity Workspace - Coding Standards

## Python
- Type hints mandatory on all function signatures
- Google-style docstrings with Args, Returns, Raises sections
- Pydantic models for complex data structures
- Ruff linter: line-length 120, indent-width 4
- Ignored rules: E402, E701, E722, F401, F811, F841

## Architecture Patterns
- Tool Isolation: All external interactions in `tools/` directory
- Stateless Tools: Pass context as arguments
- Fail Gracefully: Return error messages, never crash
- Agent tools use Pydantic for schema validation

## File Organization
- Backend code: `backend/`
- Frontend: `frontend/`
- Agent definitions: `.github/agents/`
- Swarm system: `src/`
- Tools: `tools/`
- Tests: `tests/`
- Artifacts: `artifacts/`
- Docs: `docs/`
