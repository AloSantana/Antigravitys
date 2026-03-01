#Requires -Version 5.1
<#
.SYNOPSIS
    Install Antigravity Workspace on Windows -- Comprehensive Installer
    
.DESCRIPTION
    The "one big script" installer for Antigravity Workspace on Windows 10/11.
    Checks ALL prerequisites, installs ALL dependencies, auto-detects and fixes
    common issues, verifies the installation, and prepares the workspace.
    
    Features:
    - Python 3.11+ validation with pip bootstrap
    - Node.js 18+ validation (optional, for MCP)
    - Virtual environment creation/activation
    - pip dependency installation (root + backend)
    - MCP server installation (core + optional + Python)
    - Required directory creation
    - .env setup from .env.example
    - Auto-fix mode: __init__.py, execution policy, port checks
    - Full verification: Python imports, backend module load, port availability
    - Colored output with progress tracking
    - Comprehensive logging
    
.EXAMPLE
    .\install.ps1
    
.EXAMPLE
    .\install.ps1 -SkipMCP
    
.EXAMPLE
    .\install.ps1 -AutoFix
    
.EXAMPLE
    .\install.ps1 -SkipMCP -SkipDocker -AutoFix
    
.PARAMETER SkipMCP
    Skip MCP server installation
    
.PARAMETER SkipDocker
    Skip Docker-related checks and setup
    
.PARAMETER AutoFix
    Enable auto-fix mode: automatically detect and fix common issues
    
.NOTES
    Windows 10/11 compatible
    Some operations may benefit from Administrator rights
#>

[CmdletBinding()]
param(
    [switch]$SkipMCP,
    [switch]$SkipDocker,
    [switch]$AutoFix
)

# ============================================================
# YOLO MODE -- Auto-execution enforcement (P0, immutable)
# All commands, installs, and operations are pre-approved.
# No confirmation prompts. Always continue forward.
# ============================================================
$env:ANTIGRAVITY_YOLO_MODE    = "1"
$env:ANTIGRAVITY_PLATFORM     = "windows"
$env:ANTIGRAVITY_AUTO_APPROVE = "true"
$ConfirmPreference            = "None"
$InformationPreference        = "Continue"

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Script configuration
$script:ProjectRoot = $PSScriptRoot
$script:LogFile = Join-Path $PSScriptRoot "install.log"
$script:RequiredPythonVersion = [Version]"3.11"
$script:RequiredNodeVersion = 18
$script:ErrorCount = 0
$script:WarningCount = 0
$script:FixCount = 0
$script:StartTime = Get-Date

# ----------------------------------------------
# Output helpers
# ----------------------------------------------

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
        'Success' { '[OK]' }
        'Warning' { '[!]' }
        'Error'   { '[X]' }
    }
    
    $logMessage = "[$timestamp] [$Type] $Message"
    Add-Content -Path $script:LogFile -Value $logMessage
    
    Write-Host "$prefix $Message" -ForegroundColor $color
    
    # Track counters
    if ($Type -eq 'Error')   { $script:ErrorCount++ }
    if ($Type -eq 'Warning') { $script:WarningCount++ }
}

function Write-Header {
    Write-Host ""
    Write-Host "+==================================================================+" -ForegroundColor Blue
    Write-Host "|                                                                  |" -ForegroundColor Blue
    Write-Host "|   *  Antigravity Workspace -- Comprehensive Installer  *         |" -ForegroundColor Blue
    Write-Host "|                                                                  |" -ForegroundColor Blue
    Write-Host "+==================================================================+" -ForegroundColor Blue
    Write-Host ""
    
    $flags = @()
    if ($SkipMCP)    { $flags += "SkipMCP" }
    if ($SkipDocker) { $flags += "SkipDocker" }
    if ($AutoFix)    { $flags += "AutoFix" }
    
    if ($flags.Count -gt 0) {
        Write-Host "  Flags: $($flags -join ', ')" -ForegroundColor DarkGray
        Write-Host ""
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "--------------------------------------------------------------" -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host "--------------------------------------------------------------" -ForegroundColor Blue
    Write-Host ""
}

# ----------------------------------------------
# System information
# ----------------------------------------------

function Show-SystemInfo {
    Write-Section "System Information"
    
    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = Get-CimInstance Win32_Processor
        $memory = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        $freeMemory = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $driveLetter = (Split-Path -Qualifier $PSScriptRoot).TrimEnd(':')
        $drive = Get-PSDrive $driveLetter
        $freeSpace = [math]::Round($drive.Free / 1GB, 2)
        $totalSpace = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)
        
        Write-Host "  OS           : $($os.Caption) $($os.Version)" -ForegroundColor Gray
        Write-Host "  CPU          : $($cpu.Name)" -ForegroundColor Gray
        Write-Host "  RAM          : $freeMemory GB free / $memory GB total" -ForegroundColor Gray
        $diskLabel = 'Disk (' + $driveLetter + ':)'
        Write-Host "  $diskLabel    : $freeSpace GB free / $totalSpace GB total" -ForegroundColor Gray
        Write-Host "  Project Dir  : $PSScriptRoot" -ForegroundColor Gray
        Write-Host "  PowerShell   : $($PSVersionTable.PSVersion)" -ForegroundColor Gray
        Write-Host "  Date         : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
        Write-Host ""
        
        if ($memory -lt 2) {
            Write-ColorOutput "Warning: Less than 2GB RAM available" -Type Warning
        }
        
        if ($freeSpace -lt 5) {
            Write-ColorOutput "Warning: Less than 5GB disk space available" -Type Warning
        }
    }
    catch {
        Write-ColorOutput "Could not retrieve full system info: $_" -Type Warning
    }
}

function Test-Administrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ----------------------------------------------
# Prerequisite checks
# ----------------------------------------------

function Test-PythonInstallation {
    Write-Section "Checking Python Installation"
    
    try {
        $pythonCmd = Get-Command python -ErrorAction Stop
        $versionOutput = & python --version 2>&1
        
        if ($versionOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $version = [Version]"$($matches[1]).$($matches[2]).$($matches[3])"
            
            Write-Host "  Path    : $($pythonCmd.Source)" -ForegroundColor Gray
            Write-Host "  Version : $version" -ForegroundColor Gray
            Write-Host ""
            
            if ($version -ge $script:RequiredPythonVersion) {
                Write-ColorOutput "Python $version found -- meets requirement (3.11+)" -Type Success
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
        Write-ColorOutput "Python not found in PATH" -Type Error
        Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation" -Type Warning
        return $false
    }
    
    return $false
}

function Test-PipInstallation {
    Write-ColorOutput "Checking pip..." -Type Info
    
    try {
        $ErrorActionPreference = "Continue"
        $pipVersion = & python -m pip --version 2>&1
        $ErrorActionPreference = "Stop"
        if ($pipVersion -match "pip (\S+)") {
            Write-ColorOutput "pip $($matches[1]) is available" -Type Success
        } else {
            Write-ColorOutput "pip is available" -Type Success
        }
        return $true
    }
    catch {
        Write-ColorOutput "pip not found -- attempting bootstrap..." -Type Warning
        
        try {
            $ErrorActionPreference = "Continue"
            & python -m ensurepip --upgrade 2>&1 | Out-Null
            $ErrorActionPreference = "Stop"
            Write-ColorOutput "pip bootstrapped successfully" -Type Success
            return $true
        }
        catch {
            Write-ColorOutput "pip bootstrap failed: $_" -Type Error
            Write-ColorOutput "Install pip manually: python -m ensurepip --upgrade" -Type Info
            return $false
        }
    }
}

function Test-NodeInstallation {
    Write-Section "Checking Node.js Installation"
    
    try {
        $nodeCmd = Get-Command node -ErrorAction Stop
        $versionOutput = & node --version 2>&1
        
        Write-Host "  Path    : $($nodeCmd.Source)" -ForegroundColor Gray
        Write-Host "  Version : $versionOutput" -ForegroundColor Gray
        Write-Host ""
        
        if ($versionOutput -match "v(\d+)") {
            $version = [int]$matches[1]
            
            if ($version -ge $script:RequiredNodeVersion) {
                Write-ColorOutput "Node.js $versionOutput found -- meets requirement (v$($script:RequiredNodeVersion)+)" -Type Success
                
                # Check npm
                try {
                    $npmVersion = & npm --version 2>&1
                    Write-ColorOutput "npm $npmVersion found" -Type Success
                }
                catch {
                    Write-ColorOutput "npm not found -- MCP servers may fail to install" -Type Warning
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
        Write-ColorOutput "Node.js is optional but recommended for MCP servers" -Type Info
        Write-ColorOutput "Download from: https://nodejs.org/" -Type Info
        return $false
    }
    
    return $false
}

# ----------------------------------------------
# Virtual environment
# ----------------------------------------------

function New-VirtualEnvironment {
    Write-Section "Setting up Python Virtual Environment"
    
    $venvPath = Join-Path $PSScriptRoot "venv"
    
    if (Test-Path $venvPath) {
        # Validate existing venv
        $venvPython = Join-Path $venvPath "Scripts\python.exe"
        if (Test-Path $venvPython) {
            Write-ColorOutput "Virtual environment already exists and has python.exe" -Type Success
            return $true
        }
        else {
            Write-ColorOutput "Virtual environment exists but is broken (no python.exe)" -Type Warning
            if ($AutoFix) {
                Write-ColorOutput "AutoFix: Removing broken venv and recreating..." -Type Info
                Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
                $script:FixCount++
            }
            else {
                Write-ColorOutput "Run with -AutoFix to automatically recreate" -Type Info
                return $false
            }
        }
    }
    
    Write-ColorOutput "Creating virtual environment..." -Type Info
    
    try {
        & python -m venv venv
        Write-ColorOutput "Virtual environment created at: $venvPath" -Type Success
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
            # Dot-source the activation script (no execution policy change needed
            # because the calling script is already running with -ExecutionPolicy Bypass)
            . $activateScript
            Write-ColorOutput "Virtual environment activated" -Type Success
            return $true
        }
        catch {
            # Fallback: manually set PATH to use venv python/pip
            Write-ColorOutput "Standard activation failed, using PATH fallback..." -Type Warning
            $venvScripts = Join-Path $PSScriptRoot "venv\Scripts"
            if (Test-Path (Join-Path $venvScripts "python.exe")) {
                $env:VIRTUAL_ENV = Join-Path $PSScriptRoot "venv"
                $env:PATH = "$venvScripts;$env:PATH"
                Write-ColorOutput "Virtual environment activated (PATH fallback)" -Type Success
                return $true
            }
            Write-ColorOutput "Failed to activate virtual environment: $_" -Type Warning
            Write-ColorOutput "Continuing with system Python..." -Type Info
            return $false
        }
    }
    
    return $false
}

# ----------------------------------------------
# Python dependencies
# ----------------------------------------------

function Install-PythonDependencies {
    Write-Section "Installing Python Dependencies"
    
    # Temporarily allow errors from native commands (pip writes warnings to stderr)
    $savedEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    
    Write-ColorOutput "Upgrading pip..." -Type Info
    $pipOutput = & python -m pip install --upgrade pip --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "pip upgraded" -Type Success
    } else {
        Write-ColorOutput "pip upgrade returned exit code $LASTEXITCODE (continuing anyway)" -Type Warning
    }
    
    # Install root requirements
    $rootReqs = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $rootReqs) {
        $pkgCount = (Get-Content $rootReqs | Where-Object { $_ -and -not $_.StartsWith('#') } | Measure-Object).Count
        Write-ColorOutput "Installing root requirements - $pkgCount packages..." -Type Info
        $pipOutput = & python -m pip install -r $rootReqs 2>&1
        $pipExitCode = $LASTEXITCODE
        # Show key output lines
        foreach ($rawLine in $pipOutput) {
            $line = "$rawLine"
            if ($line -match "Successfully installed") {
                Write-ColorOutput "  $line" -Type Success
            } elseif ($line -match "WARNING") {
                Write-ColorOutput "  $line" -Type Warning
            }
        }
        if ($pipExitCode -ne 0) {
            Write-ColorOutput "pip exited with code $pipExitCode for root requirements" -Type Error
            $ErrorActionPreference = $savedEAP
            return $false
        }
        Write-ColorOutput "Root requirements installed" -Type Success
    }
    else {
        Write-ColorOutput "Root requirements.txt not found" -Type Warning
    }
    
    # Install backend requirements
    $backendReqs = Join-Path $PSScriptRoot "backend\requirements.txt"
    if (Test-Path $backendReqs) {
        $pkgCount = (Get-Content $backendReqs | Where-Object { $_ -and -not $_.StartsWith('#') } | Measure-Object).Count
        Write-ColorOutput "Installing backend requirements - $pkgCount packages..." -Type Info
        $pipOutput = & python -m pip install -r $backendReqs 2>&1
        $pipExitCode = $LASTEXITCODE
        foreach ($rawLine in $pipOutput) {
            $line = "$rawLine"
            if ($line -match "Successfully installed") {
                Write-ColorOutput "  $line" -Type Success
            } elseif ($line -match "WARNING") {
                Write-ColorOutput "  $line" -Type Warning
            }
        }
        if ($pipExitCode -ne 0) {
            Write-ColorOutput "pip exited with code $pipExitCode for backend requirements" -Type Error
            $ErrorActionPreference = $savedEAP
            return $false
        }
        Write-ColorOutput "Backend requirements installed" -Type Success
    }
    else {
        Write-ColorOutput "Backend requirements.txt not found" -Type Warning
    }
    
    # Restore error preference
    $ErrorActionPreference = $savedEAP
    return $true
}

# ----------------------------------------------
# MCP servers
# ----------------------------------------------

function Install-MCPServers {
    if ($SkipMCP) {
        Write-ColorOutput "Skipping MCP server installation (-SkipMCP flag)" -Type Info
        return $true
    }
    
    Write-Section "Installing MCP Servers"
    
    # Temporarily allow stderr from native commands
    $savedEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    
    # Check if npm is available
    & npm --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "npm not found -- skipping MCP server installation" -Type Warning
        Write-ColorOutput "Install Node.js from https://nodejs.org/ to enable MCP servers" -Type Info
        $ErrorActionPreference = $savedEAP
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
    
    $installed = 0
    $failed = 0
    
    Write-ColorOutput "Installing core MCP servers ($($mcpServers.Count))..." -Type Info
    
    foreach ($server in $mcpServers) {
        Write-ColorOutput "  Installing $server..." -Type Info
        & npm install -g $server 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "  $server installed" -Type Success
            $installed++
        } else {
            Write-ColorOutput "  Failed to install $server" -Type Warning
            $failed++
        }
    }
    
    Write-ColorOutput "Installing optional MCP servers ($($optionalServers.Count))..." -Type Info
    
    foreach ($server in $optionalServers) {
        Write-ColorOutput "  Installing $server..." -Type Info
        & npm install -g $server 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "  $server installed" -Type Success
            $installed++
        } else {
            Write-ColorOutput "  Optional $server not installed (this is okay)" -Type Info
        }
    }
    
    # Python MCP server
    Write-ColorOutput "Installing Python MCP server..." -Type Info
    & python -m pip install mcp-server-python-analysis --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "  Python MCP server installed" -Type Success
        $installed++
    } else {
        Write-ColorOutput "  Python MCP server not installed (optional)" -Type Info
    }
    
    $ErrorActionPreference = $savedEAP
    Write-ColorOutput "MCP servers: $installed installed, $failed failed" -Type $(if ($failed -gt 0) { 'Warning' } else { 'Success' })
    return $true
}

# ----------------------------------------------
# Directories
# ----------------------------------------------

function New-RequiredDirectories {
    Write-Section "Creating Required Directories"
    
    $directories = @(
        "drop_zone",
        "artifacts",
        "artifacts\code",
        "artifacts\diffs",
        "artifacts\tests",
        "artifacts\screenshots",
        "artifacts\reports",
        "artifacts\logs",
        "logs",
        "data",
        "uploads",
        "frontend\static"
    )
    
    $created = 0
    $existed = 0
    
    foreach ($dir in $directories) {
        $path = Join-Path $PSScriptRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            $created++
        }
        else {
            $existed++
        }
    }
    
    Write-ColorOutput "Directories: $created created, $existed already existed" -Type Success
    return $true
}

# ----------------------------------------------
# Configuration (.env)
# ----------------------------------------------

function Initialize-Configuration {
    Write-Section "Setting up Configuration"
    
    $envPath = Join-Path $PSScriptRoot ".env"
    $envExamplePath = Join-Path $PSScriptRoot ".env.example"
    
    if (Test-Path $envPath) {
        Write-ColorOutput ".env file already exists" -Type Success
        
        # Verify it has content
        $content = Get-Content $envPath -Raw
        if ([string]::IsNullOrWhiteSpace($content)) {
            Write-ColorOutput ".env exists but is empty!" -Type Warning
            if (Test-Path $envExamplePath) {
                Copy-Item $envExamplePath $envPath -Force
                Write-ColorOutput "Restored .env from .env.example" -Type Success
                if ($AutoFix) { $script:FixCount++ }
            }
        }
        else {
            # Count configured keys
            $keyCount = (Get-Content $envPath | Where-Object { $_ -match "^\w+=.+" -and -not $_.StartsWith('#') } | Measure-Object).Count
            Write-ColorOutput "  $keyCount environment variables configured" -Type Info
        }
        
        return $true
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
NGROK_ENABLED=false

# Security Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# Advanced Settings
DEBUG_MODE=false
LOG_LEVEL=INFO

# Fill in your actual API keys above
# Run .\configure.ps1 for interactive configuration wizard
"@
        Set-Content -Path $envPath -Value $envContent
        Write-ColorOutput ".env file created" -Type Success
    }
    
    Write-ColorOutput "Edit .env with your API keys, or run .\configure.ps1" -Type Warning
    
    return $true
}

# ----------------------------------------------
# Auto-fix: detect and fix common issues
# ----------------------------------------------

function Invoke-AutoFix {
    if (-not $AutoFix) { return }
    
    Write-Section "Auto-Fix: Detecting and Fixing Issues"
    
    $fixesBefore = $script:FixCount
    
    # --- Fix 1: __init__.py in Python package directories ---
    Write-ColorOutput "Checking __init__.py files in Python packages..." -Type Info
    
    $pythonDirs = @(
        "backend",
        "backend\agent",
        "backend\rag",
        "backend\utils",
        "backend\cli",
        "src",
        "src\agents",
        "src\sandbox",
        "src\tools"
    )
    
    foreach ($dir in $pythonDirs) {
        $dirPath = Join-Path $PSScriptRoot $dir
        if (Test-Path $dirPath) {
            $initFile = Join-Path $dirPath "__init__.py"
            if (-not (Test-Path $initFile)) {
                # Check if there are any .py files in this directory
                $pyFiles = Get-ChildItem -Path $dirPath -Filter "*.py" -ErrorAction SilentlyContinue
                if ($pyFiles.Count -gt 0) {
                    New-Item -ItemType File -Path $initFile -Force | Out-Null
                    Write-ColorOutput "  Created: $dir\__init__.py" -Type Success
                    $script:FixCount++
                }
            }
        }
    }
    
    # --- Fix 2: .gitkeep in empty directories ---
    Write-ColorOutput "Checking .gitkeep in required directories..." -Type Info
    
    $keepDirs = @("drop_zone", "artifacts", "logs", "data", "uploads")
    
    foreach ($dir in $keepDirs) {
        $dirPath = Join-Path $PSScriptRoot $dir
        if (Test-Path $dirPath) {
            $gitkeep = Join-Path $dirPath ".gitkeep"
            if (-not (Test-Path $gitkeep)) {
                $items = Get-ChildItem $dirPath -ErrorAction SilentlyContinue
                if ($items.Count -eq 0) {
                    New-Item -ItemType File -Path $gitkeep -Force | Out-Null
                    Write-ColorOutput "  Created: $dir\.gitkeep" -Type Success
                    $script:FixCount++
                }
            }
        }
    }
    
    # --- Fix 3: Execution policy check ---
    Write-ColorOutput "Checking PowerShell execution policy..." -Type Info
    
    $policy = Get-ExecutionPolicy -Scope CurrentUser
    if ($policy -eq "Restricted") {
        Write-ColorOutput "  Execution policy is Restricted -- setting to RemoteSigned for CurrentUser" -Type Warning
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-ColorOutput "  Execution policy updated to RemoteSigned" -Type Success
            $script:FixCount++
        }
        catch {
            Write-ColorOutput "  Could not update execution policy (may need admin rights)" -Type Warning
        }
    }
    else {
        Write-ColorOutput "  Execution policy is '$policy' -- OK" -Type Success
    }
    
    # --- Fix 4: Check for common missing files ---
    Write-ColorOutput "Checking for required project files..." -Type Info
    
    $requiredFiles = @(
        @{ Path = "backend\main.py"; Desc = "Backend entry point" },
        @{ Path = "frontend\index.html"; Desc = "Frontend HTML" },
        @{ Path = "requirements.txt"; Desc = "Root requirements" },
        @{ Path = "backend\requirements.txt"; Desc = "Backend requirements" }
    )
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $PSScriptRoot $file.Path
        if (Test-Path $filePath) {
            Write-ColorOutput "  $($file.Desc): OK" -Type Success
        }
        else {
            Write-ColorOutput "  $($file.Desc) MISSING: $($file.Path)" -Type Error
        }
    }
    
    # --- Fix 5: Check OpenCode integration files ---
    Write-ColorOutput "Checking OpenCode integration..." -Type Info
    
    $openCodeDir = Join-Path $PSScriptRoot ".opencode"
    if (Test-Path $openCodeDir) {
        Write-ColorOutput "  .opencode/ directory exists" -Type Success
    }
    else {
        Write-ColorOutput "  .opencode/ directory not found (OpenCode not configured)" -Type Info
    }
    
    $openCodeFiles = @("opencode.json", "mcp.json", "mcp_servers.json")
    foreach ($file in $openCodeFiles) {
        $filePath = Join-Path $PSScriptRoot $file
        if (Test-Path $filePath) {
            Write-ColorOutput "  $file exists" -Type Success
        }
        else {
            Write-ColorOutput "  $file not found" -Type Info
        }
    }
    
    # --- Fix 6: Port availability ---
    Write-ColorOutput "Checking port availability..." -Type Info
    
    try {
        $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
        if ($port8000) {
            Write-ColorOutput "  Port 8000 is IN USE by PID $($port8000.OwningProcess)" -Type Warning
            Write-ColorOutput "  The start script will handle this, but you may want to stop the process" -Type Info
        }
        else {
            Write-ColorOutput "  Port 8000 is available" -Type Success
        }
    }
    catch {
        Write-ColorOutput "  Port 8000 appears available" -Type Success
    }
    
    $fixesApplied = $script:FixCount - $fixesBefore
    if ($fixesApplied -gt 0) {
        Write-ColorOutput "Auto-fix applied $fixesApplied fixes" -Type Success
    }
    else {
        Write-ColorOutput "Auto-fix: No issues to fix -- everything looks good!" -Type Success
    }
}

# ----------------------------------------------
# Docker check (optional)
# ----------------------------------------------

function Test-DockerInstallation {
    if ($SkipDocker) {
        Write-ColorOutput "Skipping Docker check (-SkipDocker flag)" -Type Info
        return $true
    }
    
    Write-ColorOutput "Checking Docker..." -Type Info
    
    try {
        $dockerVersion = & docker --version 2>&1
        Write-ColorOutput "Docker found: $dockerVersion" -Type Success
        
        # Check if Docker daemon is running
        try {
            & docker info 2>&1 | Out-Null
            Write-ColorOutput "Docker daemon is running" -Type Success
        }
        catch {
            Write-ColorOutput "Docker is installed but daemon is not running" -Type Warning
            Write-ColorOutput "Start Docker Desktop to use containerized services" -Type Info
        }
    }
    catch {
        Write-ColorOutput "Docker not found (optional -- not required for local development)" -Type Info
    }
    
    return $true
}

# ----------------------------------------------
# Verification
# ----------------------------------------------

function Test-Installation {
    Write-Section "Verifying Installation"
    
    $verifyOk = $true
    
    # --- Test 1: Python imports ---
    Write-ColorOutput "Testing Python imports..." -Type Info
    
    try {
        $testScript = @"
import sys
import logging

# Suppress warnings for clean output
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('pydantic').setLevel(logging.ERROR)

def test_imports():
    results = []
    
    # Critical dependencies
    critical = ['fastapi', 'uvicorn', 'pydantic', 'dotenv']
    for pkg in critical:
        try:
            mod = pkg if pkg != 'dotenv' else 'dotenv'
            __import__(mod)
            results.append(f'OK:{pkg}')
        except ImportError as e:
            results.append(f'FAIL:{pkg}:{e}')
    
    # Important but non-critical
    optional = ['chromadb', 'langchain', 'aiohttp', 'websockets']
    for pkg in optional:
        try:
            __import__(pkg)
            results.append(f'OK:{pkg}')
        except Exception as e:
            results.append(f'WARN:{pkg}:{e}')
    
    return results

if __name__ == '__main__':
    results = test_imports()
    for r in results:
        print(r)
    
    failures = [r for r in results if r.startswith('FAIL:')]
    sys.exit(1 if failures else 0)
"@
        $ErrorActionPreference = "Continue"
        $tempPy = Join-Path $PSScriptRoot "_verify_imports.py"
        $testScript | Set-Content -Path $tempPy -Encoding ASCII -Force
        $venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
        if (-not (Test-Path $venvPython)) { $venvPython = "python" }
        $result = & $venvPython $tempPy 2>&1 | Out-String
        $testExitCode = $LASTEXITCODE
        $ErrorActionPreference = "Stop"
        Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
        
        $lines = $result -split "`n" | Where-Object { $_.Trim() }
        $okCount = @($lines | Where-Object { $_ -match '^OK:' }).Count
        $failCount = @($lines | Where-Object { $_ -match '^FAIL:' }).Count
        $warnCount = @($lines | Where-Object { $_ -match '^WARN:' }).Count
        
        foreach ($line in $lines) {
            if ($line -match '^OK:(.+)') {
                Write-ColorOutput "  + $($matches[1])" -Type Success
            }
            elseif ($line -match '^FAIL:(.+):(.+)') {
                Write-ColorOutput "  x $($matches[1]): $($matches[2])" -Type Error
                $verifyOk = $false
            }
            elseif ($line -match '^WARN:(.+):(.+)') {
                Write-ColorOutput "  ! $($matches[1]): $($matches[2])" -Type Warning
            }
        }
        
        Write-ColorOutput "Python imports: $okCount OK, $warnCount warnings, $failCount failures" -Type $(if ($failCount -gt 0) { 'Error' } elseif ($warnCount -gt 0) { 'Warning' } else { 'Success' })
    }
    catch {
        Write-ColorOutput "Python import verification failed: $_" -Type Warning
    }
    
    # --- Test 2: Backend module load ---
    Write-ColorOutput "Testing backend module load..." -Type Info
    
    try {
        $backendPath = Join-Path $PSScriptRoot "backend"
        if (Test-Path $backendPath) {
            Push-Location $backendPath
            
            $testScript = @"
import sys
import os
import logging
logging.disable(logging.CRITICAL)

try:
    from main import app
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@
            $ErrorActionPreference = "Continue"
            $tempPy = Join-Path $backendPath "_verify_backend.py"
            $testScript | Set-Content -Path $tempPy -Encoding ASCII -Force
            $venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
            if (-not (Test-Path $venvPython)) { $venvPython = "python" }
            $result = & $venvPython $tempPy 2>&1 | Out-String
            $backendExitCode = $LASTEXITCODE
            $ErrorActionPreference = "Stop"
            Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
            
            if ($result -match 'OK') {
                Write-ColorOutput "Backend module loads successfully" -Type Success
            }
            else {
                Write-ColorOutput "Backend module has issues: $result" -Type Warning
            }
            
            Pop-Location
        }
        else {
            Write-ColorOutput "Backend directory not found!" -Type Error
            $verifyOk = $false
        }
    }
    catch {
        if ((Get-Location).Path -ne $PSScriptRoot) {
            Pop-Location
        }
        Write-ColorOutput "Backend module verification failed: $_" -Type Warning
    }
    
    # --- Test 3: Port availability ---
    Write-ColorOutput "Checking port 8000 availability..." -Type Info
    
    try {
        $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
        if ($port8000) {
            Write-ColorOutput "Port 8000 is currently in use -- start.ps1 will handle this" -Type Warning
        }
        else {
            Write-ColorOutput "Port 8000 is available" -Type Success
        }
    }
    catch {
        Write-ColorOutput "Port 8000 appears available" -Type Success
    }
    
    # --- Test 4: Git status ---
    Write-ColorOutput "Checking git repository..." -Type Info
    
    try {
        $gitBranch = & git rev-parse --abbrev-ref HEAD 2>&1
        $gitCommit = & git rev-parse --short HEAD 2>&1
        Write-ColorOutput "Git: branch '$gitBranch', commit $gitCommit" -Type Success
    }
    catch {
        Write-ColorOutput "Not a git repository or git not installed" -Type Info
    }
    
    return $verifyOk
}

# ----------------------------------------------
# Completion
# ----------------------------------------------

function Show-CompletionMessage {
    $elapsed = (Get-Date) - $script:StartTime
    $elapsedStr = "{0:mm\:ss}" -f $elapsed
    
    Write-Host ""
    
    if ($script:ErrorCount -eq 0) {
        Write-Host "+==================================================================+" -ForegroundColor Green
        Write-Host "|                                                                  |" -ForegroundColor Green
        Write-Host "|          Installation Complete!  *  Antigravity Ready             |" -ForegroundColor Green
        Write-Host "|                                                                  |" -ForegroundColor Green
        Write-Host "+==================================================================+" -ForegroundColor Green
    }
    else {
        Write-Host "+==================================================================+" -ForegroundColor Yellow
        Write-Host "|                                                                  |" -ForegroundColor Yellow
        Write-Host "|       Installation Complete (with $($script:ErrorCount) error(s))                   |" -ForegroundColor Yellow
        Write-Host "|                                                                  |" -ForegroundColor Yellow
        Write-Host "+==================================================================+" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "  Summary:" -ForegroundColor White
    Write-Host "    Time elapsed : $elapsedStr" -ForegroundColor Gray
    Write-Host "    Errors       : $($script:ErrorCount)" -ForegroundColor $(if ($script:ErrorCount -gt 0) { 'Red' } else { 'Green' })
    Write-Host "    Warnings     : $($script:WarningCount)" -ForegroundColor $(if ($script:WarningCount -gt 0) { 'Yellow' } else { 'Green' })
    if ($AutoFix) {
        Write-Host "    Fixes applied : $($script:FixCount)" -ForegroundColor $(if ($script:FixCount -gt 0) { 'Cyan' } else { 'Green' })
    }
    Write-Host ""
    
    Write-Host "  Next Steps:" -ForegroundColor White
    Write-Host ""
    Write-Host "    1. Configure API keys:" -ForegroundColor Cyan
    Write-Host "       notepad .env" -ForegroundColor White
    Write-Host "       -- or --" -ForegroundColor DarkGray
    Write-Host "       .\configure.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "    2. Start the workspace:" -ForegroundColor Cyan
    Write-Host "       .\start.ps1" -ForegroundColor White
    Write-Host "       -- or --" -ForegroundColor DarkGray
    Write-Host "       start.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "    3. Access web interface:" -ForegroundColor Cyan
    Write-Host "       http://localhost:8000" -ForegroundColor White
    Write-Host ""
    
    if ($script:ErrorCount -gt 0) {
        Write-Host "  Troubleshooting:" -ForegroundColor Yellow
        Write-Host "    - Re-run with -AutoFix: .\install.ps1 -AutoFix" -ForegroundColor White
        Write-Host "    - Check log file: $($script:LogFile)" -ForegroundColor White
        Write-Host "    - See docs\WINDOWS_SETUP.md for detailed help" -ForegroundColor White
        Write-Host ""
    }
    
    Write-ColorOutput "Log saved to: $($script:LogFile)" -Type Info
    Write-Host ""
}

# ----------------------------------------------
# Main installation flow
# ----------------------------------------------

function Main {
    Write-Header
    
    # Check if running as admin (optional warning)
    if (-not (Test-Administrator)) {
        Write-ColorOutput "Not running as Administrator (some operations may need elevation)" -Type Info
    }
    else {
        Write-ColorOutput "Running as Administrator" -Type Success
    }
    
    # Initialize log file
    "===========================================================" | Out-File -FilePath $script:LogFile
    "Antigravity Workspace Installation" | Add-Content -Path $script:LogFile
    "Started: $(Get-Date)" | Add-Content -Path $script:LogFile
    "Flags: SkipMCP=$SkipMCP, SkipDocker=$SkipDocker, AutoFix=$AutoFix" | Add-Content -Path $script:LogFile
    "===========================================================" | Add-Content -Path $script:LogFile
    
    # Show system info
    Show-SystemInfo
    
    # -- Step 1: Check Python --
    if (-not (Test-PythonInstallation)) {
        Write-Host ""
        Write-ColorOutput "Python 3.11+ is required. Please install it first." -Type Error
        Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation!" -Type Warning
        exit 1
    }
    
    # -- Step 2: Check pip --
    if (-not (Test-PipInstallation)) {
        Write-Host ""
        Write-ColorOutput "pip is required but couldn't be installed" -Type Error
        exit 1
    }
    
    # -- Step 3: Node.js (optional) --
    $hasNode = Test-NodeInstallation
    if (-not $hasNode) {
        Write-ColorOutput "Node.js is recommended but not required" -Type Info
        Write-ColorOutput "Install from: https://nodejs.org/ to enable MCP servers" -Type Info
    }
    
    # -- Step 4: Docker (optional) --
    Test-DockerInstallation
    
    # -- Step 5: Create virtual environment --
    if (-not (New-VirtualEnvironment)) {
        Write-Host ""
        Write-ColorOutput "Failed to create virtual environment" -Type Error
        exit 1
    }
    
    # -- Step 6: Activate virtual environment --
    Enable-VirtualEnvironment | Out-Null
    
    # -- Step 7: Install Python dependencies --
    if (-not (Install-PythonDependencies)) {
        Write-Host ""
        Write-ColorOutput "Failed to install Python dependencies" -Type Error
        exit 1
    }
    
    # -- Step 8: Install MCP servers --
    if ($hasNode) {
        Install-MCPServers | Out-Null
    }
    else {
        Write-ColorOutput "Skipping MCP servers (Node.js not available)" -Type Info
    }
    
    # -- Step 9: Create directories --
    New-RequiredDirectories | Out-Null
    
    # -- Step 10: Setup configuration --
    Initialize-Configuration | Out-Null
    
    # -- Step 11: Auto-fix (if enabled) --
    Invoke-AutoFix
    
    # -- Step 12: Verify installation --
    Test-Installation | Out-Null
    
    # -- Done --
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
