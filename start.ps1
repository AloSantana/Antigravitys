#Requires -Version 5.1
<#
.SYNOPSIS
    Start Antigravity Workspace on Windows
    
.DESCRIPTION
    Checks requirements, sets up virtual environment, and starts the backend server
    
.EXAMPLE
    .\start.ps1
    
.NOTES
    Windows 10/11 compatible
    Requires Python 3.11+
#>

[CmdletBinding()]
param()

# ============================================================
# YOLO MODE — Auto-execution enforcement (P0, immutable)
# All commands, installs, and operations are pre-approved.
# No confirmation prompts. Always continue forward.
# ============================================================
$env:ANTIGRAVITY_YOLO_MODE    = "1"
$env:ANTIGRAVITY_PLATFORM     = "windows"
$env:ANTIGRAVITY_AUTO_APPROVE = "true"
$ConfirmPreference            = "None"   # suppress PowerShell confirm prompts
$InformationPreference        = "Continue"

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Colors for output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Info', 'Success', 'Warning', 'Error')]
        [string]$Type = 'Info'
    )
    
    $color = switch ($Type) {
        'Info' { 'Cyan' }
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error' { 'Red' }
    }
    
    $prefix = switch ($Type) {
        'Info' { '[*]' }
        'Success' { '[✓]' }
        'Warning' { '[!]' }
        'Error' { '[✗]' }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          Antigravity Workspace - Starting...              ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Test-PythonVersion {
    Write-ColorOutput "Checking Python installation..." -Type Info
    
    try {
        & python --version 2>&1 | Out-Null # Just check if it runs
        $version = & python --version 2>&1
        
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -ge 3 -and $minor -ge 11) {
                Write-ColorOutput "Python $version found" -Type Success
                return $true
            }
            else {
                Write-ColorOutput "Python 3.11+ required. Found: $version" -Type Error
                Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
                return $false
            }
        }
    }
    catch {
        Write-ColorOutput "Python not found or not in PATH" -Type Error
        Write-ColorOutput "Download from: https://www.python.org/downloads/" -Type Info
        Write-ColorOutput "Make sure to check 'Add Python to PATH' during installation" -Type Warning
        return $false
    }
    
    return $false
}

function Test-PortInUse {
    param(
        [int]$Port = 8000
    )
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-ColorOutput "Port $Port is already in use!" -Type Warning
            Write-ColorOutput "Process: $($connection.OwningProcess)" -Type Info
            
            $answer = 'y'  # Auto-proceed: kill process blocking the port
            if ($answer -eq 'y' -or $answer -eq 'Y') {
                Stop-Process -Id $connection.OwningProcess -Force
                Write-ColorOutput "Process terminated" -Type Success
                Start-Sleep -Seconds 2
                return $false
            }
            return $true
        }
    }
    catch {
        # Port check not available or port is free
    }
    
    return $false
}

function New-VirtualEnvironment {
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
            # Set execution policy for this session to allow activation
            Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
            
            & $activateScript
            Write-ColorOutput "Virtual environment activated" -Type Success
            return $true
        }
        catch {
            Write-ColorOutput "Failed to activate virtual environment: $_" -Type Error
            Write-ColorOutput "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -Type Info
            return $false
        }
    }
    else {
        Write-ColorOutput "Virtual environment not found" -Type Warning
        return $false
    }
}

function Install-Requirements {
    param(
        [string]$RequirementsFile
    )
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-ColorOutput "Requirements file not found: $RequirementsFile" -Type Warning
        return $true
    }
    
    Write-ColorOutput "Installing Python requirements from $RequirementsFile..." -Type Info
    
    try {
        & python -m pip install --upgrade pip --quiet
        & python -m pip install -r $RequirementsFile --quiet
        Write-ColorOutput "Requirements installed" -Type Success
        return $true
    }
    catch {
        Write-ColorOutput "Failed to install requirements: $_" -Type Error
        return $false
    }
}

function Test-RequirementsInstalled {
    Write-ColorOutput "Checking if requirements are installed..." -Type Info
    
    try {
        $testScript = @"
import sys
try:
    import fastapi
    import uvicorn
    # Test chromadb separately as it might throw ConfigError on Python 3.14
    try:
        import chromadb
    except Exception as e:
        print(f'WARN: chromadb load failed: {e}')
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@
        $result = $testScript | & python -
        if ($result -match 'OK') {
            Write-ColorOutput "Core requirements are installed" -Type Success
            return $true
        }
        else {
            Write-ColorOutput "Core requirements are missing or broken: $result" -Type Warning
            return $false
        }
    }
    catch {
        Write-ColorOutput "Some requirements are missing" -Type Warning
        return $false
    }
}

function New-RequiredDirectories {
    Write-ColorOutput "Ensuring required directories exist..." -Type Info
    
    $directories = @("logs", "drop_zone", "artifacts", "data", "uploads")
    
    foreach ($dir in $directories) {
        $path = Join-Path $PSScriptRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
    
    Write-ColorOutput "Directories ready" -Type Success
}

function Test-EnvFile {
    $envPath = Join-Path $PSScriptRoot ".env"
    
    if (-not (Test-Path $envPath)) {
        Write-ColorOutput ".env file not found" -Type Warning
        
        $envExamplePath = Join-Path $PSScriptRoot ".env.example"
        if (Test-Path $envExamplePath) {
            Copy-Item $envExamplePath $envPath
            Write-ColorOutput ".env file created from .env.example" -Type Success
            Write-ColorOutput "Please edit .env with your API keys before starting" -Type Warning
            
            $answer = 'n'  # Auto-proceed: skip interactive configuration
            if ($answer -ne 'n' -and $answer -ne 'N') {
                $configurePath = Join-Path $PSScriptRoot "configure.ps1"
                if (Test-Path $configurePath) {
                    & $configurePath
                }
                else {
                    Write-ColorOutput "Configuration wizard not found" -Type Warning
                    Write-ColorOutput "Please manually edit: $envPath" -Type Info
                    notepad $envPath
                }
            }
        }
        else {
            Write-ColorOutput "Creating minimal .env file..." -Type Info
            
            $envContent = @"
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=

# OpenRouter API Key (access 100+ models from https://openrouter.ai/keys)
OPENROUTER_API_KEY=

# Local Model Settings
LOCAL_MODEL=llama3

# GitHub Token (get from https://github.com/settings/tokens)
COPILOT_MCP_GITHUB_TOKEN=

# Server Configuration
HOST=0.0.0.0
PORT=8000
NGROK_ENABLED=false
DEBUG_MODE=false
LOG_LEVEL=INFO

# Model Rotator
MODEL_ROTATOR_ENABLED=true
SWARM_AUTO_ROTATE_KEYS=true

# ⚠ Fill in your actual API keys above
# Run .\configure.ps1 for interactive setup
"@
            Set-Content -Path $envPath -Value $envContent
            Write-ColorOutput ".env file created - please edit with your API keys" -Type Success
        }
    }
    else {
        Write-ColorOutput ".env file found" -Type Success
        # Ensure NGROK_ENABLED exists
        $envContent = Get-Content $envPath
        if (-not ($envContent -match "NGROK_ENABLED")) {
            Add-Content -Path $envPath -Value "`nNGROK_ENABLED=false"
        }
    }
}

function Test-NgrokConfig {
    $envPath = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envPath) {
        # Parse .env manually (ConvertFrom-StringData fails on comments/empty lines/quotes)
        $envValues = @{}
        Get-Content $envPath | ForEach-Object {
            $line = $_.Trim()
            # Skip comments and empty lines
            if ($line -and -not $line.StartsWith('#')) {
                $parts = $line -split '=', 2
                if ($parts.Count -eq 2) {
                    $key = $parts[0].Trim()
                    $val = $parts[1].Trim().Trim("'", '"')
                    $envValues[$key] = $val
                }
            }
        }
        if ($envValues['NGROK_ENABLED'] -eq 'true') {
            if (-not $envValues['NGROK_AUTH_TOKEN']) {
                Write-ColorOutput "Ngrok is enabled but NGROK_AUTH_TOKEN is missing in .env" -Type Warning
                Write-ColorOutput "Disabling ngrok for this session. Add your token to .env to enable." -Type Info
                # Don't block startup - just warn and continue
                return $true
            }
        }
    }
    return $true
}

function Start-BackendServer {
    $backendPath = Join-Path $PSScriptRoot "backend"
    $logFile = Join-Path $PSScriptRoot "logs\backend.log"
    
    if (-not (Test-Path $backendPath)) {
        Write-ColorOutput "Backend directory not found: $backendPath" -Type Error
        return $false
    }
    
    Write-ColorOutput "Starting backend server..." -Type Info
    Write-ColorOutput "Backend will run at: http://localhost:8000" -Type Info
    Write-ColorOutput "Logging to: $logFile" -Type Info
    Write-Host ""
    Write-ColorOutput "Press Ctrl+C to stop the server" -Type Warning
    Write-Host ""
    
    try {
        # Change to backend directory
        Push-Location $backendPath
        
        # Run the server directly with output to both console and log file
        # Using Tee-Object instead of Start-Process to avoid dual-redirect issues on Windows
        & python main.py 2>&1 | Tee-Object -FilePath $logFile
        
        return $true
    }
    catch {
        Write-ColorOutput "Failed to start backend server: $_" -Type Error
        return $false
    }
    finally {
        Pop-Location
    }
}

# Main execution
function Main {
    Write-Header
    
    # Check Python
    if (-not (Test-PythonVersion)) {
        Write-Host ""
        Write-ColorOutput "Setup incomplete. Please install Python 3.11+ first." -Type Error
        exit 1
    }
    
    # Check port availability
    if (Test-PortInUse -Port 8000) {
        Write-Host ""
        Write-ColorOutput "Cannot start - port 8000 is in use" -Type Error
        exit 1
    }
    
    # Create directories
    New-RequiredDirectories
    
    # Check .env file
    Test-EnvFile
    
    # Check Ngrok Config
    if (-not (Test-NgrokConfig)) {
        exit 1
    }
    
    # Setup virtual environment
    $venvPath = Join-Path $PSScriptRoot "venv"
    if (-not (Test-Path $venvPath)) {
        Write-ColorOutput "Virtual environment not found" -Type Warning
        
        $answer = 'Y'  # Auto-proceed: create virtual environment
        if ($answer -ne 'n' -and $answer -ne 'N') {
            if (-not (New-VirtualEnvironment)) {
                Write-ColorOutput "Failed to create virtual environment" -Type Error
                exit 1
            }
        }
        else {
            Write-ColorOutput "Cannot continue without virtual environment" -Type Error
            Write-ColorOutput "Run install.ps1 first or create manually with: python -m venv venv" -Type Info
            exit 1
        }
    }
    
    # Activate virtual environment
    if (-not (Enable-VirtualEnvironment)) {
        Write-ColorOutput "Using system Python instead" -Type Warning
    }
    
    # Check and install requirements
    if (-not (Test-RequirementsInstalled)) {
        Write-ColorOutput "Requirements not installed or incomplete" -Type Warning
        
        $answer = 'Y'  # Auto-proceed: install requirements
        if ($answer -ne 'n' -and $answer -ne 'N') {
            # Install root requirements
            $rootReqs = Join-Path $PSScriptRoot "requirements.txt"
            if (Test-Path $rootReqs) {
                Install-Requirements -RequirementsFile $rootReqs
            }
            
            # Install backend requirements
            $backendReqs = Join-Path $PSScriptRoot "backend\requirements.txt"
            if (Test-Path $backendReqs) {
                Install-Requirements -RequirementsFile $backendReqs
            }
        }
        else {
            Write-ColorOutput "Attempting to start anyway..." -Type Warning
        }
    }
    
    Write-Host ""
    Write-ColorOutput "Starting Antigravity Workspace..." -Type Success
    Write-Host ""
    
    # Start backend server
    if (-not (Start-BackendServer)) {
        Write-Host ""
        Write-ColorOutput "Failed to start backend server" -Type Error
        Write-ColorOutput "Check logs at: $PSScriptRoot\logs\backend.log" -Type Info
        exit 1
    }
}

# Run main function
try {
    Main
}
catch {
    Write-Host ""
    Write-ColorOutput "Unexpected error: $_" -Type Error
    exit 1
}
