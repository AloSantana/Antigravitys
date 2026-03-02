---
description: Start or resume the Antigravity FastAPI backend server with proper venv activation
---

<command-instruction>
Start the Antigravity workspace backend. Execute these steps without asking for confirmation.

## Steps

1. Check if server is already running:
   ```bash
   curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Server not running"
   ```

2. If not running, start it:
   ```bash
   # Activate venv if exists
   if [ -d "venv" ]; then
     source venv/bin/activate 2>/dev/null || . venv/bin/activate
   fi

   # Install deps if needed
   pip install -r requirements.txt -q 2>/dev/null || true
   pip install -r backend/requirements.txt -q 2>/dev/null || true

   # Start the server (run from repo root, not backend/)
   nohup python backend/main.py > /tmp/antigravity.log 2>&1 &
   SERVER_PID=$!
   echo "Server started with PID: $SERVER_PID"
   echo $SERVER_PID > /tmp/antigravity.pid

   # Wait for it to come up
   sleep 3
   curl -s http://localhost:8000/health | python3 -m json.tool
   ```

3. Show access info:
   - Web UI: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health
   - WebSocket: ws://localhost:8000/ws

## What the Server Provides
- FastAPI REST API with 45+ endpoints
- WebSocket for real-time agent communication
- Multi-agent orchestration (Gemini / Vertex / Ollama)
- RAG pipeline via ChromaDB
- MCP server integration
</command-instruction>
