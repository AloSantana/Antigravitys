# ⚡ Quick Start Guide - GUI-First Approach

Get up and running with Antigravity Workspace in 5 minutes with the enhanced web interface!

---

## 🎯 What You'll Achieve

In the next 5 minutes, you'll:
- ✅ Install the complete workspace (1-2 minutes)
- ✅ Configure via visual Settings GUI (1-2 minutes)
- ✅ Start chatting with AI agents (1 minute)
- ✅ Explore the Performance Dashboard
- ✅ View conversation history
- ✅ Generate and collect artifacts

---

## 📋 Prerequisites

Ensure you have:
- **OS**: Ubuntu 20.04+, Debian 11+, macOS, or Windows WSL2
- **RAM**: 2GB+ available
- **Disk**: 5GB+ free space
- **Internet**: Stable connection
- **Access**: sudo/root (for installation)

---

## 🚀 Step 1: Install (1-2 minutes)

### Option A: Automated Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

# Run automated installer
./install.sh
```

The installer will:
- ✅ Install Node.js, Python 3.8+, Docker
- ✅ Setup 18+ MCP servers
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Configure systemd service (optional)

**Wait for:** "✅ Installation complete!"

### Option B: One-Line Remote VPS

```bash
# On remote Ubuntu VPS
curl -fsSL https://raw.githubusercontent.com/AloSantana/Antigravitys/main/install-remote.sh | bash
```

Includes firewall, nginx, and SSL setup!

---

## ⚙️ Step 2: Configure via GUI (1-2 minutes)

### Start the Application

```bash
# Start all services
./start.sh
```

### Open Web Interface

Open your browser:
```
http://localhost:8000
```

You'll see the enhanced multi-tab interface!

### Configure in Settings Tab

1. **Click the "⚙️ Settings" tab** (top navigation)

2. **AI Model Configuration**
   - You'll see cards for Gemini, Vertex AI, and Ollama
   - Gemini should show "✓ Configured" if you have the API key in .env
   - Click a model card to set it as active

3. **API Keys Management**
   - **Gemini API Key**: Click "👁️" to show/hide, enter your key
     - Get it from: https://aistudio.google.com/app/apikey
   - **GitHub Token**: (Optional) Enter for GitHub MCP server
     - Get it from: https://github.com/settings/tokens
   - Click "💾 Save" after entering each key

4. **MCP Server Manager**
   - See all 18+ MCP servers with real-time status
   - Toggle servers ON/OFF with switches
   - Green "● Ready" means the server is operational
   - Yellow "⚠ Missing Creds" means it needs API keys

5. **Test Connections** (Optional)
   - Click "Test Gemini", "Test Vertex", or "Test Ollama"
   - Verify your API keys work correctly

**Configuration Complete! ✅**

---

## 💬 Step 3: Chat with AI Agents (1 minute)

### Return to Chat Tab

1. Click the "💬 Chat" tab

### Select an Agent

On the right panel, you'll see 12 specialized agents:
- **full-stack-developer** - Web development
- **devops-infrastructure** - Docker, K8s, CI/CD
- **testing-stability-expert** - Testing & QA
- **performance-optimizer** - Performance tuning
- **code-reviewer** - Code review & security
- **docs-master** - Documentation
- And 6 more...

Click an agent to select it.

### Send Your First Message

Try these examples:

#### Example 1: Create a REST API
```
Agent: full-stack-developer

Message:
Create a simple REST API with FastAPI for a todo list:
- GET /todos - list all todos
- POST /todos - create a todo
- PUT /todos/{id} - update a todo
- DELETE /todos/{id} - delete a todo
Include Pydantic models and proper error handling
```

#### Example 2: Setup Docker
```
Agent: devops-infrastructure

Message:
Create a Dockerfile and docker-compose.yml for this Python FastAPI application
Include:
- Multi-stage build for smaller image
- Non-root user for security
- Volume mounts for development
- Health checks
```

#### Example 3: Write Tests
```
Agent: testing-stability-expert

Message:
Create comprehensive pytest tests for the todo API:
- Test all CRUD operations
- Mock database calls
- Test error scenarios
- Aim for 90%+ coverage
```

**Watch the agent respond with code, explanations, and instructions!**

---

## 📊 Step 4: Explore Performance Dashboard (1 minute)

### Open Performance Tab

Click the "📊 Performance" tab.

### What You'll See

1. **System Metrics**
   - 📈 **CPU Usage**: Real-time CPU chart
   - 📈 **Memory Usage**: Memory consumption chart
   - 🎯 **Disk Usage**: Circular gauge visualization

2. **Cache Performance**
   - 🎯 **Hit Rate**: Percentage display with progress bar
   - 📊 **Statistics**: Size, hits, misses
   - 📈 **Donut Chart**: Visual breakdown

3. **WebSocket Connections**
   - 🔢 **Active Connections**: Current count
   - 📊 **Connection List**: Live connection details
   - ⏱️ **Duration Stats**: Average connection time

4. **MCP Server Performance**
   - 📊 **Performance Table**: All servers with stats
   - ⚡ **Response Times**: Average, min, max
   - ✅ **Success Rates**: Percentage for each server

5. **Request Analytics**
   - 📈 **Requests/Minute**: Real-time throughput
   - ⏱️ **Response Times**: Average response chart
   - 🐌 **Slowest Endpoints**: Top 5 slowest

### Interactive Features

- **Time Range**: Select 1m, 5m, 15m, or 1h
- **Refresh**: Click 🔄 to manually refresh
- **Export**: Click 📥 to download metrics as JSON
- **Auto-Update**: Dashboard updates every 2 seconds

---

## 📜 Step 5: View Conversation History

### Access via API

```bash
# List all conversations
curl http://localhost:8000/api/conversations

# Get specific conversation with messages
curl http://localhost:8000/api/conversations/{conversation_id}

# Search conversations
curl "http://localhost:8000/api/conversations/search?q=API"

# Export conversation to Markdown
curl http://localhost:8000/api/conversations/{id}/export -o chat.md

# Get statistics
curl http://localhost:8000/api/conversations/statistics
```

### Features

- ✅ **Persistent Storage**: All chats saved to SQLite
- ✅ **Full-Text Search**: Search across all conversations
- ✅ **Export**: Save conversations as Markdown
- ✅ **Statistics**: Track usage patterns
- ✅ **Pagination**: Efficient loading of large histories
- ✅ **Agent Filtering**: Filter by agent type

---

## 🎨 Step 6: Collect Artifacts

### What Are Artifacts?

Generated content like code files, diffs, tests, screenshots, and reports are automatically organized in the `artifacts/` directory.

### Storage Structure

```
artifacts/
├── code/           # Python, JavaScript, etc.
├── diffs/          # Git diffs and patches
├── tests/          # Test files
├── screenshots/    # Images and diagrams
├── reports/        # Markdown, HTML reports
└── metadata.json   # Artifact registry
```

### Access Artifacts

```bash
# List all artifacts
curl http://localhost:8000/api/artifacts

# Store an artifact
curl -X POST http://localhost:8000/api/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "content": "base64_encoded_content_here",
    "filename": "my_script.py",
    "artifact_type": "code"
  }'

# Get artifact content
curl http://localhost:8000/api/artifacts/{id}/content

# Preview artifact
curl http://localhost:8000/api/artifacts/{id}/preview

# Search artifacts
curl "http://localhost:8000/api/artifacts/search?q=test"
```

---

## 🌐 Ecosystem Mode — Master Control Plane

Antigravitys is the **central orchestrator** for a broader AI development
ecosystem.  With a single flag you can boot the Sisyphus agent harness
(`oh-my-opencode`), the multi-agent swarm (`swarm-tools`), the message-routing
gateway (`openclaw`), and the OpenCode Agent Hub alongside the main workspace.

### Step 1 — Bootstrap sister repositories

```bash
# Clone all ecosystem repos into ecosystem/
./ecosystem-setup.sh

# Update already-cloned repos
./ecosystem-setup.sh --update

# Symlink a local checkout instead of cloning
./ecosystem-setup.sh --link ~/projects/openclaw
```

This creates an `ecosystem/` directory containing:

| Directory | Repo | Purpose |
|-----------|------|---------|
| `ecosystem/oh-my-opencode` | AloSantana/oh-my-opencode | Sisyphus agent harness |
| `ecosystem/opencode` | AloSantana/opencode | Core OpenCode engine |
| `ecosystem/openclaw` | AloSantana/openclaw | Message-routing gateway |
| `ecosystem/swarm-tools` | AloSantana/swarm-tools | Multi-agent coordination |

### Step 2 — Start the full ecosystem (one command)

```bash
# Start Antigravitys + all ecosystem daemons
./start.sh --ecosystem
```

The `--ecosystem` flag additionally starts:
- **oh-my-opencode** harness on port **9300**
- **OpenCode Agent Hub** on port **9100**
- **OpenClaw gateway** on port **9200**
- **Swarm-Tools** SQLite interface

### Step 3 — Docker ecosystem mode

```bash
# Start core services + full ecosystem in containers
docker compose --profile ecosystem up -d

# Combined with other profiles (Redis, ChromaDB)
docker compose --profile ecosystem --profile with-redis --profile with-chromadb up -d
```

### Step 4 — Manage OpenCode plugins via the API

```bash
# List installed plugins
curl http://localhost:8000/api/ecosystem/plugins

# Install a plugin from the marketplace
curl -X POST http://localhost:8000/api/ecosystem/plugins \
  -H "Content-Type: application/json" \
  -d '{"plugin_name": "opencode-plugin-github"}'

# Check full ecosystem status
curl http://localhost:8000/api/ecosystem/status

# Uninstall a plugin
curl -X DELETE http://localhost:8000/api/ecosystem/plugins/opencode-plugin-github
```

---



### Explore Advanced Features

#### 1. Use the Code Editor Tab
- Click "📝 Editor" tab
- Syntax highlighting with CodeMirror
- Edit files directly in the browser

#### 2. Interactive Terminal
- Click "🖥️ Terminal" tab
- Execute commands directly
- Real-time output

#### 3. Run Diagnostics
```bash
# Find issues automatically
python tools/auto_issue_finder.py

# Auto-fix common issues
python tools/auto_issue_finder.py --auto-fix

# Generate diagnostic report
python tools/auto_issue_finder.py --output markdown --output-file report.md
```

#### 4. Monitor System Health
```bash
# Start health monitor daemon
python tools/health_monitor.py --daemon --auto-restart --verbose

# Check status
python tools/health_monitor.py --status

# Stop daemon
python tools/health_monitor.py --stop
```

#### 5. Use GitHub Copilot Integration

In VS Code with GitHub Copilot:
```
@agent:full-stack-developer Create a user auth system
@agent:devops-infrastructure Setup CI/CD pipeline
@agent:testing-stability-expert Write integration tests
```

---

## 🔧 Common Tasks

### Start/Stop Services

```bash
# Start
./start.sh

# Stop
./stop.sh

# Restart
./stop.sh && ./start.sh

# Using systemd
sudo systemctl start antigravity
sudo systemctl stop antigravity
sudo systemctl restart antigravity
```

### View Logs

```bash
# Backend logs
tail -f logs/backend.log

# Systemd logs
sudo journalctl -u antigravity -f

# Docker logs
docker-compose logs -f
```

### Update Configuration

```bash
# Via Settings GUI (Recommended)
# 1. Open http://localhost:8000
# 2. Click ⚙️ Settings
# 3. Make changes
# 4. Click Save

# Via Command Line
nano .env
./stop.sh && ./start.sh
```

### Check Health

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed performance metrics
curl http://localhost:8000/performance/metrics

# System validation
./validate.sh
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check what's on port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or change port in .env
echo "PORT=8001" >> .env
```

### API Key Not Working

1. Open Settings tab
2. Verify API key is entered correctly
3. Click "Test Gemini" or "Test Vertex"
4. Check for error messages
5. Get new key from: https://aistudio.google.com/app/apikey

### MCP Server Not Ready

1. Settings tab → MCP Server Manager
2. Check status indicators
3. If "⚠ Missing Creds", add required API keys
4. Toggle server OFF then ON
5. Click 🔄 Refresh Status

### Performance Dashboard Not Updating

1. Check browser console for errors (F12)
2. Verify backend is running: `curl http://localhost:8000/health`
3. Reload page (Ctrl+R or Cmd+R)
4. Check that Performance tab is active

### Run Auto-Issue Finder

```bash
# Diagnose all issues
python tools/auto_issue_finder.py --verbose

# Auto-fix issues
python tools/auto_issue_finder.py --auto-fix

# See detailed output
python tools/auto_issue_finder.py --checks all --verbose
```

---

## 💡 Pro Tips

### 1. Use Keyboard Shortcuts
- **Ctrl+/** or **Cmd+/**: Toggle chat input focus
- **Tab**: Switch between tabs
- **Esc**: Close modals

### 2. Agent Selection
- Choose **full-stack-developer** for general web dev
- Choose **testing-stability-expert** when writing tests
- Choose **performance-optimizer** when optimizing
- Choose **devops-infrastructure** for deployment

### 3. Be Specific in Prompts
❌ Bad: "Create a function"
✅ Good: "Create a function to validate email addresses with regex, return bool, include tests"

### 4. Use the Settings Export
- Export your config as JSON
- Share with team
- Backup before major changes

### 5. Monitor Performance
- Check Performance tab regularly
- Watch for high CPU/memory usage
- Monitor MCP server response times
- Track request throughput

### 6. Search Conversations
Use the API to search through your chat history:
```bash
curl "http://localhost:8000/api/conversations/search?q=authentication"
```

---

## 🎯 5-Minute Checklist

After following this guide, you should have:

- ✅ Installed Antigravity Workspace
- ✅ Configured via Settings GUI
- ✅ Chatted with an AI agent
- ✅ Viewed Performance Dashboard
- ✅ Explored conversation history
- ✅ Understood artifact collection
- ✅ Know how to start/stop services
- ✅ Can troubleshoot common issues

**Congratulations! You're ready to use Antigravity Workspace! 🎉**

---

## 📚 Further Reading

### Essential Documentation
- **[Full README](README.md)**: Complete feature list
- **[Settings GUI Guide](docs/SETTINGS_GUI.md)**: Detailed settings documentation
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Comprehensive troubleshooting
- **[Auto-Issue Finder](docs/AUTO_ISSUE_FINDER.md)**: Diagnostic tool guide

### Feature Guides
- **[Architecture](docs/ARCHITECTURE.md)**: System architecture
- **[Agent Documentation](.github/agents/README.md)**: All 12 agents
- **[MCP Servers](.mcp/README.md)**: MCP integration
- **[Coding Workflow](.github/agents/CODING_WORKFLOW.md)**: Development patterns

### Advanced Topics
- **[Remote Deployment](docs/REMOTE_DEPLOYMENT.md)**: VPS deployment
- **[SSL Setup](docs/SSL_SETUP_GUIDE.md)**: HTTPS configuration
- **[Performance Tuning](PERFORMANCE.md)**: Optimization guide
- **[Docker Deployment](DEPLOYMENT.md)**: Container setup

---

## 🌟 What's Next?

### Try These Workflows

#### 1. Build a Complete Feature
```
@agent:full-stack-developer
Create a user registration system with email verification:
- Backend API with FastAPI
- Email validation and verification
- Password hashing with bcrypt
- Frontend form with validation
- Database models
```

#### 2. Setup Production Environment
```
@agent:devops-infrastructure
Setup production deployment for this app:
- Docker multi-stage build
- Kubernetes manifests
- GitHub Actions CI/CD
- Monitoring with Prometheus
- Logging with ELK stack
```

#### 3. Achieve 100% Test Coverage
```
@agent:testing-stability-expert
Create comprehensive test suite:
- Unit tests for all functions
- Integration tests for APIs
- E2E tests for workflows
- Performance tests
- Load tests with Locust
```

---

## 💬 Get Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: https://github.com/AloSantana/Antigravitys/issues
- **Discussions**: https://github.com/AloSantana/Antigravitys/discussions
- **Auto-Diagnostics**: Run `python tools/auto_issue_finder.py`

---

<div align="center">

**Happy Coding with AI! 🚀**

[⬆ Back to Top](#-quick-start-guide---gui-first-approach)

</div>
