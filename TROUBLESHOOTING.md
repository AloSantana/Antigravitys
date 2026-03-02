# 🔧 Troubleshooting Guide

Comprehensive troubleshooting guide for Antigravity Workspace Template covering all features and common issues.

---

## 🚀 Quick Diagnostics

### Use the Auto-Issue Finder First!

Before manual troubleshooting, run the smart diagnostic tool:

```bash
# Run all checks
python tools/auto_issue_finder.py --verbose

# Auto-fix common issues
python tools/auto_issue_finder.py --auto-fix

# Generate detailed report
python tools/auto_issue_finder.py --output markdown --output-file diagnostic-report.md
```

The auto-issue finder checks:
- ✅ Static code analysis
- ✅ Security vulnerabilities
- ✅ Configuration errors
- ✅ Shell script issues
- ✅ Dependency problems
- ✅ Runtime environment
- ✅ Docker configuration

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Backend Issues](#backend-issues)
3. [Frontend Issues](#frontend-issues)
4. [Settings GUI Issues](#settings-gui-issues)
5. [Performance Dashboard Issues](#performance-dashboard-issues)
6. [Database Issues (SQLite)](#database-issues-sqlite)
7. [MCP Server Issues](#mcp-server-issues)
8. [WebSocket Issues](#websocket-issues)
9. [Conversation History Issues](#conversation-history-issues)
10. [Artifact System Issues](#artifact-system-issues)
11. [Health Monitor Issues](#health-monitor-issues)
12. [Docker Issues](#docker-issues)
13. [Network & Firewall Issues](#network--firewall-issues)
14. [Performance Issues](#performance-issues)

---

## Installation Issues

### Problem: Installation Script Fails

**Symptoms:**
- `install.sh` exits with error
- "Permission denied" errors
- Package installation fails

**Solutions:**

```bash
# 1. Make script executable
chmod +x install.sh

# 2. Run with bash explicitly
bash install.sh

# 3. Check for missing dependencies
sudo apt-get update
sudo apt-get install -y curl git wget

# 4. Check disk space
df -h
# Need at least 5GB free

# 5. Check internet connection
ping google.com

# 6. View detailed error log
cat /tmp/antigravity-install.log
```

### Problem: Node.js Installation Fails

**Symptoms:**
- "node: command not found"
- npm install errors

**Solutions:**

```bash
# 1. Install Node.js manually
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Verify installation
node --version  # Should be 20.x
npm --version

# 3. Fix npm permissions
sudo chown -R $USER:$GROUP ~/.npm
sudo chown -R $USER:$GROUP ~/.config
```

### Problem: MCP Server Installation Fails

**Symptoms:**
- "Failed to install MCP server" messages
- Some servers missing

**Solutions:**

```bash
# 1. Install individually
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @github/mcp-server

# 2. Clear npm cache
npm cache clean --force

# 3. Use different registry
npm config set registry https://registry.npmjs.org/

# 4. Check globally installed packages
npm list -g --depth=0
```

### Problem: Python Virtual Environment Issues

**Symptoms:**
- "python: command not found"
- pip install failures

**Solutions:**

```bash
# 1. Install Python 3.8+
sudo apt-get install -y python3 python3-pip python3-venv

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## Backend Issues

### Problem: Backend Won't Start

**Symptoms:**
- "Address already in use" error
- ImportError messages
- Connection refused

**Solutions:**

```bash
# 1. Check what's using port 8000
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# 2. Kill the process
sudo kill -9 <PID>

# 3. Change port in .env
echo "PORT=8001" >> .env

# 4. Check Python imports
cd backend
python -c "import fastapi; print('OK')"

# 5. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 6. Check logs
tail -f logs/backend.log
```

### Problem: ImportError in Backend

**Symptoms:**
- "ModuleNotFoundError: No module named 'X'"

**Solutions:**

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install missing package
pip install <package-name>

# 3. Reinstall all requirements
pip install -r backend/requirements.txt

# 4. Check Python path
python -c "import sys; print(sys.path)"

# 5. Verify installation
pip list | grep <package-name>
```

### Problem: API Endpoints Return 500 Error

**Symptoms:**
- HTTP 500 Internal Server Error
- Stack traces in logs

**Solutions:**

```bash
# 1. Check backend logs
tail -f logs/backend.log

# 2. Enable debug mode
echo "DEBUG=true" >> .env

# 3. Test specific endpoint
curl -v http://localhost:8000/health

# 4. Check database connection
ls -la conversations.db
sqlite3 conversations.db ".tables"

# 5. Run diagnostic tool
python tools/auto_issue_finder.py --checks runtime
```

---

## Frontend Issues

### Problem: Frontend Not Loading

**Symptoms:**
- Blank page
- "Cannot connect to backend"
- JavaScript errors

**Solutions:**

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Open browser console (F12)
# Look for errors in Console tab

# 3. Clear browser cache
# Ctrl+Shift+R (hard refresh)

# 4. Check file exists
ls -la frontend/index.html

# 5. Test direct file access
firefox frontend/index.html  # Or: open, chrome
```

### Problem: Backend Connection Failed

**Symptoms:**
- "Failed to fetch" errors
- Network timeout
- CORS errors

**Solutions:**

```bash
# 1. Verify backend URL
# Check browser console for API_BASE value

# 2. Check CORS configuration in .env
echo "ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000" >> .env

# 3. Test from command line
curl http://localhost:8000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 4. Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# 5. Check nginx config (if using)
sudo nginx -t
sudo systemctl status nginx
```

---

## Settings GUI Issues

### Problem: Settings Not Saving

**Symptoms:**
- "Save failed" message
- Settings revert on reload
- 500 error on save

**Solutions:**

```bash
# 1. Check file permissions
chmod 644 .env
chmod 644 .github/copilot/mcp.json

# 2. Check disk space
df -h

# 3. Test API endpoint
curl -X POST http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"port": 8000}'

# 4. Check backend logs
tail -f logs/backend.log

# 5. Verify settings manager
python -c "from backend.settings_manager import SettingsManager; print('OK')"
```

### Problem: API Keys Not Working

**Symptoms:**
- "Invalid API key" error
- Connection test fails
- 401 Unauthorized

**Solutions:**

```bash
# 1. Verify API key format
# Gemini: Should start with "AIza"
echo $GEMINI_API_KEY | cut -c1-4

# 2. Test API key directly
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$GEMINI_API_KEY"

# 3. Get new API key
# Visit: https://aistudio.google.com/app/apikey

# 4. Check encryption
python -c "from backend.settings_manager import SettingsManager; sm = SettingsManager(); print(sm.get_api_key('GEMINI_API_KEY'))"

# 5. Clear and re-enter
# Settings GUI → API Keys → Clear → Re-enter → Save
```

### Problem: MCP Server Status Wrong

**Symptoms:**
- Shows "Missing Creds" but key is set
- Toggle doesn't work
- Status not updating

**Solutions:**

```bash
# 1. Click "🔄 Refresh Status" button

# 2. Test MCP server manually
npx @github/mcp-server --help
export GITHUB_TOKEN=<your_token>
npx @github/mcp-server

# 3. Check environment variables
printenv | grep TOKEN

# 4. Reload page (Ctrl+R)

# 5. Check MCP config
cat .github/copilot/mcp.json | jq .
```

---

## Performance Dashboard Issues

### Problem: Charts Not Rendering

**Symptoms:**
- Empty charts
- "Chart is not defined" error
- Dashboard blank

**Solutions:**

```bash
# 1. Check Chart.js is loaded
# Open browser console (F12)
# Type: typeof Chart
# Should return "function"

# 2. Verify CDN access
curl https://cdn.jsdelivr.net/npm/chart.js

# 3. Check Performance tab is active
# Charts only update when tab is visible

# 4. Test API endpoint
curl http://localhost:8000/performance/metrics

# 5. Clear browser cache and reload
# Ctrl+Shift+R
```

### Problem: Metrics Not Updating

**Symptoms:**
- Static charts
- Old data
- Update interval not working

**Solutions:**

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Verify tab is active
# Switch away and back to Performance tab

# 3. Click "🔄 Refresh" button

# 4. Check browser console for errors
# F12 → Console tab

# 5. Test metrics endpoint
curl http://localhost:8000/performance/metrics | jq .
```

### Problem: WebSocket Stats Empty

**Symptoms:**
- Shows 0 active connections
- Connection list empty
- No history

**Solutions:**

```bash
# 1. Connect via Chat tab first
# Open Chat tab and send a message

# 2. Check WebSocket connection
# Browser console → Network tab → WS filter

# 3. Test WebSocket endpoint
# Use tool like websocat:
websocat ws://localhost:8000/ws

# 4. Check backend tracking
curl http://localhost:8000/performance/websocket-stats

# 5. Restart backend
./stop.sh && ./start.sh
```

---

## Database Issues (SQLite)

### Problem: Database Locked

**Symptoms:**
- "database is locked" error
- Conversations not saving
- Timeout errors

**Solutions:**

```bash
# 1. Check for multiple backend instances
ps aux | grep "python.*main.py"
kill <PID>  # Kill extra instances

# 2. Close database connections
# Stop all processes accessing DB
./stop.sh

# 3. Check file permissions
chmod 644 conversations.db
chown $USER:$USER conversations.db

# 4. Repair database
sqlite3 conversations.db "PRAGMA integrity_check;"

# 5. Increase timeout in code
# Edit backend/conversation_manager.py
# Increase timeout in sqlite3.connect()
```

### Problem: Database Corrupted

**Symptoms:**
- "database disk image is malformed"
- SQLite errors
- Can't read conversations

**Solutions:**

```bash
# 1. Backup database
cp conversations.db conversations.db.backup

# 2. Try to recover
sqlite3 conversations.db ".dump" > dump.sql
rm conversations.db
sqlite3 conversations.db < dump.sql

# 3. Check disk health
df -h
dmesg | grep -i error

# 4. Start fresh (if recovery fails)
rm conversations.db
# Database will be recreated on next start

# 5. Restore from backup if available
cp conversations.db.backup conversations.db
```

### Problem: Conversations Not Appearing

**Symptoms:**
- API returns empty list
- New conversations not saving
- Search returns nothing

**Solutions:**

```bash
# 1. Check database exists
ls -la conversations.db

# 2. Verify tables
sqlite3 conversations.db ".tables"
# Should show: conversations, messages

# 3. Query database directly
sqlite3 conversations.db "SELECT COUNT(*) FROM conversations;"

# 4. Test API
curl http://localhost:8000/api/conversations

# 5. Check backend logs
tail -f logs/backend.log | grep conversation
```

---

## MCP Server Issues

### Problem: MCP Server Not Found

**Symptoms:**
- "server not found" error
- Agent can't use tools
- Import failures

**Solutions:**

```bash
# 1. Check globally installed
npm list -g --depth=0 | grep mcp

# 2. Install missing server
npm install -g @modelcontextprotocol/server-filesystem

# 3. Test server manually
npx @modelcontextprotocol/server-filesystem --help

# 4. Check PATH
echo $PATH | grep npm

# 5. Verify config
cat .github/copilot/mcp.json | jq '.mcpServers'
```

### Problem: GitHub MCP Server Fails

**Symptoms:**
- "authentication required"
- 401 errors
- Can't access repositories

**Solutions:**

```bash
# 1. Check token is set
echo $COPILOT_MCP_GITHUB_TOKEN | cut -c1-8

# 2. Verify token permissions
# Visit: https://github.com/settings/tokens
# Required scopes: repo, read:org

# 3. Test token
curl -H "Authorization: token $COPILOT_MCP_GITHUB_TOKEN" \
  https://api.github.com/user

# 4. Set in .env
echo "COPILOT_MCP_GITHUB_TOKEN=your_token_here" >> .env

# 5. Set in Settings GUI
# Settings → API Keys → GitHub Token → Save
```

### Problem: Python Analysis Server Missing

**Symptoms:**
- Type checking doesn't work
- No code analysis
- "python-analysis not found"

**Solutions:**

```bash
# 1. Install Python MCP server
pip install mcp-server-python-analysis

# 2. Verify installation
python -m mcp_server_python_analysis --help

# 3. Check Python version
python --version  # Need 3.8+

# 4. Add to requirements.txt
echo "mcp-server-python-analysis" >> requirements.txt

# 5. Reinstall all
pip install -r requirements.txt
```

---

## WebSocket Issues

### Problem: WebSocket Connection Fails

**Symptoms:**
- "WebSocket connection failed"
- Chat doesn't work
- Reconnection loops

**Solutions:**

```bash
# 1. Check backend WebSocket endpoint
curl http://localhost:8000/ws --include \
  --header "Connection: Upgrade" \
  --header "Upgrade: websocket"

# 2. Check for proxy issues
# If using nginx, verify WebSocket support:
sudo nginx -t

# 3. Test with simple client
# Use websocat or similar:
websocat ws://localhost:8000/ws

# 4. Check firewall
sudo ufw allow 8000/tcp

# 5. Review backend logs
tail -f logs/backend.log | grep -i websocket
```

### Problem: WebSocket Keeps Reconnecting

**Symptoms:**
- Constant reconnection attempts
- "Reconnecting..." message
- Exponential backoff visible

**Solutions:**

```bash
# 1. Check backend stability
# Ensure backend isn't crashing
ps aux | grep "python.*main.py"

# 2. Check network stability
ping localhost

# 3. Review backend errors
tail -f logs/backend.log

# 4. Adjust reconnection settings
# In frontend/index.html, modify:
# MAX_RECONNECT_ATTEMPTS
# RECONNECT_DELAY

# 5. Restart both frontend and backend
./stop.sh && ./start.sh
```

---

## Conversation History Issues

### Problem: Can't Create Conversation

**Symptoms:**
- POST returns error
- 500 Internal Server Error
- Database error

**Solutions:**

```bash
# 1. Check database permissions
chmod 644 conversations.db

# 2. Test API directly
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "agent_type": "assistant"}'

# 3. Check disk space
df -h

# 4. Verify database schema
sqlite3 conversations.db ".schema conversations"

# 5. Check backend logs
tail -f logs/backend.log | grep conversation
```

### Problem: Search Not Working

**Symptoms:**
- Search returns no results
- Known conversations not found
- Empty results

**Solutions:**

```bash
# 1. Verify data exists
sqlite3 conversations.db "SELECT COUNT(*) FROM conversations;"

# 2. Test search API
curl "http://localhost:8000/api/conversations/search?q=test"

# 3. Check search query
# Ensure query is URL-encoded
curl "http://localhost:8000/api/conversations/search?q=$(echo 'my query' | jq -sRr @uri)"

# 4. Try different search terms
curl "http://localhost:8000/api/conversations/search?q=agent"

# 5. Rebuild database (if needed)
# See "Database Corrupted" section
```

### Problem: Export Fails

**Symptoms:**
- Export button doesn't work
- Empty file downloaded
- 404 error

**Solutions:**

```bash
# 1. Test export API
curl http://localhost:8000/api/conversations/{id}/export -o test.md

# 2. Verify conversation exists
curl http://localhost:8000/api/conversations/{id}

# 3. Check conversation has messages
sqlite3 conversations.db "SELECT COUNT(*) FROM messages WHERE conversation_id = '{id}';"

# 4. Check file permissions
ls -la artifacts/

# 5. Try different browser
# Download might be blocked by browser settings
```

---

## Artifact System Issues

### Problem: Can't Store Artifacts

**Symptoms:**
- POST returns error
- "Failed to store artifact"
- 500 error

**Solutions:**

```bash
# 1. Check artifacts directory exists
ls -la artifacts/

# 2. Create if missing
mkdir -p artifacts/{code,diffs,tests,screenshots,reports,other}

# 3. Check permissions
chmod 755 artifacts
chmod 755 artifacts/*

# 4. Check disk space
df -h

# 5. Test API
curl -X POST http://localhost:8000/api/artifacts \
  -H "Content-Type: application/json" \
  -d '{"content": "dGVzdA==", "filename": "test.txt"}'
```

### Problem: Size Limit Exceeded

**Symptoms:**
- "File too large" error
- "Storage limit exceeded"
- 413 Payload Too Large

**Solutions:**

```bash
# 1. Check current usage
du -sh artifacts/

# 2. Clean up old artifacts
curl -X POST http://localhost:8000/api/artifacts/cleanup

# 3. Increase limits in backend/artifact_manager.py
# MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
# MAX_TOTAL_SIZE = 1000 * 1024 * 1024  # 1GB

# 4. Delete specific artifacts
curl -X DELETE http://localhost:8000/api/artifacts/{id}

# 5. Manually clean artifacts
rm -rf artifacts/code/*  # Be careful!
```

### Problem: Artifact Preview Not Working

**Symptoms:**
- Preview shows nothing
- "Failed to generate preview"
- Unsupported type

**Solutions:**

```bash
# 1. Check artifact type
curl http://localhost:8000/api/artifacts/{id}

# 2. Verify content is readable
curl http://localhost:8000/api/artifacts/{id}/content

# 3. Check file type support
# Preview supports: text, code, images
# Binary files may not preview

# 4. Download and view locally
curl http://localhost:8000/api/artifacts/{id}/content -o file.ext

# 5. Check backend logs
tail -f logs/backend.log | grep artifact
```

---

## Health Monitor Issues

### Problem: Health Monitor Won't Start

**Symptoms:**
- Daemon fails to start
- "Permission denied"
- PID file errors

**Solutions:**

```bash
# 1. Check PID file location
ls -la /tmp/health_monitor.pid

# 2. Remove stale PID file
rm -f /tmp/health_monitor.pid

# 3. Run in foreground first
python tools/health_monitor.py --verbose

# 4. Check permissions
chmod +x tools/health_monitor.py

# 5. Check Python path
which python
python --version
```

### Problem: Alerts Not Working

**Symptoms:**
- No alerts generated
- Thresholds not triggering
- Email not sent

**Solutions:**

```bash
# 1. Check thresholds
# Default: CPU 80%, Memory 85%, Disk 90%

# 2. Lower thresholds for testing
# Edit tools/health_monitor.py
# CPU_THRESHOLD = 50

# 3. Manually trigger alert
python -c "from tools.health_monitor import AlertManager; am = AlertManager(); am.add_alert('TEST', 'Test alert')"

# 4. Check alert history
python tools/health_monitor.py --status

# 5. Check logs
tail -f /var/log/health_monitor.log
```

### Problem: Auto-Restart Not Working

**Symptoms:**
- Services stay down
- No restart attempts
- Cooldown issues

**Solutions:**

```bash
# 1. Check restart is enabled
# Run with: --auto-restart flag

# 2. Verify service check works
curl http://localhost:8000/health

# 3. Check cooldown period
# Default 300s between restarts

# 4. Manual restart
./stop.sh && ./start.sh

# 5. Check restart logs
tail -f /var/log/health_monitor.log | grep restart
```

---

## Docker Issues

### Problem: Docker Build Fails

**Symptoms:**
- Build errors
- "No space left on device"
- Network timeout

**Solutions:**

```bash
# 1. Check Docker is running
sudo systemctl status docker

# 2. Clean Docker cache
docker system prune -af

# 3. Check disk space
df -h /var/lib/docker

# 4. Build with no cache
docker build --no-cache -t antigravity:latest .

# 5. Check Dockerfile syntax
docker build --dry-run -t test .
```

### Problem: Docker Compose Fails

**Symptoms:**
- "Service 'X' failed to build"
- Port conflicts
- Network errors

**Solutions:**

```bash
# 1. Stop existing containers
docker-compose down

# 2. Check port availability
sudo lsof -i :8000
sudo lsof -i :3000

# 3. Rebuild services
docker-compose up -d --build

# 4. Check logs
docker-compose logs -f backend

# 5. Reset everything
docker-compose down -v
docker-compose up -d --build
```

---

## Network & Firewall Issues

### Problem: Can't Access from Remote

**Symptoms:**
- Connection refused
- Timeout
- Works on localhost, not remotely

**Solutions:**

```bash
# 1. Check HOST setting in .env
echo "HOST=0.0.0.0" >> .env

# 2. Open firewall ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# 3. Check service is listening
sudo netstat -tulpn | grep 8000

# 4. Test from remote
curl http://your-server-ip:8000/health

# 5. Check nginx config (if using)
sudo nginx -t
sudo systemctl reload nginx
```

### Problem: CORS Errors

**Symptoms:**
- "CORS policy" error in browser
- Cross-origin request blocked
- Preflight fails

**Solutions:**

```bash
# 1. Set ALLOWED_ORIGINS in .env
echo "ALLOWED_ORIGINS=http://your-domain.com,http://localhost:3000" >> .env

# 2. Allow all origins (development only)
echo "ALLOWED_ORIGINS=*" >> .env

# 3. Restart backend
./stop.sh && ./start.sh

# 4. Check CORS headers
curl -H "Origin: http://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8000/api/chat -v

# 5. Update nginx config (if using)
# Add: add_header 'Access-Control-Allow-Origin' '*';
```

---

## Performance Issues

### Problem: Slow Response Times

**Symptoms:**
- High latency
- Timeout errors
- Slow API responses

**Solutions:**

```bash
# 1. Check Performance Dashboard
# Open: http://localhost:8000/ → Performance tab

# 2. Monitor system resources
htop
top
vmstat 1

# 3. Check for memory leaks
ps aux | grep python

# 4. Enable performance logging
echo "LOG_LEVEL=DEBUG" >> .env

# 5. Run performance tests
python test-performance-dashboard.py
```

### Problem: High Memory Usage

**Symptoms:**
- Memory at 90%+
- OOM errors
- Slow performance

**Solutions:**

```bash
# 1. Check memory usage
free -h
ps aux --sort=-%mem | head

# 2. Restart services
./stop.sh && ./start.sh

# 3. Reduce cache size
# Edit backend/main.py
# Reduce MAX_DATA_POINTS

# 4. Enable garbage collection
# Add to backend/main.py:
import gc
gc.collect()

# 5. Increase swap (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problem: High CPU Usage

**Symptoms:**
- CPU at 100%
- Fans loud
- Slow system

**Solutions:**

```bash
# 1. Check what's using CPU
top
htop
ps aux --sort=-%cpu | head

# 2. Reduce update intervals
# Performance Dashboard: Increase from 2s to 5s

# 3. Disable unused MCP servers
# Settings → MCP Server Manager → Toggle OFF

# 4. Limit concurrent requests
# Edit backend/main.py
# Add rate limiting

# 5. Check for infinite loops
tail -f logs/backend.log
```

---

## 🔍 Diagnostic Commands Reference

### System Health

```bash
# Quick health check
curl http://localhost:8000/health

# Detailed metrics
curl http://localhost:8000/performance/metrics | jq .

# Database check
sqlite3 conversations.db "PRAGMA integrity_check;"

# Disk usage
df -h
du -sh artifacts/
du -sh logs/
```

### Service Status

```bash
# Check processes
ps aux | grep python
ps aux | grep node

# Check ports
sudo netstat -tulpn | grep LISTEN
sudo lsof -i :8000

# Systemd status (if using)
sudo systemctl status antigravity
sudo journalctl -u antigravity -n 50
```

### Log Analysis

```bash
# Backend logs
tail -f logs/backend.log

# Grep for errors
tail -n 1000 logs/backend.log | grep -i error

# Count errors
grep -c ERROR logs/backend.log

# Last 100 errors
grep ERROR logs/backend.log | tail -100

# Health monitor logs
tail -f /var/log/health_monitor.log
```

### Auto-Diagnostics

```bash
# Run all checks
python tools/auto_issue_finder.py --verbose

# Specific checks
python tools/auto_issue_finder.py --checks static,security

# Generate report
python tools/auto_issue_finder.py --output markdown --output-file report.md

# Auto-fix
python tools/auto_issue_finder.py --auto-fix
```

---

## 🆘 Getting Help

### Before Reporting Issues

1. ✅ Run auto-issue finder
2. ✅ Check logs for errors
3. ✅ Review this troubleshooting guide
4. ✅ Search existing GitHub issues
5. ✅ Try with clean installation

### When Reporting Issues

Include:
- **OS and version** (`uname -a`)
- **Python version** (`python --version`)
- **Node.js version** (`node --version`)
- **Error messages** (full text)
- **Steps to reproduce**
- **Diagnostic report** (from auto-issue finder)
- **Relevant logs**

### Where to Get Help

- **Documentation**: [docs/](docs/) folder
- **GitHub Issues**: https://github.com/AloSantana/Antigravitys/issues
- **Discussions**: https://github.com/AloSantana/Antigravitys/discussions

---

## 💡 Prevention Best Practices

### Regular Maintenance

```bash
# Weekly: Run diagnostics
python tools/auto_issue_finder.py

# Weekly: Clean artifacts
curl -X POST http://localhost:8000/api/artifacts/cleanup

# Monthly: Update dependencies
pip install -r requirements.txt --upgrade
npm update -g

# Monthly: Review logs
grep ERROR logs/backend.log | wc -l

# Monthly: Database maintenance
sqlite3 conversations.db "VACUUM;"
```

### Monitoring

```bash
# Start health monitor
python tools/health_monitor.py --daemon --auto-restart --verbose

# Check status regularly
python tools/health_monitor.py --status

# Review Performance Dashboard daily
# http://localhost:8000/ → Performance tab
```

### Backups

```bash
# Backup database
cp conversations.db conversations.db.$(date +%Y%m%d)

# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env artifacts/ conversations.db

# Backup artifacts
rsync -av artifacts/ /backup/artifacts/
```

---

<div align="center">

**Still having issues?**

Run the auto-issue finder: `python tools/auto_issue_finder.py --auto-fix`

Or open an issue: https://github.com/AloSantana/Antigravitys/issues

[⬆ Back to Top](#-troubleshooting-guide)

</div>
