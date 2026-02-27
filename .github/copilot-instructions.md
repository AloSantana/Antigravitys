# Copilot Instructions for Antigravity Workspace Template

## Purpose

This document provides comprehensive guidance for GitHub Copilot and AI coding agents working on this repository. It follows [GitHub's best practices for Copilot coding agents](https://gh.io/copilot-coding-agent-tips).

## Quick Reference

- **Language**: Python 3.8+ (Backend), JavaScript ES6+ (Frontend)
- **Framework**: FastAPI (REST API), WebSockets (Real-time)
- **AI/ML**: Langchain, ChromaDB, Gemini AI, Ollama
- **Testing**: pytest
- **Deployment**: Docker, Docker Compose, Systemd, Kubernetes
- **CI/CD**: GitHub Actions (`.github/workflows/`)

## Repository Overview

This is an **AI-powered development workspace** with automated setup, custom coding agents, 18 MCP servers, and an enhanced web GUI for advanced development workflows. It provides a production-ready environment for AI-assisted development.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **AI/ML**: 
  - Langchain (orchestration)
  - ChromaDB (vector database)
  - Google Gemini AI (cloud model)
  - Ollama (local models)
- **Other**: Watchdog (file monitoring), WebSockets, Pydantic

### Frontend
- **Pure HTML/CSS/JavaScript** with CodeMirror for code editing
- Multi-tab interface (Chat, Code Editor, Terminal)
- Real-time WebSocket communication

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Deployment**: Systemd service, Kubernetes-ready
- **MCP Servers**: 18 Model Context Protocol servers for enhanced capabilities

## Project Structure

```
.
├── .github/
│   ├── agents/              # Custom AI agent definitions
│   ├── copilot/             # Copilot configuration (mcp.json)
│   └── workflows/           # CI/CD workflows
├── backend/
│   ├── agent/              # Agent management and orchestration
│   │   ├── manager.py      # Agent lifecycle management
│   │   ├── orchestrator.py # AI orchestration
│   │   ├── gemini_client.py # Gemini AI client
│   │   └── local_client.py  # Local Ollama client
│   ├── rag/                # RAG (Retrieval-Augmented Generation)
│   ├── utils/              # Utility functions and helpers
│   │   └── performance.py  # Performance monitoring
│   ├── watcher.py          # File watching and ingestion
│   └── main.py             # FastAPI application entry point
├── frontend/
│   └── index.html          # Enhanced web interface
├── drop_zone/              # File drop area for RAG ingestion
├── artifacts/              # Generated artifacts
├── tests/                  # Test suite
└── docs/                   # Documentation

```

## Custom AI Agents

This repository includes **12 specialized agents** for different development tasks:

1. **rapid-implementer**: Fast, autonomous end-to-end code implementation
2. **architect**: System architecture and design decisions
3. **debug-detective**: Advanced debugging and root cause analysis
4. **deep-research**: Comprehensive research and analysis (flagship agent)
5. **full-stack-developer**: Complete web application development
6. **devops-infrastructure**: Docker, Kubernetes, CI/CD
7. **testing-stability-expert**: Testing and validation
8. **performance-optimizer**: Performance profiling and optimization
9. **code-reviewer**: Security and quality reviews
10. **docs-master**: Documentation creation
11. **repo-optimizer**: Repository setup and tooling
12. **api-developer**: API design and implementation

**Usage**: `@agent:rapid-implementer Implement complete user authentication with JWT tokens`

## MCP Servers Available

### Core Development (Always Active)
- `filesystem`: File operations
- `git`: Version control
- `github`: GitHub integration (Docker-based)
- `memory`: Context persistence
- `sequential-thinking`: Enhanced reasoning

### Data & Storage
- `sqlite`: Local database

### Web & Automation
- `puppeteer`: Browser automation
- `fetch`: HTTP requests

### Infrastructure & Utilities
- `docker`: Container management
- `time`: Time and timezone operations

## Development Guidelines

### Code Style & Conventions

#### Python
- **Style**: Follow PEP 8
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Imports**: Absolute imports, grouped (standard lib, third-party, local)
- **Async**: Use async/await for I/O operations
- **Error Handling**: Specific exception types, proper logging

**Error Handling Best Practices:**
```python
import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

async def process_request(
    request_id: str,
    data: Dict[str, Any],
    timeout: Optional[int] = 30
) -> Dict[str, Any]:
    """Process a request with the given data.
    
    Args:
        request_id: Unique identifier for the request
        data: Request payload
        timeout: Optional timeout in seconds
        
    Returns:
        Processed response data
        
    Raises:
        ValueError: If request_id is invalid
        TimeoutError: If processing exceeds timeout
    """
    # Validate inputs
    if not request_id or not isinstance(request_id, str):
        raise ValueError("request_id must be a non-empty string")
    
    # Handle edge cases
    if not data:
        logger.warning(f"Empty data for request {request_id}")
        return {"status": "empty", "request_id": request_id}
    
    try:
        # Implementation with timeout using asyncio.wait_for
        async def _process() -> Dict[str, Any]:
            """Core processing logic for the request.
            
            This is a placeholder implementation; replace with real logic.
            """
            # TODO: Replace this with actual processing code.
            return data

        result = await asyncio.wait_for(_process(), timeout=timeout)
        return {"status": "success", "data": result}
    except TimeoutError:
        logger.error(f"Request {request_id} timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Failed to process request {request_id}: {e}", exc_info=True)
        # Re-raise with context
        raise RuntimeError(f"Processing failed: {e}") from e
```

**Common Edge Cases to Handle:**
- Empty or None inputs
- Invalid data types
- Network timeouts
- File not found errors
- Permission errors
- Concurrent access issues
- Resource exhaustion (memory, disk, connections)

Example:
```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def process_request(
    request_id: str,
    data: Dict[str, Any],
    timeout: Optional[int] = 30
) -> Dict[str, Any]:
    """Process a request with the given data.
    
    Args:
        request_id: Unique identifier for the request
        data: Request payload
        timeout: Optional timeout in seconds
        
    Returns:
        Processed response data
        
    Raises:
        ValueError: If request_id is invalid
        TimeoutError: If processing exceeds timeout
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Failed to process request {request_id}: {e}")
        raise
```

#### JavaScript/Frontend
- **Style**: Modern ES6+ syntax
- **Async**: Use async/await over callbacks
- **Error Handling**: Try-catch blocks with user-friendly messages
- **DOM**: Vanilla JS, minimize dependencies
- **WebSocket**: Maintain connection state, handle reconnection

**Frontend Error Handling:**
```javascript
// API call with error handling
async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch data:', error);
        
        // Show user-friendly message using console and optionally alert
        console.error('Unable to load data. Please try again.');
        
        // Return default/fallback data
        return { status: 'error', message: error.message };
    }
}

// WebSocket with reconnection
class ResilientWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectDelay = 1000; // Reset delay
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket closed, reconnecting...');
            setTimeout(() => this.connect(), this.reconnectDelay);
            // Exponential backoff
            this.reconnectDelay = Math.min(
                this.reconnectDelay * 2, 
                this.maxReconnectDelay
            );
        };
    }
    
    send(data) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not ready, message dropped. Consider implementing a queue.');
        }
    }
}
```

### Testing

- **Framework**: pytest
- **Location**: `tests/` directory
- **Coverage**: Aim for >80% coverage on critical paths
- **Types**:
  - Unit tests: `test_*.py` (fast, isolated)
  - Integration tests: `test_integration_*.py` (with dependencies)
  - System tests: `test_system.py` (end-to-end)

**Running Tests:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage (requires pytest-cov: pip install pytest-cov)
pytest --cov=backend --cov-report=term-missing tests/

# Run specific test file
pytest tests/test_agent.py -v

# Run specific test function
pytest tests/test_agent.py::test_agent_creation -v

# Run tests matching pattern
pytest -k "agent" -v
```

Example:
```python
import pytest
from backend.agent.manager import AgentManager

@pytest.fixture
def agent_manager():
    """Fixture for AgentManager instance."""
    return AgentManager()

def test_agent_creation(agent_manager):
    """Test that agents are created correctly."""
    agent = agent_manager.create_agent("test-agent")
    assert agent is not None
    assert agent.name == "test-agent"
```

### API Design

- **Framework**: FastAPI
- **Endpoints**: RESTful conventions
- **Versioning**: `/api/v1/` prefix for versioned endpoints
- **Status Codes**: Proper HTTP status codes (200, 201, 400, 404, 500)
- **Documentation**: Auto-generated with FastAPI (available at `/docs`)
- **Error Responses**: Consistent JSON error format

Example:
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

class AgentRequest(BaseModel):
    name: str
    type: str
    config: dict = {}

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentRequest):
    """Create a new agent instance."""
    try:
        # Implementation
        return {"agent_id": "123", "status": "created"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### Code Quality & Linting

**Note**: The repository currently uses pytest for testing. Linting tools listed below can be added as needed following the minimal dependencies philosophy. Install them first before running the commands:
```bash
pip install black flake8 mypy isort
```

**Tools:**
- **black**: Code formatting (configure in `pyproject.toml` if needed)
- **flake8** or **ruff**: Linting (add to requirements if needed)
- **mypy**: Type checking
- **isort**: Import sorting

**Running Quality Checks:**
```bash
# Format code with black
black backend/ tests/

# Check formatting
black --check backend/ tests/

# Run linter
flake8 backend/ tests/

# Type checking
mypy backend/

# Sort imports
isort backend/ tests/
```

### Performance Considerations

- **Async I/O**: Use async for all I/O operations (file, network, database)
- **Caching**: Leverage Redis/in-memory caching for expensive operations
- **Vector DB**: ChromaDB for similarity search (RAG)
- **Monitoring**: Use performance monitoring endpoints (`/performance/*`)
- **Batch Operations**: Prefer batch processing for multiple items

### Security Best Practices

- **Environment Variables**: Never commit secrets, use `.env` files
- **API Keys**: Store in environment variables with `COPILOT_MCP_*` prefix
- **Input Validation**: Use Pydantic models for request validation
- **Authentication**: JWT tokens for API authentication (when implemented)
- **CORS**: Configured appropriately for production
- **Dependencies**: Keep dependencies updated, check for vulnerabilities

### AI/Agent Development

When working with AI agents:

1. **Agent Files**: Located in `.github/agents/*.agent.md`
2. **Agent Metadata**: Use YAML frontmatter for configuration
3. **MCP Integration**: Specify required MCP servers in metadata
4. **Prompts**: Clear, specific instructions in agent files
5. **Orchestration**: Use `backend/agent/orchestrator.py` for multi-agent workflows

### File Organization

- **Backend**: All Python backend code in `backend/`
- **Frontend**: All web UI code in `frontend/`
- **Agents**: Agent definitions in `.github/agents/`
- **Config**: Configuration in `.github/copilot/` and `.mcp/`
- **Scripts**: Utility scripts in root (install.sh, start.sh, etc.)
- **Docs**: Documentation in `docs/` and root-level `.md` files
- **Drop Zone**: User-uploaded files in `drop_zone/` (for RAG)
- **Artifacts**: Generated content in `artifacts/`

### Environment Setup

Required environment variables (see `.env.example`):
```bash
# AI Models
GEMINI_API_KEY=your_api_key_here
LOCAL_MODEL=llama3

# GitHub Integration  
COPILOT_MCP_GITHUB_TOKEN=your_token_here

# Optional Services
COPILOT_MCP_BRAVE_API_KEY=
COPILOT_MCP_POSTGRES_CONNECTION_STRING=

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**Environment Setup Steps:**
```bash
# 1. Copy example environment file
cp .env.example .env

# 2. Edit with your credentials
nano .env  # or vim .env

# 3. Run configuration wizard (interactive)
./configure.sh

# 4. Validate configuration
./validate.sh
```

**Multiple Environments:**
```bash
# Development
cp .env.example .env.development
# Edit .env.development with dev settings

# Production
cp .env.example .env.production
# Edit .env.production with prod settings

# Load specific environment (start.sh reads from .env)
cp .env.development .env   # for development
./start.sh
# or:
cp .env.production .env    # for production
./start.sh
```

### Running the Application

```bash
# Quick start
./start.sh

# Or manually
cd backend
python main.py

# With Docker
docker-compose up -d

# Run tests
pytest tests/ -v
```

### Building & Dependencies

**Installing Dependencies:**
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install development dependencies (testing, linting)
pip install pytest pytest-cov black flake8 mypy
```

**Verifying Installation:**
```bash
# Run validation script
./validate.sh

# Or manual health check
./health-check.sh

# Check service status (if using systemd)
sudo systemctl status antigravity
```

### Common Tasks

#### Adding a New API Endpoint
1. Define Pydantic models for request/response
2. Create router in appropriate module
3. Add route handler with proper error handling
4. Include in main.py router registration
5. Add tests in `tests/`

#### Adding a New Agent
1. Create `*.agent.md` in `.github/agents/`
2. Add YAML frontmatter with metadata
3. Document agent capabilities and workflows
4. Test agent with `@agent:your-agent-name` syntax

#### Adding a New MCP Server
1. Install MCP server (npm or pip)
2. Add configuration to `.github/copilot/mcp.json`
3. Add environment variables if needed
4. Document in COPILOT_SETUP.md

#### Optimizing Performance
1. Use `@agent:performance-optimizer` for analysis
2. Profile with `/performance/analysis` endpoint
3. Implement caching where appropriate
4. Use async operations for I/O
5. Monitor with `/performance/metrics`

## Workflow Patterns

### Fast Feature Development (New!)
```
1. @agent:architect - Design the feature architecture
2. @agent:rapid-implementer - Implement complete feature end-to-end
3. @agent:testing-stability-expert - Create comprehensive tests
4. @agent:code-reviewer - Security and quality review
5. @agent:docs-master - Document the feature
```

### Deep Research Workflow (New!)
```
1. @agent:deep-research - Comprehensive analysis of problem/technology
2. @agent:architect - Design solution based on research
3. @agent:rapid-implementer - Implement the solution
4. @agent:code-reviewer - Review implementation
```

### Systematic Debugging (New!)
```
1. @agent:debug-detective - Investigate and identify root cause
2. @agent:rapid-implementer - Implement the fix
3. @agent:testing-stability-expert - Add regression tests
4. @agent:code-reviewer - Review the fix
```

### Feature Development (Classic)
```
1. @agent:repo-optimizer - Setup feature structure
2. [Implement feature]
3. @agent:testing-stability-expert - Create tests
4. @agent:code-reviewer - Review implementation
5. @agent:docs-master - Document the feature
```

### Bug Fix
```
1. @agent:debug-detective - Analyze root cause (or code-reviewer)
2. [Fix the bug]
3. @agent:testing-stability-expert - Add regression tests
4. @agent:performance-optimizer - Check performance impact
```

### Performance Optimization
```
1. @agent:performance-optimizer - Profile and identify bottlenecks
2. [Implement optimizations]
3. @agent:testing-stability-expert - Verify correctness
4. @agent:code-reviewer - Review changes
```

### Technology Evaluation (New!)
```
1. @agent:deep-research - Research and compare options
2. @agent:architect - Evaluate architectural fit
3. @agent:rapid-implementer - Create proof-of-concept
4. @agent:code-reviewer - Security analysis
```

## Continuous Integration

- **Testing**: Automated tests run on PR
- **Linting**: Code quality checks
- **Security**: Dependency scanning
- **Build**: Docker image building
- **Deploy**: Automated deployment on merge to main

### GitHub Actions Workflows

**Test Workflow** (`.github/workflows/test.yml`):
- Triggered on: Push to `main`, Pull Requests
- Python versions: 3.12
- Steps: Install dependencies → Run pytest

**Deploy Workflow** (`.github/workflows/deploy.yml`):
- Triggered on: Push to `main`
- Steps: Build Docker image → Deploy to production

**Running CI Locally:**
```bash
# Run tests (same as CI)
pytest tests/ -v

# Run in Docker (same as CI environment)
docker-compose up -d
docker-compose exec backend pytest tests/ -v

# Validate before pushing
./validate.sh
```

## Monitoring & Debugging

### Health Checks & Monitoring

- **Health Check**: `./health-check.sh` or `/health` endpoint
- **Logs**: Check `sudo journalctl -u antigravity -f`
- **Metrics**: `/performance/metrics` endpoint
- **Validation**: `./validate.sh` for comprehensive checks

**Key Endpoints:**
```bash
# Health status
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/performance/metrics

# Performance analysis
curl http://localhost:8000/performance/analysis

# API documentation
http://localhost:8000/docs
```

### Debugging Tips

**Backend Debugging:**
```bash
# Run with debug logging
cd backend
python -m pdb main.py

# Check application logs
tail -f logs/app.log  # If logging to file

# View systemd service logs
sudo journalctl -u antigravity -n 100 -f

# Check running processes
ps aux | grep python
```

**Common Issues:**
1. **Port already in use**: Check with `lsof -i :8000`, kill process or change port
2. **Module not found**: Ensure virtual environment is activated and dependencies installed
3. **API key errors**: Verify `.env` file contains correct keys
4. **Database errors**: Check ChromaDB initialization and permissions
5. **MCP server issues**: Verify MCP servers are installed (`npm list -g`)

**WebSocket Debugging:**
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => console.error('Error:', e);
```

### Troubleshooting Workflow

1. **Check service status**: `./health-check.sh`
2. **Review logs**: `sudo journalctl -u antigravity -f`
3. **Validate configuration**: `./validate.sh`
4. **Test API endpoints**: Visit `/docs` and test interactively
5. **Check dependencies**: Ensure all MCP servers and Python packages installed
6. **Review environment**: Verify `.env` file has all required variables

## Documentation

- **README.md**: Main project documentation
- **COPILOT_SETUP.md**: Copilot and agent setup guide
- **TROUBLESHOOTING.md**: Common issues and solutions
- **.github/agents/README.md**: Agent quick reference
- **API Docs**: Auto-generated at `/docs` endpoint

## Important Notes

1. **Never commit secrets** - Use environment variables
2. **Always use type hints** in Python code
3. **Write tests** for new functionality
4. **Update documentation** when changing features
5. **Use appropriate agents** for specialized tasks
6. **Follow async patterns** for I/O operations
7. **Validate inputs** with Pydantic models
8. **Handle errors gracefully** with proper logging
9. **Optimize after profiling** - don't prematurely optimize
10. **Keep dependencies updated** and secure

## Pull Request Guidelines

When creating or reviewing PRs:

1. **Before Submitting:**
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Validate setup
   ./validate.sh
   
   # Check code quality (if tools installed)
   black --check backend/ tests/
   flake8 backend/ tests/
   ```

2. **PR Description Should Include:**
   - Summary of changes
   - Related issue numbers
   - Testing performed
   - Breaking changes (if any)
   - Screenshots for UI changes

3. **Code Review Checklist:**
   - [ ] Code follows style guidelines
   - [ ] Tests pass locally
   - [ ] New tests added for new features
   - [ ] Documentation updated
   - [ ] No secrets in code
   - [ ] Error handling is appropriate
   - [ ] Performance impact considered

## Getting Help

- **Agent Docs**: `.github/agents/README.md`
- **MCP Docs**: `.mcp/README.md` 
- **Workflow Guides**: `.github/agents/CODING_WORKFLOW.md`
- **Issues**: https://github.com/primoscope/antigravity-workspace-template/issues
- **Discussions**: https://github.com/primoscope/antigravity-workspace-template/discussions

---

**When in doubt**: Use the specialized agents! They have deep knowledge of their domains and can guide you effectively.
