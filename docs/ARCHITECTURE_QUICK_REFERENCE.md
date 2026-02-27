# Antigravity Workspace - Architecture Quick Reference

> **Quick access guide to the complete architecture documentation**

## 📚 Full Documentation

For complete details, see [ARCHITECTURE.md](./ARCHITECTURE.md) (1,490+ lines)

---

## 🎯 System Overview (30-Second Version)

**Antigravity Workspace** = FastAPI Backend + HTML/JS Frontend + Hybrid AI (Gemini + Ollama) + RAG Pipeline

**Key Components**:
- **Orchestrator**: Routes queries to local/cloud LLM based on complexity
- **RAG Pipeline**: Auto-ingests files from drop_zone, provides context
- **File Watcher**: Monitors drop_zone, triggers ingestion
- **Agent Manager**: Loads 7+ specialized AI agents
- **WebSocket**: Real-time bidirectional communication

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: HTML/CSS/JS + CodeMirror + WebSocket             │
├─────────────────────────────────────────────────────────────┤
│ API: FastAPI + REST Endpoints + WebSocket Server           │
├─────────────────────────────────────────────────────────────┤
│ ORCHESTRATION: Complexity Analysis + Caching + RAG         │
├─────────────────────────────────────────────────────────────┤
│ AI: Gemini (cloud) + Ollama (local) + Agent Manager        │
├─────────────────────────────────────────────────────────────┤
│ DATA: ChromaDB (vectors) + Cache + File System             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Key Files & Responsibilities

### Backend (Python)

| File | Purpose | Key Features |
|------|---------|--------------|
| **backend/main.py** | FastAPI app entry point | API endpoints, WebSocket, lifecycle |
| **backend/agent/orchestrator.py** | Core routing logic | LLM selection, caching, RAG integration |
| **backend/agent/manager.py** | Agent management | Load/query/recommend agents |
| **backend/agent/gemini_client.py** | Cloud LLM interface | Gemini API, rate limiting |
| **backend/agent/local_client.py** | Local LLM interface | Ollama HTTP API, connection pooling |
| **backend/rag/ingest.py** | File ingestion | Batch processing, chunking, embedding |
| **backend/rag/store.py** | Vector storage | ChromaDB interface, semantic search |
| **backend/watcher.py** | File monitoring | Watchdog, debouncing, async tasks |
| **backend/utils/performance.py** | Performance monitoring | Metrics, health checks, recommendations |
| **backend/utils/file_utils.py** | File operations | Directory tree builder |

### Frontend (JavaScript)

| File | Purpose | Key Features |
|------|---------|--------------|
| **frontend/index.html** | Complete UI | Chat, editor, file tree, WebSocket |

### Source Modules (Python)

| File | Purpose | Key Features |
|------|---------|--------------|
| **src/agent.py** | Agent template | Think-Act-Reflect pattern |
| **src/config.py** | Settings | Pydantic configuration |
| **src/memory.py** | Conversation memory | JSON persistence |

---

## 🔌 API Endpoints

### Core Endpoints

```
GET  /                   # Health check
GET  /health             # System status + watcher + cache
GET  /files              # File tree from drop_zone
POST /upload             # Upload files
POST /agent/ask          # Process AI query (alternative to WebSocket)
POST /agent/clear-cache  # Clear response cache
GET  /agent/stats        # Cache statistics
WS   /ws                 # Real-time communication
```

### Performance Endpoints

```
GET /performance/health    # System health status
GET /performance/metrics   # Current performance snapshot
GET /performance/summary   # Statistical summary
GET /performance/analysis  # With recommendations
GET /performance/report    # Formatted text report
```

---

## 🧠 Request Processing Flow

### 1. Simple Query (Fast Path)
```
User → WebSocket → Orchestrator → Cache Check → Cached Response → User
                                    (if hit)
```

### 2. Complex Query (Full Path)
```
User → WebSocket → Orchestrator
  ↓
  → Assess Complexity (high/low)
  ↓
  → Generate Embedding (Local or Gemini)
  ↓
  → Query Vector Store (retrieve top 5, use top 3)
  ↓
  → Augment Prompt with Context
  ↓
  → Route to LLM:
     • High Complexity → Gemini
     • Low Complexity → Local LLM (fallback to Gemini if fail)
  ↓
  → Cache Response (LRU + TTL)
  ↓
  → Return with Metrics → User
```

### 3. File Upload Flow
```
User → Upload Files → /upload → Save to drop_zone
  ↓
  Watcher Detects → Debounce 2s → Process Folder
  ↓
  Batch Files (5 concurrent) → Read + Chunk + Embed
  ↓
  Store in ChromaDB with Metadata
```

---

## 🎨 Design Patterns Used

1. **Orchestrator Pattern**: Centralized routing (Orchestrator)
2. **Repository Pattern**: Data abstraction (VectorStore, MemoryManager)
3. **Strategy Pattern**: Runtime LLM selection
4. **Observer Pattern**: File watching (Watcher)
5. **Circuit Breaker Pattern**: Retry logic + fallback
6. **Cache-Aside Pattern**: Response caching (LRU + TTL)
7. **Pipeline Pattern**: RAG ingestion stages
8. **Adapter Pattern**: Unified LLM interface (GeminiClient, LocalClient)
9. **Manager Pattern**: Agent/Performance managers
10. **Asynchronous Processing**: async/await throughout

---

## ⚡ Performance Optimizations

| Optimization | Location | Impact |
|-------------|----------|--------|
| **Response Caching** | Orchestrator | ~90% hit rate on repeated queries |
| **Connection Pooling** | LocalClient | Reduced connection overhead |
| **Batch Processing** | Ingestion | 5x faster than sequential |
| **Debouncing** | Watcher | Prevents duplicate processing |
| **Smart RAG Skipping** | Orchestrator | Saves embedding time for simple queries |
| **Chunking with Overlap** | Ingestion | Better context preservation |
| **Async Everywhere** | All I/O | High concurrency |

---

## 🔍 Complexity Assessment

**High Complexity** → **Gemini** (more capable but slower/costlier):
- Keywords: plan, design, architecture, implement, debug, refactor, optimize, etc.
- Multiple questions + long query
- Code patterns: ```, function, class, def, async, import

**Low Complexity** → **Local LLM** (faster, cheaper):
- Simple questions
- Short queries (< 100 chars)
- No complex reasoning required

**Always**: Fallback to Gemini if Local fails

---

## 🗂️ Data Structures

### Agent Metadata
```python
{
  "name": str,
  "type": str,
  "expertise": str,
  "priority": str,
  "description": str,
  "capabilities": List[str],
  "tools": List[str],
  "file_path": str
}
```

### Chunk Metadata
```python
{
  "source": str,        # Full file path
  "filename": str,      # Base filename
  "chunk_id": str,      # "path:chunk_num"
  "chunk_num": int,     # Chunk index
  "total_chunks": int   # Total chunks for file
}
```

### Cache Entry
```python
(response: Dict[str, Any], timestamp: float)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
LOCAL_MODEL=llama3.2                  # Ollama model
HOST=0.0.0.0                          # Backend host
PORT=8000                             # Backend port
GOOGLE_API_KEY=<same as GEMINI>       # For src/agent.py
```

### Important Paths

```
drop_zone/                 # Monitored directory
backend/data/chroma/       # Vector DB (if persistent)
logs/performance_metrics.json  # Performance data
agent_memory.json          # Memory storage (src/)
.github/agents/*.agent.md  # Agent definitions
```

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "watcher": "running",
  "cache_hit_rate": "87.5%"
}
```

### Agent Stats
```bash
curl http://localhost:8000/agent/stats
```

Response:
```json
{
  "cache_hit_rate": 0.875,
  "cache_hits": 42,
  "cache_misses": 6,
  "cache_size": 23
}
```

### Performance Analysis
```bash
curl http://localhost:8000/performance/analysis
```

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Ollama (if using local LLM)
```bash
ollama serve
ollama pull llama3.2
```

### 3. Open Frontend
```bash
# Open frontend/index.html in browser
# Or serve with:
python -m http.server 3000 --directory frontend
```

### 4. Test Upload
```bash
# Drop files into drop_zone/
# Watch logs for ingestion
```

---

## 🐛 Common Issues & Solutions

### Issue: "Could not connect to Ollama"
```bash
# Solution 1: Start Ollama
ollama serve

# Solution 2: Check port
lsof -i :11434

# Solution 3: Pull model
ollama pull llama3.2
```

### Issue: Cache not working
```bash
# Check stats
curl http://localhost:8000/agent/stats

# Clear cache
curl -X POST http://localhost:8000/agent/clear-cache
```

### Issue: Files not ingesting
```bash
# Check watcher status
curl http://localhost:8000/health

# Verify file extension
# Supported: .md, .py, .js, .txt, .html, .css, .json, .jsx, .ts, .tsx

# Check file size < 1MB
```

### Issue: WebSocket disconnects
```javascript
// Check browser console
// Auto-reconnect after 3s

// Force reconnect
connectWebSocket();
```

---

## 📈 Metrics & KPIs

### Performance Targets
- **Response Time**: < 500ms (cached), < 3s (uncached)
- **Cache Hit Rate**: > 70%
- **Ingestion Speed**: ~5 files/sec
- **CPU Usage**: < 80%
- **Memory Usage**: < 80%

### Monitoring Intervals
- Performance metrics: Every 60s
- File tree refresh: Every 10s
- WebSocket reconnect: After 3s

---

## 🎯 Integration Points

### Frontend ↔ Backend
- **REST API**: `http://localhost:8000/*`
- **WebSocket**: `ws://localhost:8000/ws`
- **CORS**: Enabled for all origins

### Backend ↔ Ollama
- **Generate**: `POST http://localhost:11434/api/generate`
- **Embed**: `POST http://localhost:11434/api/embeddings`

### Backend ↔ Gemini
- **Library**: `google.generativeai`
- **Model**: `gemini-pro` (generation), `models/embedding-001` (embedding)

### Backend ↔ File System
- **Watch**: `<project_root>/drop_zone`
- **Upload**: `<project_root>/drop_zone/<filename>`

---

## 📚 Further Reading

- **Full Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Setup Guide**: [../SETUP.md](../SETUP.md)
- **Quick Start**: [../QUICKSTART.md](../QUICKSTART.md)
- **Troubleshooting**: [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Performance**: [../PERFORMANCE.md](../PERFORMANCE.md)

---

## 🤝 Agent System

### Available Agents (7 total)

1. **full-stack-developer**: End-to-end web applications (React, FastAPI, SQL)
2. **devops-infrastructure**: Deployment & containers (Docker, K8s, CI/CD)
3. **testing-stability-expert**: Comprehensive testing (PyTest, Jest)
4. **performance-optimizer**: Speed & efficiency (Profiling, Caching)
5. **code-reviewer**: Security & quality (Security, Best Practices)
6. **docs-master**: Documentation excellence (Docs, Guides)
7. **repo-optimizer**: Repository structure & tooling (Setup, Organization)

### Agent Selection in UI
```javascript
// Click agent card or type in chat
@full-stack-developer create a REST API
@testing-stability-expert write tests for auth
```

### Agent Recommendation API
```python
from backend.agent.manager import AgentManager

manager = AgentManager()
agent = manager.recommend_agent("Create a Docker container")
# Returns: devops-infrastructure agent
```

---

## 🔐 Security Notes

### Current Implementation
- ⚠️ No authentication on API or WebSocket
- ⚠️ CORS allows all origins
- ✅ File upload size limited to 1MB
- ✅ File extension whitelist
- ⚠️ No rate limiting

### Recommended Additions
1. JWT-based authentication
2. Restrict CORS to specific domains
3. Implement rate limiting (e.g., 100 req/min)
4. Input validation/sanitization
5. Prompt injection protection

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_orchestrator.py

# With coverage
pytest --cov=backend tests/
```

### Test Structure
```
tests/
├── test_agent.py          # Agent functionality
├── test_orchestrator.py   # Routing, caching
└── test_rag.py            # Ingestion, retrieval
```

---

## 📦 Dependencies

### Backend (Python)
- **Web**: fastapi, uvicorn
- **AI**: google-generativeai, aiohttp
- **RAG**: chromadb, watchdog
- **Utils**: python-dotenv, psutil, pydantic-settings

### Frontend (JavaScript)
- **Editor**: CodeMirror 5.65.2
- **No frameworks**: Vanilla JS

---

## 🎓 Learning Resources

### Key Concepts
1. **RAG (Retrieval-Augmented Generation)**: Enhancing LLM responses with retrieved context
2. **Vector Embeddings**: Dense numerical representations of text for semantic search
3. **LRU Cache**: Least Recently Used eviction policy
4. **WebSocket**: Full-duplex communication protocol
5. **Async/Await**: Non-blocking asynchronous programming

### Recommended Reading
- FastAPI docs: https://fastapi.tiangolo.com/
- ChromaDB docs: https://docs.trychroma.com/
- Ollama docs: https://github.com/ollama/ollama
- Gemini API: https://ai.google.dev/docs

---

**Last Updated**: 2024-12-19  
**Version**: 1.0  
**Maintained By**: Repository Optimizer Agent

---

*For detailed architecture diagrams, sequence flows, and in-depth component analysis, see [ARCHITECTURE.md](./ARCHITECTURE.md)*
