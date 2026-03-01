---
title: Integrate Docker MCP Gateway connection verification
---

## Initial User Prompt
https://docs.docker.com/ai/mcp-catalog-and-toolkit/get-started/#verify-connections

## Refined Description (What / Why)
**What:** Add first-class support to configure and verify a Docker MCP Toolkit *gateway* (“MCP_DOCKER”) connection from within the Antigravity Workspace.

**Why:** Users need a fast, reliable way to confirm that Docker’s MCP Toolkit gateway is actually reachable and providing tools (and to see actionable errors when it isn’t), matching Docker’s recommended “verify connections” workflow.

## Scope

### In-scope
- A configurable Docker MCP gateway server entry (conceptually `MCP_DOCKER`) that runs via `docker mcp gateway run --profile <profile>` over `stdio`.
- A “Verify connection” workflow that:
  - Attempts to connect to the gateway with a bounded timeout.
  - Confirms the MCP handshake succeeds.
  - Fetches and displays the available tool list (at minimum: tool names and count).
  - Produces a clear status result: **Connected** or **Not connected**, with a human-readable reason.
- A programmatic surface for verification results (e.g., an internal API endpoint) suitable for UI and CLI usage.
- Logging/telemetry appropriate for troubleshooting (no secrets in logs).

### Out-of-scope
- Installing Docker Desktop, enabling the Docker MCP Toolkit beta feature, or creating Docker MCP profiles.
- Verifying connectivity for third-party clients (Claude Desktop, Cursor, Codex, etc.) beyond linking to Docker’s docs.
- Implementing or changing Docker MCP servers inside the profile (catalog selection/configuration).
- Adding new non-Docker MCP servers or reworking existing MCP server management beyond what is needed to support the gateway.

## Acceptance Criteria

### Connection verification
1) **Given** Docker Desktop is installed, Docker is running, and the configured profile exists, **when** the user runs “Verify connection”, **then** the workspace reports **Connected** and returns a non-empty list of tools (or an explicit “0 tools available” message if the profile contains none).

2) **Given** Docker is not installed or not on PATH, **when** the user runs “Verify connection”, **then** the workspace reports **Not connected** with a message indicating Docker is missing and how to fix it.

3) **Given** Docker is installed but the Docker daemon is not running, **when** the user runs “Verify connection”, **then** the workspace reports **Not connected** with a message indicating Docker must be started.

4) **Given** Docker is installed but `docker mcp` is unavailable (feature disabled/unsupported version), **when** the user runs “Verify connection”, **then** the workspace reports **Not connected** with a message indicating MCP Toolkit/Gateway is unavailable and points to the official setup steps.

5) **Given** the configured profile name does not exist (or is invalid), **when** the user runs “Verify connection”, **then** the workspace reports **Not connected** with a message that identifies the profile problem.

6) **Given** the gateway starts but does not complete an MCP handshake within the configured timeout, **when** the user runs “Verify connection”, **then** the workspace reports **Not connected** and includes a timeout-specific error message.

### Non-functional / safety
7) Verification must be **read-only by default** (no destructive tool calls) and must not require any API keys beyond what the Docker profile itself requires.

8) Verification must not log sensitive values (tokens, keys, full environment dumps).

## Primary User Scenarios

1) **First-time setup check**
- User configures the Docker MCP gateway profile name in the workspace.
- User clicks/runs “Verify connection”.
- User sees a Connected result and a tool list/count.

2) **Troubleshooting a broken setup**
- User runs “Verify connection”.
- User sees Not connected with a specific cause (Docker missing/daemon down/`docker mcp` missing/profile not found/timeout).
- User fixes the issue and re-runs verification successfully.

## Error Scenarios
- Docker CLI not installed / not discoverable.
- Docker daemon not running or inaccessible due to permissions.
- Docker Desktop version does not support MCP Toolkit / feature not enabled.
- Profile name not found.
- Gateway process exits immediately with non-zero status.
- Handshake fails or times out.

## Notes / References
- Docker documentation: “Verify connections” section (linked in Initial User Prompt).

## Implementation Process

### LLM-as-Judge verification

#### Verification Summary
| Step | Verification level | Threshold | Primary artifacts |
|------|---------------------|-----------|-------------------|
| 0.1 (Settings keys + defaults) | Single | 4.0 / 5.0 | Diff (settings + docs) |
| 0.2 (Request/response schema) | Single | 4.2 / 5.0 | Diff (Pydantic models) |
| 1.1 (Docker preflight checks) | Panel | 4.2 / 5.0 | Diff (helpers + error mapping) |
| 1.2 (MCP stdio handshake + tools/list) | Panel | 4.3 / 5.0 | Diff (stdio client + cleanup) |
| 1.3 (FastAPI endpoint) | Single | 4.1 / 5.0 | Diff (backend/main.py route) |
| 2.1 (Settings update + stored profile usage) | Single | 4.0 / 5.0 | Diff (settings update path + verify usage) |
| 2.2 (Fix-oriented reason strings + doc link) | Per-Item | 4.0 / 5.0 | Diff (message templates + mapping) |
| 3.1 (Tests) | Panel | 4.3 / 5.0 | Diff (tests) + test output |
| 3.2 (Docs) | Single | 4.0 / 5.0 | Diff (docs) |

**Scoring rule:** Judge assigns 1–5 per criterion, computes weighted average (weights sum to 1.0). Passing requires score ≥ threshold.

---

### Phase 0 — Setup

#### Step 0.1: Confirm configuration surface + defaults
- **Goal:** Define where the Docker MCP gateway profile name + timeout live, and keep them consistent across API/CLI/UI.
- **Output:** New settings keys (env + settings manager) for Docker MCP gateway verification.
- **Success criteria:**
  - A default profile name can be absent; verification returns a validation error that clearly asks for it.
  - A timeout value is configurable and enforced (no hangs).
- **Subtasks:**
  - Add env settings (e.g., `DOCKER_MCP_PROFILE`, `DOCKER_MCP_VERIFY_TIMEOUT_SECONDS`) and document defaults.
  - Ensure `SettingsManager.get_settings()` returns these values (non-sensitive).
  - Add/adjust `.env.example` and relevant docs snippet describing how to set the profile.

##### LLM-as-Judge Verification (Step 0.1)
- **Verification level:** Single
- **Threshold:** 4.0 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Settings definition correctness (0.35):** Keys exist, types are correct, defaults are sensible, and missing profile produces a clear validation error.
  - **Timeout configuration + enforcement (0.25):** Timeout is configurable and is used to bound verification (no unbounded waits).
  - **Settings surfacing (0.20):** Values are correctly exposed via the existing settings manager for UI/CLI (non-sensitive only).
  - **Documentation / `.env.example` alignment (0.20):** `.env.example` and docs mention the new keys and match implemented behavior.

#### Step 0.2: Decide verification contract (response schema)
- **Goal:** Make verification results stable for future UI + CLI use.
- **Output:** Pydantic models for request/response (backend).
- **Success criteria:** Response includes `connected: bool`, `reason: str`, `tools: [{name, description?}]`, `tools_count: int`, and `duration_ms`.
- **Subtasks:**
  - Define request: `{ profile: str | null }` (allow override), `{ timeout_seconds: int | null }`.
  - Define response fields and a small, enumerated `failure_type` (e.g., `docker_missing`, `daemon_down`, `docker_mcp_unavailable`, `profile_invalid`, `handshake_timeout`, `gateway_exit`, `unknown`).

##### LLM-as-Judge Verification (Step 0.2)
- **Verification level:** Single
- **Threshold:** 4.2 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Schema completeness + clarity (0.45):** Request/response models contain all required fields, with clear optionality and consistent naming.
  - **Failure typing (0.20):** `failure_type` is enumerated, stable, and covers acceptance-criteria paths without ambiguity.
  - **JSON serialization stability (0.20):** Models serialize cleanly to JSON for the API surface; no non-serializable fields.
  - **Backward compatibility posture (0.15):** Contract is designed for UI/CLI usage (e.g., tools_count matches tools length; reason is always non-empty).

---

### Phase 1 — Foundational

#### Step 1.1: Implement Docker preflight checks (no MCP yet)
- **Goal:** Produce actionable, specific “Not connected” reasons before attempting an MCP handshake.
- **Output:** A backend helper that runs Docker CLI checks with timeouts and maps errors to the acceptance criteria.
- **Success criteria:**
  - Missing Docker on PATH → `docker_missing`.
  - Docker daemon not running → `daemon_down`.
  - `docker mcp` not available → `docker_mcp_unavailable`.
  - Invalid/missing profile name → `profile_invalid`.
- **Subtasks:**
  - Add a small subprocess runner with timeout + captured stdout/stderr (no env dumps).
  - Implement checks (examples):
    - `docker version` or `docker info` to detect daemon accessibility.
    - `docker mcp --help` (or equivalent) to detect MCP Toolkit availability.
    - `docker mcp profile ls` (or equivalent) to detect profile existence (fallback to parsing gateway error if listing is unavailable).
  - Normalize platform-specific errors (Windows/macOS/Linux) into consistent `failure_type`.

##### LLM-as-Judge Verification (Step 1.1)
- **Verification level:** Panel
- **Threshold:** 4.2 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Preflight coverage (0.35):** Implements the required checks (docker present, daemon up, `docker mcp` present, profile validity) with correct command selection.
  - **Error-to-failure_type mapping (0.35):** Maps real-world error modes to the specified `failure_type`s in a deterministic, user-actionable way.
  - **Timeout + non-hanging behavior (0.20):** All subprocess calls are bounded; timeouts are handled and reported as such.
  - **Safety/logging hygiene (0.10):** No sensitive data is logged; stderr/stdout are truncated/sanitized appropriately.

#### Step 1.2: Add minimal MCP stdio handshake + tools discovery for verification
- **Goal:** Verify “real” MCP connectivity by completing the handshake and listing tools.
- **Output:** A minimal stdio MCP client used only by the verification workflow.
- **Success criteria:**
  - Handshake completes within timeout.
  - Tools list is fetched and returned (names + count; empty list allowed).
  - Gateway process is always cleaned up (no orphaned processes).
- **Subtasks:**
  - Implement stdio transport framing according to the MCP spec used by Docker’s gateway (documented in code and test-covered).
  - Send MCP `initialize`, await response; then call `tools/list`, await response.
  - Enforce deadlines per phase (spawn, handshake, tools/list) and return timeout-specific errors.
  - Ensure shutdown: attempt graceful MCP shutdown if available, then terminate/kill if needed.

##### LLM-as-Judge Verification (Step 1.2)
- **Verification level:** Panel
- **Threshold:** 4.3 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Protocol correctness (0.30):** Implements MCP stdio JSON-RPC framing and message correlation correctly for Docker gateway use.
  - **Handshake + tools discovery completeness (0.25):** Performs `initialize` and `tools/list` and parses returned tool entries into the response schema.
  - **Timeout discipline (0.20):** Enforces deadlines for spawn/handshake/tools/list and returns the correct timeout-specific failure.
  - **Process lifecycle safety (0.20):** Ensures gateway process cleanup in all paths (success, timeout, early exit), using terminate→kill escalation.
  - **Error reporting quality (0.05):** Produces actionable reason strings without leaking internal exceptions.

#### Step 1.3: Wire verification into the backend as an internal API endpoint
- **Goal:** Provide a programmatic surface usable by UI and CLI.
- **Output:** FastAPI endpoint in `backend/main.py` (monolith rule) that returns the verification response schema.
- **Success criteria:**
  - Endpoint returns HTTP 200 with `connected=false` for expected “not connected” states (no stack traces to client).
  - Unexpected errors return a generic failure with safe logging (no secrets).
- **Subtasks:**
  - Add `POST /api/mcp/docker/verify` (or similar) in `backend/main.py`.
  - Add structured logging: start/stop, duration, failure_type, high-level error message.

##### LLM-as-Judge Verification (Step 1.3)
- **Verification level:** Single
- **Threshold:** 4.1 / 5.0
- **Rubric (weights sum to 1.0):**
  - **API contract adherence (0.35):** Endpoint returns the defined response schema consistently, including `duration_ms` and tool fields.
  - **HTTP semantics (0.25):** Expected failures return HTTP 200 with `connected=false`; validation errors are handled consistently (no stack traces).
  - **Error handling + safe logging (0.25):** Unexpected exceptions are caught and mapped to `failure_type=unknown` with sanitized logs.
  - **Request override behavior (0.15):** Request-level `profile`/`timeout_seconds` override stored settings when provided.

---

### Phase 2 — User Stories

#### Step 2.1: First-time setup check flow
- **Goal:** Allow a user to configure profile name and verify successfully.
- **Output:** Settings update path + verify endpoint working together.
- **Success criteria:**
  - User sets profile name in workspace settings; verify returns `connected=true` and `tools_count`.
- **Subtasks:**
  - Add settings update support for `DOCKER_MCP_PROFILE` (via existing settings management).
  - Ensure verify endpoint uses stored profile if request override not supplied.

##### LLM-as-Judge Verification (Step 2.1)
- **Verification level:** Single
- **Threshold:** 4.0 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Settings update correctness (0.45):** Profile name can be set via existing settings management pathways; validation is clear when absent/invalid.
  - **Defaulting/override logic (0.30):** Endpoint uses stored profile by default and respects request overrides.
  - **User-facing behavior consistency (0.15):** Response fields remain consistent (`tools_count` matches `tools`).
  - **Non-sensitive settings handling (0.10):** No secrets are introduced into settings surfaces.

#### Step 2.2: Troubleshooting flow with targeted messages
- **Goal:** Users can quickly identify which prerequisite is missing.
- **Output:** Human-readable `reason` strings aligned to acceptance criteria.
- **Success criteria:**
  - Each error scenario maps to a distinct `failure_type` and a fix-oriented `reason`.
- **Subtasks:**
  - Implement message templates for each failure_type (mention “start Docker”, “install Docker”, “enable MCP Toolkit”, “check profile name”).
  - Add a doc link field in the response for `docker_mcp_unavailable` pointing at Docker’s official setup steps.

##### LLM-as-Judge Verification (Step 2.2)
- **Verification level:** Per-Item
- **Threshold:** 4.0 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Distinctness per failure_type (0.45):** Each `failure_type` yields a meaningfully distinct `reason` (no generic “failed” messages).
  - **Fix-oriented guidance (0.25):** `reason` text tells the user the next action (install/start/enable/check).
  - **Doc-link behavior (0.15):** `docker_mcp_unavailable` includes an official Docker setup link field.
  - **Safety + no leakage (0.15):** Reasons do not include stack traces, env dumps, or sensitive fragments.

---

### Phase 3 — Polish

#### Step 3.1: Tests (unit-first, optional integration)
- **Goal:** Make verification logic reliable without requiring Docker in CI.
- **Output:** Unit tests with subprocess + MCP-stdio mocked; optional integration tests gated by marker.
- **Success criteria:**
  - Unit tests cover all acceptance criteria paths by mocking subprocess outputs and MCP responses.
  - Integration test (optional) is skipped unless Docker + MCP Toolkit is available.
- **Subtasks:**
  - Add tests for: docker missing, daemon down, `docker mcp` missing, profile invalid, gateway exit, handshake timeout, tools list success.
  - Ensure logs are sanitized (no secrets) via assertions on logged fields if practical.

##### LLM-as-Judge Verification (Step 3.1)
- **Verification level:** Panel
- **Threshold:** 4.3 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Scenario coverage (0.45):** Unit tests cover the acceptance-criteria outcomes and listed failure modes with clear assertions.
  - **Isolation/mocking quality (0.20):** Tests do not require Docker in CI; subprocess and stdio are mocked deterministically.
  - **Timeout + cleanup validation (0.15):** Tests exercise timeout paths and confirm cleanup behavior (no orphan processes / proper kill escalation behavior via mocks).
  - **Integration gating (0.10):** Optional integration tests are correctly marked and skipped unless prerequisites exist.
  - **Log sanitization checks (0.10):** Where practical, tests assert that logs do not contain sensitive values.

#### Step 3.2: Documentation + operator guidance
- **Goal:** Reduce support burden by documenting setup + failure modes.
- **Output:** Short doc section describing how to set profile and interpret verification results.
- **Success criteria:** Docs match the returned failure types and suggested fixes.
- **Subtasks:**
  - Update existing MCP docs/guide to include the new Docker gateway verify endpoint + settings keys.

##### LLM-as-Judge Verification (Step 3.2)
- **Verification level:** Single
- **Threshold:** 4.0 / 5.0
- **Rubric (weights sum to 1.0):**
  - **Config documentation completeness (0.35):** Docs describe required settings keys, defaults, and where to set them.
  - **Endpoint usage clarity (0.25):** Docs show how to call the verify endpoint and interpret response fields.
  - **Troubleshooting alignment (0.25):** Docs list failure types and recommended fixes consistent with implementation.
  - **No contradictions (0.15):** Documentation matches actual code behavior (no stale keys/paths).

---

## Blockers / Risks (with mitigations)

- **Blocker:** The exact MCP stdio framing/handshake fields required by Docker’s gateway may differ from assumptions.
  - **Mitigation:** Validate against the official MCP spec and a real `docker mcp gateway run ...` session; add a focused integration test and keep the stdio client minimal.
- **Risk:** Gateway process can hang or outlive verification.
  - **Mitigation:** Enforce timeouts and implement reliable cleanup (terminate → kill escalation) in `finally` blocks.
- **Risk:** Inconsistent config formats (`transport` vs `type`) across existing MCP config files.
  - **Mitigation:** Keep Docker verification config isolated to this feature (explicit settings + on-demand process), and only touch shared MCP config parsing if required by the task.

## Definition of Done
- All acceptance criteria in this task pass via unit tests (mocked) and manual verification on at least one machine with Docker MCP Toolkit enabled.
- The verify endpoint returns stable response schema with `connected`, `reason`, and tool list/count.
- Verification is bounded by timeouts, is read-only by default, and does not log secrets.
- Documentation is updated with configuration keys and troubleshooting guidance.
