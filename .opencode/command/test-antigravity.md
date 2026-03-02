---
description: Run the full Antigravity test suite with coverage report
---

<command-instruction>
Run Antigravity tests. Execute immediately without asking.

## Quick Test (unit only)
```bash
pytest tests/unit/ -v --tb=short 2>&1 | tail -30
```

## Full Suite with Coverage
```bash
pytest tests/ -v --tb=short --cov=backend --cov=src \
  --cov-report=term-missing \
  -m "not requires_ollama and not requires_gemini and not slow" \
  2>&1 | tail -50
```

## By Category
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires running backend)
pytest tests/ -v -m integration

# Performance tests
pytest tests/performance/ -v

# Skip external service tests
pytest tests/ -v -m "not requires_ollama and not requires_gemini"
```

## Key Test Files
| File | Coverage |
|------|----------|
| `tests/unit/test_orchestrator.py` | Agent orchestration |
| `tests/unit/test_agent_manager.py` | Agent lifecycle |
| `tests/test_swarm.py` | Swarm system |
| `tests/test_mcp.py` | MCP integration |
| `tests/test_rag.py` | RAG pipeline |
| `tests/test_settings_api.py` | Settings API |

## Markers Available
- `unit` — fast, isolated
- `integration` — requires running services
- `e2e` — end-to-end
- `slow` — >5 seconds
- `requires_ollama` — needs local Ollama
- `requires_gemini` — needs Gemini API key
- `asyncio` — async tests

After running, summarize: total passed/failed, key failures with file:line.
</command-instruction>
