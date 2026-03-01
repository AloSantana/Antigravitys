# MCP Gateway Setup Guide

**Generated:** 2026-03-01  
**Purpose:** Configure OpenCode MCP servers to connect to Docker-based MCP Gateway and dashboard

---

## Overview

This guide covers:
1. Configuring OpenCode MCP clients to connect to an MCP Gateway
2. Setting up React dashboard connections using the `use-mcp` hook
3. Common gateway patterns (AgentGateway, Sandboxed.sh/Open Agent)

---

## Part 1: OpenCode MCP Configuration

### Configuration File Location

OpenCode reads MCP server configurations from:
- **Global:** `~/.opencode/config.json`
- **Project:** `.opencode/config.json` (in project root)

### Basic Structure

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "server-name": {
        "type": "sse" | "http" | "stdio",
        "url": "http://gateway-host:port/mcp/endpoint",
        "enabled": true
      }
    }
  }
}
```

### Transport Types

| Type | Use Case | Endpoint Pattern |
|------|----------|------------------|
| `sse` | Server-Sent Events (traditional) | `http://host:port/mcp/sse` |
| `http` | Streamable HTTP (better performance) | `http://host:port/mcp/http` |
| `stdio` | Local process (not for gateways) | N/A |

---

## Part 2: Gateway Connection Patterns

### AgentGateway (Most Common)

**Default Port:** `15000`

**SSE Transport:**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "agentgateway": {
        "type": "sse",
        "url": "http://localhost:15000/mcp/sse",
        "enabled": true
      }
    }
  }
}
```

**HTTP Transport (Recommended):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "agentgateway": {
        "type": "http",
        "url": "http://localhost:15000/mcp/http",
        "enabled": true
      }
    }
  }
}
```

### Docker Compose Setup

If using Docker Compose, replace `localhost` with service name:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "agentgateway": {
        "type": "http",
        "url": "http://agentgateway:15000/mcp/http",
        "enabled": true
      }
    }
  }
}
```

### Sandboxed.sh / Open Agent

**Website:** https://sandboxed.sh  
**Repository:** Th0rgal/sandboxed.sh

Sandboxed.sh uses similar gateway patterns. MCP server configs are stored in `library/mcp/*.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "sandboxed-gateway": {
        "type": "http",
        "url": "http://sandboxed-gateway:8080/mcp/http",
        "enabled": true
      }
    }
  }
}
```

---

## Part 3: React Dashboard Integration

### Installation

Install the `use-mcp` library:

```bash
npm install use-mcp
# or
pnpm add use-mcp
# or
yarn add use-mcp
```

### Basic Usage

```typescript
import { useMcp } from 'use-mcp/react';

function MCPDashboard() {
  const {
    state,      // Connection state
    tools,      // Available tools from MCP server
    error,      // Error message if connection fails
    callTool,   // Function to call tools
    retry,      // Retry connection
  } = useMcp({
    url: 'http://localhost:15000/mcp',
    enabled: true,
    logLevel: 'normal'
  });

  // Handle loading states
  if (state === 'discovering' || state === 'connecting') {
    return <div>Connecting to MCP gateway...</div>;
  }

  if (state === 'failed') {
    return (
      <div>
        <p>Connection failed: {error}</p>
        <button onClick={retry}>Retry</button>
      </div>
    );
  }

  if (state !== 'ready') {
    return <div>Loading...</div>;
  }

  // Render tools
  return (
    <div>
      <h2>Available Tools</h2>
      <ul>
        {tools.map(tool => (
          <li key={tool.name}>{tool.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Connection States

The `state` field has these possible values:

| State | Description |
|-------|-------------|
| `discovering` | Initial service discovery |
| `authenticating` | OAuth/auth flow in progress |
| `connecting` | Establishing connection |
| `loading` | Loading tools/resources |
| `ready` | Connected and ready |
| `failed` | Connection failed |

### Calling Tools

```typescript
function ToolInvoker() {
  const { callTool, state } = useMcp({
    url: 'http://localhost:15000/mcp'
  });

  const handleSendEmail = async () => {
    try {
      const result = await callTool('send-email', {
        to: 'user@example.com',
        subject: 'Hello',
        body: 'Test message'
      });
      console.log('Result:', result);
    } catch (error) {
      console.error('Tool call failed:', error);
    }
  };

  if (state !== 'ready') {
    return <div>Waiting for connection...</div>;
  }

  return (
    <button onClick={handleSendEmail}>
      Send Email
    </button>
  );
}
```

### With Authentication

```typescript
const { state, tools } = useMcp({
  url: 'http://localhost:15000/mcp',
  headers: {
    Authorization: 'Bearer YOUR_API_KEY'
  },
  enabled: true,
  logLevel: 'silent'
});
```

### Advanced: Custom Connection Management

```typescript
import { useMcp } from 'use-mcp/react';
import { useState, useEffect } from 'react';

function AdvancedDashboard() {
  const [gatewayUrl, setGatewayUrl] = useState('http://localhost:15000/mcp');
  const [isEnabled, setIsEnabled] = useState(true);

  const {
    state,
    tools,
    error,
    callTool,
    retry
  } = useMcp({
    url: gatewayUrl,
    enabled: isEnabled,
    logLevel: 'normal'
  });

  // Auto-retry on failure
  useEffect(() => {
    if (state === 'failed') {
      const timer = setTimeout(() => {
        console.log('Auto-retrying connection...');
        retry();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [state, retry]);

  // Connection status indicator
  const getStatusColor = () => {
    switch (state) {
      case 'ready': return 'green';
      case 'failed': return 'red';
      case 'connecting': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <div>
      <div style={{ backgroundColor: getStatusColor(), padding: '10px' }}>
        Status: {state}
      </div>

      <div>
        <input
          type="text"
          value={gatewayUrl}
          onChange={(e) => setGatewayUrl(e.target.value)}
          placeholder="Gateway URL"
        />
        <button onClick={() => setIsEnabled(!isEnabled)}>
          {isEnabled ? 'Disconnect' : 'Connect'}
        </button>
      </div>

      {error && <div style={{ color: 'red' }}>Error: {error}</div>}

      {state === 'ready' && (
        <div>
          <h3>Tools ({tools.length})</h3>
          <ul>
            {tools.map(tool => (
              <li key={tool.name}>
                <strong>{tool.name}</strong>
                <p>{tool.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## Part 4: Docker Integration

### docker-compose.yml Example

```yaml
version: '3.8'

services:
  agentgateway:
    image: agentgateway/agentgateway:latest
    ports:
      - "15000:15000"
    environment:
      - MCP_SERVERS_CONFIG=/config/servers.json
    volumes:
      - ./mcp-config:/config
    networks:
      - mcp-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_MCP_GATEWAY_URL=http://agentgateway:15000/mcp
    depends_on:
      - agentgateway
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

### Environment Variables

For React apps, expose the gateway URL:

```bash
# .env
REACT_APP_MCP_GATEWAY_URL=http://localhost:15000/mcp
REACT_APP_MCP_LOG_LEVEL=normal
```

Then in your component:

```typescript
const { state, tools } = useMcp({
  url: process.env.REACT_APP_MCP_GATEWAY_URL,
  logLevel: process.env.REACT_APP_MCP_LOG_LEVEL as 'silent' | 'normal'
});
```

---

## Part 5: Troubleshooting

### Connection Issues

**Problem:** "Connection failed" or stuck in "connecting" state

**Solutions:**
1. Verify gateway is running: `curl http://localhost:15000/health`
2. Check network access from Docker containers
3. Verify port mappings in docker-compose.yml
4. Check gateway logs for errors

### CORS Issues

If connecting from browser, ensure gateway has CORS headers:

```javascript
// Gateway configuration (example)
{
  "cors": {
    "allowOrigins": ["http://localhost:3000"],
    "allowMethods": ["GET", "POST"],
    "allowHeaders": ["Content-Type", "Authorization"]
  }
}
```

### Authentication Errors

**Problem:** "Authentication failed" state

**Solutions:**
1. Check API key/token validity
2. Verify headers are correctly set
3. Check gateway auth configuration
4. Review OAuth flow if using OAuth

### Tool Discovery Issues

**Problem:** `tools` array is empty

**Solutions:**
1. Wait for `state === 'ready'` before accessing tools
2. Check gateway has tools registered
3. Verify MCP server configurations on gateway
4. Review gateway logs for tool registration errors

---

## Part 6: Quick Reference

### OpenCode Config Template

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "GATEWAY_NAME": {
        "type": "http",
        "url": "http://GATEWAY_HOST:GATEWAY_PORT/mcp/http",
        "enabled": true
      }
    }
  }
}
```

### React Hook Template

```typescript
const { state, tools, error, callTool, retry } = useMcp({
  url: 'http://GATEWAY_HOST:GATEWAY_PORT/mcp',
  headers: { Authorization: 'Bearer YOUR_API_KEY' },
  enabled: true,
  logLevel: 'normal'
});
```

### Common Gateway Ports

| Gateway | Default Port | Endpoint Pattern |
|---------|--------------|------------------|
| AgentGateway | 15000 | `/mcp/sse` or `/mcp/http` |
| Sandboxed.sh | 8080 | `/mcp/http` |
| Custom | Varies | Check documentation |

---

## Resources

- **AgentGateway OpenCode docs:** https://agentgateway.dev/docs/integrations/mcp-clients/opencode/
- **Sandboxed.sh:** https://sandboxed.sh
- **OpenCode MCP docs:** https://opencode.ai/docs/mcp-servers/
- **use-mcp GitHub:** https://github.com/mcp-use/mcp-use
- **MCP Protocol Spec:** https://modelcontextprotocol.io/

---

## Next Steps

1. **Identify your gateway setup:**
   - Are you using AgentGateway, Sandboxed.sh, or a custom gateway?
   - What port is it running on?
   - What transport does it support (SSE vs HTTP)?

2. **Update OpenCode config:**
   - Edit `~/.opencode/config.json` or `.opencode/config.json`
   - Replace placeholders with your actual gateway details

3. **Set up React dashboard:**
   - Install `use-mcp` package
   - Create dashboard component using examples above
   - Configure environment variables for gateway URL

4. **Test connection:**
   - Verify gateway is accessible
   - Check OpenCode can discover tools
   - Test dashboard connection and tool invocation

5. **Monitor and debug:**
   - Enable logging in both OpenCode and React dashboard
   - Check gateway logs for issues
   - Use browser dev tools to inspect network requests
