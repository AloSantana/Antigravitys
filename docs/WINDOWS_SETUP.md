# Windows Setup Guide

Complete guide for setting up Antigravity Workspace on Windows 10/11.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Configuration](#configuration)
- [Running the Workspace](#running-the-workspace)
- [Troubleshooting](#troubleshooting)
- [Common Issues](#common-issues)
- [Advanced Topics](#advanced-topics)

---

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   - Download: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: During installation, check **"Add Python to PATH"**
   - Verify installation:
     ```powershell
     python --version
     # Should show: Python 3.11.x or higher
     ```

2. **Git for Windows** (recommended)
   - Download: https://git-scm.com/download/win
   - Or use GitHub Desktop: https://desktop.github.com/

### Optional but Recommended

3. **Node.js 18+** (for MCP servers)
   - Download: https://nodejs.org/
   - Choose LTS version
   - Verify installation:
     ```powershell
     node --version
     npm --version
     ```

4. **Ollama** (for local AI models)
   - Download: https://ollama.ai
   - After installation, pull a model:
     ```powershell
     ollama pull llama3
     ```

### System Requirements

- **OS**: Windows 10 (build 1809+) or Windows 11
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk**: 5GB free space minimum
- **CPU**: Any modern 64-bit processor

---

## Quick Start

### Option 1: Automated Installation (Recommended)

1. **Clone or download the repository**
   ```powershell
   git clone https://github.com/yourusername/antigravity-workspace.git
   cd antigravity-workspace
   ```

2. **Run the installer**
   ```powershell
   .\install.ps1
   ```
   
   If you get an execution policy error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Configure your environment**
   ```powershell
   .\configure.ps1
   ```
   
   Or manually edit `.env` file:
   ```powershell
   notepad .env
   ```

4. **Start the workspace**
   ```powershell
   .\start.ps1
   ```
   
   Or double-click `start.bat`

5. **Access the interface**
   - Open browser: http://localhost:8000

### Option 2: Double-Click Installation

1. Extract the ZIP file
2. Double-click `start.bat`
3. Follow the prompts

---

## Detailed Installation

### Step 1: Install Python

1. Download Python 3.11+ from https://www.python.org/downloads/
2. Run the installer
3. ✅ **Check "Add Python to PATH"**
4. Click "Install Now"
5. Verify:
   ```powershell
   python --version
   pip --version
   ```

### Step 2: Install Node.js (Optional)

1. Download from https://nodejs.org/
2. Run installer (keep default options)
3. Verify:
   ```powershell
   node --version
   npm --version
   ```

### Step 3: Clone Repository

Using Git:
```powershell
git clone https://github.com/yourusername/antigravity-workspace.git
cd antigravity-workspace
```

Or download ZIP and extract.

### Step 4: Run Installation Script

Open PowerShell in the project directory:

```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run installer
.\install.ps1
```

The installer will:
- ✅ Check Python and Node.js versions
- ✅ Create virtual environment (`venv` folder)
- ✅ Install Python dependencies
- ✅ Install MCP servers (if Node.js available)
- ✅ Create required directories
- ✅ Set up configuration file

### Step 5: Configuration

Run the configuration wizard:

```powershell
.\configure.ps1
```

You'll be prompted to configure:

1. **Gemini API Key** (required)
   - Get from: https://aistudio.google.com/app/apikey
   
2. **GitHub Token** (optional)
   - Get from: https://github.com/settings/tokens
   - Required scopes: `repo`, `read:org`

3. **Model Selection**
   - `auto` - Automatic (recommended)
   - `gemini` - Always use Gemini
   - `vertex` - Always use Vertex AI
   - `ollama` - Local models with cloud fallback

4. **Ngrok** (optional)
   - For public URL access
   - Get token: https://dashboard.ngrok.com/

5. **Server Settings**
   - Host: `0.0.0.0` (default)
   - Port: `8000` (default)

---

## Configuration

### Manual Configuration

Edit `.env` file directly:

```powershell
notepad .env
```

### Required Settings

```ini
# Gemini API Key (required)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Optional Settings

```ini
# Local AI Model
LOCAL_MODEL=llama3
ACTIVE_MODEL=auto

# GitHub Integration
COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# Ngrok Tunnel
NGROK_ENABLED=false
NGROK_AUTH_TOKEN=

# Debug Mode
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Environment Variables

You can also set environment variables instead of `.env`:

```powershell
$env:GEMINI_API_KEY = "your_key_here"
$env:PORT = "8000"
```

---

## Running the Workspace

### Method 1: PowerShell Script (Recommended)

```powershell
.\start.ps1
```

### Method 2: Batch File

Double-click `start.bat` or run:
```cmd
start.bat
```

### Method 3: Manual Start

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend
cd backend
python main.py
```

### Stopping the Server

Press `Ctrl+C` in the terminal window.

### Running in Background

To run as a background service, use NSSM (Non-Sucking Service Manager):

```powershell
# Install NSSM (using Chocolatey)
choco install nssm

# Create service
nssm install AntigravityWorkspace "C:\path\to\venv\Scripts\python.exe" "C:\path\to\backend\main.py"
nssm set AntigravityWorkspace AppDirectory "C:\path\to\backend"

# Start service
nssm start AntigravityWorkspace
```

---

## Troubleshooting

### PowerShell Execution Policy Error

**Error:**
```
.\install.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Python Not Found

**Error:**
```
python : The term 'python' is not recognized
```

**Solutions:**

1. **Reinstall Python** with "Add to PATH" checked
2. **Manually add to PATH:**
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
3. **Restart terminal** after making changes

### Virtual Environment Activation Fails

**Error:**
```
Activate.ps1 cannot be loaded
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\venv\Scripts\Activate.ps1
```

### Port Already in Use

**Error:**
```
Port 8000 is already in use
```

**Solutions:**

1. **Find and kill process:**
   ```powershell
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

2. **Use different port:**
   Edit `.env`:
   ```ini
   PORT=8001
   ```

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
pip install -r backend\requirements.txt
```

### Firewall Blocking Connection

**Windows Firewall** may block Python:

1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Click **Change settings**
4. Find **Python** or click **Allow another app**
5. Browse to: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
6. Check both **Private** and **Public**
7. Click **OK**

### SSL Certificate Errors (pip)

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Slow Installation

If pip is slow:

```powershell
# Use a different mirror
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Or disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## Common Issues

### Issue: Backend Crashes on Startup

**Check logs:**
```powershell
type logs\backend.log
```

**Common causes:**
1. Missing API keys in `.env`
2. Port already in use
3. Missing dependencies

**Solution:**
```powershell
# Verify .env file
notepad .env

# Reinstall dependencies
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt --force-reinstall
```

### Issue: Can't Access from Another Device

**To access from another computer on your network:**

1. **Find your local IP:**
   ```powershell
   ipconfig
   # Look for "IPv4 Address" under your active network adapter
   # Example: 192.168.1.100
   ```

2. **Update ALLOWED_ORIGINS in `.env`:**
   ```ini
   ALLOWED_ORIGINS=http://192.168.1.100:8000,http://localhost:8000
   ```

3. **Configure Windows Firewall:**
   ```powershell
   # Allow port 8000 through firewall
   netsh advfirewall firewall add rule name="Antigravity Backend" dir=in action=allow protocol=TCP localport=8000
   ```

4. **Access from another device:**
   ```
   http://192.168.1.100:8000
   ```

### Issue: Ollama Not Working

**Check if Ollama is running:**
```powershell
# Test Ollama
ollama list

# Start Ollama service
ollama serve
```

**Pull model:**
```powershell
ollama pull llama3
```

**Verify in `.env`:**
```ini
LOCAL_MODEL=llama3
```

### Issue: MCP Servers Not Found

**Solution:**
```powershell
# Install globally with npm
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking

# Verify installation
npm list -g --depth=0
```

---

## Advanced Topics

### Running with Docker on Windows

1. **Install Docker Desktop:**
   - Download: https://www.docker.com/products/docker-desktop/

2. **Build and run:**
   ```powershell
   docker-compose up -d
   ```

3. **View logs:**
   ```powershell
   docker-compose logs -f
   ```

### Custom Python Version

If you need a specific Python version:

```powershell
# Create venv with specific Python
py -3.11 -m venv venv

# Or
C:\Python311\python.exe -m venv venv
```

### Development Mode

For development with auto-reload:

1. **Edit `.env`:**
   ```ini
   DEBUG_MODE=true
   LOG_LEVEL=DEBUG
   ```

2. **Start with uvicorn reload:**
   ```powershell
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Performance Tuning

**For better performance:**

```ini
# In .env
CACHE_TTL_SECONDS=600
CACHE_MAX_SIZE=200
RAG_MAX_CONCURRENT_EMBEDDINGS=15
```

**Windows Defender exclusions:**
Add these folders to Windows Defender exclusions for faster file operations:
- Project root folder
- `venv` folder
- `node_modules` folder (if present)

### Scheduled Tasks

**Run workspace on Windows startup:**

1. Open **Task Scheduler**
2. Create Basic Task
3. Name: "Antigravity Workspace"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `powershell.exe`
7. Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\start.ps1"`
8. Finish

### Using with VS Code

1. **Open in VS Code:**
   ```powershell
   code .
   ```

2. **Select Python interpreter:**
   - `Ctrl+Shift+P`
   - "Python: Select Interpreter"
   - Choose `.\venv\Scripts\python.exe`

3. **Integrated terminal:**
   - Terminal will auto-activate venv

### Network Configuration

**For VPS/Remote Access:**

1. **Configure `.env`:**
   ```ini
   REMOTE_ACCESS=true
   EXTERNAL_HOST=your-domain.com
   ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
   ```

2. **Setup port forwarding** on your router:
   - Forward external port 80 → internal port 8000

3. **Or use Ngrok:**
   ```ini
   NGROK_ENABLED=true
   NGROK_AUTH_TOKEN=your_ngrok_token
   ```

---

## Getting Help

### Documentation

- **Main README:** [README.md](../README.md)
- **API Reference:** [API_QUICK_REFERENCE.md](../API_QUICK_REFERENCE.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

### Logs

Check logs for detailed error information:

```powershell
# View latest log entries
type logs\backend.log | select -Last 50

# Follow logs in real-time (PowerShell 7+)
Get-Content logs\backend.log -Wait -Tail 50
```

### System Information

Get system info for bug reports:

```powershell
# Windows version
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Python version
python --version

# Node version
node --version

# Installed packages
pip list

# NPM global packages
npm list -g --depth=0
```

### Community Support

- **Issues:** https://github.com/yourusername/antigravity-workspace/issues
- **Discussions:** https://github.com/yourusername/antigravity-workspace/discussions

---

## Uninstallation

To completely remove Antigravity Workspace:

```powershell
# Stop any running instances
# Then delete the project folder and:

# Remove virtual environment
Remove-Item -Recurse -Force venv

# Remove MCP servers
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @modelcontextprotocol/server-memory
npm uninstall -g @modelcontextprotocol/server-sequential-thinking

# Remove scheduled tasks (if created)
# Open Task Scheduler and delete "Antigravity Workspace" task

# Remove firewall rules (if created)
netsh advfirewall firewall delete rule name="Antigravity Backend"
```

---

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use environment variables** for production
3. **Restrict ALLOWED_ORIGINS** in production
4. **Use HTTPS** for remote access
5. **Keep dependencies updated:**
   ```powershell
   pip install --upgrade -r requirements.txt
   ```
6. **Use firewall rules** to restrict access
7. **Don't run as Administrator** unless necessary

---

## Tips & Tricks

### Quick Commands

Save these as PowerShell aliases:

```powershell
# Add to $PROFILE
function Start-Antigravity { & "$PSScriptRoot\start.ps1" }
function Stop-Antigravity { Get-Process python | Where-Object {$_.Path -like "*antigravity*"} | Stop-Process }
function Restart-Antigravity { Stop-Antigravity; Start-Antigravity }
```

### Keyboard Shortcuts

When server is running:
- `Ctrl+C` - Stop server gracefully
- `Ctrl+Z` - Suspend process (use with caution)

### Monitoring

**Monitor resource usage:**
```powershell
# CPU and memory
Get-Process python | Format-Table Name, CPU, WorkingSet -AutoSize

# Detailed info
Get-Process python | Select-Object *
```

### Backup Configuration

**Backup your configuration:**
```powershell
# Create backup
Copy-Item .env .env.backup

# Restore backup
Copy-Item .env.backup .env
```

---

## What's Next?

After successful installation:

1. ✅ **Explore the Interface** - http://localhost:8000
2. 📚 **Read the Documentation** - [README.md](../README.md)
3. 🚀 **Try Example Workflows** - [examples/](../examples/)
4. 🛠️ **Configure MCP Servers** - [.mcp/README.md](../.mcp/README.md)
5. 🎨 **Customize Settings** - Edit `.env` file

---

**Enjoy using Antigravity Workspace on Windows! 🚀**
