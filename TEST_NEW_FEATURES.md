# Testing Guide - New Frontend Features

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Python 3.9+ installed
# 2. Node.js (for frontend server)
# 3. All dependencies installed

cd /path/to/antigravity-workspace-template
pip install -r requirements.txt
```

### Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 3000

# Or use any static server:
# npx serve -s . -p 3000
```

**Open Browser:**
```
http://localhost:3000
```

---

## ✅ Test Checklist

### 🐝 Swarm Tab Tests

#### Basic Functionality
- [ ] **Navigate to tab**: Click "🐝 Swarm" - tab activates without errors
- [ ] **UI loads**: All sections visible (task input, agents, plan, results)
- [ ] **Agent cards**: 4 agent cards display with green status indicators

#### Task Execution
- [ ] **Simple task**:
  ```
  Task: "Hello world"
  Expected: Delegation plan + results appear
  ```

- [ ] **Complex task**:
  ```
  Task: "Create a REST API for todo items with CRUD operations"
  Expected: 
    - Delegation plan shows multiple agents
    - Each agent completes subtask
    - Final result synthesizes outputs
  ```

- [ ] **Error handling**:
  ```
  Task: (empty)
  Expected: Alert "Please enter a task"
  ```

#### Loading States
- [ ] Button shows "⏳ Executing..." during execution
- [ ] Button disabled during execution
- [ ] Button returns to normal after completion

#### Results Display
- [ ] Delegation plan appears in collapsible panel
- [ ] Each agent's result shows in separate card
- [ ] Success/error status badges display correctly
- [ ] JSON results are formatted and readable

---

### 🏖️ Sandbox Tab Tests

#### Basic Functionality
- [ ] **Navigate to tab**: Click "🏖️ Sandbox" - tab activates
- [ ] **UI loads**: Editor, controls, and output panel visible
- [ ] **Language selector**: Can switch between Python/JS/Bash

#### Python Execution
- [ ] **Simple print**:
  ```python
  print("Hello World")
  
  Expected stdout: "Hello World"
  Exit code: 0
  ```

- [ ] **Variables and loops**:
  ```python
  for i in range(5):
      print(f"Count: {i}")
  
  Expected: 5 lines of output
  Exit code: 0
  ```

- [ ] **Error handling**:
  ```python
  print(undefined_variable)
  
  Expected stderr: NameError message
  Exit code: 1
  Status: Failed
  ```

#### JavaScript Execution
- [ ] **Console output**:
  ```javascript
  console.log("Hello from JS");
  for (let i = 0; i < 3; i++) {
      console.log(`Count: ${i}`);
  }
  
  Expected: 4 lines in stdout
  ```

- [ ] **Error handling**:
  ```javascript
  throw new Error("Test error");
  
  Expected: Error message in stderr
  ```

#### Bash Execution
- [ ] **Simple commands**:
  ```bash
  echo "Hello from Bash"
  pwd
  ls -la
  
  Expected: Command outputs
  ```

#### Controls
- [ ] **Timeout field**: Accepts numbers 1-300
- [ ] **Clear button**: Empties editor and output
- [ ] **Sandbox type**: Local/Docker selector works

#### Output Display
- [ ] stdout shows in green
- [ ] stderr shows in red
- [ ] Exit code displays correctly
- [ ] Execution time shows in seconds
- [ ] Long output scrolls properly

---

### 🔧 Tools Tab Tests

#### MCP Servers
- [ ] **Server cards load**: Multiple servers display on tab activation
- [ ] **Status indicators**: Running servers show green, stopped show gray
- [ ] **Tool counts**: Each server shows tool count
- [ ] **Refresh button**: Reloads server status

#### Tool Discovery
- [ ] **Tools list loads**: All tools from all servers display
- [ ] **Tool count**: Matches sum of server tool counts
- [ ] **Tool details**: Each tool shows name, server, description

#### Search Functionality
- [ ] **Search by name**: 
  ```
  Search: "read"
  Expected: Only "read_file", "read_*" tools shown
  ```

- [ ] **Search by description**:
  ```
  Search: "filesystem"
  Expected: All filesystem-related tools
  ```

- [ ] **Clear search**: Empty search shows all tools

#### Tool Selection
- [ ] **Click tool**: Tool highlights, details panel appears
- [ ] **Tool name**: Displays in details section
- [ ] **Description**: Shows full description
- [ ] **Schema**: Input schema renders as formatted JSON
- [ ] **Server badge**: Shows which server provides tool

#### Tool Testing

**Test 1: Read File (filesystem)**
```json
{
  "path": "/home/runner/work/antigravity-workspace-template/README.md"
}

Expected: File contents in result
```

**Test 2: Git Status (git)**
```json
{}

Expected: Git status output
```

**Test 3: Invalid Arguments**
```json
{
  "invalid_field": "test"
}

Expected: Error message explaining invalid schema
```

#### Auto-Generated Examples
- [ ] Selecting tool populates test input
- [ ] Example matches schema structure
- [ ] All required fields present
- [ ] Optional fields included

#### Results Display
- [ ] Results show formatted JSON
- [ ] Long results scroll properly
- [ ] Errors display clearly
- [ ] Success results show full data

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch"
**Cause**: Backend not running  
**Solution**: 
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Issue: "CORS error"
**Cause**: Frontend/backend on different domains  
**Solution**: Check `backend/main.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "No MCP servers found"
**Cause**: MCP servers not configured  
**Solution**: Check `mcp_servers.json` exists and is valid

### Issue: "Sandbox execution fails"
**Cause**: Sandbox not configured  
**Solution**: 
- Check Python/Node.js installed
- Verify execute permissions
- Check timeout settings

### Issue: "Swarm task hangs"
**Cause**: Long-running task or agent timeout  
**Solution**: 
- Wait longer (complex tasks take time)
- Check backend logs
- Try simpler task first

---

## 📊 Performance Tests

### Load Testing
```bash
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

### Response Times
- Swarm execution: 5-30 seconds (task dependent)
- Sandbox execution: 0.1-5 seconds (code dependent)
- MCP tool discovery: < 1 second
- MCP tool execution: 0.1-2 seconds

---

## 🔍 Browser Console Checks

### No Errors
Open browser console (F12), check for:
- ❌ No JavaScript errors
- ❌ No 404 (file not found) errors
- ❌ No CORS errors
- ✅ Only info/debug messages

### Expected Messages
```
[INFO] WebSocket connected
[INFO] Swarm capabilities loaded
[INFO] Tools loaded: 42 tools from 6 servers
```

---

## 📱 Mobile Testing

### Responsive Layout
1. Open browser dev tools (F12)
2. Toggle device toolbar (mobile view)
3. Test each tab:
   - [ ] Layout adapts to mobile
   - [ ] Text is readable
   - [ ] Buttons are tappable
   - [ ] No horizontal scroll
   - [ ] Content fits screen

### Touch Interactions
- [ ] Tabs switch with tap
- [ ] Buttons respond to touch
- [ ] Scrolling works smoothly
- [ ] Text inputs open keyboard

---

## 🎨 Visual Regression Tests

### Dark Theme
- [ ] All backgrounds are dark (#0f172a, #1e293b)
- [ ] Text is light and readable
- [ ] Accent colors (blue, green, purple) visible
- [ ] No white flashes or backgrounds

### Consistent Styling
- [ ] All buttons use same style
- [ ] Cards have consistent borders and shadows
- [ ] Spacing is uniform
- [ ] Fonts match existing tabs

### Animations
- [ ] Hover effects work smoothly
- [ ] Loading spinners rotate
- [ ] Status indicators pulse
- [ ] Tab transitions are smooth

---

## ✅ Acceptance Criteria

Before marking as complete, verify:

### Functionality
- ✅ All tabs load without errors
- ✅ All API calls succeed
- ✅ Error handling works
- ✅ Loading states display correctly
- ✅ Results format properly

### UI/UX
- ✅ Consistent with existing design
- ✅ Responsive on mobile
- ✅ No visual glitches
- ✅ Smooth animations
- ✅ Clear user feedback

### Code Quality
- ✅ No console errors
- ✅ No memory leaks
- ✅ Efficient rendering
- ✅ Clean code structure

### Documentation
- ✅ Inline comments present
- ✅ Function purposes clear
- ✅ API endpoints documented
- ✅ Usage examples provided

---

## 🚀 Production Readiness

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] No TODO or FIXME comments
- [ ] Error handling comprehensive
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Documentation updated

### Monitoring
After deployment, monitor:
- Response times
- Error rates
- Usage patterns
- User feedback

---

## 📞 Support

**Issues?**
1. Check this guide first
2. Review browser console
3. Check backend logs
4. Test with curl
5. Read FRONTEND_INTEGRATION_COMPLETE.md

**Need Help?**
- GitHub Issues: [repo]/issues
- Documentation: See docs/ folder
- Quick Reference: FRONTEND_QUICK_REFERENCE.md

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Ready for Testing ✅
