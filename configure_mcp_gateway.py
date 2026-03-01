import json
from pathlib import Path
import glob

GATEWAY_IP = "172.17.0.1" # Default docker bridge IP
GATEWAY_PORT = "8080"
GATEWAY_URL = f"http://{GATEWAY_IP}:{GATEWAY_PORT}/sse"

search_patterns = [
    "**/mcp.json",
    "**/opencode.json",
    "**/mcp_servers.json",
    "**/*mcp_config*.json",
    "**/*mcp_settings*.json"
]

files_to_update = set()
for pattern in search_patterns:
    for path in Path(".").rglob(pattern):
        if "node_modules" not in str(path) and "venv" not in str(path) and ".git" not in str(path):
            files_to_update.add(path)

print(f"Found {len(files_to_update)} MCP config files to process.")

for p in files_to_update:
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        servers_key = "mcpServers" if "mcpServers" in data else "mcp" if "mcp" in data else None
        if not servers_key:
            continue
            
        # Disable all local standard IO servers to prevent conflict
        for key, server in data[servers_key].items():
            if isinstance(server, dict) and "command" in server:
                server["enabled"] = False
            
        # Add the multiplexed Docker Open Agent Gateway connection
        data[servers_key]["docker-agent-gateway"] = {
            "type": "sse",
            "url": GATEWAY_URL,
            "enabled": True,
            "description": "Docker Open Agent Gateway (sandboxed.sh/docker-mcp multiplexer)"
        }
        
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        print(f"Successfully configured: {p}")
    except Exception as e:
        print(f"Failed to process {p}: {e}")

