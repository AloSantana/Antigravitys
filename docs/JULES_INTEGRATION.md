# Jules Integration & Dual-Agent Mode Guide

## Overview

This guide explains how to use **Jules** (Anthropic's coding assistant) and the **dual-agent coordination system** in the Antigravity Workspace. These features enable seamless collaboration between multiple AI agents for enhanced coding workflows.

## Table of Contents

1. [Introduction to Jules](#introduction-to-jules)
2. [Dual-Agent Mode](#dual-agent-mode)
3. [Getting Started](#getting-started)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Agent Collaboration Patterns](#agent-collaboration-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Introduction to Jules

**Jules** is a specialized AI agent focused on:
- **Code Quality**: Deep code analysis and refactoring
- **Collaboration**: Seamless coordination with other agents
- **Code Review**: Security and quality audits
- **Test Generation**: Comprehensive test coverage
- **Knowledge Transfer**: Clear documentation and explanations

### Jules vs Other Agents

| Feature | Jules | rapid-implementer | architect |
|---------|-------|-------------------|-----------|
| Focus | Quality & Collaboration | Speed & Completeness | System Design |
| Code Review | ✅ Expert | ⚠️ Basic | ⚠️ Architectural |
| Implementation | ✅ Refined | ✅ Fast | ❌ Planning Only |
| Refactoring | ✅ Expert | ⚠️ Basic | ⚠️ Structural |
| Collaboration | ✅ Native | ⚠️ Limited | ✅ Design Phase |
| Priority | 10 (Highest) | 9 | 8 |

---

## Dual-Agent Mode

Dual-agent mode allows multiple agents to work together on the same task, each contributing their expertise.

### Modes of Collaboration

#### 1. Sequential Mode
Agents work one after another, building on each other's output.

```
User Request → Agent 1 → Agent 2 → Agent 3 → Final Result
```

**Best for:**
- Quality pipelines (implement → review → test)
- Step-by-step refinement
- Context-dependent tasks

#### 2. Parallel Mode
Agents work simultaneously on independent aspects.

```
                ┌─ Agent 1 ─┐
User Request ───┼─ Agent 2 ─┼→ Combined Result
                └─ Agent 3 ─┘
```

**Best for:**
- Independent tasks
- Faster processing
- Multiple perspectives

### Agent Handoffs

Handoffs transfer context from one agent to another seamlessly:

```python
# Agent A completes work
handoff = {
    "from_agent": "rapid-implementer",
    "to_agent": "jules",
    "context": {"code": "...", "files_modified": [...]},
    "reason": "code review needed"
}
```

---

## Getting Started

### 1. Basic Usage

#### Single Agent (Jules)
```bash
# Via REST API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Review the authentication code", "agent": "jules"}'
```

#### Dual-Agent Collaboration
```bash
# Sequential: rapid-implementer → jules
curl -X POST http://localhost:8000/api/agents/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Implement and review user login feature",
    "agents": ["rapid-implementer", "jules"],
    "mode": "sequential"
  }'
```

### 2. Web Interface

Access the enhanced web UI at `http://localhost:8000`:

1. **Select Agent**: Choose "Jules" from the agent dropdown
2. **Dual-Agent**: Enable "Dual-Agent Mode" toggle
3. **Choose Partners**: Select collaborating agents
4. **Chat**: Send your request

---

## API Reference

### Agent Session Management

#### Create Session
```http
POST /api/agents/session
Content-Type: application/json

{
  "agent_name": "jules",
  "context": {"task": "code review"},
  "is_primary": true
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "agent_name": "jules",
  "created_at": 1234567890.0,
  "is_primary": true,
  "message": "Created agent session for jules"
}
```

#### List Active Sessions
```http
GET /api/agents/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-1",
      "agent_name": "jules",
      "created_at": 1234567890.0,
      "is_primary": true
    }
  ],
  "total": 1
}
```

#### End Session
```http
DELETE /api/agents/session/{session_id}
```

### Agent Handoffs

#### Execute Handoff
```http
POST /api/agents/handoff
Content-Type: application/json

{
  "from_agent": "rapid-implementer",
  "to_agent": "jules",
  "context": {"code": "def hello(): pass"},
  "reason": "code review needed"
}
```

#### Get Handoff History
```http
GET /api/agents/handoffs?agent_name=jules&limit=10
```

### Collaborative Processing

#### Collaborate
```http
POST /api/agents/collaborate
Content-Type: application/json

{
  "request": "Build and test user authentication",
  "agents": ["rapid-implementer", "testing-stability-expert", "jules"],
  "mode": "sequential"
}
```

### Agent Routing

#### Get Best Agent
```http
GET /api/agents/route?request=Review%20this%20code&exclude=code-reviewer
```

**Response:**
```json
{
  "recommended_agent": "jules",
  "request": "Review this code"
}
```

### Shared Context

#### Update Context
```http
POST /api/agents/context?key=project_name&value=antigravity
```

#### Get Context
```http
GET /api/agents/context?key=project_name
```

### Statistics

#### Get Agent Stats
```http
GET /api/agents/stats
```

**Response:**
```json
{
  "active_sessions": 2,
  "total_handoffs": 15,
  "handoff_by_agent": {
    "jules": 10,
    "rapid-implementer": 8
  },
  "shared_context_size": 5,
  "agent_priorities": {
    "jules": 10,
    "rapid-implementer": 9
  }
}
```

---

## Usage Examples

### Example 1: Code Review Pipeline

**Goal**: Implement a feature and have Jules review it.

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Implement feature
response = requests.post(f"{BASE_URL}/api/agents/collaborate", json={
    "request": "Implement user password reset with email verification",
    "agents": ["rapid-implementer", "jules"],
    "mode": "sequential"
})

result = response.json()
print("Implementation:", result["results"]["rapid-implementer"])
print("Review:", result["results"]["jules"])
```

### Example 2: Parallel Code Analysis

**Goal**: Get multiple perspectives on code quality.

```python
# Analyze code from different angles
response = requests.post(f"{BASE_URL}/api/agents/collaborate", json={
    "request": "Analyze the payment processing module for issues",
    "agents": ["jules", "code-reviewer", "performance-optimizer"],
    "mode": "parallel"
})

# Each agent provides independent analysis
for agent, result in response.json()["results"].items():
    print(f"\n{agent} Analysis:")
    print(result["response"])
```

### Example 3: Smart Agent Routing

**Goal**: Let the system choose the best agent.

```python
# Get recommendation
response = requests.get(f"{BASE_URL}/api/agents/route", params={
    "request": "This function is running slow, need to optimize it"
})

recommended = response.json()["recommended_agent"]
print(f"Best agent: {recommended}")  # Output: performance-optimizer

# Use recommended agent
response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "Optimize the slow function",
    "agent": recommended
})
```

### Example 4: Agent Handoff with Context

**Goal**: Manually control handoffs between agents.

```python
# Step 1: rapid-implementer builds feature
impl_response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "Implement user profile update endpoint",
    "agent": "rapid-implementer"
})

# Step 2: Handoff to Jules for review
handoff = requests.post(f"{BASE_URL}/api/agents/handoff", json={
    "from_agent": "rapid-implementer",
    "to_agent": "jules",
    "context": {
        "implementation": impl_response.json()["response"],
        "files": ["api/user.py", "tests/test_user.py"]
    },
    "reason": "security and quality review"
})

# Step 3: Jules reviews
review_response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "Review the user profile update endpoint for security issues",
    "agent": "jules"
})
```

---

## Agent Collaboration Patterns

### Pattern 1: Quality Pipeline
**Use Case**: Ensure high-quality code delivery

```
rapid-implementer → jules → testing-stability-expert → docs-master
      (build)      (review)        (test)              (document)
```

### Pattern 2: Iterative Refinement
**Use Case**: Continuous improvement cycle

```
architect → rapid-implementer → jules → rapid-implementer (fixes) → jules (final review)
 (design)     (implement)      (review)    (improvements)            (approve)
```

### Pattern 3: Parallel Analysis
**Use Case**: Multi-perspective code assessment

```
                     ┌─ jules (quality) ─────┐
Code to Analyze ─────┼─ code-reviewer (security) ─┼─→ Combined Report
                     └─ performance-optimizer (speed) ─┘
```

### Pattern 4: Bug Fix Workflow
**Use Case**: Systematic bug resolution

```
debug-detective → jules → rapid-implementer → testing-stability-expert
  (diagnose)    (analyze)    (implement fix)        (verify fix)
```

### Pattern 5: Feature Development
**Use Case**: End-to-end feature creation

```
architect → rapid-implementer → jules → testing-stability-expert → docs-master
 (design)     (implement)      (refine)         (test)              (document)
```

---

## Best Practices

### 1. Choose the Right Agent

Use the routing endpoint to get recommendations:
```bash
curl "http://localhost:8000/api/agents/route?request=your-task-here"
```

### 2. Use Sequential Mode for Quality Pipelines

When order matters and context needs to flow:
```json
{
  "agents": ["rapid-implementer", "jules", "testing-stability-expert"],
  "mode": "sequential"
}
```

### 3. Use Parallel Mode for Independent Tasks

When tasks don't depend on each other:
```json
{
  "agents": ["docs-master", "testing-stability-expert"],
  "mode": "parallel"
}
```

### 4. Leverage Shared Context

Share information across all agents:
```bash
# Set context
curl -X POST "http://localhost:8000/api/agents/context?key=coding_style&value=PEP8"

# All agents can now access this
```

### 5. Track Agent Performance

Monitor which agents work best together:
```bash
curl http://localhost:8000/api/agents/stats
```

### 6. Clean Up Sessions

End sessions when done to free resources:
```bash
curl -X DELETE http://localhost:8000/api/agents/session/{session_id}
```

---

## Troubleshooting

### Agent Not Responding

**Issue**: Agent doesn't produce output

**Solution**:
1. Check agent is spelled correctly: `jules`, not `Jules`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check logs: `tail -f logs/backend.log`

### Handoff Context Lost

**Issue**: Context not transferring between agents

**Solution**:
1. Use sequential mode, not parallel
2. Include explicit context in handoff request
3. Check shared context: `GET /api/agents/context`

### Slow Collaborative Processing

**Issue**: Multi-agent requests take too long

**Solution**:
1. Use parallel mode when possible
2. Reduce number of agents
3. Check cache hit rate: `GET /performance/metrics`

### Agent Priority Conflicts

**Issue**: Wrong agent getting selected

**Solution**:
1. Use explicit agent selection instead of routing
2. Exclude unwanted agents: `?exclude=agent1,agent2`
3. Check current priorities: `GET /api/agents/stats`

---

## Integration with GitHub Copilot

In VS Code with GitHub Copilot:

```
@agent:jules Review this authentication code for security issues

@agent:jules + @agent:rapid-implementer Implement and refine user registration
```

---

## Performance Considerations

### Agent Coordination Overhead

- **Session Creation**: ~1ms
- **Handoff**: ~2ms
- **Context Sharing**: <1ms
- **Routing**: ~5ms

### Caching

Agent responses are cached with:
- **TTL**: 5 minutes (configurable via `CACHE_TTL_SECONDS`)
- **Max Size**: 100 entries (configurable via `CACHE_MAX_SIZE`)
- **Hit Rate**: Typically 40-60%

### Scaling

- **Concurrent Sessions**: Unlimited (memory-limited)
- **Handoffs/minute**: ~1000
- **API Rate Limits**: 30 requests/minute per endpoint

---

## Further Reading

- [Jules Agent Definition](.github/agents/jules.agent.md)
- [Agent Orchestration Guide](.github/agents/AGENT_ORCHESTRATION.md)
- [Coding Workflow Patterns](.github/agents/CODING_WORKFLOW.md)
- [API Documentation](http://localhost:8000/docs)

---

## Support

- **Issues**: https://github.com/primoscope/antigravity-workspace-template/issues
- **Discussions**: https://github.com/primoscope/antigravity-workspace-template/discussions
- **Documentation**: [docs/](docs/)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-09
**Status**: Production Ready
