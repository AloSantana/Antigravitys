# Windows Support - Complete Index

Quick navigation for all Windows-related files and documentation.

## 🎯 Quick Start

**For Windows Users**: Choose your preferred method:

### Method 1: Automated Setup (Recommended)
```powershell
.\install.ps1    # Install everything
.\configure.ps1  # Configure settings
.\start.ps1      # Start the workspace
```

### Method 2: Double-Click
1. Double-click `start.bat`
2. Follow the prompts

### Method 3: Read First
1. Read [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)
2. Follow the detailed guide

---

## 📁 Files Overview

### PowerShell Scripts

#### 1. **start.ps1**
- **Purpose**: Start the Antigravity Workspace
- **Size**: 11.4 KB
- **Usage**: `.\start.ps1`
- **Features**:
  - Python version check
  - Virtual environment setup
  - Port availability check
  - Automatic dependency installation
  - Backend server launch

#### 2. **install.ps1**
- **Purpose**: Complete installation and setup
- **Size**: 19.7 KB
- **Usage**: `.\install.ps1`
- **Options**:
  - `.\install.ps1 -SkipMCP` - Skip MCP servers
  - `.\install.ps1 -SkipDocker` - Skip Docker setup
- **Features**:
  - System requirements check
  - Python 3.11+ validation
  - Virtual environment creation
  - Dependency installation
  - MCP server setup
  - Configuration initialization

#### 3. **configure.ps1**
- **Purpose**: Interactive configuration wizard
- **Size**: 20.7 KB
- **Usage**: `.\configure.ps1`
- **Features**:
  - Gemini API setup
  - Vertex AI configuration
  - Model selection
  - GitHub integration
  - Ngrok setup
  - Optional services
  - Server settings

#### 4. **start.bat**
- **Purpose**: Simple batch launcher
- **Size**: 918 bytes
- **Usage**: Double-click or `start.bat`
- **Features**:
  - PowerShell wrapper
  - Error handling
  - User-friendly messages

---

## 📚 Documentation

### Complete Guides

#### 1. **docs/WINDOWS_SETUP.md**
**Complete Windows 10/11 Setup Guide**

**Size**: 14.8 KB  
**Sections**:
- Prerequisites
- Quick Start
- Detailed Installation
- Configuration
- Running the Workspace
- Troubleshooting
- Common Issues
- Advanced Topics

**Topics Covered**:
- Python installation
- Node.js setup
- Virtual environment management
- Firewall configuration
- Port management
- Remote access
- Ollama integration
- MCP server management
- Security best practices
- Performance tuning

**When to Use**:
- First-time installation
- Troubleshooting issues
- Advanced configuration
- Remote access setup

#### 2. **docs/WINDOWS_QUICK_REFERENCE.md**
**Quick Command Reference**

**Size**: 11.5 KB  
**Sections**:
- Scripts Overview
- Installation Commands
- Configuration Commands
- Common Commands
- Troubleshooting Commands
- Virtual Environment Management
- Firewall Configuration
- Process Management
- Network Configuration
- Development Commands
- Backup and Restore
- Quick Fixes

**When to Use**:
- Quick command lookup
- Daily operations
- Troubleshooting
- Development tasks

#### 3. **WINDOWS_IMPLEMENTATION_COMPLETE.md**
**Technical Implementation Documentation**

**Size**: 14.9 KB  
**Contents**:
- Implementation overview
- Technical details
- Feature comparison
- Testing checklist
- Deployment readiness
- Maintenance notes

**When to Use**:
- Understanding implementation
- Contributing to project
- Technical review
- Quality assurance

---

## 🎓 Learning Path

### For Beginners

1. **Start Here**: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Prerequisites
2. **Install**: Run `.\install.ps1`
3. **Configure**: Run `.\configure.ps1`
4. **Start**: Run `.\start.ps1` or double-click `start.bat`
5. **Reference**: Bookmark [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)

### For Advanced Users

1. **Quick Reference**: [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)
2. **Advanced Topics**: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Advanced Topics
3. **Manual Configuration**: Edit `.env` directly
4. **Customization**: Modify PowerShell scripts

### For Developers

1. **Implementation**: [WINDOWS_IMPLEMENTATION_COMPLETE.md](WINDOWS_IMPLEMENTATION_COMPLETE.md)
2. **Script Comments**: Read inline documentation
3. **Error Handling**: Study error handling patterns
4. **Testing**: Review testing checklist

---

## 🔧 Common Tasks

### Installation & Setup

| Task | Command | Documentation |
|------|---------|---------------|
| Full installation | `.\install.ps1` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Configure settings | `.\configure.ps1` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Start workspace | `.\start.ps1` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |
| Check requirements | `python --version` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |

### Configuration

| Task | Command | Documentation |
|------|---------|---------------|
| Interactive config | `.\configure.ps1` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Manual config | `notepad .env` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Backup config | `Copy-Item .env .env.backup` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |
| Restore config | `Copy-Item .env.backup .env` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |

### Troubleshooting

| Issue | Solution | Documentation |
|-------|----------|---------------|
| Execution policy | `Set-ExecutionPolicy RemoteSigned` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Python not found | Check PATH | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Port in use | Kill process | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |
| Import errors | Reinstall requirements | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |

### Maintenance

| Task | Command | Documentation |
|------|---------|---------------|
| Update dependencies | `pip install --upgrade -r requirements.txt` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |
| View logs | `type logs\backend.log` | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |
| Clean install | Remove venv and reinstall | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Backup data | Archive directories | [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) |

---

## 🚨 Troubleshooting Index

### Common Issues

| Issue | Quick Fix | Detailed Guide |
|-------|-----------|----------------|
| Scripts won't run | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#powershell-execution-policy-error) |
| Python not found | Add to PATH or reinstall | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#python-not-found) |
| Port already in use | `netstat -ano \| findstr :8000` then kill | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#port-already-in-use) |
| venv activation fails | Run as Administrator or bypass policy | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#virtual-environment-activation-fails) |
| Import errors | `pip install -r requirements.txt --force-reinstall` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#import-errors) |
| Firewall blocking | Add Python to firewall exceptions | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#firewall-blocking-connection) |

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "running scripts is disabled" | Execution policy restriction | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#powershell-execution-policy-error) |
| "python is not recognized" | Python not in PATH | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#python-not-found) |
| "Port 8000 is already in use" | Another process using port | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#port-already-in-use) |
| "ModuleNotFoundError" | Missing Python package | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#import-errors) |
| "cannot be loaded" | Script execution blocked | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#virtual-environment-activation-fails) |

---

## 📊 Feature Matrix

| Feature | start.ps1 | install.ps1 | configure.ps1 | Documentation |
|---------|-----------|-------------|---------------|---------------|
| Python version check | ✅ | ✅ | - | ✅ |
| Virtual environment | ✅ | ✅ | - | ✅ |
| Dependency install | ✅ | ✅ | - | ✅ |
| Port check | ✅ | - | - | ✅ |
| .env creation | ✅ | ✅ | ✅ | ✅ |
| Interactive prompts | ✅ | ✅ | ✅ | ✅ |
| Error handling | ✅ | ✅ | ✅ | ✅ |
| Color output | ✅ | ✅ | ✅ | - |
| Logging | - | ✅ | - | ✅ |
| MCP servers | - | ✅ | - | ✅ |
| API validation | - | - | ✅ | ✅ |
| GitHub integration | - | - | ✅ | ✅ |
| Ngrok setup | - | - | ✅ | ✅ |
| Ollama config | - | - | ✅ | ✅ |

---

## 🎯 Use Case Guide

### I Want To...

#### Install for the First Time
1. Read: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Quick Start
2. Run: `.\install.ps1`
3. Run: `.\configure.ps1`
4. Run: `.\start.ps1`

#### Just Start Working
1. Double-click: `start.bat`
2. Or run: `.\start.ps1`

#### Change Configuration
1. Run: `.\configure.ps1`
2. Or edit: `notepad .env`

#### Fix a Problem
1. Check: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Troubleshooting
2. Check: [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) → Quick Fixes
3. Check logs: `type logs\backend.log`

#### Understand Implementation
1. Read: [WINDOWS_IMPLEMENTATION_COMPLETE.md](WINDOWS_IMPLEMENTATION_COMPLETE.md)
2. Review: Script comments
3. Check: Testing checklist

#### Find a Command
1. Check: [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)
2. Use: Ctrl+F to search

#### Set Up Remote Access
1. Read: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Advanced Topics → Network Configuration
2. Configure: Firewall and port forwarding
3. Or use: Ngrok via `.\configure.ps1`

#### Run on Startup
1. Read: [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md) → Scheduled Tasks
2. Create: Task Scheduler entry
3. Or use: NSSM for Windows service

---

## 📱 Quick Reference Cards

### Installation Commands
```powershell
.\install.ps1              # Full install
.\install.ps1 -SkipMCP    # Skip MCP servers
.\configure.ps1           # Interactive config
.\start.ps1               # Start workspace
```

### Daily Commands
```powershell
.\start.ps1               # Start
notepad .env              # Edit config
type logs\backend.log     # View logs
python --version          # Check Python
```

### Troubleshooting Commands
```powershell
# Fix execution policy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Check port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

---

## 🔗 External Resources

### Prerequisites
- **Python**: https://www.python.org/downloads/
- **Node.js**: https://nodejs.org/
- **Git**: https://git-scm.com/download/win
- **Ollama**: https://ollama.ai

### API Keys
- **Gemini**: https://aistudio.google.com/app/apikey
- **GitHub**: https://github.com/settings/tokens
- **Ngrok**: https://dashboard.ngrok.com/get-started/your-authtoken
- **Brave Search**: https://brave.com/search/api/

### Support
- **Issues**: https://github.com/yourusername/antigravity-workspace/issues
- **Discussions**: https://github.com/yourusername/antigravity-workspace/discussions

---

## 📋 Checklist

### Before Installation
- [ ] Python 3.11+ installed
- [ ] Python added to PATH
- [ ] Node.js installed (optional)
- [ ] Git installed
- [ ] Downloaded/cloned repository

### After Installation
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Can access http://localhost:8000
- [ ] Bookmarked documentation

### For Production
- [ ] Firewall configured
- [ ] ALLOWED_ORIGINS set
- [ ] API keys secured
- [ ] Backups configured
- [ ] Monitoring set up

---

## 🆘 Getting Help

### Step-by-Step
1. **Check Quick Reference**: [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)
2. **Check Troubleshooting**: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md#troubleshooting)
3. **Check Logs**: `type logs\backend.log`
4. **Search Documentation**: Use Ctrl+F
5. **Ask Community**: GitHub Issues/Discussions

### Include When Asking
```powershell
# System info
python --version
node --version
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Error message
type logs\backend.log | select -Last 50

# Configuration (remove sensitive data!)
type .env
```

---

## ✅ Verification

After setup, verify everything works:

```powershell
# 1. Check Python
python --version  # Should be 3.11+

# 2. Check venv
Test-Path .\venv  # Should be True

# 3. Check requirements
.\venv\Scripts\python.exe -c "import fastapi, uvicorn, chromadb"

# 4. Check .env
Test-Path .\.env  # Should be True

# 5. Start workspace
.\start.ps1

# 6. Test access
Start-Process http://localhost:8000
```

---

## 📦 File Summary

```
Windows Support Files (7 files, ~78 KB)
├── PowerShell Scripts (4 files, ~53 KB)
│   ├── start.ps1         (11.4 KB)
│   ├── install.ps1       (19.7 KB)
│   ├── configure.ps1     (20.7 KB)
│   └── start.bat         (918 bytes)
└── Documentation (3 files, ~25 KB)
    ├── docs/WINDOWS_SETUP.md              (14.8 KB)
    ├── docs/WINDOWS_QUICK_REFERENCE.md    (11.5 KB)
    └── WINDOWS_IMPLEMENTATION_COMPLETE.md (14.9 KB)
```

---

**Ready to Start?** → [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Quick Start

**Need Help?** → [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) → Troubleshooting

**Looking for Commands?** → [WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)

---

**Last Updated**: February 10, 2024  
**Version**: 1.0.0  
**Status**: ✅ Complete
