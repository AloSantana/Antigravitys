import json
from pathlib import Path

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

for p in files_to_update:
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        servers_key = "mcpServers" if "mcpServers" in data else "mcp" if "mcp" in data else None
        if not servers_key or "docker-agent-gateway" not in data[servers_key]:
            continue
            
        # Update the port from 8080 to 3000
        url = data[servers_key]["docker-agent-gateway"].get("url", "")
        if "8080" in url:
            data[servers_key]["docker-agent-gateway"]["url"] = url.replace("8080", "3000")
            
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Updated port to 3000 in: {p}")
    except Exception as e:
        print(f"Failed to process {p}: {e}")
