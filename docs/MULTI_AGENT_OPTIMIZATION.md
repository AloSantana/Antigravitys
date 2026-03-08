# Multi-Agent Optimization — Deep Analysis & Plan

> **Branch**: `copilot/optimize-multi-agents-work`  
> **Status**: Implemented  

---

## 1. Problem Statement

The existing swarm system executed worker agents **sequentially** — each worker ran
one at a time, so total latency equalled the *sum* of all worker execution times.
For a three-worker swarm (Coder + Reviewer + Researcher), this meant unnecessary
idle time while agents waited for the previous agent to finish.

Additional issues identified:
- No caching — identical tasks triggered a full re-execution every time.
- Router used a simple `any(keyword in task)` check with no confidence scoring.
- No execution-time telemetry — impossible to identify slow agents.
- `reset_history()` on `BaseAgent` cleared history but didn't reset metrics counters.

---

## 2. Changes Implemented

### 2.1 `src/swarm.py` — Parallel Execution, Caching & Metrics

| Before | After |
|--------|-------|
| Sequential `for` loop over workers | `asyncio.gather(*coroutines)` — all workers run concurrently |
| No caching | SHA-256-keyed result cache with configurable TTL (default 300 s) |
| No timing output | `wall_time_ms` on every result; cache-hit path skips workers entirely |
| No swarm metrics | `get_swarm_metrics()` exposes hit-rate, avg wall time, per-agent stats |
| No task priority | `TaskPriority` enum (LOW / NORMAL / HIGH / CRITICAL) attached to executions |

**Key method: `SwarmOrchestrator.execute()`**

```python
# Old — sequential
for agent_name, sub_task in delegation_plan.items():
    result = await agent.execute(sub_task, context)   # blocks until done
    worker_results[agent_name] = result

# New — parallel
worker_coroutines = [
    self._execute_worker(name, sub_task, context, verbose)
    for name, sub_task in delegation_plan.items()
]
results_list = await asyncio.gather(*worker_coroutines)   # all run at once
worker_results = dict(results_list)
```

Performance impact (simulated I/O scenario — 3 workers, 100 ms each):
- **Sequential**: ~300 ms total
- **Parallel**: ~100 ms total (**3× faster**)

For real LLM-backed workers with typical 1–5 s latency, the gain is proportional
to the number of workers dispatched concurrently.

### 2.2 `src/agents/base_agent.py` — Per-Agent Metrics

Added lightweight telemetry without breaking any existing behaviour:

```python
# New fields
self.total_tasks: int = 0
self.successful_tasks: int = 0
self.failed_tasks: int = 0
self.total_execution_time: float = 0.0

# New method
def get_metrics(self) -> Dict[str, Any]: ...

# Updated
def reset_history(self):
    self.history.clear()
    # also resets metric counters
```

### 2.3 `src/agents/router_agent.py` — Smarter Routing

Old router: single `any(keyword in task_lower)` — binary match, no priority.

New router:
1. Tokenises the task into words **and bigrams**.
2. Scores each worker type by counting matching keywords against expanded keyword
   sets (`_CODER_KEYWORDS`, `_REVIEWER_KEYWORDS`, `_RESEARCHER_KEYWORDS`).
3. Returns **confidence scores** proportional to keyword overlap.
4. Exposes `confidence_scores` in the result for observability.

```python
scores = self._score_task(task)   # {Coder: 3, Reviewer: 1, Researcher: 0}
total = sum(scores.values()) or 1
confidence = {k: round(v / total, 3) for k, v in scores.items() if v > 0}
# → {Coder: 0.75, Reviewer: 0.25}
```

### 2.4 Worker Agents — Execution Timing

`CoderAgent`, `ReviewerAgent`, `ResearcherAgent` now time their own `execute()`
calls and include `execution_time_ms` in the result dict. This feeds both the
per-agent metrics in `BaseAgent` and the swarm-level synthesis summary.

---

## 3. Remaining Optimization Opportunities

The following items were identified but are **not** in scope for this PR (they
require LLM API integration or larger structural changes):

### 3.1 LLM-Backed Workers (High Impact)
The worker agents currently produce static placeholder output. Connecting them
to the Gemini / Vertex / Ollama clients in `backend/agent/` would unlock the
full value of parallel dispatch.

**Recommended approach**: Inject an `orchestrator` instance into each worker so
it can call `orchestrator.process_request()` for real LLM responses.

### 3.2 Adaptive Routing (Medium Impact)
The router could learn from historical execution times (stored in agent metrics)
to skip expensive agents when time budget is tight, or assign high-confidence
tasks only to the best-matched agent.

### 3.3 Worker Pool / Concurrency Limits (Medium Impact)
For high-traffic scenarios, add an `asyncio.Semaphore` to cap concurrent
upstream LLM calls and avoid rate-limit errors.

```python
_semaphore = asyncio.Semaphore(5)  # max 5 concurrent LLM calls

async def _execute_worker(self, ...):
    async with _semaphore:
        return await agent.execute(sub_task, context)
```

### 3.4 Priority Queue (Low Impact at current scale)
`TaskPriority` is already attached to results. For a multi-user deployment, wire
it into a `asyncio.PriorityQueue` so CRITICAL tasks preempt NORMAL ones.

### 3.5 Persistent Cache (Low Impact)
Replace the in-memory `dict` cache with Redis (already in `docker-compose.yml`)
so cache survives server restarts and is shared across multiple worker processes.

---

## 4. Architecture After Optimization

```
User Request
    │
    ▼
SwarmOrchestrator.execute()
    │
    ├─ Cache hit? ──► Return cached result (⚡ near-zero latency)
    │
    ▼
RouterAgent.execute()            ← keyword scoring + confidence
    │  returns delegation_plan
    │
    ├─────────────────────────────────────────────────────┐
    │ asyncio.gather()  (all workers start simultaneously) │
    ▼                    ▼                    ▼           │
CoderAgent          ReviewerAgent       ResearcherAgent  │
execute()           execute()           execute()        │
    │                    │                    │           │
    └────────────────────┴────────────────────┘           │
                         ▼                               │
              RouterAgent.synthesize_results()           │
                         │                               │
                         ▼                               │
              Final result + wall_time_ms                │
                         │                               │
                         └───────────────────────────────┘
                                  store in cache
```

---

## 5. Running & Verifying

```bash
# Run all swarm tests (56 tests, should all pass)
pytest tests/test_swarm.py -v --override-ini="addopts="

# Quick smoke-test in Python
python - <<'EOF'
import asyncio
from src.swarm import SwarmOrchestrator, TaskPriority

async def main():
    swarm = SwarmOrchestrator(cache_ttl=60)
    
    result = await swarm.execute(
        "Research best practices and implement a caching module",
        verbose=True,
        priority=TaskPriority.HIGH,
    )
    print("Workers used:", result["workers_used"])
    print("Wall time:   ", result["wall_time_ms"], "ms")
    
    # Second call — should hit cache
    result2 = await swarm.execute(
        "Research best practices and implement a caching module",
        verbose=False,
    )
    print("From cache:", result2["from_cache"])  # True
    
    print("\nSwarm metrics:")
    import json
    print(json.dumps(swarm.get_swarm_metrics(), indent=2))

asyncio.run(main())
EOF
```

---

## 6. Backward Compatibility

All public API signatures are **unchanged**:

- `SwarmOrchestrator()` still works with zero arguments (uses default `cache_ttl=300`)
- `swarm.execute(task, verbose=True)` signature extended with optional `priority` kwarg
- `swarm.reset()` still clears message bus and agent histories (also clears cache now)
- `swarm.get_message_log()` and `swarm.get_agent_capabilities()` unchanged
- All 56 existing tests pass without modification
