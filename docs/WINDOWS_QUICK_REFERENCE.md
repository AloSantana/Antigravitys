# Windows Scripts Quick Reference

Quick reference for Windows PowerShell scripts in Antigravity Workspace.

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `install.ps1` | Full installation and setup | `.\install.ps1` |
| `configure.ps1` | Interactive configuration wizard | `.\configure.ps1` |
| `start.ps1` | Start the workspace | `.\start.ps1` |
| `start.bat` | Batch launcher (double-click) | Double-click or `start.bat` |

---

## Installation

### Quick Install
```powershell
# 1. Clone repository
git clone https://github.com/yourusername/antigravity-workspace.git
cd antigravity-workspace

# 2. Run installer
.\install.ps1

# 3. Configure
.\configure.ps1

# 4. Start
.\start.ps1
```

### Installation Options
```powershell
# Skip MCP server installation
.\install.ps1 -SkipMCP

# Skip Docker setup
.\install.ps1 -SkipDocker

# Both
.\install.ps1 -SkipMCP -SkipDocker
```

---

## Configuration

### Interactive Configuration
```powershell
.\configure.ps1
```

### Manual Configuration
```powershell
# Edit .env file
notepad .env

# Or use VS Code
code .env
```

### Required Settings
```ini
GEMINI_API_KEY=your_key_here
HOST=0.0.0.0
PORT=8000
```

---

## Starting the Workspace

### Method 1: PowerShell Script
```powershell
.\start.ps1
```

### Method 2: Batch File
```cmd
start.bat
```
Or double-click `start.bat` in Windows Explorer.

### Method 3: Manual Start
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Start backend
cd backend
python main.py
```

---

## Common Commands

### Check Python Version
```powershell
python --version
# Should show: Python 3.11.x or higher
```

### Check Node.js Version
```powershell
node --version
npm --version
```

### Verify Installation
```powershell
# Check if virtual environment exists
Test-Path .\venv

# Check if requirements are installed
.\venv\Scripts\python.exe -c "import fastapi, uvicorn, chromadb"
```

### Update Dependencies
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Update pip
python -m pip install --upgrade pip

# Update all packages
pip install --upgrade -r requirements.txt
pip install --upgrade -r backend\requirements.txt
```

---

## Troubleshooting Commands

### Execution Policy Issues
```powershell
# Check current policy
Get-ExecutionPolicy

# Set for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Bypass for single script
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

### Port Issues
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Alternative: Use Get-NetTCPConnection
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property OwningProcess
Stop-Process -Id <PID> -Force
```

### View Logs
```powershell
# View full log
type logs\backend.log

# View last 50 lines
type logs\backend.log | select -Last 50

# Follow logs (PowerShell 7+)
Get-Content logs\backend.log -Wait -Tail 50
```

### Clean Installation
```powershell
# Remove virtual environment
Remove-Item -Recurse -Force venv

# Reinstall
.\install.ps1
```

---

## Virtual Environment

### Activate
```powershell
.\venv\Scripts\Activate.ps1
```

### Deactivate
```powershell
deactivate
```

### Recreate
```powershell
# Remove old venv
Remove-Item -Recurse -Force venv

# Create new venv
python -m venv venv

# Activate and install
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r backend\requirements.txt
```

---

## Firewall Configuration

### Allow Python Through Firewall
```powershell
# Add firewall rule
netsh advfirewall firewall add rule name="Antigravity Backend" dir=in action=allow protocol=TCP localport=8000

# Remove firewall rule
netsh advfirewall firewall delete rule name="Antigravity Backend"

# List firewall rules
netsh advfirewall firewall show rule name=all | findstr "Antigravity"
```

### Windows Defender Firewall (GUI)
1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Click **Change settings**
4. Add Python: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
5. Check **Private** and **Public**

---

## Environment Variables

### Set Temporarily (Current Session)
```powershell
$env:GEMINI_API_KEY = "your_key_here"
$env:PORT = "8000"
```

### Set Permanently (User)
```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_key_here", "User")
```

### Set Permanently (System - requires admin)
```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_key_here", "Machine")
```

### View All Environment Variables
```powershell
Get-ChildItem Env:
```

---

## Process Management

### Find Python Processes
```powershell
Get-Process python
```

### Stop Backend Process
```powershell
# By name (stops all python processes - use carefully!)
Stop-Process -Name python

# By port
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
}
```

### Monitor Process
```powershell
# CPU and memory usage
Get-Process python | Format-Table Name, CPU, WorkingSet -AutoSize

# Detailed info
Get-Process python | Select-Object *
```

---

## Network Configuration

### Find Local IP Address
```powershell
# Method 1
ipconfig

# Method 2
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}

# Method 3 (simplified)
(Get-NetIPConfiguration).IPv4Address.IPAddress
```

### Test Connection
```powershell
# Test if backend is responding
Invoke-WebRequest -Uri http://localhost:8000 -Method GET

# Or use curl
curl http://localhost:8000
```

### Port Forwarding
```powershell
# Add port proxy (requires admin)
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=8000 connectaddress=127.0.0.1

# Remove port proxy
netsh interface portproxy delete v4tov4 listenport=80 listenaddress=0.0.0.0

# Show all port proxies
netsh interface portproxy show all
```

---

## MCP Server Management

### Install MCP Servers
```powershell
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
```

### List Installed MCP Servers
```powershell
npm list -g --depth=0 | findstr modelcontextprotocol
```

### Update MCP Servers
```powershell
npm update -g @modelcontextprotocol/server-filesystem
npm update -g @modelcontextprotocol/server-memory
npm update -g @modelcontextprotocol/server-sequential-thinking
```

### Uninstall MCP Servers
```powershell
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @modelcontextprotocol/server-memory
npm uninstall -g @modelcontextprotocol/server-sequential-thinking
```

---

## Ollama Management

### Check Ollama Status
```powershell
ollama list
```

### Pull Models
```powershell
ollama pull llama3
ollama pull mistral
ollama pull codellama
```

### Run Model Test
```powershell
ollama run llama3 "Hello, how are you?"
```

### Remove Model
```powershell
ollama rm llama3
```

---

## Development Commands

### Run Tests
```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Run pytest
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/test_main.py::test_function_name
```

### Format Code
```powershell
# Install black (if not installed)
pip install black

# Format all Python files
black .

# Check what would be formatted
black --check .
```

### Lint Code
```powershell
# Install flake8 (if not installed)
pip install flake8

# Run linter
flake8 backend/

# With specific rules
flake8 backend/ --max-line-length=100 --ignore=E501,W503
```

---

## Backup and Restore

### Backup Configuration
```powershell
# Backup .env
Copy-Item .env .env.backup

# Backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .env ".env.backup.$timestamp"
```

### Restore Configuration
```powershell
Copy-Item .env.backup .env
```

### Backup Entire Setup
```powershell
# Create backup directory
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir

# Copy important files
Copy-Item .env "$backupDir\.env"
Copy-Item logs "$backupDir\logs" -Recurse
Copy-Item data "$backupDir\data" -Recurse
Copy-Item drop_zone "$backupDir\drop_zone" -Recurse

# Create archive
Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
```

---

## System Information

### Get System Info
```powershell
# OS information
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture

# CPU information
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# Memory information
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory

# Disk space
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free
```

### Check Python Package Versions
```powershell
pip list
pip show fastapi
pip show uvicorn
```

### Check System Requirements
```powershell
# Python version
python --version

# Pip version
pip --version

# Node.js version
node --version

# NPM version
npm --version

# Git version
git --version

# PowerShell version
$PSVersionTable.PSVersion
```

---

## Scheduled Tasks

### Create Startup Task
```powershell
# Create task to run on startup (requires admin)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PSScriptRoot\start.ps1`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "AntigravityWorkspace" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

### Remove Scheduled Task
```powershell
Unregister-ScheduledTask -TaskName "AntigravityWorkspace" -Confirm:$false
```

### List Scheduled Tasks
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Antigravity*"}
```

---

## Quick Fixes

### Fix: Scripts Won't Run
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Fix: Python Not Found
```powershell
# Find Python installation
Get-Command python -All

# Add to PATH temporarily
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311"
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\Scripts"
```

### Fix: Port in Use
```powershell
# Kill process on port 8000
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
}
```

### Fix: Import Errors
```powershell
.\venv\Scripts\Activate.ps1
pip install --force-reinstall -r requirements.txt
pip install --force-reinstall -r backend\requirements.txt
```

---

## Useful PowerShell Aliases

Add these to your PowerShell profile (`$PROFILE`):

```powershell
# Open profile for editing
notepad $PROFILE

# Add these lines:
function astart { & "$PSScriptRoot\antigravity-workspace\start.ps1" }
function aconfig { & "$PSScriptRoot\antigravity-workspace\configure.ps1" }
function astop { Get-Process python | Stop-Process -Force }
function alogs { Get-Content "$PSScriptRoot\antigravity-workspace\logs\backend.log" -Wait -Tail 50 }
```

Then use:
```powershell
astart   # Start workspace
aconfig  # Configure
astop    # Stop workspace
alogs    # View logs
```

---

## Links

- **Full Documentation**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Main README**: [../README.md](../README.md)
- **Troubleshooting**: [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **API Reference**: [../API_QUICK_REFERENCE.md](../API_QUICK_REFERENCE.md)

---

**Last Updated**: 2024
