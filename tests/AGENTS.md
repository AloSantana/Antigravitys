# TESTS — Pytest Suite

## OVERVIEW

Pytest test suite covering backend + src with unit/integration/e2e/performance tiers. Heavy mocking pattern — most tests mock external AI services.

## STRUCTURE

```
tests/
├── conftest.py              # 430 lines — shared fixtures, sys.path setup, mock factories
├── unit/                    # Fast isolated tests
├── integration/             # Tests requiring service connections
├── e2e/                     # Full system tests
├── performance/             # Load/perf benchmarks (7 files)
├── config/                  # Configuration validation tests (3 files)
├── test_agent.py            # GeminiAgent tests
├── test_orchestrator.py     # Orchestrator tests
├── test_swarm.py            # Swarm system tests (771 lines)
├── test_model_rotator.py    # Model rotator tests
├── test_mcp.py              # MCP integration tests (883 lines)
├── test_sandbox.py          # Sandbox execution tests (710 lines)
├── test_settings_api.py     # Settings API endpoint tests
├── test_conversation_api.py # Conversation API tests
├── test_artifact_api.py     # Artifact API tests
├── test_memory.py           # Memory manager tests (591 lines)
├── test_health_monitor.py   # Health monitor tests (685 lines)
└── ... (32 test files total)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add unit test | `tests/unit/` or `tests/test_*.py` | Use `@pytest.mark.unit` marker |
| Add integration test | `tests/integration/` | Use `@pytest.mark.integration` marker |
| Add fixture | `tests/conftest.py` | Shared fixtures: mock clients, temp dirs, test files |
| Test with Ollama | Any test file | Use `@pytest.mark.requires_ollama` marker |
| Test with Gemini | Any test file | Use `@pytest.mark.requires_gemini` marker |
| Performance test | `tests/performance/` | Use `@pytest.mark.slow` marker |

## CONVENTIONS

- **Markers required**: `unit`, `integration`, `e2e`, `slow`, `asyncio`, `requires_ollama`, `requires_gemini`
- `--strict-markers` enforced — undefined markers fail
- Coverage: `--cov=backend --cov=src --cov-branch` — HTML + terminal + XML reports
- Max 5 failures then stop (`--maxfail=5`)
- Test timeout: 300s per test (`timeout_method=thread`)
- `asyncio_mode = auto` — async tests work without explicit event loop fixtures
- `conftest.py` adds `project_root` and `project_root/backend` to `sys.path`

## ANTI-PATTERNS

- **DO NOT** delete failing tests to make suite pass
- **DO NOT** use real API keys in tests — mock external services
- **DO NOT** skip markers — `--strict-markers` will catch undefined markers
- **DO NOT** add tests to root `tests/` without appropriate marker

## NOTES

- `conftest.py` provides: `event_loop`, `temp_dir`, `test_file`, `test_py_file` and many mock fixtures
- Rate limiter auto-disabled when `pytest` in `sys.modules` (see `backend/main.py`)
- Largest test files: `test_mcp.py` (883), `test_swarm.py` (771), `test_sandbox.py` (710)
- `tests/config/` has specialized config validation tests (setup scripts, configuration rules)
