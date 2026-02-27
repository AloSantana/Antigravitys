# Optional MCP Servers

The main `mcp.json` configuration includes only MCP servers that work out-of-the-box without requiring manual user credentials. This document explains how to add optional servers that require additional setup.

## Why These Were Removed

The following servers were removed from the default configuration because they require user-specific secrets or manual configuration that the Copilot coding agent cannot auto-configure:

- `postgres` - Requires database connection string
- `brave-search` - Requires API key
- `kubernetes` - Requires kubectl configuration
- `playwright` - Conflicts with puppeteer, heavier alternative
- `slack` - Requires bot token
- `aws` - Requires AWS credentials
- `sentry` - Requires DSN and auth token
- `gitlab` - Requires GitLab token
- `python-analysis` - Package not readily available

## How to Add Optional Servers

To add any of these servers back, edit `.github/copilot/mcp.json` and add the server configuration under `mcpServers`:

### PostgreSQL Database

```json
"postgres": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "mcp-server-postgres"],
  "env": {
    "POSTGRES_CONNECTION_STRING": "${COPILOT_MCP_POSTGRES_CONNECTION_STRING}"
  }
}
```

**Required environment variable:**
```bash
export COPILOT_MCP_POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:port/db"
```

### Brave Search (Web Search)

```json
"brave-search": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "${COPILOT_MCP_BRAVE_API_KEY}"
  }
}
```

**Required environment variable:**
```bash
export COPILOT_MCP_BRAVE_API_KEY="your_brave_api_key_here"
```

Get an API key from: https://brave.com/search/api/

### Kubernetes Cluster Management

```json
"kubernetes": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-kubernetes"]
}
```

**Required setup:**
- kubectl must be installed and configured
- Valid kubeconfig file at `~/.kube/config`

### Playwright (Alternative to Puppeteer)

```json
"playwright": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@anthropic/server-playwright"]
}
```

**Note:** Playwright is heavier than Puppeteer. Use one or the other, not both.

### Slack Integration

```json
"slack": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_BOT_TOKEN": "${COPILOT_MCP_SLACK_BOT_TOKEN}",
    "SLACK_TEAM_ID": "${COPILOT_MCP_SLACK_TEAM_ID}"
  }
}
```

**Required environment variables:**
```bash
export COPILOT_MCP_SLACK_BOT_TOKEN="xoxb-your-token"
export COPILOT_MCP_SLACK_TEAM_ID="T1234567890"
```

### AWS Cloud Services

```json
"aws": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "mcp-server-aws"],
  "env": {
    "AWS_ACCESS_KEY_ID": "${COPILOT_MCP_AWS_ACCESS_KEY_ID}",
    "AWS_SECRET_ACCESS_KEY": "${COPILOT_MCP_AWS_SECRET_ACCESS_KEY}",
    "AWS_REGION": "${COPILOT_MCP_AWS_REGION}"
  }
}
```

**Required environment variables:**
```bash
export COPILOT_MCP_AWS_ACCESS_KEY_ID="your_access_key"
export COPILOT_MCP_AWS_SECRET_ACCESS_KEY="your_secret_key"
export COPILOT_MCP_AWS_REGION="us-east-1"
```

### Sentry Error Tracking

```json
"sentry": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sentry"],
  "env": {
    "SENTRY_DSN": "${COPILOT_MCP_SENTRY_DSN}",
    "SENTRY_AUTH_TOKEN": "${COPILOT_MCP_SENTRY_AUTH_TOKEN}"
  }
}
```

**Required environment variables:**
```bash
export COPILOT_MCP_SENTRY_DSN="https://xxx@sentry.io/xxx"
export COPILOT_MCP_SENTRY_AUTH_TOKEN="your_auth_token"
```

### GitLab Integration

```json
"gitlab": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "mcp-server-gitlab"],
  "env": {
    "GITLAB_TOKEN": "${COPILOT_MCP_GITLAB_TOKEN}",
    "GITLAB_URL": "${COPILOT_MCP_GITLAB_URL}"
  }
}
```

**Required environment variables:**
```bash
export COPILOT_MCP_GITLAB_TOKEN="your_gitlab_token"
export COPILOT_MCP_GITLAB_URL="https://gitlab.com"  # or your self-hosted URL
```

### Python Code Analysis

```json
"python-analysis": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-everything"]
}
```

**Note:** The `mcp_server_python_analysis` package is not a standard pip package. Use `@modelcontextprotocol/server-everything` as a general-purpose alternative, or install a custom Python analysis MCP server if available.

## Environment Variable Management

Add environment variables to your `.env` file or export them in your shell:

```bash
# .env file
COPILOT_MCP_GITHUB_TOKEN=ghp_your_token_here
COPILOT_MCP_BRAVE_API_KEY=your_brave_key_here
COPILOT_MCP_POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:port/db
# ... etc
```

Then source the file:
```bash
source .env
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export COPILOT_MCP_GITHUB_TOKEN="ghp_your_token_here"
# ... etc
```

## Verifying Server Configuration

After adding a server, verify it works:

1. Restart your Copilot session
2. Check the logs for any errors
3. Test the server's functionality with a simple command

## Getting Help

If you encounter issues with optional servers:
1. Check that all required environment variables are set
2. Verify credentials are valid
3. Ensure required tools (kubectl, etc.) are installed
4. Review the MCP server's documentation

---

**Note:** The default `mcp.json` is optimized for immediate use without manual configuration. Only add optional servers when you specifically need their functionality and can provide the required credentials.
