# MCP Server Diagnostic Report
**Date:** 2026-03-01 21:30 UTC  
**Test Duration:** 5 minutes

---

## CONTAINER STATUS ✓ RUNNING

```
CONTAINER ID: 7cdc5c6c0507
NAME: sandboxed-sh-sandboxed-sh-1
STATUS: Up 11 minutes
IMAGE: sandboxed-sh-sandboxed-sh
PORTS: 0.0.0.0:3000->80/tcp, [::]:3000->80/tcp
```

---

## PORT AVAILABILITY ✓ LISTENING

**localhost:3000 (IPv4/IPv6):**
```
TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING
TCP    [::]:3000              [::]:0                 LISTENING
TCP    [::1]:3000             [::]:0                 LISTENING
```
✓ Port is actively listening on all interfaces (0.0.0.0, [::], [::1])

---

## ENDPOINT TESTS

### Root Endpoint (/)
```
curl -s http://localhost:3000/
HTTP Status: 200
Response: Next.js application (cached, prerendered)
```
✓ Gateway responds successfully

### Test Endpoints (/sse, /mcp)
```
curl http://localhost:3000/sse
HTTP Status: 404
Response: Not Found (Next.js 404 page)

curl http://localhost:3000/mcp
HTTP Status: 404
Response: Not Found (Next.js 404 page)
```
❌ **ISSUE**: The expected `/sse` and `/mcp` endpoints are NOT available

### Available API Endpoints
```
GET /api/health
HTTP Status: 200
Response: {"status":"ok","version":"0.10.0","dev_mode":true,"auth_required":false,"auth_mode":"disabled","max_iterations":50,"library_remote":"https://github.com/Th0rgal/sandboxed-library-template.git"}

GET /api/library/mcps
HTTP Status: 200
Response: {"example-remote-mcp":{"type":"remote","url":"https://example.com/mcp","headers":{},"enabled":false}}
```
✓ The gateway IS responding with API endpoints

---

## DOCKER GATEWAY CONNECTIVITY

**Test: Reach via Docker Gateway IP (172.17.0.1:3000)**
```
ping 172.17.0.1
Result: Request timed out
(100% packet loss)

curl http://172.17.0.1:3000/api/health
Result: Failed to connect to 172.17.0.1 port 3000 after 21048 ms
```
❌ **CRITICAL ISSUE**: Docker gateway IP 172.17.0.1 is NOT reachable from host

**Reason:** On Windows, Docker Desktop uses Hyper-V or WSL2 network isolation. The IP 172.17.0.1 is unreachable from the Windows host—containers themselves can reach it (to reach the host), but the host cannot reach it.

---

## MCP SERVER CONFIGURATION

**Found in mcp.json / mcp_servers.json:**
```json
{
  "docker-agent-gateway": {
    "type": "sse",
    "url": "http://172.17.0.1:3000/sse",
    "enabled": true,
    "description": "Docker Open Agent Gateway (sandboxed.sh/docker-mcp multiplexer)"
  }
}
```

**Status:** 
- ✓ Configured in 3 locations: `./mcp.json`, `./mcp_servers.json`, `./.agent/mcp_config.json`
- ✓ All point to `http://172.17.0.1:3000/sse`
- ✓ All have `"enabled": true`

---

## SUMMARY OF FINDINGS

| Component | Status | Notes |
|-----------|--------|-------|
| **Container Running** | ✓ YES | sandboxed-sh-sandboxed-sh-1 active |
| **Port 3000 Listening** | ✓ YES | All interfaces (0.0.0.0, ::, ::1) |
| **localhost:3000 Access** | ✓ YES | HTTP 200 on / and /api/* endpoints |
| **Expected /sse Endpoint** | ❌ NO | Returns 404 Not Found |
| **Expected /mcp Endpoint** | ❌ NO | Returns 404 Not Found |
| **Docker Gateway IP Reachable** | ❌ NO | 172.17.0.1 unreachable from host |
| **MCP Config Synchronized** | ⚠️ PARTIAL | Config present but points to unreachable IP |

---

## ROOT CAUSE ANALYSIS

1. **Missing /sse endpoint:** The `sandboxed-sh` container is a Next.js app that doesn't expose `/sse` or `/mcp` at root level. It provides API routes at `/api/*` instead.

2. **Unreachable 172.17.0.1:** On Windows, Docker containers are isolated in a VM. The gateway IP 172.17.0.1 is **only reachable from inside containers**, not from the Windows host.

3. **Configuration desynchronization:** All MCP configs point to `http://172.17.0.1:3000/sse`, which cannot work on Windows host.

---

## RECOMMENDATIONS

### ✓ For localhost access (host-only):
```json
{
  "docker-agent-gateway": {
    "type": "sse",
    "url": "http://localhost:3000/api/health",
    "enabled": true,
    "description": "Docker Open Agent Gateway (accessible via localhost)"
  }
}
```

### ✓ For proper MCP SSE endpoint:
Check if container exposes SSE at an alternative path (e.g., `/api/sse`)
```bash
curl http://localhost:3000/api/
# or check container docs for SSE endpoint
```

### ✓ To fix Docker networking:
On Windows, use Docker Desktop's host.docker.internal instead:
```json
{
  "docker-agent-gateway": {
    "type": "sse",
    "url": "http://host.docker.internal:3000/api/sse",
    "enabled": true
  }
}
```

---

## NEXT STEPS

1. **Verify correct SSE endpoint:** Test `curl http://localhost:3000/api/*` to find actual MCP/SSE routes
2. **Update MCP config** to use correct endpoint (localhost or host.docker.internal)
3. **Test MCP connectivity** from agents to confirm synchronization
4. **Check container logs** for endpoint definitions: `docker logs sandboxed-sh-sandboxed-sh-1`

