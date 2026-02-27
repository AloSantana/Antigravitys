# Frontend Quick Reference Guide

## 🚀 Quick Start

### View New Features
1. Start backend: `cd backend && python -m uvicorn main:app --reload --port 8000`
2. Open frontend: Navigate to `http://localhost:3000`
3. Click new tabs: **🐝 Swarm**, **🏖️ Sandbox**, **🔧 Tools**

---

## 🐝 Swarm Tab

### Execute Multi-Agent Task

```javascript
// Navigate to Swarm tab
// Enter task in textarea
"Create a REST API for user management with authentication"

// Click: 🚀 Execute with Swarm
// View: Delegation plan + Agent results
```

### API Endpoint
```bash
curl -X POST http://localhost:8000/api/swarm/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Build a login system", "verbose": true}'
```

### Key Functions
- `executeSwarm()` - Run swarm task
- `displaySwarmResults()` - Show results
- `loadSwarmCapabilities()` - Load agents

---

## 🏖️ Sandbox Tab

### Execute Code

```javascript
// Navigate to Sandbox tab
// Select language: Python / JavaScript / Bash
// Enter code:
print("Hello from Antigravity!")

// Set timeout: 30 seconds
// Click: ▶️ Run Code
// View: stdout, stderr, exit code, execution time
```

### API Endpoint
```bash
curl -X POST http://localhost:8000/api/sandbox/run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello World\")",
    "language": "python",
    "timeout": 30
  }'
```

### Key Functions
- `runSandbox()` - Execute code
- `displaySandboxResults()` - Show output
- `clearSandbox()` - Reset editor

---

## 🔧 Tools Tab

### Test MCP Tool

```javascript
// Navigate to Tools tab
// Wait for tools to load
// Search: "filesystem" or "git"
// Click a tool to select
// View details and schema
// Modify arguments JSON
// Click: 🚀 Execute Tool
// View results
```

### API Endpoints
```bash
# List all tools
curl http://localhost:8000/api/mcp/tools

# Get tool details
curl http://localhost:8000/api/mcp/tools/read_file?server=filesystem

# Execute tool
curl -X POST http://localhost:8000/api/mcp/tools/read_file/execute \
  -H "Content-Type: application/json" \
  -d '{
    "server": "filesystem",
    "arguments": {"path": "/path/to/file"}
  }'
```

### Key Functions
- `loadMCPServers()` - Load server status
- `loadToolsList()` - Discover tools
- `selectTool()` - Show tool details
- `testTool()` - Execute tool

---

## 🎨 CSS Classes Reference

### Swarm
- `.swarm-container` - Main container
- `.swarm-task-input` - Task textarea
- `.swarm-execute-btn` - Execute button
- `.swarm-agent-card` - Agent status card
- `.swarm-plan-display` - Plan visualization
- `.swarm-result-item` - Result item

### Sandbox
- `.sandbox-container` - Main container
- `.sandbox-editor` - Code editor
- `.sandbox-btn-primary` - Run button
- `.sandbox-output-content` - Output display
- `.sandbox-meta-item` - Metadata

### Tools
- `.tools-container` - Main container
- `.tools-search-bar` - Search input
- `.tools-item` - Tool list item
- `.tools-details-panel` - Details view
- `.tools-test-input` - Test arguments
- `.tools-test-result` - Test results

---

## 🔧 JavaScript State Objects

### Swarm State
```javascript
swarmState = {
  executing: boolean,   // Currently executing
  currentTask: string   // Active task
}
```

### Sandbox State
```javascript
sandboxState = {
  executing: boolean    // Currently running code
}
```

### Tools State
```javascript
toolsState = {
  mcpServers: [],      // MCP server list
  tools: [],           // Filtered tools
  allTools: [],        // All discovered tools
  selectedTool: null   // Currently selected tool
}
```

---

## 🎯 Common Tasks

### Add Loading Spinner
```javascript
container.innerHTML = `
  <div class="tools-loading">
    <div class="tools-loading-spinner"></div>
    <div>Loading...</div>
  </div>
`;
```

### Show Error Message
```javascript
container.innerHTML = `
  <div class="tools-empty-state">
    Failed to load<br>
    <small>${escapeHtml(error.message)}</small>
  </div>
`;
```

### Display JSON Result
```javascript
resultDiv.textContent = JSON.stringify(data, null, 2);
```

### Escape HTML
```javascript
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

---

## 🐛 Debugging

### Check Tab Activation
```javascript
// Open browser console
// Look for: "Swarm capabilities loaded" or similar messages
console.log('Current active panel:', 
  document.querySelector('.content-panel.active').id);
```

### Test API Endpoints
```bash
# Check if backend is running
curl http://localhost:8000/health

# Test swarm endpoint
curl -X POST http://localhost:8000/api/swarm/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "test", "verbose": true}'

# Test sandbox endpoint
curl -X POST http://localhost:8000/api/sandbox/run \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1)", "language": "python"}'

# Test MCP tools
curl http://localhost:8000/api/mcp/tools
```

### Common Issues

**Tabs not showing**
- Check: `data-panel` attribute matches panel ID
- Verify: Tab click handlers attached

**API calls failing**
- Check: Backend server running on port 8000
- Verify: CORS configured correctly
- Test: Endpoint with curl

**Tools not loading**
- Check: MCP servers configured in backend
- Verify: MCP servers running
- Test: `/api/mcp/status` endpoint

---

## 📱 Mobile Support

All new tabs are responsive:

```css
@media (max-width: 1024px) {
  /* Sidebars hidden on mobile */
  /* Full-width main content */
  /* Single column grids */
}
```

---

## 🔒 Security

### HTML Escaping
Always escape user input before displaying:

```javascript
// ✅ GOOD
element.textContent = userInput;
element.innerHTML = escapeHtml(userInput);

// ❌ BAD
element.innerHTML = userInput;  // XSS risk!
```

### API Error Handling
Never expose internal errors to users:

```javascript
try {
  const response = await fetch(url);
  // ...
} catch (error) {
  console.error('Internal error:', error);  // Log full error
  alert('Failed to load data');             // Show generic message
}
```

---

## 📊 Performance Tips

### Lazy Load Data
```javascript
// Only load when tab is activated
if (panel.classList.contains('active')) {
  loadData();
}
```

### Debounce Search
```javascript
let searchTimeout;
function filterTools() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    // Do actual filtering
  }, 300);
}
```

### Efficient DOM Updates
```javascript
// Build HTML string first
const html = items.map(item => `<div>...</div>`).join('');
// Then update DOM once
container.innerHTML = html;
```

---

## 🎨 Theme Customization

### CSS Variables
```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --accent-blue: #3b82f6;
  --accent-green: #10b981;
  --accent-purple: #8b5cf6;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
}
```

### Override Styles
Add custom styles at end of `<style>` block:

```css
/* Custom overrides */
.swarm-execute-btn {
  background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
}
```

---

## 📝 Code Examples

### Add New Tab

1. **Add tab button**:
```html
<div class="tab" data-panel="newtab">
  🆕 New Tab
</div>
```

2. **Add panel content**:
```html
<div class="content-panel" id="newtab-panel">
  <div class="newtab-container">
    <!-- Content here -->
  </div>
</div>
```

3. **Add styles**:
```css
.newtab-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
```

4. **Add JavaScript**:
```javascript
async function loadNewTabData() {
  try {
    const response = await fetch(`${API_BASE}/newtab/data`);
    const data = await response.json();
    displayNewTabData(data);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 🔗 Related Files

- **Frontend**: `frontend/index.html` (main file)
- **Backend**: `backend/main.py` (API routes)
- **Swarm**: `backend/agents/swarm.py`
- **Sandbox**: `backend/sandbox/executor.py`
- **MCP**: `backend/mcp/client.py`
- **Docs**: `FRONTEND_INTEGRATION_COMPLETE.md`

---

## ✅ Testing Checklist

Quick verification:

```bash
# 1. Start backend
python -m uvicorn backend.main:app --reload

# 2. Open browser
# http://localhost:3000

# 3. Test each tab
[ ] Click "🐝 Swarm" - loads without errors
[ ] Click "🏖️ Sandbox" - loads without errors  
[ ] Click "🔧 Tools" - loads without errors

# 4. Execute functions
[ ] Swarm: Execute task
[ ] Sandbox: Run code
[ ] Tools: Test tool

# 5. Check console
[ ] No JavaScript errors
[ ] API calls succeed
```

---

## 🆘 Support

**Issues?**
1. Check browser console for errors
2. Verify backend is running
3. Test API endpoints with curl
4. Review `FRONTEND_INTEGRATION_COMPLETE.md`

**Need help?**
- Backend API: See `API_QUICK_REFERENCE.md`
- Full docs: See `FRONTEND_INTEGRATION_COMPLETE.md`
- Examples: Check inline comments in `index.html`

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
