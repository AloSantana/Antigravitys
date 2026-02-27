# Repo Stabilization Plan (Orchestration Phase 1)

## Goal

Ensure the repository works fully, specifically fixing sandbox environments, model configurations, and ensuring seamless builds and execution on Windows.

## Agents Invoked

1. **backend-specialist**: Review and fix Model Configurations (MCP, OpenCode) and Backend Startup.
2. **devops-engineer**: Ensure Sandbox and Docker configurations are correct, and all `start.ps1` / `install.ps1` scripts execute without errors.
3. **test-engineer**: Run all test suites, verification scripts (`checklist.py`), and validate the build.

## Phase 2 Implementation Steps (Parallel Execution)

- **Step 1 (DevOps)**: Verify and fix sandbox Docker configurations (`Dockerfile.sandbox`, `docker-compose.yml`) and powershell scripts.
- **Step 2 (Backend)**: Inspect and fix `mcp_config.json`, `mcp_servers.json`, `opencode.json` and any AI model configuration files.
- **Step 3 (Test)**: Run `pytest` and `.agent/scripts/checklist.py` to confirm the repository is 100% operational.
