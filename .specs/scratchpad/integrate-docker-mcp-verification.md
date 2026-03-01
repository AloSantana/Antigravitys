# Scratchpad — Integrate Docker MCP Gateway connection verification (LLM-as-Judge additions)

## Goal of this pass
Add **LLM-as-Judge verification** sections per implementation step (0.1–3.2) with:
- Verification level (Panel/Single/Per-Item/None)
- Custom rubric with weighted criteria (sum = 1.0)
- Threshold (typically 4.0/5.0)
- A summary table for quick scanning

## What I read / anchored on
- The task is scoped to **Docker MCP Toolkit gateway** verification via `docker mcp gateway run --profile <profile>` over **stdio**, requiring:
  - Docker CLI + daemon checks
  - MCP handshake completion
  - `tools/list` retrieval
  - Bounded timeouts + reliable process cleanup
  - Safe logging (no secrets)
- The task is decomposed into steps 0.1–3.2; verification should align to each step’s stated success criteria and acceptance criteria.

## Verification design decisions (why these levels)
- **Panel** for steps where correctness is both protocol/process-safety critical and easy to “overfit” with partial implementations:
  - 1.1 (preflight mapping), 1.2 (stdio protocol + cleanup), 3.1 (tests)
- **Single** for steps that are mostly schema/config/API wiring and can be judged as a cohesive artifact:
  - 0.1, 0.2, 1.3, 2.1, 3.2
- **Per-Item** for message-template quality where each `failure_type` must be distinct and actionable:
  - 2.2

## Rubric construction notes
- Weights emphasize the most failure-prone outcomes:
  - Protocol correctness + process cleanup for 1.2
  - Error mapping determinism + actionable outcomes for 1.1 and 2.2
  - Coverage + isolation for 3.1 (CI must not require Docker)
- Thresholds:
  - 4.3 for 1.2 and 3.1 to force higher confidence in the risky parts
  - 4.2 for 0.2 and 1.1 (contract + mapping)
  - 4.0–4.1 for wiring/docs steps

## Artifacts expectations (what the judge should look at)
- Diffs for code changes per step
- Test output for Step 3.1
- Docs and `.env.example` for Steps 0.1 and 3.2

## Sanity checks
- Each rubric sums to 1.0
- Each step has an explicit level + threshold
- Summary table aligns with per-step sections
