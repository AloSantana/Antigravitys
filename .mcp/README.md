# MCP Server Configuration Guide

This document explains the Model Context Protocol (MCP) server configurations for the Antigravity Workspace Template project.

## What is MCP?

The Model Context Protocol (MCP) enables AI assistants like GitHub Copilot and Claude to interact with external tools and services. MCP servers provide structured interfaces for tasks like file operations, database queries, web scraping, and more.

## Configuration Files

### 1. `.github/copilot/mcp.json`
**Purpose**: GitHub Copilot MCP server configuration  
**Usage**: Used by GitHub Copilot in VS Code, GitHub.com, and other GitHub Copilot-enabled environments  
**Features**: 
- Optimized with priority levels
- Includes detailed tool descriptions
- Optional servers disabled by default for performance

### 2. `.mcp/config.json`
**Purpose**: Generic MCP configuration for Claude Desktop and other MCP clients  
**Usage**: Used by applications that support MCP protocol directly (Claude Desktop, Cursor, etc.)  
**Features**: 
- Streamlined for essential operations
- Compatible with standard MCP clients

## Configured MCP Servers

### 🔴 High Priority (Always Enabled)

#### **filesystem**
- **Tools**: read_file, write_file, edit_file, create_directory, list_directory, move_file, search_files
- **Use Case**: All file system operations
- **Performance**: Fast, local operations
- **Why Essential**: Required for all code editing and file management tasks

#### **git**
- **Tools**: git_status, git_diff, git_commit, git_add, git_log, git_show, git_branch
- **Use Case**: Version control operations
- **Performance**: Fast, local operations
- **Why Essential**: Critical for managing code changes and repository operations

#### **github**
- **Tools**: get_issue, get_pull_request, search_code, create_issue, list_commits, list_branches
- **Use Case**: GitHub integration for issues, PRs, and code search
- **Performance**: Network-dependent, but cached
- **Requires**: `GITHUB_TOKEN` or `COPILOT_MCP_GITHUB_TOKEN` environment variable
- **Why Essential**: Enables seamless GitHub workflow integration

#### **python-analysis**
- **Tools**: run_mypy, analyze_complexity, find_imports, get_definitions
- **Use Case**: Python type checking, code analysis, and quality checks
- **Performance**: Medium, depends on project size
- **Requires**: `mcp_server_python_analysis` Python package
- **Installation**: `pip install mcp-server-python-analysis`
- **Why Essential**: Maintains code quality for Python projects

#### **memory**
- **Tools**: create_entities, create_relations, read_graph, search_nodes
- **Use Case**: Knowledge graph for maintaining project context and entity relationships
- **Performance**: Fast, in-memory operations
- **Why Essential**: Helps AI maintain context across conversations

#### **sequential-thinking**
- **Tools**: sequentialthinking
- **Use Case**: Enhanced reasoning for complex problems with step-by-step analysis
- **Performance**: Fast, client-side processing
- **Why Essential**: Improves AI reasoning on complex tasks

### 🟡 Medium Priority (Enabled by Default)

#### **sqlite**
- **Tools**: read_query, write_query, create_table, list_tables, describe_table
- **Use Case**: Local database operations for application data
- **Performance**: Fast, local database
- **Configuration**: Default path is `./data.db`
- **When to Use**: For projects using SQLite databases

#### **puppeteer**
- **Tools**: puppeteer_navigate, puppeteer_screenshot, puppeteer_click, puppeteer_fill
- **Use Case**: Browser automation for web scraping and testing
- **Performance**: Medium, requires browser launch
- **When to Use**: Web scraping, UI testing, screenshot capture
- **Note**: Choose puppeteer OR playwright, not both

#### **fetch**
- **Tools**: fetch
- **Use Case**: Simple HTTP requests for fetching web content
- **Performance**: Network-dependent
- **When to Use**: API calls, downloading files, web content retrieval

#### **docker**
- **Tools**: list_containers, run_container, stop_container, list_images, build_image
- **Use Case**: Docker container and image management
- **Performance**: Medium, requires Docker daemon
- **When to Use**: Working with containerized applications

### 🟢 Low Priority (Disabled by Default - Enable When Needed)

#### **postgres**
- **Status**: ⚠️ Disabled by default
- **Tools**: query, execute, list_tables, describe_table
- **Use Case**: PostgreSQL database operations
- **Requires**: `POSTGRES_CONNECTION_STRING` environment variable
- **Enable When**: Working with PostgreSQL databases
- **Configuration**: Set `"enabled": true` in mcp.json

#### **playwright**
- **Status**: ⚠️ Disabled by default
- **Tools**: browser_navigate, browser_screenshot, browser_click, browser_evaluate
- **Use Case**: Advanced web scraping and browser automation
- **Performance**: Heavier than puppeteer
- **Enable When**: Need specific Playwright features not available in Puppeteer
- **Note**: Use puppeteer instead for most use cases

#### **brave-search**
- **Status**: ⚠️ Disabled by default
- **Tools**: brave_web_search, brave_local_search
- **Use Case**: Web search capabilities integrated into AI workflows
- **Requires**: `BRAVE_API_KEY` environment variable
- **Enable When**: Need web search integration
- **Get API Key**: https://brave.com/search/api/

#### **kubernetes**
- **Status**: ⚠️ Disabled by default
- **Tools**: get_pods, get_services, get_deployments, describe_resource, logs
- **Use Case**: Kubernetes cluster management
- **Requires**: kubectl configured with cluster access
- **Enable When**: Working with Kubernetes deployments

## Environment Variables Setup

### Required Variables

```bash
# For GitHub integration (required for github MCP server)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# For GitHub Copilot MCP (alternative naming)
export COPILOT_MCP_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

### Optional Variables

```bash
# For Brave Search (if enabled)
export BRAVE_API_KEY="BSAxxxxxxxxxxxxxxx"
export COPILOT_MCP_BRAVE_API_KEY="BSAxxxxxxxxxxxxxxx"

# For PostgreSQL (if enabled)
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@localhost:5432/dbname"
export COPILOT_MCP_POSTGRES_CONNECTION_STRING="postgresql://user:pass@localhost:5432/dbname"
```

### Setting Up Environment Variables

#### For Local Development (.env file)
```bash
# Create .env file in project root
cat > .env << 'EOF'
GITHUB_TOKEN=your_github_token_here
BRAVE_API_KEY=your_brave_api_key_here
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/dbname
EOF

# Load environment variables
source .env
```

#### For GitHub Codespaces
1. Go to Repository Settings → Secrets and variables → Codespaces
2. Add repository secrets:
   - `GITHUB_TOKEN`
   - `BRAVE_API_KEY` (optional)
   - `POSTGRES_CONNECTION_STRING` (optional)

#### For VS Code
1. Create `.vscode/settings.json`:
```json
{
  "terminal.integrated.env.linux": {
    "GITHUB_TOKEN": "${env:GITHUB_TOKEN}",
    "COPILOT_MCP_GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
  }
}
```

## Installation & Setup

### Prerequisites
```bash
# Node.js (for npx commands)
node --version  # Should be v16 or higher

# Python (for python-analysis server)
python --version  # Should be 3.8 or higher
```

### Install MCP Server Dependencies

#### Python Analysis Server
```bash
pip install mcp-server-python-analysis
```

#### Verify Installation
```bash
# Test filesystem server
npx -y @modelcontextprotocol/server-filesystem --help

# Test git server
npx -y @modelcontextprotocol/server-git --help

# Test GitHub server
npx -y @github/mcp-server --help
```

## Enabling Optional Servers

### Method 1: Edit Configuration File

Edit `.github/copilot/mcp.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "enabled": true,  // Change from false to true
      "env": {
        "POSTGRES_CONNECTION_STRING": "${COPILOT_MCP_POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

### Method 2: Create Custom Configuration

For project-specific needs, create `.github/copilot/mcp.local.json` (gitignored):

```json
{
  "mcpServers": {
    "brave-search": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-key-here"
      },
      "enabled": true
    }
  }
}
```

## Performance Optimization

### Startup Time Comparison

| Configuration | Servers | Startup Time | Memory Usage |
|---------------|---------|--------------|--------------|
| All servers enabled | 14 | ~4-6 seconds | ~600-800 MB |
| Optimized (default) | 10 | ~1-2 seconds | ~300-400 MB |
| Minimal (core only) | 6 | ~0.5-1 second | ~200-300 MB |

### Memory Usage by Server

- **filesystem**: ~50 MB (essential)
- **git**: ~30 MB (essential)
- **github**: ~60 MB (essential)
- **python-analysis**: ~80 MB (project-dependent)
- **memory**: ~40 MB
- **sequential-thinking**: ~20 MB
- **sqlite**: ~30 MB
- **puppeteer**: ~150-200 MB (browser instance)
- **docker**: ~50 MB
- **fetch**: ~20 MB

### Optimization Tips

1. **Disable unused servers**: Set `"enabled": false` for servers you don't use
2. **Use puppeteer instead of playwright**: Lighter weight for most use cases
3. **Enable postgres/kubernetes only when needed**: Heavy servers for specific tasks
4. **Cache npm packages globally**: Speeds up server initialization
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @github/mcp-server
   ```

## Troubleshooting

### Server Not Loading

**Symptom**: MCP server fails to start or tools are unavailable

**Solutions**:
1. Verify `npx` is installed: `npx --version`
2. Check package exists: `npm view @modelcontextprotocol/server-filesystem`
3. Verify environment variables: `echo $GITHUB_TOKEN`
4. Check server logs (location depends on client application)
5. Test server independently:
   ```bash
   npx @modelcontextprotocol/server-filesystem .
   ```

### Slow Startup

**Symptom**: Long delay before MCP servers are ready

**Solutions**:
1. Disable unused servers (set `"enabled": false`)
2. Check network connectivity for npm package downloads
3. Cache packages globally:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-memory
   npm install -g @github/mcp-server
   ```
4. Use local package installations instead of npx -y

### Tool Not Working

**Symptom**: Specific MCP tool fails or returns errors

**Solutions**:
1. Verify server is enabled: Check `"enabled"` field in config
2. Check server-specific requirements: API keys, Python packages, etc.
3. Verify permissions: File system access, Docker daemon running, etc.
4. Test tool independently with example data
5. Check server documentation for known limitations

### Python Analysis Server Issues

**Symptom**: Python analysis tools not working

**Solutions**:
```bash
# Reinstall the package
pip uninstall mcp-server-python-analysis
pip install mcp-server-python-analysis

# Verify installation
python -m mcp_server_python_analysis --help

# Check project path configuration
export PROJECT_PATH="/path/to/your/project"
```

## Best Practices

### 1. Minimal Configuration Principle
- Start with essential servers only (filesystem, git, github)
- Add servers as needed for specific tasks
- Remove unused servers periodically
- Review configuration quarterly

### 2. Environment Management
- Use `.env` files for local development
- Use GitHub Secrets for CI/CD and Codespaces
- Never commit API keys or tokens to version control
- Rotate tokens regularly for security

### 3. Server Selection Guidelines
- **Browser automation**: Use puppeteer (lighter) unless you specifically need Playwright features
- **Databases**: Use sqlite for local development, postgres for production data
- **Search**: Enable brave-search only if you need web search integration
- **Containers**: Enable docker by default for containerized development
- **Kubernetes**: Enable only when actively deploying to K8s clusters

### 4. Performance Monitoring
- Monitor startup time after configuration changes
- Track memory usage with Activity Monitor / Task Manager
- Disable servers that cause slowdowns
- Use browser DevTools to inspect MCP communication

### 5. Security Considerations
- Use read-only tokens when possible
- Limit filesystem server scope to project directories
- Rotate API keys regularly
- Review server permissions periodically
- Keep MCP servers updated to latest versions

## Usage Examples

### Example 1: File Operations
```
# AI can use filesystem server to:
- Read and analyze codebase structure
- Create new files and directories
- Edit existing files
- Search for specific patterns
- Move and organize files
```

### Example 2: Git Workflow
```
# AI can use git server to:
- Check repository status
- View diffs of changes
- Commit changes with messages
- Create and switch branches
- View commit history
```

### Example 3: GitHub Integration
```
# AI can use github server to:
- Search for code across repositories
- Read and create issues
- Review and create pull requests
- Fetch file contents from GitHub
- List branches and commits
```

### Example 4: Code Analysis
```
# AI can use python-analysis server to:
- Run type checking with mypy
- Analyze code complexity
- Find import dependencies
- Get function and class definitions
```

### Example 5: Database Operations
```
# AI can use sqlite server to:
- Query application data
- Create and modify tables
- Analyze data patterns
- Generate reports
```

## Support & Resources

### Official Documentation
- [MCP Official Website](https://modelcontextprotocol.io/)
- [MCP Server Implementations](https://github.com/modelcontextprotocol/servers)
- [GitHub Copilot MCP Docs](https://docs.github.com/copilot/mcp)

### Community Resources
- [MCP Discussions](https://github.com/modelcontextprotocol/discussions)
- [Server Repository Issues](https://github.com/modelcontextprotocol/servers/issues)

### Project-Specific Support
- [Antigravity Template Issues](https://github.com/AloSantana/Antigravitys/issues)
- [Antigravity Template Discussions](https://github.com/AloSantana/Antigravitys/discussions)

## Migration Guide

### From No MCP to MCP-Enabled

**Before** (No MCP):
- AI has limited access to external tools
- Manual file operations required
- No database query capabilities
- Limited code analysis

**After** (MCP-Enabled):
- AI can read/write files automatically
- Direct Git and GitHub operations
- Database querying and analysis
- Advanced code quality checks
- Web scraping and automation

### Testing After Setup

1. **Verify Core Servers**: Restart your IDE and check MCP server status
2. **Test Essential Tools**: Try file operations, git commands
3. **Enable Optional Servers**: Add one at a time and test
4. **Monitor Performance**: Check startup time and memory usage
5. **Iterate and Optimize**: Disable unused servers, adjust configuration

## Changelog

### Version 1.0.0 (2026-02-06)
- Initial MCP configuration
- 14 MCP servers configured (10 enabled by default)
- Optimized for performance and usability
- Comprehensive documentation

---

**Last Updated**: 2026-02-06  
**Maintained by**: Antigravity Workspace Template Team  
**License**: MIT
