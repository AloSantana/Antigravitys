# ⚙️ Settings GUI - Complete Guide

**Visual configuration management for Antigravity Workspace**

The Settings GUI provides a user-friendly interface to configure all aspects of your Antigravity workspace without editing configuration files manually.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Accessing Settings](#accessing-settings)
3. [AI Model Configuration](#ai-model-configuration)
4. [API Keys Management](#api-keys-management)
5. [MCP Server Manager](#mcp-server-manager)
6. [Server Configuration](#server-configuration)
7. [Environment Variables Editor](#environment-variables-editor)
8. [Configuration Export](#configuration-export)
9. [Security Features](#security-features)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### Features

- **🤖 AI Model Configuration**: Switch between Gemini, Vertex AI, and Ollama
- **🔑 API Keys Management**: Secure encrypted storage with visibility toggle
- **🔌 MCP Server Manager**: Enable/disable servers with real-time status
- **🖥️ Server Configuration**: Host, port, CORS settings
- **📝 Environment Variables**: Visual editor for non-sensitive variables
- **📦 Configuration Export**: One-click JSON export (sanitized)

### Benefits

- ✅ **No Terminal Required**: Configure everything via web interface
- ✅ **Real-Time Validation**: Test API keys and connections instantly
- ✅ **Secure Storage**: API keys encrypted with Fernet encryption
- ✅ **Visual Feedback**: Color-coded status indicators
- ✅ **Undo Changes**: Reset to previous configuration
- ✅ **Export/Share**: Download sanitized config for team sharing

---

## Accessing Settings

### Step 1: Start the Application

```bash
./start.sh
```

### Step 2: Open Web Interface

Open your browser:
```
http://localhost:8000
```

### Step 3: Navigate to Settings

Click the **⚙️ Settings** tab in the top navigation bar.

You'll see six main sections:
1. AI Model Configuration
2. API Keys Management
3. MCP Server Manager
4. Server Configuration
5. Environment Variables
6. Configuration Export

---

## AI Model Configuration

### Overview

Manage your AI model providers:
- **Gemini AI**: Google's Gemini Pro (free tier available)
- **Vertex AI**: Enterprise-grade Gemini via GCP
- **Ollama**: Local open-source models (runs on your machine)

### Features

- **Model Cards**: Visual display of available models
- **Status Indicators**: 
  - ✓ Configured (green) - Ready to use
  - ⚠ Missing Creds (yellow) - Needs API key
  - ✗ Not Configured (red) - Not set up
- **Active Model**: Highlighted with blue border
- **Quick Switch**: Click any card to set as active
- **Connection Testing**: Test button for each provider

### Usage

#### 1. View Available Models

The section displays three model cards:

```
┌─────────────────────────────────┐
│ 🤖 Gemini AI                    │
│ Status: ✓ Configured            │
│ Model: gemini-pro               │
│ [ACTIVE]                        │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🏢 Vertex AI                    │
│ Status: ⚠ Missing Credentials  │
│ Model: gemini-pro (via GCP)    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🦙 Ollama                       │
│ Status: ✓ Ready                 │
│ Model: llama3                   │
└─────────────────────────────────┘
```

#### 2. Set Active Model

Click on any model card to set it as the active model.

The active model:
- Shows **[ACTIVE]** badge
- Has a blue highlight border
- Will be used for all AI requests

#### 3. Test Connections

Click the test buttons below the cards:
- **Test Gemini**: Sends test request to Gemini API
- **Test Vertex**: Sends test request to Vertex AI
- **Test Ollama**: Checks Ollama local service

**Success**: Green checkmark with "Connection successful"
**Failure**: Red X with error message

### API Endpoints

```bash
# Get available models
curl http://localhost:8000/settings/models

# Set active model
curl -X POST http://localhost:8000/settings/models \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini"}'

# Test connection
curl -X POST http://localhost:8000/settings/test-connection/gemini
```

---

## API Keys Management

### Overview

Securely manage API keys for various services:
- Gemini AI API Key
- Vertex AI API Key
- GitHub Personal Access Token
- And more...

### Security Features

- **🔒 Fernet Encryption**: All API keys encrypted at rest
- **👁️ Toggle Visibility**: Show/hide sensitive values
- **🔐 Redacted Display**: Shows only partial key (e.g., `AIza...1234`)
- **✅ Format Validation**: Checks key format before saving
- **🚫 Protected Variables**: Sensitive vars can't be edited via env editor

### Usage

#### 1. Enter API Keys

Each service has its own input section:

```
┌────────────────────────────────────────┐
│ Gemini AI API Key                      │
│ [••••••••••••••••••] [👁️] [💾 Save]  │
│ Get your key: https://aistudio...     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GitHub Token (for GitHub MCP)          │
│ [••••••••••••••••••] [👁️] [💾 Save]  │
│ Required scopes: repo, read:org       │
└────────────────────────────────────────┘
```

#### 2. Toggle Visibility

Click the **👁️** button to show/hide the API key.

- **Hidden**: Shows `••••••••••••••••••`
- **Visible**: Shows full key: `AIzaSyYourActualKey123456789`

#### 3. Save API Key

1. Enter or paste your API key
2. Click **💾 Save** button
3. Wait for confirmation message

**Success**: "API key saved successfully" (green)
**Failure**: "Failed to save API key" (red) with error details

#### 4. Validation

The system validates API keys:
- **Gemini**: Must start with `AIza`
- **Vertex**: Must be valid GCP key format
- **GitHub**: Must be valid token format (ghp_...)

### Getting API Keys

#### Gemini AI API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza`)
5. Paste into Settings GUI
6. Click Save

#### GitHub Personal Access Token
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`
4. Generate token
5. Copy immediately (shown only once)
6. Paste into Settings GUI
7. Click Save

#### Vertex AI (Enterprise)
1. Visit: https://console.cloud.google.com/
2. Enable Vertex AI API
3. Create service account
4. Download JSON key
5. Extract API key
6. Configure in Settings GUI

### API Endpoints

```bash
# Update API key
curl -X POST http://localhost:8000/settings/api-keys \
  -H "Content-Type: application/json" \
  -d '{"service": "GEMINI_API_KEY", "key": "AIza..."}'

# Validate API key
curl -X POST http://localhost:8000/settings/validate \
  -H "Content-Type: application/json" \
  -d '{"service": "gemini", "key": "AIza..."}'
```

---

## MCP Server Manager

### Overview

Enable/disable and monitor Model Context Protocol (MCP) servers.

MCP servers provide specialized tools to AI agents:
- **filesystem**: File operations
- **git**: Version control
- **github**: GitHub API access
- **docker**: Container management
- **postgres**: Database operations
- And 13+ more...

### Features

- **Real-Time Status**: See which servers are operational
- **Toggle Switches**: Enable/disable servers with one click
- **Credential Indicators**: Shows which servers need API keys
- **Refresh Button**: Update status on demand
- **Server Count**: Total servers and enabled count

### Usage

#### 1. View Server List

The MCP Server Manager displays all available servers:

```
┌─────────────────────────────────────────────┐
│ 🔌 MCP Server Manager    [🔄 Refresh Status]│
├─────────────────────────────────────────────┤
│ filesystem        ● Ready           [ON] ▶  │
│ git               ● Ready           [ON] ▶  │
│ github            ⚠ Missing Creds   [OFF]▶  │
│ memory            ● Ready           [ON] ▶  │
│ sqlite            ● Ready           [ON] ▶  │
│ docker            ● Ready           [ON] ▶  │
│ kubernetes        ● Ready           [OFF]▶  │
│ postgres          ⚠ Missing Creds   [OFF]▶  │
│ brave-search      ⚠ Missing API Key [OFF]▶  │
│ ... (9 more servers)                        │
└─────────────────────────────────────────────┘
```

#### 2. Understand Status Indicators

- **● Ready** (green): Server is configured and operational
- **⚠ Missing Creds** (yellow): Server needs API key or token
- **⚠ Missing API Key** (yellow): Needs API key (e.g., Brave Search)
- **✗ Not Installed** (red): Server not installed (rare)

#### 3. Toggle Servers

Click the toggle switch to enable/disable a server:
- **[ON]**: Server is active and available to agents
- **[OFF]**: Server is disabled

**Note**: Disabling a server doesn't uninstall it, just makes it unavailable to agents.

#### 4. Refresh Status

Click **🔄 Refresh Status** to update all server statuses.

This checks:
- Installation status
- Credential availability
- Connection health

#### 5. Fix Missing Credentials

If a server shows "Missing Creds":
1. Note which credential is needed (e.g., GITHUB_TOKEN)
2. Go to **API Keys Management** section above
3. Enter the required credential
4. Click **💾 Save**
5. Return to MCP Server Manager
6. Click **🔄 Refresh Status**
7. Server should now show **● Ready**

### MCP Server Details

| Server | Purpose | Credentials Needed |
|--------|---------|-------------------|
| filesystem | File operations | None |
| git | Version control | None |
| github | GitHub API | GITHUB_TOKEN |
| memory | State persistence | None |
| sqlite | Database ops | None |
| postgres | PostgreSQL ops | CONNECTION_STRING |
| docker | Container mgmt | None |
| kubernetes | K8s management | None |
| brave-search | Web search | BRAVE_API_KEY |
| puppeteer | Browser automation | None |
| fetch | HTTP requests | None |
| slack | Slack integration | SLACK_TOKEN |
| aws | AWS operations | AWS credentials |
| sentry | Error tracking | SENTRY_DSN |
| gitlab | GitLab API | GITLAB_TOKEN |
| sequential-thinking | Planning | None |
| python-analysis | Code analysis | None |
| time | Time operations | None |

### API Endpoints

```bash
# Get MCP server status
curl http://localhost:8000/settings/mcp

# Toggle MCP server
curl -X POST http://localhost:8000/settings/mcp/github \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## Server Configuration

### Overview

Configure basic server settings:
- **Host**: Network interface to bind to
- **Backend Port**: Port for FastAPI backend
- **Frontend Port**: Port for frontend (if serving separately)
- **CORS Origins**: Allowed origins for cross-origin requests

### Features

- **Visual Inputs**: Text fields for each setting
- **Apply Button**: Save changes to .env file
- **Reset Button**: Restore previous values
- **Validation**: Checks for valid host/port formats

### Usage

#### 1. Configure Host

```
┌────────────────────────────────┐
│ Host                           │
│ [0.0.0.0                    ]  │
│ Use 0.0.0.0 for all interfaces│
│ Use 127.0.0.1 for localhost   │
└────────────────────────────────┘
```

Common values:
- `0.0.0.0`: Listen on all network interfaces (remote access)
- `127.0.0.1`: Listen only on localhost (local access only)
- `10.0.0.5`: Listen on specific IP address

#### 2. Configure Ports

```
┌────────────────────────────────┐
│ Backend Port                   │
│ [8000                       ]  │
└────────────────────────────────┘

┌────────────────────────────────┐
│ Frontend Port                  │
│ [3000                       ]  │
└────────────────────────────────┘
```

Default ports:
- Backend: `8000`
- Frontend: `3000`

**Important**: Avoid ports already in use (check with `sudo lsof -i :<port>`)

#### 3. Configure CORS

```
┌────────────────────────────────────────────┐
│ CORS Allowed Origins (comma-separated)    │
│ [http://localhost:3000,http://localhost:...│
└────────────────────────────────────────────┘
```

Examples:
- Development: `http://localhost:3000,http://localhost:8000`
- Production: `https://yourdomain.com`
- All origins (insecure): `*`

#### 4. Apply Changes

1. Modify any settings
2. Click **💾 Apply** button
3. Settings are saved to `.env` file
4. **Restart required**: Stop and start backend to apply changes

```bash
./stop.sh
./start.sh
```

#### 5. Reset Changes

Click **🔄 Reset** to restore previous values before applying.

### API Endpoints

```bash
# Get current settings
curl http://localhost:8000/settings

# Update settings
curl -X POST http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -d '{
    "host": "0.0.0.0",
    "port": 8000,
    "frontend_port": 3000
  }'
```

---

## Environment Variables Editor

### Overview

Edit non-sensitive environment variables directly in the GUI.

### Features

- **Table View**: All variables in sortable table
- **Inline Editing**: Click to edit values
- **Protected Variables**: API keys can't be edited here (use API Keys section)
- **Reload Button**: Refresh from .env file
- **Auto-Save**: Changes saved immediately

### Usage

#### 1. View Variables

```
┌─────────────────────────────────────────────────┐
│ 📝 Environment Variables    [🔄 Reload]        │
├──────────────────┬──────────────────┬───────────┤
│ Variable         │ Value            │ Actions   │
├──────────────────┼──────────────────┼───────────┤
│ DEBUG_MODE       │ false            │ [Edit]    │
│ LOG_LEVEL        │ INFO             │ [Edit]    │
│ MAX_CONNECTIONS  │ 100              │ [Edit]    │
│ TIMEOUT          │ 30               │ [Edit]    │
└──────────────────┴──────────────────┴───────────┘
```

#### 2. Edit Variable

1. Click **[Edit]** button next to variable
2. Input field appears
3. Modify value
4. Press **Enter** or click outside to save
5. **Esc** to cancel

#### 3. Protected Variables

These variables are **protected** and cannot be edited here:
- `GEMINI_API_KEY`
- `VERTEX_API_KEY`
- `GITHUB_TOKEN`
- `COPILOT_MCP_GITHUB_TOKEN`
- `BRAVE_API_KEY`
- Any variable ending in `_KEY`, `_TOKEN`, `_SECRET`, or `_PASSWORD`

Use the **API Keys Management** section to edit these.

#### 4. Reload from File

Click **🔄 Reload** to refresh variables from `.env` file.

This is useful if you edited `.env` manually and want to see changes.

### Safe Variables to Edit

- `DEBUG_MODE`: Enable debug logging
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `MAX_CONNECTIONS`: Maximum concurrent connections
- `TIMEOUT`: Request timeout in seconds
- `CACHE_SIZE`: Cache size limit
- `RATE_LIMIT`: Requests per minute
- Any custom application settings

### API Endpoints

```bash
# Get environment variables (non-sensitive)
curl http://localhost:8000/settings/env

# Update environment variable
curl -X POST http://localhost:8000/settings/env \
  -H "Content-Type: application/json" \
  -d '{
    "key": "DEBUG_MODE",
    "value": "true"
  }'
```

---

## Configuration Export

### Overview

Export your configuration as JSON for:
- **Backup**: Save current configuration
- **Sharing**: Share config with team members
- **Migration**: Move to another server
- **Documentation**: Record configuration state

### Features

- **One-Click Export**: Download instantly
- **Sanitized Output**: API keys redacted
- **Timestamped Filename**: `antigravity-config-YYYY-MM-DD.json`
- **Pretty JSON**: Human-readable formatting

### Usage

#### 1. Export Configuration

Click **📥 Export Configuration** button.

A file will download: `antigravity-config-2024-02-07.json`

#### 2. Export Contents

```json
{
  "timestamp": "2024-02-07T14:30:00Z",
  "version": "2.0.0",
  "settings": {
    "host": "0.0.0.0",
    "port": 8000,
    "frontend_port": 3000,
    "cors_origins": ["http://localhost:3000"],
    "active_model": "gemini"
  },
  "mcp_servers": {
    "filesystem": {"enabled": true, "status": "ready"},
    "git": {"enabled": true, "status": "ready"},
    "github": {"enabled": false, "status": "missing_creds"}
  },
  "environment": {
    "DEBUG_MODE": "false",
    "LOG_LEVEL": "INFO",
    "MAX_CONNECTIONS": "100"
  },
  "api_keys": {
    "gemini": "configured",
    "vertex": "not_configured",
    "github": "configured"
  }
}
```

**Note**: Actual API keys are **NOT** included. Status shows only `configured` or `not_configured`.

#### 3. Import Configuration (Manual)

To use an exported config on another machine:

1. Copy the JSON file to new server
2. Extract settings you want to apply
3. Update `.env` file manually with values
4. Or use Settings GUI to reconfigure

**Future Enhancement**: Import functionality coming soon!

### API Endpoints

```bash
# Export configuration
curl http://localhost:8000/settings/export -o config.json

# Pretty print
curl http://localhost:8000/settings/export | jq .
```

---

## Security Features

### Encryption

**Fernet Encryption** for API keys:
- Symmetric encryption (AES 128-bit)
- Unique encryption key per installation
- Keys encrypted before storage
- Decrypted only when needed

**Encryption Key**: Stored in `backend/.encryption_key` (auto-generated)

### Best Practices

1. **Never Commit API Keys**: Add `.env` to `.gitignore`
2. **Use Environment Variables**: Store secrets in `.env`, not code
3. **Rotate Keys Regularly**: Change API keys periodically
4. **Limit Permissions**: Use least-privilege access tokens
5. **Monitor Usage**: Check API usage in provider dashboards
6. **Backup Encryption Key**: Save `backend/.encryption_key` securely

### Protected Storage

Files containing sensitive data:
- `.env`: Environment variables (gitignored)
- `backend/.encryption_key`: Encryption key (gitignored)
- `.github/copilot/mcp.json`: May contain tokens (be careful)

**Never**:
- ❌ Commit `.env` to git
- ❌ Share API keys in chat/email
- ❌ Log API keys
- ❌ Display keys in UI (use redaction)
- ❌ Store keys in database unencrypted

### Redaction

API keys displayed in GUI are redacted:
- Shows first 4 and last 4 characters
- Middle characters replaced with `...`
- Example: `AIza...1234` instead of `AIzaSyYourFullKeyHere1234`

To see full key:
- Click **👁️** toggle button
- Full key displayed temporarily
- Click again to hide

---

## API Reference

### Complete Settings API

#### GET /settings
Get current settings

**Response:**
```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "frontend_port": 3000,
  "cors_origins": ["http://localhost:3000"],
  "active_model": "gemini"
}
```

#### POST /settings
Update settings

**Request:**
```json
{
  "host": "0.0.0.0",
  "port": 8001
}
```

#### GET /settings/models
Get available AI models

**Response:**
```json
{
  "models": [
    {
      "id": "gemini",
      "name": "Gemini AI",
      "status": "configured",
      "active": true
    },
    {
      "id": "vertex",
      "name": "Vertex AI",
      "status": "missing_credentials",
      "active": false
    }
  ]
}
```

#### POST /settings/models
Set active model

**Request:**
```json
{
  "model": "gemini"
}
```

#### GET /settings/mcp
Get MCP server status

**Response:**
```json
{
  "servers": {
    "filesystem": {
      "enabled": true,
      "status": "ready"
    },
    "github": {
      "enabled": false,
      "status": "missing_credentials",
      "required_credential": "GITHUB_TOKEN"
    }
  }
}
```

#### POST /settings/mcp/{server}
Toggle MCP server

**Request:**
```json
{
  "enabled": true
}
```

#### POST /settings/api-keys
Update API key

**Request:**
```json
{
  "service": "GEMINI_API_KEY",
  "key": "AIzaSy..."
}
```

#### POST /settings/validate
Validate API key

**Request:**
```json
{
  "service": "gemini",
  "key": "AIzaSy..."
}
```

**Response:**
```json
{
  "valid": true,
  "message": "API key is valid"
}
```

#### GET /settings/env
Get environment variables (non-sensitive)

**Response:**
```json
{
  "variables": {
    "DEBUG_MODE": "false",
    "LOG_LEVEL": "INFO"
  }
}
```

#### POST /settings/env
Update environment variable

**Request:**
```json
{
  "key": "DEBUG_MODE",
  "value": "true"
}
```

#### GET /settings/export
Export configuration

**Response**: JSON file download

#### POST /settings/test-connection/{service}
Test connection to service

**Services**: `gemini`, `vertex`, `ollama`

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "details": {
    "response_time_ms": 234
  }
}
```

---

## Troubleshooting

### Settings Not Saving

**Problem**: Changes don't persist

**Solutions**:
1. Check file permissions: `chmod 644 .env`
2. Check disk space: `df -h`
3. View backend logs: `tail -f logs/backend.log`
4. Restart backend: `./stop.sh && ./start.sh`

### API Key Validation Fails

**Problem**: "Invalid API key" error

**Solutions**:
1. Verify key format (Gemini starts with `AIza`)
2. Check for extra spaces
3. Get new key from provider
4. Test key with curl (see API Reference)
5. Check rate limits in provider dashboard

### MCP Server Status Wrong

**Problem**: Server shows wrong status

**Solutions**:
1. Click **🔄 Refresh Status**
2. Verify credentials in API Keys section
3. Test MCP server manually: `npx @github/mcp-server --help`
4. Check environment variables: `printenv | grep TOKEN`
5. Restart backend

### Can't Toggle MCP Server

**Problem**: Toggle doesn't work

**Solutions**:
1. Check browser console for errors
2. Verify backend is running
3. Test API: `curl http://localhost:8000/settings/mcp`
4. Clear browser cache
5. Try different browser

### Configuration Export Empty

**Problem**: Export file has no data

**Solutions**:
1. Ensure settings are saved first
2. Check backend logs for errors
3. Test export API: `curl http://localhost:8000/settings/export`
4. Try different browser
5. Check download folder permissions

---

## Related Documentation

- **[Troubleshooting Guide](../TROUBLESHOOTING.md)**: Common issues
- **[Quick Start Guide](../QUICKSTART.md)**: Getting started
- **[API Reference](../README.md#api-reference)**: All endpoints
- **[Phase 2 Summary](../PHASE2_IMPLEMENTATION_SUMMARY.md)**: Implementation details

---

<div align="center">

**Need More Help?**

Check the [Troubleshooting Guide](../TROUBLESHOOTING.md) or open an issue!

[⬆ Back to Top](#️-settings-gui---complete-guide)

</div>
