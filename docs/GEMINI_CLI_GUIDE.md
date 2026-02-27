# Gemini CLI & Agent Framework Integration

## Overview

This directory contains tools for interacting with the Antigravity Workspace agent framework, including:
- **Gemini CLI**: Command-line interface for Google Gemini AI
- **Agent Demo**: Comprehensive demonstration of multi-agent collaboration
- **Integration Examples**: Real-world usage patterns

## 🚀 Quick Start

### Gemini CLI

The Gemini CLI provides direct command-line access to Gemini AI and the agent orchestration system.

#### Installation

No additional installation required if you've already set up the Antigravity Workspace.

#### Basic Usage

```bash
# Navigate to backend directory
cd backend/cli

# Chat with Gemini
python gemini_cli.py chat "Explain machine learning"

# Generate embeddings
python gemini_cli.py embed "Sample text for analysis"

# Analyze a code file
python gemini_cli.py analyze ../../backend/main.py

# Multi-agent collaboration
python gemini_cli.py multi-agent "Build user authentication" --agents jules rapid-implementer

# Show system status
python gemini_cli.py status
```

### Agent Framework Demo

The agent demo showcases flawless integration between all agents.

```bash
# Navigate to examples directory
cd examples

# Run the full integration demo
python agent_demo.py
```

## 📖 Gemini CLI Commands

### chat

Chat with Gemini AI.

```bash
python gemini_cli.py chat "Your prompt here" [--format plain|json|markdown]
```

**Options:**
- `--format plain`: Plain text output (default)
- `--format json`: JSON structured output
- `--format markdown`: Markdown formatted output

**Examples:**
```bash
# Plain text
python gemini_cli.py chat "What is FastAPI?"

# JSON output
python gemini_cli.py chat "Summarize Python" --format json

# Markdown output
python gemini_cli.py chat "List Python features" --format markdown
```

### embed

Generate embeddings for text.

```bash
python gemini_cli.py embed "Text to embed" [--format plain|json]
```

**Examples:**
```bash
# Generate embedding
python gemini_cli.py embed "Machine learning is fascinating"

# JSON output with dimensions
python gemini_cli.py embed "Data science" --format json
```

### analyze

Analyze a code file using Gemini AI.

```bash
python gemini_cli.py analyze <file_path>
```

**Analysis includes:**
- Purpose and functionality
- Key components and structure
- Potential improvements
- Security considerations

**Example:**
```bash
python gemini_cli.py analyze ../backend/agent/orchestrator.py
```

### multi-agent

Execute tasks using multiple agents in collaboration.

```bash
python gemini_cli.py multi-agent "Task description" [--agents agent1 agent2 ...]
```

**Available Agents:**
- `jules`: Code quality and collaboration
- `rapid-implementer`: Fast implementation
- `architect`: System design
- `debug-detective`: Debugging
- `testing-stability-expert`: Testing
- `code-reviewer`: Code review
- `performance-optimizer`: Performance
- `full-stack-developer`: Full-stack
- `devops-infrastructure`: DevOps
- `docs-master`: Documentation
- `repo-optimizer`: Repository optimization
- `api-developer`: API development
- `deep-research`: Research

**Examples:**
```bash
# Default: jules + rapid-implementer
python gemini_cli.py multi-agent "Build REST API for user management"

# Custom agents
python gemini_cli.py multi-agent "Optimize database queries" \
  --agents performance-optimizer code-reviewer

# Full pipeline
python gemini_cli.py multi-agent "Complete feature: user profiles" \
  --agents architect rapid-implementer jules testing-stability-expert docs-master
```

### status

Show comprehensive system status.

```bash
python gemini_cli.py status
```

**Displays:**
- Active agents (13)
- AI provider configuration
- MCP servers status
- Environment variables
- System capabilities
- Agent statistics

## 🎭 Agent Framework Demo

The agent demo (`examples/agent_demo.py`) demonstrates:

### Demo 1: Jules Autonomous Engineering
- Autonomous code analysis
- Self-directed improvements
- Quality assessment
- Recommendations generation

### Demo 2: Sequential Multi-Agent Collaboration
**Workflow:** architect → rapid-implementer → jules → testing-expert

Shows how agents build on each other's work:
1. **Architect**: Designs system architecture
2. **Rapid Implementer**: Implements the design
3. **Jules**: Reviews and refines code
4. **Testing Expert**: Creates comprehensive tests

### Demo 3: Parallel Multi-Agent Analysis
**Agents working simultaneously:**
- Jules: Code quality analysis
- Code Reviewer: Security audit
- Performance Optimizer: Performance analysis

### Demo 4: Seamless Agent Handoff
Demonstrates context-aware handoffs:
- Debug Detective finds bug → Jules fixes it → Testing Expert verifies
- Full context preservation
- Handoff history tracking

### Demo 5: Real-time System Status
Shows current system state:
- Active agents
- Configuration status
- Statistics
- Capabilities

## 🔧 Configuration

### Environment Variables

Required:
```bash
GEMINI_API_KEY=your_gemini_api_key
```

Optional:
```bash
VERTEX_API_KEY=your_vertex_api_key
COPILOT_MCP_GITHUB_TOKEN=your_github_token
HOST=0.0.0.0
PORT=8000
CACHE_TTL_SECONDS=300
```

### Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys

3. Run configuration wizard:
```bash
./configure.sh
```

## 📊 Output Formats

### Plain Text
Default format, human-readable output.

### JSON
Structured data for programmatic processing:
```json
{
  "prompt": "Your prompt",
  "response": "AI response",
  "model": "gemini-pro",
  "status": "success"
}
```

### Markdown
Formatted markdown for documentation:
```markdown
## Prompt
Your prompt here

## Response
AI response here
```

## 🎯 Use Cases

### 1. Quick AI Queries
```bash
python gemini_cli.py chat "How do I implement OAuth2 in FastAPI?"
```

### 2. Code Analysis
```bash
python gemini_cli.py analyze suspicious_file.py
```

### 3. Multi-Agent Development
```bash
# Design and implement
python gemini_cli.py multi-agent "Create user authentication system" \
  --agents architect rapid-implementer

# Review and test
python gemini_cli.py multi-agent "Review authentication code" \
  --agents jules code-reviewer testing-stability-expert
```

### 4. Documentation Generation
```bash
python gemini_cli.py multi-agent "Document the API endpoints" \
  --agents docs-master
```

### 5. Performance Optimization
```bash
python gemini_cli.py multi-agent "Optimize slow database queries" \
  --agents performance-optimizer code-reviewer
```

## 🔍 Troubleshooting

### API Key Not Set
```
ERROR: GEMINI_API_KEY not set in environment
```
**Solution**: Set `GEMINI_API_KEY` in `.env` file

### Import Errors
```
ModuleNotFoundError: No module named 'agent'
```
**Solution**: Run CLI from `backend/cli/` directory or ensure Python path is set

### Agent Not Found
```
ValueError: Unknown agent 'agent-name'
```
**Solution**: Check agent name spelling, use `status` command to see available agents

## 📈 Performance Tips

1. **Use Caching**: Responses are automatically cached for 5 minutes
2. **Batch Operations**: Use multi-agent for complex tasks
3. **Format Selection**: Use JSON format for programmatic processing
4. **Parallel Mode**: For independent tasks, agents work in parallel

## 🔗 Integration with GitHub Copilot

In VS Code with GitHub Copilot:
```
@agent:jules Review this code for security issues
@agent:rapid-implementer Implement user registration endpoint
```

## 📚 Additional Resources

- [Jules Agent Documentation](../../.github/agents/jules.agent.md)
- [Integration Guide](../../docs/JULES_INTEGRATION.md)
- [API Documentation](http://localhost:8000/docs)
- [Agent Quick Reference](../../.github/agents/README.md)

## 🆘 Support

- **Issues**: https://github.com/primoscope/antigravity-workspace-template/issues
- **Discussions**: https://github.com/primoscope/antigravity-workspace-template/discussions

---

**Version**: 1.0.0
**Last Updated**: 2026-02-09
**Status**: Production Ready ✅
