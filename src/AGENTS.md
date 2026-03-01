# SRC — Agent SDK

## OVERVIEW

Standalone agent SDK: Gemini agent with Think-Act-Reflect loop, swarm orchestration, MCP client, model rotation, and sandboxed execution.

## STRUCTURE

```
src/
├── agent.py         # GeminiAgent — core agent with tool discovery, MCP, memory (426 lines)
├── config.py        # Pydantic Settings — all env-based config, MCPServerConfig model (94 lines)
├── swarm.py         # SwarmOrchestrator + MessageBus — router-worker coordination
├── model_rotator.py # Multi-provider API key rotation with health monitoring (522 lines)
├── memory.py        # MemoryManager — agent conversation memory with summarization
├── mcp_client.py    # MCP server connections + tool discovery (485 lines)
├── swarm_demo.py    # Demo script for swarm system
├── agents/          # Swarm worker agents
│   ├── base_agent.py     # BaseAgent ABC — inherit + implement execute()
│   ├── router_agent.py   # Task analysis, delegation planning, result synthesis
│   ├── coder_agent.py    # Code implementation worker
│   ├── reviewer_agent.py # Code review worker
│   └── researcher_agent.py # Research worker
├── sandbox/         # Code execution isolation
│   ├── base.py      # SandboxBase ABC
│   ├── local_exec.py   # Local subprocess execution
│   ├── docker_exec.py  # Docker container execution
│   └── factory.py      # Factory: returns local or docker based on SANDBOX_TYPE env
└── tools/           # Tool registry
    ├── example_tool.py  # Template for new tools
    ├── execution_tool.py # Code execution via sandbox
    ├── mcp_tools.py     # MCP-discovered tools
    └── openai_proxy.py  # OpenAI-compatible API proxy
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new tool | `tools/` | Create function, auto-discovered by `agent.py._discover_tools()` |
| Add swarm worker | `agents/` | Inherit `BaseAgent`, implement `async execute(task, context)` |
| Change model config | `config.py` | `Settings` class, reads from `.env` |
| API key rotation | `model_rotator.py` | `KeyStatus` enum, `APIKey` dataclass, backoff logic |
| MCP server setup | `config.py` → `MCPServerConfig` | Also `mcp_servers.json` at project root |
| Sandbox config | `config.py` | `SANDBOX_TYPE` (local/docker), timeout, limits |

## CONVENTIONS

- Tool auto-discovery: any function in `src/tools/` matching pattern gets registered by `agent.py`
- Agent instantiation: `GeminiAgent` loads context from `.context/*.md` files at init
- MCP tools prefixed with `mcp_` (configurable via `MCP_TOOL_PREFIX`)
- Model rotator uses `KeyStatus` enum: AVAILABLE, RATE_LIMITED, ERROR, DISABLED
- Sandbox factory pattern: `SANDBOX_TYPE=local` or `SANDBOX_TYPE=docker`

## ANTI-PATTERNS

- **DO NOT** import from `backend/` — `src/` is a standalone SDK
- **DO NOT** bypass the sandbox for code execution
- **DO NOT** hardcode API keys — use `config.py` Settings which reads `.env`

## NOTES

- `src/` vs `backend/`: src is the agent SDK (can run standalone), backend is the HTTP server that wraps it
- `GeminiAgent` gracefully degrades to mock mode if no API key set
- Model rotator tracks: total_requests, successful_requests, rate_limit_hits, consecutive_errors
- `swarm.py` has both `MessageBus` (communication) and `SwarmOrchestrator` (coordination)
