# Frontend Integration Plan for Feature Overhaul

## Overview

This document outlines the plan to update the frontend and web UI to reflect all new features, functions, tools, examples, and usage patterns implemented in the comprehensive feature overhaul.

## New Features to Integrate

### 1. Swarm Agent System
- Multi-agent orchestration interface
- Task delegation visualization
- Agent status monitoring
- Result synthesis display

### 2. MCP Tool Management
- MCP server status dashboard
- Tool discovery interface
- Tool execution controls
- Server configuration management

### 3. Sandbox Execution
- Code editor with syntax highlighting
- Multi-language support (Python, JS, Bash)
- Execution results display
- Sandbox configuration panel

### 4. Enhanced Agent Configuration
- Model selection (Gemini/Vertex/Ollama/Auto)
- Agent settings management
- Memory management controls
- Context file viewer

### 5. Real-Time Tool Discovery
- Auto-discovered tools list
- Tool documentation viewer
- Usage examples
- Interactive tool testing

## UI Components to Add/Update

### Tab Structure (Enhanced)

```
┌─────────────────────────────────────────────────────────────┐
│  Chat  │  Code  │  Terminal  │  Swarm  │  Sandbox  │  Tools │
└─────────────────────────────────────────────────────────────┘
```

### New Tabs

#### 1. **Swarm Tab**
```html
<div id="swarm-tab" class="tab-content">
  <div class="swarm-controls">
    <h3>Multi-Agent Swarm Orchestrator</h3>
    
    <!-- Task Input -->
    <textarea id="swarm-task" placeholder="Enter task for swarm..."></textarea>
    <button id="execute-swarm">Execute with Swarm</button>
    
    <!-- Agent Status -->
    <div class="agent-status">
      <h4>Available Agents</h4>
      <div class="agent-card" data-agent="router">
        <span class="status-indicator active"></span>
        <strong>Router</strong>: Task Analysis & Delegation
      </div>
      <div class="agent-card" data-agent="coder">
        <span class="status-indicator active"></span>
        <strong>Coder</strong>: Code Implementation
      </div>
      <div class="agent-card" data-agent="reviewer">
        <span class="status-indicator active"></span>
        <strong>Reviewer</strong>: Code Review & QA
      </div>
      <div class="agent-card" data-agent="researcher">
        <span class="status-indicator active"></span>
        <strong>Researcher</strong>: Research & Analysis
      </div>
    </div>
    
    <!-- Delegation Plan -->
    <div class="delegation-plan">
      <h4>Delegation Plan</h4>
      <div id="plan-display"></div>
    </div>
    
    <!-- Results -->
    <div class="swarm-results">
      <h4>Execution Results</h4>
      <div id="swarm-output"></div>
    </div>
  </div>
</div>
```

#### 2. **Sandbox Tab**
```html
<div id="sandbox-tab" class="tab-content">
  <div class="sandbox-controls">
    <h3>Code Sandbox</h3>
    
    <!-- Language Selection -->
    <select id="sandbox-language">
      <option value="python">Python</option>
      <option value="javascript">JavaScript</option>
      <option value="bash">Bash</option>
    </select>
    
    <!-- Sandbox Type -->
    <select id="sandbox-type">
      <option value="local">Local</option>
      <option value="docker">Docker</option>
    </select>
    
    <!-- Code Editor -->
    <div class="code-editor-container">
      <textarea id="sandbox-code" placeholder="Enter code to execute..."></textarea>
    </div>
    
    <!-- Controls -->
    <div class="sandbox-actions">
      <button id="run-sandbox">Run Code</button>
      <button id="clear-sandbox">Clear</button>
      <input type="number" id="sandbox-timeout" placeholder="Timeout (s)" value="30">
    </div>
    
    <!-- Results -->
    <div class="sandbox-output">
      <h4>Output</h4>
      <div class="output-section">
        <strong>stdout:</strong>
        <pre id="sandbox-stdout"></pre>
      </div>
      <div class="output-section">
        <strong>stderr:</strong>
        <pre id="sandbox-stderr"></pre>
      </div>
      <div class="output-meta">
        <span id="sandbox-exitcode"></span>
        <span id="sandbox-time"></span>
      </div>
    </div>
  </div>
</div>
```

#### 3. **Tools Tab**
```html
<div id="tools-tab" class="tab-content">
  <div class="tools-management">
    <h3>MCP Tool Management</h3>
    
    <!-- MCP Status -->
    <div class="mcp-status">
      <h4>MCP Servers</h4>
      <div id="mcp-servers-list"></div>
    </div>
    
    <!-- Tool Discovery -->
    <div class="tool-discovery">
      <h4>Discovered Tools</h4>
      <input type="text" id="tool-search" placeholder="Search tools...">
      <div id="tools-list"></div>
    </div>
    
    <!-- Tool Details -->
    <div class="tool-details">
      <h4>Tool Details</h4>
      <div id="tool-info">
        <p>Select a tool to view details</p>
      </div>
    </div>
    
    <!-- Tool Testing -->
    <div class="tool-testing">
      <h4>Test Tool</h4>
      <textarea id="tool-args" placeholder='{"arg1": "value1"}'></textarea>
      <button id="test-tool">Execute Tool</button>
      <pre id="tool-result"></pre>
    </div>
  </div>
</div>
```

## JavaScript Functions to Add

### Swarm System
```javascript
// Execute swarm task
async function executeSwarmTask(task, verbose = true) {
  const response = await fetch('/api/swarm/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task, verbose})
  });
  return await response.json();
}

// Load agent capabilities
async function loadAgentCapabilities() {
  const response = await fetch('/api/swarm/capabilities');
  const data = await response.json();
  displayAgentCapabilities(data.capabilities);
}

// Display delegation plan
function displayDelegationPlan(plan) {
  const planDiv = document.getElementById('plan-display');
  planDiv.innerHTML = Object.entries(plan)
    .map(([agent, task]) => `
      <div class="plan-item">
        <strong>${agent}:</strong> ${task}
      </div>
    `).join('');
}
```

### Sandbox System
```javascript
// Execute code in sandbox
async function executeSandboxCode(code, language, timeout) {
  const response = await fetch('/api/sandbox/run', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code, language, timeout})
  });
  return await response.json();
}

// Display sandbox results
function displaySandboxResults(result) {
  document.getElementById('sandbox-stdout').textContent = result.stdout;
  document.getElementById('sandbox-stderr').textContent = result.stderr;
  document.getElementById('sandbox-exitcode').textContent = 
    `Exit Code: ${result.exit_code}`;
  document.getElementById('sandbox-time').textContent = 
    `Time: ${result.execution_time.toFixed(3)}s`;
}

// Get sandbox status
async function loadSandboxStatus() {
  const response = await fetch('/api/sandbox/status');
  return await response.json();
}
```

### MCP Tools
```javascript
// Load MCP servers
async function loadMCPServers() {
  const response = await fetch('/api/mcp/status');
  const data = await response.json();
  displayMCPServers(data);
}

// Display tools list
function displayToolsList(tools) {
  const toolsList = document.getElementById('tools-list');
  toolsList.innerHTML = tools.map(tool => `
    <div class="tool-item" onclick="showToolDetails('${tool.name}')">
      <strong>${tool.name}</strong>
      <p>${tool.description}</p>
    </div>
  `).join('');
}

// Show tool details
function showToolDetails(toolName) {
  // Fetch and display tool details
}
```

## CSS Styling

```css
/* Swarm Tab Styles */
.agent-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc;
}

.status-indicator.active {
  background: #4caf50;
  box-shadow: 0 0 8px #4caf50;
}

.delegation-plan {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

/* Sandbox Tab Styles */
.code-editor-container {
  margin: 15px 0;
}

.code-editor-container textarea {
  width: 100%;
  height: 300px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.sandbox-output {
  margin-top: 20px;
  padding: 15px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 8px;
}

.sandbox-output pre {
  margin: 10px 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Tools Tab Styles */
.tool-item {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin: 8px 0;
  cursor: pointer;
  transition: background 0.2s;
}

.tool-item:hover {
  background: #f0f0f0;
}

.tool-details {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}
```

## Implementation Steps

1. **Phase 1: Update HTML Structure**
   - Add new tabs to navigation
   - Create tab content containers
   - Add necessary form controls

2. **Phase 2: Implement JavaScript Functions**
   - Add API call functions
   - Implement display functions
   - Add event listeners

3. **Phase 3: Style Components**
   - Add CSS for new components
   - Ensure responsive design
   - Match existing theme

4. **Phase 4: Integration**
   - Connect to backend APIs
   - Test all functionality
   - Handle error cases

5. **Phase 5: Documentation**
   - Update user guide
   - Add usage examples
   - Create screenshots

## Files to Modify

- `frontend/index.html` - Add new tabs and components
- `frontend/index.html` (inline styles) - Add CSS
- `frontend/index.html` (inline scripts) - Add JavaScript

## Testing Checklist

- [ ] Swarm task execution works
- [ ] Agent status displays correctly
- [ ] Sandbox code execution works
- [ ] Multi-language support works
- [ ] MCP tools list loads
- [ ] Tool details display correctly
- [ ] All APIs respond correctly
- [ ] Error handling works
- [ ] UI is responsive
- [ ] Works on mobile devices

## Timeline Estimate

- HTML Structure: 2-3 hours
- JavaScript Implementation: 3-4 hours
- CSS Styling: 2-3 hours
- Testing & Refinement: 2-3 hours
- **Total: 10-13 hours**

## Success Criteria

✅ All new features accessible from web UI  
✅ Seamless integration with existing interface  
✅ Responsive and mobile-friendly  
✅ Comprehensive error handling  
✅ User-friendly and intuitive  
✅ Well-documented  

---

**Status**: Ready for implementation  
**Priority**: High (per user requirement)  
**Dependencies**: All backend features complete ✅