#Requires -Version 5.1
<#
.SYNOPSIS
    Install Antigravity Workspace on Windows
    
.DESCRIPTION
    Automated installation script for Windows 10/11
    - Checks prerequisites (Python 3.11+, Node.js)
    - Creates virtual environment
    - Installs Python dependencies
    - Installs MCP servers
    - Sets up configuration
    
.EXAMPLE
    .\install.ps1
    
.EXAMPLE
    .\install.ps1 -SkipMCP
    
.PARAMETER SkipMCP
    Skip MCP server installation
    
.PARAMETER SkipDocker
    Skip Docker-related checks and setup
    
.NOTES
    Windows 10/11 compatible
    Requires Administrator rights for some operations
#>

[CmdletBinding()]
param(
    [switch]$SkipMCP,
    [switch]$SkipDocker
)

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Script configuration
$script:LogFile = Join-Path $PSScriptRoot "install.log"
$script:RequiredPythonVersion = [Version]"3.11"
$script:RequiredNodeVersion = 18

# Colors for output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('Info', 'Success', 'Warning', 'Error')]
        [string]$Type = 'Info'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Type) {
        'Info'    { 'Cyan' }
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error'   { 'Red' }
    }
    
    $prefix = switch ($Type) {
        'Info'    { '[*]' }
        'Success' { '[✓]' }
        'Warning' { '[!]' }
        'Error'   { '[✗]' }
    }
    
    $logMessage = "[$timestamp] [$Type] $Message"
    Add-Content -Path $script:LogFile -Value $logMessage
    
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║     Antigravity Workspace - Windows Installation          ║" -ForegroundColor Blue
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══ $Title ═══" -ForegroundColor Blue
    Write-Host ""
}

function Test-Administrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PythonInstallation {
    Write-Section "Checking Python Installation"
    
    try {
        $pythonCmd = Get-Command python -ErrorAction Stop
        $versionOutput = & python --version 2>&1
        
        if ($versionOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $version = [Version]"$($matches[1]).$($matches[2]).$($matches[3])"
            
            if ($version -ge $script:RequiredPythonVersion) {
                Write-ColorOutput "Python $version found" -Type Success
                return $true
            }
            else {
                Write-ColorOutput "Python $version found, but 3.11+ required" -Type Error
                Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
                return $false
            }
        }
    }
    catch {
        Write-ColorOutput "Python not found" -Type Error
        Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation" -Type Warning
        return $false
    }
    
    return $false
}

function Test-PipInstallation {
    Write-ColorOutput "Checking pip..." -Type Info
    
    try {
        & python -m pip --version | Out-Null
        Write-ColorOutput "pip is available" -Type Success
        return $true
    }
    catch {
        Write-ColorOutput "pip not found" -Type Error
        Write-ColorOutput "Installing pip..." -Type Info
        
        try {
            & python -m ensurepip --upgrade
            Write-ColorOutput "pip installed" -Type Success
            return $true
        }
        catch {
            Write-ColorOutput "Failed to install pip" -Type Error
            return $false
        }
    }
}

function Test-NodeInstallation {
    Write-Section "Checking Node.js Installation"
    
    try {
        $nodeCmd = Get-Command node -ErrorAction Stop
        $versionOutput = & node --version 2>&1
        
        if ($versionOutput -match "v(\d+)") {
            $version = [int]$matches[1]
            
            if ($version -ge $script:RequiredNodeVersion) {
                Write-ColorOutput "Node.js $versionOutput found" -Type Success
                
                # Check npm
                try {
                    $npmVersion = & npm --version 2>&1
                    Write-ColorOutput "npm $npmVersion found" -Type Success
                }
                catch {
                    Write-ColorOutput "npm not found" -Type Warning
                }
                
                return $true
            }
            else {
                Write-ColorOutput "Node.js $versionOutput found, but v$($script:RequiredNodeVersion)+ recommended" -Type Warning
                Write-ColorOutput "Download from: https://nodejs.org/" -Type Info
                return $true # Don't fail, just warn
            }
        }
    }
    catch {
        Write-ColorOutput "Node.js not found" -Type Warning
        Write-ColorOutput "Download from: https://nodejs.org/" -Type Info
        Write-ColorOutput "Node.js is optional but recommended for MCP servers" -Type Info
        return $false
    }
    
    return $false
}

function New-VirtualEnvironment {
    Write-Section "Setting up Python Virtual Environment"
    
    $venvPath = Join-Path $PSScriptRoot "venv"
    
    if (Test-Path $venvPath) {
        Write-ColorOutput "Virtual environment already exists" -Type Success
        return $true
    }
    
    Write-ColorOutput "Creating virtual environment..." -Type Info
    
    try {
        & python -m venv venv
        Write-ColorOutput "Virtual environment created" -Type Success
        return $true
    }
    catch {
        Write-ColorOutput "Failed to create virtual environment: $_" -Type Error
        return $false
    }
}

function Enable-VirtualEnvironment {
    $activateScript = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        Write-ColorOutput "Activating virtual environment..." -Type Info
        
        try {
            # Set execution policy for this session
            Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
            
            & $activateScript
            Write-ColorOutput "Virtual environment activated" -Type Success
            return $true
        }
        catch {
            Write-ColorOutput "Failed to activate virtual environment: $_" -Type Warning
            Write-ColorOutput "Continuing with system Python..." -Type Info
            return $false
        }
    }
    
    return $false
}

function Install-PythonDependencies {
    Write-Section "Installing Python Dependencies"
    
    Write-ColorOutput "Upgrading pip..." -Type Info
    try {
        & python -m pip install --upgrade pip --quiet
        Write-ColorOutput "pip upgraded" -Type Success
    }
    catch {
        Write-ColorOutput "Failed to upgrade pip (continuing anyway)" -Type Warning
    }
    
    # Install root requirements
    $rootReqs = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $rootReqs) {
        Write-ColorOutput "Installing root requirements..." -Type Info
        try {
            & python -m pip install -r $rootReqs
            Write-ColorOutput "Root requirements installed" -Type Success
        }
        catch {
            Write-ColorOutput "Failed to install root requirements: $_" -Type Error
            return $false
        }
    }
    
    # Install backend requirements
    $backendReqs = Join-Path $PSScriptRoot "backend\requirements.txt"
    if (Test-Path $backendReqs) {
        Write-ColorOutput "Installing backend requirements..." -Type Info
        try {
            & python -m pip install -r $backendReqs
            Write-ColorOutput "Backend requirements installed" -Type Success
        }
        catch {
            Write-ColorOutput "Failed to install backend requirements: $_" -Type Error
            return $false
        }
    }
    else {
        Write-ColorOutput "Backend requirements.txt not found" -Type Warning
    }
    
    return $true
}

function Install-MCPServers {
    if ($SkipMCP) {
        Write-ColorOutput "Skipping MCP server installation (--SkipMCP flag)" -Type Info
        return $true
    }
    
    Write-Section "Installing MCP Servers"
    
    # Check if npm is available
    try {
        & npm --version | Out-Null
    }
    catch {
        Write-ColorOutput "npm not found - skipping MCP server installation" -Type Warning
        Write-ColorOutput "Install Node.js from https://nodejs.org/ to enable MCP servers" -Type Info
        return $true
    }
    
    # Core MCP servers
    $mcpServers = @(
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-sequential-thinking"
    )
    
    # Optional MCP servers
    $optionalServers = @(
        "mcp-server-docker"
    )
    
    Write-ColorOutput "Installing core MCP servers..." -Type Info
    
    foreach ($server in $mcpServers) {
        Write-ColorOutput "Installing $server..." -Type Info
        try {
            & npm install -g $server 2>&1 | Out-Null
            Write-ColorOutput "$server installed" -Type Success
        }
        catch {
            Write-ColorOutput "Failed to install $server (continuing...)" -Type Warning
        }
    }
    
    Write-ColorOutput "Installing optional MCP servers..." -Type Info
    
    foreach ($server in $optionalServers) {
        Write-ColorOutput "Installing $server..." -Type Info
        try {
            & npm install -g $server 2>&1 | Out-Null
            Write-ColorOutput "$server installed" -Type Success
        }
        catch {
            Write-ColorOutput "Optional $server not installed (this is okay)" -Type Info
        }
    }
    
    # Try to install Python MCP server
    Write-ColorOutput "Installing Python MCP server..." -Type Info
    try {
        & python -m pip install mcp-server-python-analysis --quiet
        Write-ColorOutput "Python MCP server installed" -Type Success
    }
    catch {
        Write-ColorOutput "Python MCP server not installed (optional)" -Type Info
    }
    
    Write-ColorOutput "MCP server installation completed" -Type Success
    return $true
}

function New-RequiredDirectories {
    Write-Section "Creating Required Directories"
    
    $directories = @(
        "drop_zone",
        "artifacts",
        "logs",
        "data",
        "frontend\static"
    )
    
    foreach ($dir in $directories) {
        $path = Join-Path $PSScriptRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            Write-ColorOutput "Created: $dir" -Type Info
        }
    }
    
    Write-ColorOutput "All directories ready" -Type Success
    return $true
}

function Initialize-Configuration {
    Write-Section "Setting up Configuration"
    
    $envPath = Join-Path $PSScriptRoot ".env"
    $envExamplePath = Join-Path $PSScriptRoot ".env.example"
    
    if (Test-Path $envPath) {
        Write-ColorOutput ".env file already exists" -Type Success
        
        $answer = 'N'  # Auto-proceed: skip reconfiguration (existing .env is good)
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            # Backup existing
            $backupPath = "$envPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $envPath $backupPath
            Write-ColorOutput "Backed up existing .env to $backupPath" -Type Info
        }
        else {
            return $true
        }
    }
    
    if (Test-Path $envExamplePath) {
        Copy-Item $envExamplePath $envPath
        Write-ColorOutput "Created .env from .env.example" -Type Success
    }
    else {
        Write-ColorOutput "Creating minimal .env file..." -Type Info
        
        $envContent = @"
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=

# OpenRouter API Key (access 100+ models from https://openrouter.ai/keys)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Local Model Settings
LOCAL_MODEL=llama3

# Active AI Model Selection
# Options: 'gemini', 'vertex', 'ollama', 'openrouter', 'auto'
ACTIVE_MODEL=auto

# Model Rotator (Multi-Key Support)
MODEL_ROTATOR_ENABLED=true
SWARM_AUTO_ROTATE_KEYS=true
SMART_RATE_LIMIT_HANDOFF=true

# Multiple keys (comma-separated for rotation)
GEMINI_API_KEYS=
OPENROUTER_API_KEYS=
OPENAI_API_KEYS=

# GitHub Token (get from https://github.com/settings/tokens)
# Required scopes: repo, read:org
COPILOT_MCP_GITHUB_TOKEN=

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# Advanced Settings
DEBUG_MODE=false
LOG_LEVEL=INFO

# ⚠ IMPORTANT: Fill in your actual API keys above
# Run .\configure.ps1 for interactive configuration wizard
"@
        Set-Content -Path $envPath -Value $envContent
        Write-ColorOutput ".env file created" -Type Success
    }
    
    Write-ColorOutput "Please edit .env with your API keys" -Type Warning
    
    $answer = 'n'  # Auto-proceed: skip interactive configuration
    if ($answer -ne 'n' -and $answer -ne 'N') {
        $configurePath = Join-Path $PSScriptRoot "configure.ps1"
        if (Test-Path $configurePath) {
            & $configurePath
        }
        else {
            Write-ColorOutput "Configuration wizard not found, opening in notepad..." -Type Info
            Start-Process notepad $envPath
        }
    }
    
    return $true
}

function Test-Installation {
    Write-Section "Verifying Installation"
    
    Write-ColorOutput "Testing Python imports..." -Type Info
    
    try {
        $testScript = @"
import sys
import logging

# Suppress warnings for clean output
logging.getLogger('chromadb').setLevel(logging.ERROR)

def test_imports():
    errors = []
    
    # Critical dependencies
    try:
        import fastapi
        import uvicorn
    except ImportError as e:
        print(f'CRITICAL_FAIL: {e}')
        return False

    # Optional but recommended
    try:
        import chromadb
    except Exception as e:
        # Catch pydantic errors on Python 3.14+
        print(f'OPTIONAL_WARNING: chromadb (Vector Store) failed to load: {e}')
        print('Vector capabilities will be disabled, but core features will work.')
    
    return True

if __name__ == '__main__':
    if test_imports():
        print('OK')
        sys.exit(0)
    else:
        sys.exit(1)
"@
        $result = $testScript | & python -
        
        if ($result -match 'OK') {
            if ($result -match 'OPTIONAL_WARNING') {
                Write-ColorOutput "Python dependencies verified (with warnings for optional components)" -Type Warning
                $result -split "`n" | Where-Object { $_ -match 'OPTIONAL_WARNING' } | ForEach-Object { Write-ColorOutput $_ -Type Info }
            }
            else {
                Write-ColorOutput "Python dependencies verified" -Type Success
            }
        }
        else {
            Write-ColorOutput "Python dependency verification failed: $result" -Type Error
        }
    }
    catch {
        Write-ColorOutput "Python dependency verification failed: $_" -Type Warning
    }
    
    Write-ColorOutput "Testing backend module..." -Type Info
    
    try {
        $backendPath = Join-Path $PSScriptRoot "backend"
        if (Test-Path $backendPath) {
            Push-Location $backendPath
            
            $testScript = @"
import sys
try:
    from main import app
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@
            $result = $testScript | & python -
            
            if ($result -eq 'OK') {
                Write-ColorOutput "Backend module loads successfully" -Type Success
            }
            else {
                Write-ColorOutput "Backend module has issues: $result" -Type Warning
            }
            
            Pop-Location
        }
    }
    catch {
        if (Get-Location -ne $PSScriptRoot) {
            Pop-Location
        }
        Write-ColorOutput "Backend module verification failed: $_" -Type Warning
    }
    
    Write-ColorOutput "Installation verification completed" -Type Success
    return $true
}

function Show-CompletionMessage {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                            ║" -ForegroundColor Green
    Write-Host "║        Installation Complete! 🎉                          ║" -ForegroundColor Green
    Write-Host "║                                                            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-ColorOutput "Next Steps:" -Type Success
    Write-Host ""
    Write-Host "  1. Edit configuration:" -ForegroundColor Cyan
    Write-Host "     notepad .env" -ForegroundColor White
    Write-Host ""
    Write-Host "  2. Or run configuration wizard:" -ForegroundColor Cyan
    Write-Host "     .\configure.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  3. Start the workspace:" -ForegroundColor Cyan
    Write-Host "     .\start.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  4. Access web interface:" -ForegroundColor Cyan
    Write-Host "     http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "  For detailed help, see:" -ForegroundColor Cyan
    Write-Host "     docs\WINDOWS_SETUP.md" -ForegroundColor White
    Write-Host ""
    Write-ColorOutput "Installation log saved to: $script:LogFile" -Type Info
    Write-Host ""
}

function Show-SystemInfo {
    Write-Section "System Information"
    
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor
    $memory = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $driveLetter = (Split-Path -Qualifier $PSScriptRoot).TrimEnd(':')
    $freeSpace = [math]::Round((Get-PSDrive $driveLetter).Free / 1GB, 2)
    
    Write-Host "OS: $($os.Caption) $($os.Version)" -ForegroundColor Gray
    Write-Host "CPU: $($cpu.Name)" -ForegroundColor Gray
    Write-Host "RAM: $memory GB" -ForegroundColor Gray
    Write-Host "Free Disk Space: $freeSpace GB" -ForegroundColor Gray
    
    if ($memory -lt 2) {
        Write-ColorOutput "Warning: Less than 2GB RAM available" -Type Warning
    }
    
    if ($freeSpace -lt 5) {
        Write-ColorOutput "Warning: Less than 5GB disk space available" -Type Warning
    }
}

# Main installation flow
function Main {
    Write-Header
    
    # Check if running as admin (optional warning)
    if (-not (Test-Administrator)) {
        Write-ColorOutput "Not running as Administrator" -Type Warning
        Write-ColorOutput "Some operations may require elevation" -Type Info
        Write-Host ""
    }
    
    # Initialize log file
    "Installation started at $(Get-Date)" | Out-File -FilePath $script:LogFile
    
    # Show system info
    Show-SystemInfo
    
    # Check prerequisites
    if (-not (Test-PythonInstallation)) {
        Write-Host ""
        Write-ColorOutput "Python 3.11+ is required. Please install it first." -Type Error
        Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation!" -Type Warning
        exit 1
    }
    
    if (-not (Test-PipInstallation)) {
        Write-Host ""
        Write-ColorOutput "pip is required but couldn't be installed" -Type Error
        exit 1
    }
    
    # Node.js is optional
    $hasNode = Test-NodeInstallation
    if (-not $hasNode) {
        Write-ColorOutput "Node.js is recommended but not required" -Type Warning
        Write-ColorOutput "You can install it later from: https://nodejs.org/" -Type Info
    }
    
    # Create virtual environment
    if (-not (New-VirtualEnvironment)) {
        Write-Host ""
        Write-ColorOutput "Failed to create virtual environment" -Type Error
        exit 1
    }
    
    # Activate virtual environment
    Enable-VirtualEnvironment | Out-Null
    
    # Install Python dependencies
    if (-not (Install-PythonDependencies)) {
        Write-Host ""
        Write-ColorOutput "Failed to install Python dependencies" -Type Error
        exit 1
    }
    
    # Install MCP servers (if Node.js available)
    if ($hasNode) {
        Install-MCPServers | Out-Null
    }
    else {
        Write-ColorOutput "Skipping MCP servers (Node.js not available)" -Type Info
    }
    
    # Create directories
    New-RequiredDirectories | Out-Null
    
    # Setup configuration
    Initialize-Configuration | Out-Null
    
    # Verify installation
    Test-Installation | Out-Null
    
    # Show completion message
    Show-CompletionMessage
}

# Run main installation
try {
    Main
}
catch {
    Write-Host ""
    Write-ColorOutput "Installation failed: $_" -Type Error
    Write-ColorOutput "Check log file: $script:LogFile" -Type Info
    exit 1
}
