# GitHub Copilot Custom Agents - Quick Reference

This repository includes **13 specialized AI agents** optimized for development workflows with **10 MCP servers** for enhanced capabilities, plus **dual-agent collaboration mode** for seamless teamwork.

## 🤖 Available Custom Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **jules** ⭐ NEW | Code quality, collaboration, refactoring | Code review, quality improvement, agent coordination |
| **rapid-implementer** | Fast, autonomous code implementation | Speed-focused feature development, end-to-end implementation |
| **architect** | System architecture and design | Designing systems, architectural decisions, reviewing architecture |
| **debug-detective** | Advanced debugging and root cause analysis | Investigating bugs, systematic debugging, problem diagnosis |
| **deep-research** | Comprehensive research and analysis | Repository analysis, problem investigation, solution research |
| **repo-optimizer** | Repository setup, tooling, function improvements | Setting up projects, improving tools, enhancing functions |
| **testing-stability-expert** | Comprehensive testing, stability validation | Writing tests, ensuring reliability, quality assurance |
| **docs-master** | Documentation creation and verification | Writing docs, verifying accuracy, updating guides |
| **code-reviewer** | Code quality and security review | Reviewing PRs, checking security, ensuring best practices |
| **performance-optimizer** | Performance tuning and optimization | Fixing slow code, reducing memory usage, profiling |
| **full-stack-developer** | Complete web application development | Building full features, frontend+backend work |
| **devops-infrastructure** | Docker, Kubernetes, CI/CD | Infrastructure setup, deployment, DevOps tasks |
| **api-developer** | API design and implementation | Creating REST APIs, API documentation, endpoint design |

## ⚡ Quick Start Examples

### Using Agents with GitHub Copilot

```bash
# In GitHub Copilot Chat (VS Code, GitHub.com, etc.)

# Fast implementation
@agent:rapid-implementer Implement complete user authentication with JWT tokens

# System design
@agent:architect Design a scalable microservices architecture for this application

# Advanced debugging
@agent:debug-detective Investigate why the login endpoint returns 500 errors intermittently

# Deep research
@agent:deep-research Analyze this repository and provide a comprehensive health assessment

# Repository optimization
@agent:repo-optimizer Setup pre-commit hooks and linting for this Python project

# Testing
@agent:testing-stability-expert Create comprehensive unit tests for src/utils/parser.py

# Documentation
@agent:docs-master Verify all features in README.md are implemented and working

# Code review
@agent:code-reviewer Review the changes in src/api/auth.py for security issues

# Performance
@agent:performance-optimizer Optimize the database queries in src/repositories/user_repo.py

# Full-stack development
@agent:full-stack-developer Build a complete user profile management feature

# DevOps
@agent:devops-infrastructure Setup Docker Compose for local development

# API development
@agent:api-developer Design and implement REST API endpoints for blog posts
```

### Agent + MCP Server Combinations

The agents automatically leverage MCP servers for enhanced capabilities:

#### Rapid Implementer + MCP Servers
```
🤖 rapid-implementer uses:
  📁 filesystem - Batch read/write operations
  🔧 git - Version control
  🐙 github - Search patterns
  🧠 memory - Remember implementation patterns
  🧮 sequential-thinking - Plan complex features
```

#### Architect + MCP Servers
```
🤖 architect uses:
  📁 filesystem - Analyze codebase structure
  🔧 git - Study evolution patterns
  🐙 github - Research best practices
  🧠 memory - Store architectural decisions
  🧮 sequential-thinking - Design complex systems
```

#### Debug Detective + MCP Servers
```
🤖 debug-detective uses:
  📁 filesystem - Read code and logs
  🔧 git - Analyze code history
  🐙 github - Find similar issues
  🧠 memory - Remember bug patterns
  🧮 sequential-thinking - Systematic debugging
```

#### Deep Research + MCP Servers
```
🤖 deep-research uses:
  📁 filesystem - Comprehensive code analysis
  🔧 git - Historical analysis
  🐙 github - Cross-repo research
  🧠 memory - Maintain research context
  🧮 sequential-thinking - Multi-phase research
  🌐 fetch - External documentation
  🗄️ sqlite - Store research findings
```

#### Repo Optimizer + MCP Servers
```
🤖 repo-optimizer uses:
  📁 filesystem - Read/write config files
  🔧 git - Manage version control
  🐙 github - Search best practices
  🧠 memory - Remember patterns
```

#### Testing Expert + MCP Servers
```
🤖 testing-stability-expert uses:
  📁 filesystem - Create test files
  🐙 github - Find test patterns
  🧠 memory - Remember edge cases
  🧮 sequential-thinking - Plan test strategies
```

#### Docs Master + MCP Servers
```
🤖 docs-master uses:
  📁 filesystem - Write documentation
  🌐 fetch - Verify links
  📸 puppeteer - Capture screenshots
  🐙 github - Search examples
  🧠 memory - Track doc structure
```

## 🎯 Workflow Patterns

### Pattern 1: Fast Feature Development
```
1. @agent:architect - Design the feature architecture
2. @agent:rapid-implementer - Implement the complete feature
3. @agent:testing-stability-expert - Create comprehensive tests
4. @agent:code-reviewer - Review for quality and security
5. @agent:docs-master - Document the feature
```

### Pattern 2: Bug Investigation & Fix
```
1. @agent:debug-detective - Investigate and identify root cause
2. @agent:rapid-implementer - Implement the fix
3. @agent:testing-stability-expert - Add regression tests
4. @agent:code-reviewer - Review the fix
```

### Pattern 3: System Design
```
1. @agent:deep-research - Research best practices and patterns
2. @agent:architect - Design the system architecture
3. @agent:rapid-implementer - Implement core components
4. @agent:code-reviewer - Architectural review
```

### Pattern 4: Repository Analysis
```
1. @agent:deep-research - Comprehensive repository health analysis
2. @agent:architect - Review architecture and propose improvements
3. @agent:repo-optimizer - Implement tooling improvements
4. @agent:docs-master - Update documentation
```

### Pattern 5: Feature Development
```
1. @agent:repo-optimizer - Setup feature branch and structure
2. [Develop feature]
3. @agent:testing-stability-expert - Create comprehensive tests
4. @agent:code-reviewer - Review implementation
5. @agent:docs-master - Document the feature
```

### Pattern 6: Performance Issue
```
1. @agent:debug-detective - Identify performance bottleneck
2. @agent:performance-optimizer - Implement optimizations
3. @agent:testing-stability-expert - Verify stability after optimization
4. @agent:code-reviewer - Review for correctness
```

### Pattern 7: Technology Evaluation
```
1. @agent:deep-research - Research technology options and best practices
2. @agent:architect - Evaluate architectural fit
3. @agent:repo-optimizer - Prototype integration
4. @agent:code-reviewer - Security and quality review
```

## 🔧 MCP Server Capabilities

### Core Development (Always Active)
- **filesystem** - File operations (read, write, edit, search)
- **git** - Version control (commit, branch, diff, log)
- **github** - GitHub integration (issues, PRs, code search)
- **memory** - Context persistence across sessions
- **sequential-thinking** - Enhanced reasoning for complex tasks

### Data & Storage
- **sqlite** - Local database operations

### Web & Automation
- **puppeteer** - Browser automation and testing
- **fetch** - HTTP requests and web content

### Infrastructure & Utilities
- **docker** - Container management
- **time** - Time and timezone operations

## 📚 Documentation

### For Agents
- [`rapid-implementer.agent.md`](.github/agents/rapid-implementer.agent.md) - Speed-focused implementation
- [`architect.agent.md`](.github/agents/architect.agent.md) - System architecture and design
- [`debug-detective.agent.md`](.github/agents/debug-detective.agent.md) - Advanced debugging
- [`deep-research.agent.md`](.github/agents/deep-research.agent.md) - Comprehensive research and analysis
- [`repo-optimizer.agent.md`](.github/agents/repo-optimizer.agent.md) - Repository optimization guide
- [`testing-stability-expert.agent.md`](.github/agents/testing-stability-expert.agent.md) - Testing strategies
- [`docs-master.agent.md`](.github/agents/docs-master.agent.md) - Documentation best practices
- [`code-reviewer.agent.md`](.github/agents/code-reviewer.agent.md) - Code review standards
- [`performance-optimizer.agent.md`](.github/agents/performance-optimizer.agent.md) - Performance patterns
- [`full-stack-developer.agent.md`](.github/agents/full-stack-developer.agent.md) - Full-stack development
- [`devops-infrastructure.agent.md`](.github/agents/devops-infrastructure.agent.md) - DevOps and infrastructure
- [`api-developer.agent.md`](.github/agents/api-developer.agent.md) - API design and implementation

### For MCP Servers
- [`.mcp/README.md`](.mcp/README.md) - Complete MCP server documentation
- [`.github/copilot/mcp.json`](.github/copilot/mcp.json) - GitHub Copilot MCP config
- [`.github/copilot/OPTIONAL_SERVERS.md`](.github/copilot/OPTIONAL_SERVERS.md) - Optional MCP servers guide
- [`.mcp/config.json`](.mcp/config.json) - Generic MCP client config

### Workflow Guides
- [`AGENT_ORCHESTRATION.md`](.github/agents/AGENT_ORCHESTRATION.md) - Multi-agent coordination
- [`CODING_WORKFLOW.md`](.github/agents/CODING_WORKFLOW.md) - Optimized development workflows

## 🚀 Advanced Usage

### Chaining Agents
```bash
# Complex task requiring multiple agents

# Step 1: Research and design
@agent:deep-research Research best practices for implementing user authentication
# Then:
@agent:architect Design authentication system architecture

# Step 2: Implementation
@agent:rapid-implementer Implement the authentication system based on the architecture

# Step 3: Quality assurance
@agent:testing-stability-expert Create comprehensive tests for authentication
# Then:
@agent:code-reviewer Review authentication implementation for security

# Step 4: Documentation
@agent:docs-master Document the authentication system and API
```

### Using with Specific MCP Servers
Agents automatically use appropriate MCP servers, but you can request specific functionality:

```bash
# Will use github + git MCP servers
@agent:deep-research Search GitHub for authentication best practices and analyze patterns

# Will use filesystem + sequential-thinking MCP servers  
@agent:architect Analyze the current codebase architecture and propose improvements

# Will use git + github MCP servers
@agent:debug-detective Use git history to find when this bug was introduced

# Will use fetch + github MCP servers
@agent:deep-research Research and compare authentication libraries for Python
```

### Environment Variables
For full MCP functionality, set these environment variables:

```bash
# Required for GitHub integration
export COPILOT_MCP_GITHUB_TOKEN="ghp_your_token_here"

# Optional (see .github/copilot/OPTIONAL_SERVERS.md for more)
export COPILOT_MCP_BRAVE_API_KEY="your_brave_api_key"
export COPILOT_MCP_POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:port/db"
```

## 💡 Tips for Best Results

1. **Be Specific**: Clear instructions get better results
   - ❌ "Fix the code"
   - ✅ "Review auth.py for SQL injection vulnerabilities"

2. **Use Right Agent**: Match task to agent expertise
   - Fast implementation → rapid-implementer
   - System design → architect
   - Debugging → debug-detective
   - Research → deep-research
   - Testing → testing-stability-expert
   - Docs → docs-master
   - Performance → performance-optimizer

3. **Leverage MCP**: Agents use MCP servers automatically
   - No need to manually specify
   - They choose optimal tools for the task

4. **Iterate**: Agents can work incrementally
   - Start with one agent
   - Chain to others as needed
   - Build up complexity gradually

5. **Verify**: Always review agent outputs
   - Agents are powerful but not perfect
   - Human oversight ensures quality

## 🔄 Continuous Improvement

The agent + MCP configuration enables:
- **Rapid Development** via rapid-implementer agent
- **Systematic Debugging** via debug-detective agent
- **Deep Analysis** via deep-research agent
- **Architectural Excellence** via architect agent
- **Automated quality checks** via code-reviewer
- **Context persistence** via memory server
- **Enhanced reasoning** via sequential-thinking
- **Real-time GitHub integration** via github server
- **Automated testing** via testing-stability-expert
- **Performance monitoring** via performance-optimizer

## 📊 Expected Benefits

With this configuration, you can expect:
- **Faster Development**: Agents automate repetitive tasks
- **Higher Quality**: Automated reviews and testing
- **Better Documentation**: Consistent, verified docs
- **Improved Performance**: Proactive optimization
- **Enhanced Security**: Automated security reviews

## 🆘 Getting Help

- **Agent Issues**: Check individual agent documentation
- **MCP Issues**: See [MCP README](.mcp/README.md)
- **Workflow Questions**: See [AGENT_ORCHESTRATION.md](.github/agents/AGENT_ORCHESTRATION.md)
- **Project Issues**: [Open an issue](https://github.com/AloSantana/Antigravitys/issues)

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-06  
**License**: MIT
