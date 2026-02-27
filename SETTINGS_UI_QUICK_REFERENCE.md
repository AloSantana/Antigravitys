# Settings UI Enhancement - Quick Reference

## 🚀 Quick Start

### Running the Test Suite
```bash
./test-settings-ui.sh
```

### Manual Testing
1. Start backend: `./start.sh`
2. Open frontend: `http://localhost:3000`
3. Navigate to Settings tab
4. Test new features

---

## 📡 API Endpoints

### Get Models
```bash
curl http://localhost:8000/settings/models
```
**Response:**
```json
{
  "success": true,
  "models": [...],
  "active_model": "gemini"
}
```

### Set Active Model
```bash
curl -X POST "http://localhost:8000/settings/models?model_id=gemini"
```
**Response:**
```json
{
  "success": true,
  "message": "Active model set to gemini"
}
```

### Reload Environment
```bash
curl -X POST http://localhost:8000/settings/reload-env
```
**Response:**
```json
{
  "success": true,
  "environment_reload": {
    "reloaded": true,
    "changes": ["ACTIVE_MODEL changed from auto to gemini"]
  },
  "orchestrator_reinitialized": true
}
```

### Ngrok Status
```bash
curl http://localhost:8000/ngrok/status
```
**Response:**
```json
{
  "active": true,
  "public_url": "https://xyz.ngrok.io",
  "ws_url": "wss://xyz.ngrok.io/ws"
}
```

---

## 🎨 UI Components

### 1. Live Status Banner
**Element ID**: `liveStatusBanner`
**Auto-refresh**: Every 5 seconds
**Function**: `updateLiveStatusBanner()`

**Sub-elements**:
- `statusActiveModel` - Current active model
- `statusNgrokUrl` - Ngrok public URL
- `statusBackendHealth` - Backend health status

### 2. Model Selection
**Container**: `model-selection-group`
**Function**: `selectModel(modelValue)`

**Radio Options**:
- `gemini` - Google Gemini AI
- `vertex` - Vertex AI (Enterprise)
- `ollama` - Ollama (Local)
- `auto` - Auto-select based on complexity

### 3. Reload Environment Button
**Function**: `reloadEnvironment()`
**Status Element**: `reloadEnvStatus`

### 4. Ngrok Tunnel Section
**Container**: `ngrokStatusContainer`
**Function**: `refreshNgrokStatus()`

**Elements**:
- `ngrokStatusBadge` - Status indicator
- `ngrokPublicUrl` - Public URL input
- `ngrokWsUrl` - WebSocket URL input

---

## 🔧 JavaScript Functions

### Model Selection
```javascript
// Select a model
selectModel('gemini');

// Load current active model
await loadActiveModel();
```

### Environment Management
```javascript
// Reload environment
await reloadEnvironment();
```

### Status Updates
```javascript
// Update live status banner
await updateLiveStatusBanner();

// Refresh ngrok status
await refreshNgrokStatus();
```

### Auto-refresh Control
```javascript
// Start auto-refresh (5-second interval)
startLiveStatusRefresh();

// Stop auto-refresh
stopLiveStatusRefresh();
```

### Utilities
```javascript
// Copy to clipboard
copyToClipboard('ngrokPublicUrl');
```

---

## 🎯 CSS Classes

### Status Banners
```css
.live-status-banner        /* Main banner container */
.status-banner-item        /* Individual status item */
.status-banner-label       /* Label styling */
.status-banner-value       /* Value styling */
```

### Model Selection
```css
.model-selection-section   /* Container */
.model-selection-group     /* Grid layout */
.model-radio-option        /* Radio wrapper */
.model-radio-content       /* Card content */
.model-radio-icon          /* Icon display */
.model-radio-label         /* Model name */
.model-radio-desc          /* Description */
```

### Status Indicators
```css
.status-indicator          /* Base class */
.status-connected          /* Green (success) */
.status-disconnected       /* Red (error) */
.status-warning            /* Yellow (warning) */
```

---

## 📝 Common Tasks

### Change Active Model
```javascript
// Via JavaScript
selectModel('gemini');

// Via HTML
<input type="radio" name="activeModel" value="gemini" onchange="selectModel('gemini')">
```

### Get Current Status
```javascript
// Get all status info
await updateLiveStatusBanner();

// Check specific status
const response = await fetch(`${API_BASE}/settings/models`);
const data = await response.json();
console.log('Active model:', data.active_model);
```

### Handle Environment Changes
```javascript
// After changing .env file
await reloadEnvironment();

// This will:
// 1. Reload all environment variables
// 2. Reinitialize orchestrator
// 3. Update UI
// 4. Show what changed
```

---

## 🐛 Debugging

### Check Console
```javascript
// Enable debug logging
localStorage.setItem('debug', 'true');

// View network requests
// Open DevTools -> Network tab
// Filter by "settings" or "ngrok"
```

### Test Endpoints Manually
```bash
# Health check
curl http://localhost:8000/health

# Get models
curl http://localhost:8000/settings/models

# Test connection
curl -X POST http://localhost:8000/settings/test-connection/gemini
```

### Verify HTML Changes
```bash
# Check for new elements
grep -n "live-status-banner" frontend/index.html
grep -n "model-selection-group" frontend/index.html
grep -n "reloadEnvironment" frontend/index.html
grep -n "ngrokStatusContainer" frontend/index.html
```

---

## ⚡ Performance Tips

### Auto-refresh Lifecycle
- Starts when Settings tab opens
- Pauses when switching away
- Resumes when returning
- Interval: 5 seconds

### Optimizations
```javascript
// Batch API calls
Promise.all([
    fetch(`${API_BASE}/settings/models`),
    fetch(`${API_BASE}/ngrok/status`),
    fetch(`${API_BASE}/health`)
]).then(/* handle responses */);

// Debounce rapid changes
let debounceTimer;
function debouncedReload() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(reloadEnvironment, 300);
}
```

---

## 🔒 Security Notes

### API Keys
- Never log API keys to console
- Clear input fields after saving
- Use password type for sensitive inputs
- Server-side validation required

### CORS
- Ensure proper CORS configuration
- Frontend and backend must match
- Check `allowed_origins` in settings

---

## 🎨 Customization

### Change Refresh Interval
```javascript
// In startLiveStatusRefresh()
liveStatusInterval = setInterval(() => {
    updateLiveStatusBanner();
}, 10000); // 10 seconds instead of 5
```

### Add New Status Items
```html
<!-- In live-status-banner -->
<div class="status-banner-item">
    <span class="status-banner-label">🔥 New Status:</span>
    <span class="status-banner-value" id="statusNewItem">Value</span>
</div>
```

```javascript
// In updateLiveStatusBanner()
document.getElementById('statusNewItem').textContent = 'New Value';
```

### Customize Model Options
```html
<!-- Add new model option -->
<label class="model-radio-option">
    <input type="radio" name="activeModel" value="newmodel" onchange="selectModel('newmodel')">
    <div class="model-radio-content">
        <div class="model-radio-icon">🚀</div>
        <div class="model-radio-label">New Model</div>
        <div class="model-radio-desc">Description</div>
    </div>
</label>
```

---

## 📚 Related Files

- `frontend/index.html` - All UI code
- `backend/main.py` - API endpoints
- `SETTINGS_UI_ENHANCEMENT.md` - Full documentation
- `test-settings-ui.sh` - Test suite

---

## 🚨 Troubleshooting

### Issue: Status banner not updating
**Solution**: Check console for errors, verify auto-refresh is running

### Issue: Model selection not working
**Solution**: Verify backend endpoint, check network tab, ensure model exists

### Issue: Reload environment fails
**Solution**: Check .env file permissions, verify backend logs

### Issue: Ngrok status shows error
**Solution**: Ensure ngrok is running, check ngrok configuration

### Issue: Copy to clipboard not working
**Solution**: Browser must be on HTTPS or localhost, check permissions

---

## ✅ Testing Checklist

- [ ] Run `./test-settings-ui.sh`
- [ ] Test each model selection
- [ ] Click reload environment button
- [ ] Verify live status updates
- [ ] Test ngrok status display
- [ ] Try copy to clipboard
- [ ] Switch between tabs
- [ ] Check auto-refresh behavior
- [ ] Test error states
- [ ] Verify mobile responsiveness

---

## 📞 Support

For issues:
1. Check browser console
2. Review network requests
3. Check backend logs
4. Verify environment variables
5. Test endpoints with curl

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready
