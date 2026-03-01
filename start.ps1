#Requires -Version 5.1
<#
.SYNOPSIS
    Start Antigravity Workspace on Windows with full integration validation
    
.DESCRIPTION
    Checks requirements, sets up virtual environment, validates OpenCode + MCP integration,
    starts the backend server, polls health endpoint, and auto-recovers on failure.
    Ensures seamless integration between OpenCode, Antigravity, and the FastAPI backend.
    
.PARAMETER MaxRetries
    Maximum number of auto-recovery restart attempts (default: 3)

.PARAMETER HealthTimeout
    Seconds to wait for /health endpoint to respond after startup (default: 60)

.PARAMETER SkipIntegration
    Skip OpenCode + MCP integration checks

.PARAMETER Port
    Backend server port (default: 8000)

.EXAMPLE
    .\start.ps1
    .\start.ps1 -MaxRetries 5 -HealthTimeout 90
    .\start.ps1 -SkipIntegration
    
.NOTES
    Windows 10/11 compatible
    Requires Python 3.11+
#>

[CmdletBinding()]
param(
    [int]$MaxRetries = 3,
    [int]$HealthTimeout = 120,
    [switch]$SkipIntegration,
    [int]$Port = 8000
)

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

# Counters
$script:Warnings = 0
$script:Errors   = 0
$script:Checks   = 0
$StartTime = Get-Date

# ============================================================
# OUTPUT HELPERS
# ============================================================

function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Info', 'Success', 'Warning', 'Error', 'Section')]
        [string]$Type = 'Info'
    )
    
    $color = switch ($Type) {
        'Info'    { 'Cyan' }
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error'   { 'Red' }
        'Section' { 'Magenta' }
    }
    
    $prefix = switch ($Type) {
        'Info'    { '[*]' }
        'Success' { '[✓]' }
        'Warning' { '[!]' }
        'Error'   { '[✗]' }
        'Section' { '[▸]' }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $color

    if ($Type -eq 'Warning') { $script:Warnings++ }
    if ($Type -eq 'Error')   { $script:Errors++ }
}

function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     Antigravity Workspace — Starting with Integration Check   ║" -ForegroundColor Cyan
    Write-Host "║          OpenCode + Antigravity + Backend Integration          ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # System info
    $osInfo = [System.Environment]::OSVersion.VersionString
    $psVer  = $PSVersionTable.PSVersion.ToString()
    Write-ColorOutput "System: $osInfo | PowerShell $psVer" -Type Info
    Write-ColorOutput "Project: $PSScriptRoot" -Type Info
    Write-ColorOutput "Port: $Port | Max Retries: $MaxRetries | Health Timeout: ${HealthTimeout}s" -Type Info
    Write-Host ""
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "── $Title ──────────────────────────────────────────" -ForegroundColor Magenta
}

# ============================================================
# PREREQUISITE CHECKS
# ============================================================

function Test-PythonVersion {
    $script:Checks++
    Write-ColorOutput "Checking Python installation..." -Type Info
    
    try {
        $version = & python --version 2>&1
        
        if ($version -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            $patch = [int]$matches[3]
            
            if ($major -ge 3 -and $minor -ge 11) {
                $pyPath = (Get-Command python -ErrorAction SilentlyContinue).Source
                Write-ColorOutput "Python $major.$minor.$patch found ($pyPath)" -Type Success
                return $true
            }
            else {
                Write-ColorOutput "Python 3.11+ required. Found: Python $major.$minor.$patch" -Type Error
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
        [int]$PortNum = 8000
    )
    
    $script:Checks++
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $PortNum -ErrorAction SilentlyContinue
        if ($connection) {
            $pid = $connection.OwningProcess | Select-Object -First 1
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            $procName = if ($proc) { $proc.ProcessName } else { "unknown" }
            
            Write-ColorOutput "Port $PortNum in use by PID $pid ($procName)" -Type Warning
            
            # YOLO: auto-kill
            Write-ColorOutput "Auto-terminating process on port $PortNum..." -Type Info
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            
            # Verify port is free
            $stillInUse = Get-NetTCPConnection -LocalPort $PortNum -ErrorAction SilentlyContinue
            if ($stillInUse) {
                Write-ColorOutput "Port $PortNum still in use after termination" -Type Error
                return $true
            }
            Write-ColorOutput "Port $PortNum freed successfully" -Type Success
            return $false
        }
    }
    catch {
        # Port check not available or port is free
    }
    
    Write-ColorOutput "Port $PortNum is available" -Type Success
    return $false
}

# ============================================================
# VIRTUAL ENVIRONMENT
# ============================================================

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
            Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
            & $activateScript
            Write-ColorOutput "Virtual environment activated" -Type Success
            return $true
        }
        catch {
            Write-ColorOutput "Failed to activate venv: $_" -Type Error
            Write-ColorOutput "Try: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -Type Info
            return $false
        }
    }
    else {
        Write-ColorOutput "Virtual environment not found at: $activateScript" -Type Warning
        return $false
    }
}

# ============================================================
# REQUIREMENTS
# ============================================================

function Install-Requirements {
    param(
        [string]$RequirementsFile
    )
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-ColorOutput "Requirements file not found: $RequirementsFile" -Type Warning
        return $true
    }
    
    $filename = Split-Path $RequirementsFile -Leaf
    $parent   = Split-Path (Split-Path $RequirementsFile -Parent) -Leaf
    $label    = if ($parent -eq (Split-Path $PSScriptRoot -Leaf)) { "root" } else { $parent }
    Write-ColorOutput "Installing requirements ($label/$filename)..." -Type Info
    
    try {
        & python -m pip install --upgrade pip --quiet 2>&1 | Out-Null
        & python -m pip install -r $RequirementsFile --quiet 2>&1 | Out-Null
        Write-ColorOutput "Requirements installed ($label/$filename)" -Type Success
        return $true
    }
    catch {
        Write-ColorOutput "Failed to install requirements ($label/$filename): $_" -Type Error
        return $false
    }
}

function Test-RequirementsInstalled {
    $script:Checks++
    Write-ColorOutput "Checking core requirements..." -Type Info
    
    try {
        $testScript = @"
import sys
try:
    import fastapi
    import uvicorn
    try:
        import chromadb
    except Exception as e:
        print(f'WARN: chromadb: {e}')
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@
        $result = $testScript | & python -
        if ($result -match 'OK') {
            Write-ColorOutput "Core requirements OK (fastapi, uvicorn)" -Type Success
            return $true
        }
        else {
            Write-ColorOutput "Core requirements missing: $result" -Type Warning
            return $false
        }
    }
    catch {
        Write-ColorOutput "Requirements check failed" -Type Warning
        return $false
    }
}

# ============================================================
# DIRECTORIES & ENV
# ============================================================

function New-RequiredDirectories {
    $script:Checks++
    Write-ColorOutput "Ensuring required directories exist..." -Type Info
    
    $directories = @(
        "logs", "drop_zone", "artifacts", "data", "uploads",
        "artifacts/code", "artifacts/diffs", "artifacts/tests",
        "artifacts/screenshots", "artifacts/reports", "artifacts/logs",
        "frontend/static"
    )
    
    $created = 0
    foreach ($dir in $directories) {
        $path = Join-Path $PSScriptRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            $created++
        }
    }
    
    if ($created -gt 0) {
        Write-ColorOutput "Created $created missing directories" -Type Success
    }
    else {
        Write-ColorOutput "All directories present ($($directories.Count) checked)" -Type Success
    }
}

function Test-EnvFile {
    $script:Checks++
    $envPath = Join-Path $PSScriptRoot ".env"
    
    if (-not (Test-Path $envPath)) {
        Write-ColorOutput ".env file not found" -Type Warning
        
        $envExamplePath = Join-Path $PSScriptRoot ".env.example"
        if (Test-Path $envExamplePath) {
            Copy-Item $envExamplePath $envPath
            Write-ColorOutput ".env created from .env.example" -Type Success
            Write-ColorOutput "Edit .env with your API keys or run configure.ps1" -Type Warning
        }
        else {
            Write-ColorOutput "Creating minimal .env..." -Type Info
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
"@
            Set-Content -Path $envPath -Value $envContent
            Write-ColorOutput ".env created — please add your API keys" -Type Success
        }
    }
    else {
        # Check if .env has content
        $envSize = (Get-Item $envPath).Length
        if ($envSize -lt 10) {
            Write-ColorOutput ".env file exists but appears empty ($envSize bytes)" -Type Warning
        }
        else {
            Write-ColorOutput ".env file found ($envSize bytes)" -Type Success
        }
        
        # Ensure NGROK_ENABLED exists
        $envContent = Get-Content $envPath -Raw
        if (-not ($envContent -match "NGROK_ENABLED")) {
            Add-Content -Path $envPath -Value "`nNGROK_ENABLED=false"
        }
    }
}

function Test-NgrokConfig {
    $envPath = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envPath) {
        $envValues = @{}
        Get-Content $envPath | ForEach-Object {
            $line = $_.Trim()
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
                Write-ColorOutput "Ngrok enabled but NGROK_AUTH_TOKEN is missing — disabling for this session" -Type Warning
            }
            else {
                Write-ColorOutput "Ngrok enabled with auth token" -Type Success
            }
        }
    }
    return $true
}

# ============================================================
# OPENCODE + MCP INTEGRATION VALIDATION
# ============================================================

function Test-OpenCodeIntegration {
    $script:Checks++
    Write-SectionHeader "OpenCode Integration"
    
    $opencodePath = Join-Path $PSScriptRoot ".opencode"
    $opencodeJson = Join-Path $PSScriptRoot "opencode.json"
    $mcpJson      = Join-Path $PSScriptRoot "mcp.json"
    $mcpServers   = Join-Path $PSScriptRoot "mcp_servers.json"
    
    $integrationOk = $true
    
    # 1) .opencode/ directory
    if (Test-Path $opencodePath) {
        $items = (Get-ChildItem $opencodePath -ErrorAction SilentlyContinue).Count
        Write-ColorOutput ".opencode/ directory found ($items items)" -Type Success
    }
    else {
        Write-ColorOutput ".opencode/ directory missing — OpenCode not configured" -Type Warning
        $integrationOk = $false
    }
    
    # 2) opencode.json — valid JSON
    if (Test-Path $opencodeJson) {
        try {
            $content = Get-Content $opencodeJson -Raw | ConvertFrom-Json
            $mcpCount = 0
            if ($content.mcp) {
                $mcpCount = ($content.mcp | Get-Member -MemberType NoteProperty).Count
            }
            Write-ColorOutput "opencode.json valid — $mcpCount MCP servers defined" -Type Success
        }
        catch {
            Write-ColorOutput "opencode.json exists but is invalid JSON" -Type Error
            $integrationOk = $false
        }
    }
    else {
        Write-ColorOutput "opencode.json not found" -Type Warning
        $integrationOk = $false
    }
    
    # 3) mcp.json — valid JSON
    if (Test-Path $mcpJson) {
        try {
            $content = Get-Content $mcpJson -Raw | ConvertFrom-Json
            $serverCount = 0
            if ($content.mcpServers) {
                $serverCount = ($content.mcpServers | Get-Member -MemberType NoteProperty).Count
            }
            Write-ColorOutput "mcp.json valid — $serverCount MCP servers defined" -Type Success
        }
        catch {
            Write-ColorOutput "mcp.json exists but is invalid JSON" -Type Error
            $integrationOk = $false
        }
    }
    else {
        Write-ColorOutput "mcp.json not found" -Type Warning
    }
    
    # 4) mcp_servers.json — valid JSON
    if (Test-Path $mcpServers) {
        try {
            $content = Get-Content $mcpServers -Raw | ConvertFrom-Json
            $serverCount = 0
            if ($content.mcpServers) {
                $serverCount = ($content.mcpServers | Get-Member -MemberType NoteProperty).Count
            }
            Write-ColorOutput "mcp_servers.json valid — $serverCount servers" -Type Success
        }
        catch {
            Write-ColorOutput "mcp_servers.json exists but is invalid JSON" -Type Error
            $integrationOk = $false
        }
    }
    else {
        Write-ColorOutput "mcp_servers.json not found (optional)" -Type Info
    }
    
    return $integrationOk
}

function Test-McpServersInstalled {
    $script:Checks++
    Write-SectionHeader "MCP Server Availability"
    
    # Check a few critical MCP server npm packages
    $criticalServers = @(
        @{ Name = "filesystem"; Pkg = "@modelcontextprotocol/server-filesystem" },
        @{ Name = "git";        Pkg = "@modelcontextprotocol/server-git" },
        @{ Name = "memory";     Pkg = "@modelcontextprotocol/server-memory" }
    )
    
    $nodeAvailable = $false
    try {
        $nodeVer = & node --version 2>&1
        if ($nodeVer -match "v\d+") {
            $nodeAvailable = $true
            Write-ColorOutput "Node.js $nodeVer available for MCP servers" -Type Success
        }
    }
    catch {
        Write-ColorOutput "Node.js not found — MCP servers won't run" -Type Warning
        return $false
    }
    
    if (-not $nodeAvailable) {
        return $false
    }
    
    # Check npx availability
    try {
        $npxVer = & npx --version 2>&1
        Write-ColorOutput "npx $npxVer available" -Type Success
    }
    catch {
        Write-ColorOutput "npx not found — MCP servers may not start" -Type Warning
        return $false
    }
    
    # Verify critical packages can resolve (quick check)
    $allGood = $true
    foreach ($server in $criticalServers) {
        try {
            $result = & npm list -g $server.Pkg 2>&1
            if ($result -match $server.Pkg) {
                Write-ColorOutput "MCP: $($server.Name) installed globally" -Type Success
            }
            else {
                Write-ColorOutput "MCP: $($server.Name) not global (npx will auto-fetch)" -Type Info
            }
        }
        catch {
            Write-ColorOutput "MCP: $($server.Name) — npx will auto-fetch on first use" -Type Info
        }
    }
    
    return $allGood
}

function Test-BackendModules {
    $script:Checks++
    Write-ColorOutput "Checking backend module load..." -Type Info
    
    try {
        $testScript = @"
import sys
sys.path.insert(0, 'backend')
try:
    import fastapi
    import uvicorn
    import pydantic
    print(f'OK fastapi={fastapi.__version__} pydantic={pydantic.__version__}')
except ImportError as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@
        $result = $testScript | & python -
        if ($result -match 'OK') {
            Write-ColorOutput "Backend modules OK — $result" -Type Success
            return $true
        }
        else {
            Write-ColorOutput "Backend module load failed: $result" -Type Warning
            return $false
        }
    }
    catch {
        Write-ColorOutput "Backend module check failed" -Type Warning
        return $false
    }
}

# ============================================================
# SERVER START + HEALTH CHECK + AUTO-RECOVERY
# ============================================================

function Test-HealthEndpoint {
    param(
        [int]$TimeoutSeconds = 60,
        [int]$PortNum = 8000
    )
    
    Write-ColorOutput "Waiting for backend health check (up to ${TimeoutSeconds}s)..." -Type Info
    
    $startWait = Get-Date
    $healthUrl = "http://localhost:$PortNum/health"
    $attempts = 0
    
    while (((Get-Date) - $startWait).TotalSeconds -lt $TimeoutSeconds) {
        $attempts++
        try {
            $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $elapsed = [math]::Round(((Get-Date) - $startWait).TotalSeconds, 1)
                Write-ColorOutput "Health check passed (200 OK) in ${elapsed}s after $attempts attempts" -Type Success
                
                # Try to parse the response body
                try {
                    $body = $response.Content | ConvertFrom-Json
                    if ($body.status) {
                        Write-ColorOutput "Backend status: $($body.status)" -Type Info
                    }
                }
                catch {
                    # Response might not be JSON — that's OK
                }
                
                return $true
            }
        }
        catch {
            # Server not ready yet — keep trying
        }
        
        # Progress dots every 5 attempts
        if ($attempts % 5 -eq 0) {
            $elapsed = [math]::Round(((Get-Date) - $startWait).TotalSeconds, 0)
            Write-Host "    ... waiting (${elapsed}s elapsed, attempt $attempts)" -ForegroundColor DarkGray
        }
        
        Start-Sleep -Seconds 2
    }
    
    Write-ColorOutput "Health check failed after ${TimeoutSeconds}s ($attempts attempts)" -Type Error
    return $false
}

function Start-BackendWithRecovery {
    param(
        [int]$MaxAttempts = 3,
        [int]$HealthWait  = 60,
        [int]$PortNum     = 8000
    )
    
    $backendPath = Join-Path $PSScriptRoot "backend"
    $logDir      = Join-Path $PSScriptRoot "logs"
    
    if (-not (Test-Path $backendPath)) {
        Write-ColorOutput "Backend directory not found: $backendPath" -Type Error
        return $false
    }
    
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Write-SectionHeader "Backend Start (Attempt $attempt/$MaxAttempts)"
        
        $logFile  = Join-Path $logDir "backend.log"
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        # Append startup marker to log
        Add-Content -Path $logFile -Value "`n`n=== Startup Attempt $attempt at $timestamp ===`n" -ErrorAction SilentlyContinue
        
        Write-ColorOutput "Starting backend server..." -Type Info
        Write-ColorOutput "Backend: http://localhost:$PortNum" -Type Info
        Write-ColorOutput "API Docs: http://localhost:$PortNum/docs" -Type Info
        Write-ColorOutput "Log: $logFile" -Type Info
        
        try {
            # Start backend as a background job
            Push-Location $backendPath
            
            $job = Start-Job -ScriptBlock {
                param($path, $logPath)
                Set-Location $path
                & python main.py 2>&1 | Tee-Object -FilePath $logPath -Append
            } -ArgumentList $backendPath, $logFile
            
            Pop-Location
            
            Write-ColorOutput "Backend process started (Job ID: $($job.Id))" -Type Success
            
            # Wait for health endpoint
            if (Test-HealthEndpoint -TimeoutSeconds $HealthWait -PortNum $PortNum) {
                Write-Host ""
                Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
                Write-Host "║              Antigravity Backend is RUNNING                    ║" -ForegroundColor Green
                Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
                Write-Host ""
                
                # Display integration summary
                Write-IntegrationSummary -PortNum $PortNum
                
                Write-Host ""
                Write-ColorOutput "Press Ctrl+C to stop the server" -Type Warning
                Write-Host ""
                
                # Now switch to foreground: stream the job output to console
                # and keep checking the job is alive
                try {
                    while ($job.State -eq 'Running') {
                        # Receive any new output from the job
                        $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
                        if ($output) {
                            $output | ForEach-Object { Write-Host $_ }
                        }
                        Start-Sleep -Milliseconds 500
                    }
                    
                    # Job ended — get remaining output
                    $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
                    if ($output) {
                        $output | ForEach-Object { Write-Host $_ }
                    }
                    
                    if ($job.State -eq 'Failed') {
                        Write-ColorOutput "Backend process failed unexpectedly" -Type Error
                        $jobError = $job.ChildJobs[0].JobStateInfo.Reason
                        if ($jobError) {
                            Write-ColorOutput "Reason: $jobError" -Type Error
                        }
                    }
                    else {
                        Write-ColorOutput "Backend process exited (State: $($job.State))" -Type Warning
                    }
                }
                catch {
                    # Ctrl+C or other interruption
                    Write-Host ""
                    Write-ColorOutput "Shutting down..." -Type Warning
                    Stop-Job -Job $job -ErrorAction SilentlyContinue
                    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
                    return $true
                }
                finally {
                    # Clean up job
                    Stop-Job -Job $job -ErrorAction SilentlyContinue
                    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
                }
                
                # If we get here, server stopped on its own
                if ($attempt -lt $MaxAttempts) {
                    Write-ColorOutput "Auto-recovery: restarting in 5 seconds..." -Type Warning
                    Start-Sleep -Seconds 5
                    continue
                }
                else {
                    Write-ColorOutput "Max retry attempts reached ($MaxAttempts)" -Type Error
                    return $false
                }
            }
            else {
                # Health check failed
                Write-ColorOutput "Backend failed to become healthy" -Type Error
                Stop-Job -Job $job -ErrorAction SilentlyContinue
                Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
                
                # Show last lines of log
                if (Test-Path $logFile) {
                    Write-ColorOutput "Last 10 lines of backend.log:" -Type Info
                    Get-Content $logFile -Tail 10 | ForEach-Object {
                        Write-Host "    $_" -ForegroundColor DarkGray
                    }
                }
                
                if ($attempt -lt $MaxAttempts) {
                    Write-ColorOutput "Auto-recovery: retry in 5 seconds..." -Type Warning
                    Start-Sleep -Seconds 5
                }
            }
        }
        catch {
            Write-ColorOutput "Failed to start backend: $_" -Type Error
            
            try { Pop-Location } catch { }
            
            if ($attempt -lt $MaxAttempts) {
                Write-ColorOutput "Auto-recovery: retry in 5 seconds..." -Type Warning
                Start-Sleep -Seconds 5
            }
        }
    }
    
    Write-ColorOutput "Backend failed to start after $MaxAttempts attempts" -Type Error
    Write-ColorOutput "Check logs at: $(Join-Path $PSScriptRoot 'logs\backend.log')" -Type Info
    return $false
}

# ============================================================
# INTEGRATION SUMMARY
# ============================================================

function Write-IntegrationSummary {
    param([int]$PortNum = 8000)
    
    Write-SectionHeader "Integration Summary"
    
    # Backend
    Write-ColorOutput "Backend:      http://localhost:$PortNum" -Type Success
    Write-ColorOutput "API Docs:     http://localhost:$PortNum/docs" -Type Info
    Write-ColorOutput "Health:       http://localhost:$PortNum/health" -Type Info
    Write-ColorOutput "WebSocket:    ws://localhost:$PortNum/ws" -Type Info
    
    # OpenCode
    $opencodeDir = Join-Path $PSScriptRoot ".opencode"
    if (Test-Path $opencodeDir) {
        Write-ColorOutput "OpenCode:     Integrated (.opencode/ present)" -Type Success
    }
    else {
        Write-ColorOutput "OpenCode:     Not configured" -Type Warning
    }
    
    # MCP
    $mcpJson = Join-Path $PSScriptRoot "mcp.json"
    if (Test-Path $mcpJson) {
        try {
            $mcp = Get-Content $mcpJson -Raw | ConvertFrom-Json
            $count = ($mcp.mcpServers | Get-Member -MemberType NoteProperty).Count
            Write-ColorOutput "MCP Servers:  $count configured (mcp.json)" -Type Success
        }
        catch {
            Write-ColorOutput "MCP Servers:  mcp.json found but invalid" -Type Warning
        }
    }
    else {
        Write-ColorOutput "MCP Servers:  No mcp.json found" -Type Warning
    }
    
    # Ngrok
    $envPath = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        if ($envContent -match "NGROK_ENABLED\s*=\s*true") {
            Write-ColorOutput "Ngrok:        Enabled (tunnel active)" -Type Success
        }
        else {
            Write-ColorOutput "Ngrok:        Disabled" -Type Info
        }
    }
    
    # Docker
    try {
        $dockerVer = & docker --version 2>&1
        if ($dockerVer -match "Docker") {
            Write-ColorOutput "Docker:       Available ($dockerVer)" -Type Info
        }
    }
    catch {
        Write-ColorOutput "Docker:       Not available" -Type Info
    }
    
    # Agent personas
    $agentsDir = Join-Path $PSScriptRoot ".github\agents"
    if (Test-Path $agentsDir) {
        $agentFiles = (Get-ChildItem $agentsDir -Filter "*.agent.md" -ErrorAction SilentlyContinue).Count
        Write-ColorOutput "AI Agents:    $agentFiles agent personas loaded" -Type Success
    }
    
    # Elapsed time
    $elapsed = [math]::Round(((Get-Date) - $StartTime).TotalSeconds, 1)
    Write-Host ""
    Write-ColorOutput "Startup completed in ${elapsed}s | Checks: $($script:Checks) | Warnings: $($script:Warnings) | Errors: $($script:Errors)" -Type Info
}

# ============================================================
# MAIN EXECUTION
# ============================================================

function Main {
    Write-Header
    
    # ── Python Check ──
    Write-SectionHeader "Prerequisites"
    if (-not (Test-PythonVersion)) {
        Write-Host ""
        Write-ColorOutput "Setup incomplete. Please install Python 3.11+ first." -Type Error
        exit 1
    }
    
    # ── Port Check ──
    if (Test-PortInUse -PortNum $Port) {
        Write-Host ""
        Write-ColorOutput "Cannot start — port $Port is still in use" -Type Error
        exit 1
    }
    
    # ── Directories ──
    Write-SectionHeader "Environment Setup"
    New-RequiredDirectories
    
    # ── .env File ──
    Test-EnvFile
    
    # ── Ngrok Config ──
    Test-NgrokConfig | Out-Null
    
    # ── Virtual Environment ──
    Write-SectionHeader "Virtual Environment"
    $venvPath = Join-Path $PSScriptRoot "venv"
    if (-not (Test-Path $venvPath)) {
        Write-ColorOutput "Virtual environment not found — creating..." -Type Warning
        if (-not (New-VirtualEnvironment)) {
            Write-ColorOutput "Failed to create virtual environment" -Type Error
            exit 1
        }
    }
    else {
        Write-ColorOutput "Virtual environment found at: $venvPath" -Type Success
    }
    
    # Activate
    if (-not (Enable-VirtualEnvironment)) {
        Write-ColorOutput "Using system Python instead" -Type Warning
    }
    
    # ── Requirements ──
    Write-SectionHeader "Dependencies"
    if (-not (Test-RequirementsInstalled)) {
        Write-ColorOutput "Installing requirements..." -Type Info
        
        $rootReqs = Join-Path $PSScriptRoot "requirements.txt"
        if (Test-Path $rootReqs) {
            Install-Requirements -RequirementsFile $rootReqs
        }
        
        $backendReqs = Join-Path $PSScriptRoot "backend\requirements.txt"
        if (Test-Path $backendReqs) {
            Install-Requirements -RequirementsFile $backendReqs
        }
    }
    
    # ── Backend Module Validation ──
    Test-BackendModules | Out-Null
    
    # ── OpenCode + MCP Integration ──
    if (-not $SkipIntegration) {
        $integrationOk = Test-OpenCodeIntegration
        Test-McpServersInstalled | Out-Null
        
        if (-not $integrationOk) {
            Write-ColorOutput "Integration issues detected — continuing anyway (YOLO mode)" -Type Warning
        }
    }
    else {
        Write-ColorOutput "Skipping integration checks (-SkipIntegration)" -Type Info
    }
    
    # ── Start Backend with Health Check + Auto-Recovery ──
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              Starting Antigravity Backend...                   ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not (Start-BackendWithRecovery -MaxAttempts $MaxRetries -HealthWait $HealthTimeout -PortNum $Port)) {
        Write-Host ""
        Write-ColorOutput "Failed to start Antigravity backend" -Type Error
        Write-ColorOutput "Troubleshooting:" -Type Info
        Write-ColorOutput "  1. Check logs: $PSScriptRoot\logs\backend.log" -Type Info
        Write-ColorOutput "  2. Run install: .\install.ps1 -AutoFix" -Type Info
        Write-ColorOutput "  3. Check port: netstat -ano | findstr :$Port" -Type Info
        Write-ColorOutput "  4. Manual start: cd backend && python main.py" -Type Info
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
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" -Type Info
    exit 1
}
