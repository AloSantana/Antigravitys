# Windows Support Section - Add to Main README.md

Add this section to the main README.md under installation instructions:

---

## 🪟 Windows Installation

### Prerequisites
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
  - ⚠️ **Important**: Check "Add Python to PATH" during installation
- **Node.js 18+** (optional) - [Download](https://nodejs.org/)
- **Git for Windows** - [Download](https://git-scm.com/download/win)

### Quick Start

#### Method 1: Automated Installation (Recommended)
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

#### Method 2: Double-Click Start
1. Extract or clone the repository
2. Double-click `start.bat`
3. Follow the prompts

#### Method 3: Manual Installation
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -r backend\requirements.txt

# Configure
.\configure.ps1

# Start backend
cd backend
python main.py
```

### Windows-Specific Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `start.ps1` | Start the workspace | `.\start.ps1` |
| `install.ps1` | Full installation | `.\install.ps1` |
| `configure.ps1` | Configuration wizard | `.\configure.ps1` |
| `start.bat` | Batch launcher | Double-click or `start.bat` |

### Troubleshooting

**Execution Policy Error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python Not Found:**
- Reinstall Python with "Add to PATH" checked
- Or manually add to PATH in System Environment Variables

**Port 8000 In Use:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Documentation

- **Complete Setup Guide**: [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)
- **Quick Reference**: [docs/WINDOWS_QUICK_REFERENCE.md](docs/WINDOWS_QUICK_REFERENCE.md)
- **Windows Index**: [WINDOWS_INDEX.md](WINDOWS_INDEX.md)

---

## Badge Suggestions

Add these badges to the top of README.md:

```markdown
![Windows Support](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
```

Or simpler versions:

```markdown
[![Windows](https://img.shields.io/badge/Windows-10%2F11-blue.svg)](docs/WINDOWS_SETUP.md)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1%2B-blue.svg)](docs/WINDOWS_SETUP.md)
```

---

## Table of Contents Update

Update the table of contents to include:

```markdown
## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Linux/macOS](#linuxmacos-installation)
  - [Windows](#windows-installation) ← Add this
  - [Docker](#docker-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Documentation](#documentation)
  - [Windows Support](#windows-support) ← Add this
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
```

---

## Documentation Section Update

Add under the Documentation section:

```markdown
### Windows Support

Complete documentation for Windows 10/11 users:

- **[Windows Setup Guide](docs/WINDOWS_SETUP.md)** - Complete installation and configuration
- **[Windows Quick Reference](docs/WINDOWS_QUICK_REFERENCE.md)** - Command cheat sheet
- **[Windows Index](WINDOWS_INDEX.md)** - Navigation hub for all Windows resources

PowerShell scripts included:
- `start.ps1` - Start the workspace
- `install.ps1` - Automated installation
- `configure.ps1` - Interactive configuration wizard
- `start.bat` - Simple batch launcher
```

---

## Quick Links Update

Add to the quick links section:

```markdown
### Quick Links

- 📖 [Documentation](README.md)
- 🐧 [Linux Setup](SETUP.md)
- 🪟 [Windows Setup](docs/WINDOWS_SETUP.md) ← Add this
- 🐳 [Docker Guide](DEPLOYMENT.md)
- 🚀 [Quick Start](QUICKSTART.md)
```

---

## Platform Compatibility Table

Add this table to show platform support:

```markdown
## Platform Support

| Platform | Status | Installation Script | Documentation |
|----------|--------|---------------------|---------------|
| Linux | ✅ Full Support | `./install.sh` | [SETUP.md](SETUP.md) |
| macOS | ✅ Full Support | `./install.sh` | [SETUP.md](SETUP.md) |
| Windows 10/11 | ✅ Full Support | `.\install.ps1` | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| Docker | ✅ Full Support | `docker-compose up` | [DEPLOYMENT.md](DEPLOYMENT.md) |
```

---

## Features Section Update

Add to the features list:

```markdown
## Features

- 🤖 AI-powered workspace with Gemini/Vertex AI/Ollama
- 💬 Real-time chat interface with WebSocket
- 📁 Intelligent file management and RAG
- 🔧 MCP (Model Context Protocol) integration
- 🌐 Optional Ngrok tunneling for remote access
- 🐧 Linux & macOS support
- 🪟 **Native Windows 10/11 support** ← Add this
- 📝 Comprehensive logging and debugging
- 🔒 Secure configuration management
- 📊 Performance monitoring and optimization
```

---

## Installation Script Comparison

Add this comparison table:

```markdown
### Installation Scripts Comparison

| Feature | Linux/macOS (`install.sh`) | Windows (`install.ps1`) |
|---------|---------------------------|-------------------------|
| Python check | ✅ | ✅ |
| Virtual environment | ✅ | ✅ |
| Dependencies | ✅ | ✅ |
| MCP servers | ✅ | ✅ |
| Configuration | ✅ | ✅ |
| Error handling | ✅ | ✅ Enhanced |
| Interactive wizard | ✅ | ✅ Enhanced |
| Logging | ✅ | ✅ |
| Port checking | ✅ | ✅ Enhanced |
```

---

## System Requirements Section

Update system requirements:

```markdown
## System Requirements

### Linux/macOS
- Python 3.11+
- Node.js 18+ (optional, for MCP servers)
- 4GB RAM (8GB recommended)
- 5GB free disk space

### Windows
- Windows 10 (build 1809+) or Windows 11
- Python 3.11+ (with "Add to PATH" enabled)
- PowerShell 5.1+ (included in Windows 10/11)
- Node.js 18+ (optional, for MCP servers)
- 4GB RAM (8GB recommended)
- 5GB free disk space

### Docker
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
```

---

This content should be added to your main README.md to properly document Windows support.
