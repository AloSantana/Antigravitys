# ⚙️ Phase 2 Quick Reference Card

## 🚀 Quick Start

### Access Settings UI
```
1. Start backend: cd backend && uvicorn main:app --reload
2. Open browser: http://localhost:8000
3. Click: ⚙️ Settings tab
```

---

## 📡 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/settings` | GET | Get all settings |
| `/settings` | POST | Update settings |
| `/settings/models` | GET | List AI models |
| `/settings/models?model_id={id}` | POST | Set active model |
| `/settings/mcp` | GET | List MCP servers |
| `/settings/mcp/{server}` | POST | Toggle server |
| `/settings/api-keys` | POST | Update API key |
| `/settings/validate` | POST | Validate key |
| `/settings/env` | GET | List env vars |
| `/settings/env` | POST | Update env var |
| `/settings/export` | GET | Export config |
| `/settings/test-connection/{service}` | POST | Test service |

---

## 🎨 UI Sections

1. **🤖 AI Model Configuration** - View/switch models, test connections
2. **🔑 API Keys Management** - Add/update API keys securely
3. **🔌 MCP Server Manager** - Enable/disable MCP servers
4. **🖥️ Server Configuration** - Host, ports, CORS settings
5. **📝 Environment Variables** - Edit non-sensitive vars
6. **📦 Configuration Export** - Download config as JSON

---

## 🔧 Common Tasks

### Add Gemini API Key
```javascript
// In UI: API Keys Management section
1. Enter key in "Gemini API Key" field
2. Click "💾 Save"
3. Wait for confirmation

// Via API
POST /settings/api-keys
{
  "key_var": "GEMINI_API_KEY",
  "value": "AIzaSyYourKeyHere"
}
```

### Switch to Ollama
```javascript
// In UI: AI Model Configuration section
1. Click on "Ollama (Local)" card
2. Card turns green with "● ACTIVE"

// Via API
POST /settings/models?model_id=ollama
```

### Enable GitHub MCP Server
```javascript
// In UI: MCP Server Manager section
1. Find "github" server
2. Click toggle switch (turns green)

// Via API
POST /settings/mcp/github
{
  "enabled": true
}
```

### Test Gemini Connection
```javascript
// In UI: AI Model Configuration section
1. Click "Test Gemini" button
2. See status: ✓ Success or ✗ Error

// Via API
POST /settings/test-connection/gemini
```

### Export Configuration
```javascript
// In UI: Configuration Export section
1. Click "📥 Export Configuration"
2. JSON file downloads automatically

// Via API
GET /settings/export
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/test_settings_api.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_settings_api.py::TestSettingsEndpoints -v
```

### Run With Coverage
```bash
pytest tests/test_settings_api.py --cov=backend --cov-report=html
```

---

## 🔒 Security Notes

### Protected Variables
Cannot be edited via env editor (use API key management):
- `GEMINI_API_KEY`
- `VERTEX_API_KEY`
- `COPILOT_MCP_GITHUB_TOKEN`
- `DATABASE_URL`
- `SECRET_KEY`

### Key Storage
- Encrypted with Fernet (symmetric)
- Encryption key: `.encryption_key` file (0600 permissions)
- Keys redacted in UI: `AIza...1234`

### Validation
- Backend: Pydantic models + custom validators
- Frontend: Client-side validation before submit
- Format checks: Gemini (starts with "AIza"), GitHub (starts with "ghp_")

---

## 📁 File Locations

### Backend
```
backend/
├── settings_manager.py    # Core settings logic (633 lines)
├── main.py               # API endpoints (364 lines added)
└── requirements.txt      # Dependencies (updated)
```

### Frontend
```
frontend/
└── index.html           # Settings UI (1,107 lines added)
```

### Tests
```
tests/
└── test_settings_api.py # Test suite (558 lines, 37 tests)
```

### Documentation
```
├── PHASE2_SETTINGS_COMPLETE.md        # Full documentation
├── PHASE2_IMPLEMENTATION_SUMMARY.md   # Implementation summary
└── PHASE2_QUICK_REFERENCE.md         # This file
```

---

## 🐛 Troubleshooting

### Settings Not Loading
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS
# Ensure ALLOWED_ORIGINS includes your frontend URL

# Check browser console
# Open DevTools > Console tab
```

### API Key Save Fails
```bash
# Verify key format
# Gemini: AIzaSy...
# GitHub: ghp_... or github_pat_...

# Check key length
# Must be at least 10 characters

# Verify backend logs
# Look for validation errors
```

### MCP Server Shows "Missing Credentials"
```bash
# Add required API key
# Example for GitHub:
# 1. Go to API Keys Management
# 2. Add COPILOT_MCP_GITHUB_TOKEN
# 3. Refresh MCP server list
```

### Connection Test Fails
```bash
# Ollama
# Ensure Ollama is running: ollama serve

# Gemini/Vertex
# Verify API key is correct
# Check internet connection
```

---

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Ctrl/Cmd + K` - Focus search (if implemented)
- `Esc` - Close modals/prompts

### Best Practices
1. **Always test connections** after adding keys
2. **Export config regularly** for backup
3. **Use strong API keys** from official sources
4. **Restart server** after major config changes
5. **Check browser console** for detailed errors

### Performance
- Settings load automatically on first visit
- Use "🔄 Refresh" sparingly (auto-refresh not needed)
- Export config is lightweight (no sensitive data)

---

## 📊 Status Indicators

### Colors
- 🟢 **Green** - Success, Ready, Enabled
- 🔴 **Red** - Error, Disabled, Not Configured
- 🟡 **Yellow** - Warning, Missing Credentials

### Badges
- **✓ Configured** - Model/server is set up
- **✗ Not Configured** - Needs API key
- **● Ready** - MCP server ready to use
- **⚠ Missing Credentials** - Add required keys
- **● ACTIVE** - Currently selected model

---

## 🔗 Related Endpoints

### Health Check
```bash
GET /health
# Returns backend status
```

### Agent Stats
```bash
GET /agent/stats
# Returns AI provider status
```

### File Structure
```bash
GET /files
# Returns project file tree
```

---

## 📞 Support

### Check Logs
```bash
# Backend logs
# Terminal running uvicorn

# Frontend logs
# Browser DevTools > Console
```

### Documentation
- **Full Guide**: `PHASE2_SETTINGS_COMPLETE.md`
- **Implementation**: `PHASE2_IMPLEMENTATION_SUMMARY.md`
- **This Reference**: `PHASE2_QUICK_REFERENCE.md`

### Testing
```bash
# Validate implementation
bash validate-phase2.sh

# Run tests
pytest tests/test_settings_api.py -v
```

---

## ✅ Checklist

### Initial Setup
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend running (`uvicorn main:app --reload`)
- [ ] Frontend accessible (`http://localhost:8000`)
- [ ] Settings tab visible

### Configuration
- [ ] Gemini API key added (if using Gemini)
- [ ] Vertex API key added (if using Vertex)
- [ ] GitHub token added (if using GitHub MCP)
- [ ] Active model selected
- [ ] Connection tested

### Verification
- [ ] All settings load without errors
- [ ] MCP servers show correct status
- [ ] Environment variables visible
- [ ] Export works

---

## 🎯 Quick Examples

### Example 1: Complete Gemini Setup
```bash
1. Add API key in UI
2. Click "Test Gemini" → ✓ Success
3. Click Gemini model card → ● ACTIVE
4. Start using!
```

### Example 2: Enable All MCP Servers
```bash
1. Add GitHub token (if needed)
2. Go to MCP Server Manager
3. Toggle each server → All green
4. Click "🔄 Refresh"
```

### Example 3: Configure Remote Access
```bash
1. Go to Server Configuration
2. Set CORS origins: http://your-ip:3000,http://your-ip:8000
3. Click "💾 Apply Changes"
4. Restart server
```

---

**Phase 2 Quick Reference - Version 2.0.0**  
**For detailed documentation, see `PHASE2_SETTINGS_COMPLETE.md`**
