# GitHub Copilot & Custom Agents Setup Guide

This guide helps you configure and start using the custom agents and MCP servers in this repository.

## What You Get

✅ **5 Specialized AI Agents** for development workflows
✅ **14 MCP Servers** for enhanced capabilities  
✅ **Optimized workflows** for common dev tasks
✅ **Production-ready** configuration

## Quick Setup (5 minutes)

### Automated Setup (Recommended)

Run the automated setup scripts:

```bash
# Make scripts executable (if needed)
chmod +x quick-fix.sh health-check.sh

# 1. Quick fix common issues
./quick-fix.sh
# Or: bash quick-fix.sh

# 2. Verify everything works
./health-check.sh
# Or: bash health-check.sh
```

These scripts will automatically:
- Create .env file template
- Install MCP servers
- Clear caches
- Validate configuration
- Check prerequisites

### Manual Setup (Alternative)

### Step 1: Prerequisites Check

```bash
# Check Node.js (required for MCP servers)
node --version
# Should be v16 or higher

# Check Python (required for python-analysis)
python --version
# Should be 3.8 or higher

# Check npm/npx
npx --version
```

If you don't have these, install them first:
- Node.js: https://nodejs.org/
- Python: https://www.python.org/

### Step 2: Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# Required for GitHub integration
GITHUB_TOKEN=your_github_token_here
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# Optional - enable as needed
# BRAVE_API_KEY=your_brave_api_key
# POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
EOF
```

**Get a GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the token and add to `.env`

### Step 3: Install Python MCP Server (Optional)

For Python code analysis:

```bash
pip install mcp-server-python-analysis
```

### Step 4: Verify Configuration

```bash
# Test that MCP config is valid
cat .github/copilot/mcp.json | python -m json.tool > /dev/null && echo "✅ MCP config valid"

# Test an MCP server
npx -y @modelcontextprotocol/server-filesystem . --help
```

### Step 5: Load Environment Variables

```bash
# Load environment variables
source .env

# Verify
echo $GITHUB_TOKEN | cut -c1-8
# Should show first 8 characters of your token
```

## Using Custom Agents

### In GitHub Copilot (VS Code, GitHub.com)

```bash
# Open GitHub Copilot Chat and use agents:

@agent:repo-optimizer Setup pre-commit hooks for Python
@agent:testing-stability-expert Create tests for src/utils.py
@agent:docs-master Update API documentation
@agent:code-reviewer Review security of auth.py
@agent:performance-optimizer Profile database queries
```

### Available Agents

| Agent Name | Purpose | Example Usage |
|------------|---------|---------------|
| `repo-optimizer` | Repository setup & tooling | Setup linting and CI/CD |
| `testing-stability-expert` | Testing & validation | Create comprehensive tests |
| `docs-master` | Documentation | Verify docs accuracy |
| `code-reviewer` | Code quality & security | Review PR for security |
| `performance-optimizer` | Performance tuning | Optimize slow functions |

## MCP Servers Enabled

### Always Active (Core Development)
- ✅ **filesystem** - File operations
- ✅ **git** - Version control
- ✅ **github** - GitHub integration
- ✅ **python-analysis** - Code analysis
- ✅ **memory** - Context persistence
- ✅ **sequential-thinking** - Enhanced reasoning

### Active by Default
- ✅ **sqlite** - Database operations
- ✅ **puppeteer** - Browser automation
- ✅ **fetch** - HTTP requests
- ✅ **docker** - Container management

### Disabled (Enable When Needed)
- ⚠️ **postgres** - PostgreSQL (set enabled: true)
- ⚠️ **playwright** - Alternative to puppeteer
- ⚠️ **brave-search** - Web search (needs API key)
- ⚠️ **kubernetes** - K8s management

## Enabling Optional Servers

To enable an optional MCP server:

1. Edit `.github/copilot/mcp.json`
2. Find the server (e.g., "postgres")
3. Change `"enabled": false` to `"enabled": true`
4. Add required environment variables to `.env`
5. Reload your IDE/editor

Example - Enable PostgreSQL:

```json
{
  "postgres": {
    "enabled": true,  // Changed from false
    "env": {
      "POSTGRES_CONNECTION_STRING": "${COPILOT_MCP_POSTGRES_CONNECTION_STRING}"
    }
  }
}
```

Then add to `.env`:
```bash
COPILOT_MCP_POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/dbname
```

## Testing Your Setup

### Test 1: Basic Agent Usage

```bash
# In GitHub Copilot Chat:
@agent:repo-optimizer What is the structure of this repository?
```

Expected: Agent analyzes and describes repository structure

### Test 2: MCP Server Usage

```bash
# Ask agent to use filesystem MCP:
@agent:docs-master List all markdown files in this repository
```

Expected: Agent lists all .md files

### Test 3: Code Analysis

```bash
# Use python-analysis MCP:
@agent:code-reviewer Run type checking on src/ directory
```

Expected: Agent runs mypy and reports results

## Common Issues & Solutions

### Issue: "MCP server not found"

**Solution**: Install the MCP server
```bash
# For filesystem server
npx -y @modelcontextprotocol/server-filesystem

# For git server  
npx -y @modelcontextprotocol/server-git

# For GitHub server
npx -y @github/mcp-server
```

### Issue: "GitHub token not found"

**Solution**: Check environment variables
```bash
# Verify token is set
echo $GITHUB_TOKEN

# If not set, load .env
source .env

# Or set directly
export GITHUB_TOKEN="your_token_here"
export COPILOT_MCP_GITHUB_TOKEN="your_token_here"
```

### Issue: "Agent not responding as expected"

**Solution**: Be more specific in your request
```
❌ Generic: "fix this"
✅ Specific: "@agent:code-reviewer Review src/auth.py for SQL injection vulnerabilities"
```

### Issue: "Agent seems stuck or hanging"

**Solution**: Run diagnostic scripts
```bash
# Quick health check
./health-check.sh

# If issues found, run quick fix
./quick-fix.sh

# See detailed troubleshooting
cat TROUBLESHOOTING.md
```

**Common causes:**
- MCP server not starting
- Missing environment variables  
- Network timeout
- Resource exhaustion

See **TROUBLESHOOTING.md** for comprehensive solutions.

### Issue: "Python analysis not working"

**Solution**: Install the Python MCP server
```bash
pip install mcp-server-python-analysis

# Verify installation
python -m mcp_server_python_analysis --help
```

### Issue: "Slow startup time"

**Solution**: Disable unused MCP servers
```json
// In .github/copilot/mcp.json
{
  "playwright": { "enabled": false },
  "kubernetes": { "enabled": false },
  "brave-search": { "enabled": false }
}
```

## IDE-Specific Setup

### VS Code

1. Install GitHub Copilot extension
2. Reload window (Cmd/Ctrl + R)
3. Open Copilot Chat
4. Type `@agent:` to see available agents

### GitHub.com

1. Navigate to repository
2. Open Copilot Chat in browser
3. Type `@agent:` to see available agents

### GitHub Codespaces

1. Add secrets to repository:
   - Settings → Secrets → Codespaces
   - Add `GITHUB_TOKEN`
2. Launch Codespace
3. Agents are automatically available

## Verifying Everything Works

Run this complete verification:

```bash
#!/bin/bash
echo "🔍 Verifying GitHub Copilot & Agents Setup..."

# Check Node.js
echo -n "Node.js: "
node --version && echo "✅" || echo "❌ Install Node.js"

# Check Python
echo -n "Python: "
python --version && echo "✅" || echo "❌ Install Python"

# Check GitHub token
echo -n "GitHub Token: "
[ ! -z "$GITHUB_TOKEN" ] && echo "✅" || echo "⚠️  Set GITHUB_TOKEN in .env"

# Check MCP config
echo -n "MCP Config: "
python -m json.tool < .github/copilot/mcp.json > /dev/null && echo "✅" || echo "❌"

# Check Python MCP server
echo -n "Python Analysis: "
python -c "import mcp_server_python_analysis" 2>/dev/null && echo "✅" || echo "⚠️  Optional: pip install mcp-server-python-analysis"

# Test filesystem MCP
echo -n "Filesystem MCP: "
npx -y @modelcontextprotocol/server-filesystem --version > /dev/null 2>&1 && echo "✅" || echo "⚠️  May need npm"

echo ""
echo "✨ Setup verification complete!"
echo "   If all checks passed, you're ready to use custom agents."
echo ""
echo "Try: @agent:repo-optimizer Analyze this repository structure"
```

## Next Steps

1. **Read the Documentation**
   - [Copilot Instructions](.github/copilot-instructions.md) - Repository guidelines for GitHub Copilot
   - [Agent README](.github/agents/README.md) - Agent overview
   - [MCP Guide](.mcp/README.md) - MCP server details
   - [Workflows](.github/agents/CODING_WORKFLOW.md) - Optimized workflows

2. **Try Your First Agent**
   ```bash
   @agent:repo-optimizer Analyze the repository structure and suggest improvements
   ```

3. **Explore Workflows**
   - Try the bug fix workflow
   - Test feature development workflow
   - Experiment with agent combinations

4. **Customize for Your Project**
   - Enable/disable MCP servers as needed
   - Create project-specific agent prompts
   - Document your workflows

## Getting Help

- **Documentation**: Check `.github/agents/` and `.mcp/` directories
- **Issues**: https://github.com/AloSantana/Antigravitys/issues
- **MCP Docs**: https://modelcontextprotocol.io/
- **Copilot Docs**: https://docs.github.com/copilot

## Advanced Configuration

### Global MCP Server Installation

For faster startup, install MCP servers globally:

```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @github/mcp-server
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-fetch
```

### Custom Agent Prompts

You can create project-specific agent behaviors by adding to agent files or creating new ones in `.github/agents/`.

### CI/CD Integration

Add agent checks to your GitHub Actions:

```yaml
# .github/workflows/ai-checks.yml
name: AI Quality Checks
on: [pull_request]
jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: AI Code Review
        run: |
          # Use agents in CI (requires GitHub Copilot for Business)
          echo "Running AI-powered code review..."
```

## Summary

You now have:
- ✅ 5 specialized agents for development tasks
- ✅ 14 MCP servers for enhanced capabilities  
- ✅ Optimized workflows for common scenarios
- ✅ Production-ready configuration

**Start coding with AI superpowers! 🚀**

---

**Configuration Version**: 1.0.0  
**Last Updated**: 2026-02-06  
**Maintained By**: Antigravity Workspace Template Team
