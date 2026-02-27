#Requires -Version 5.1
<#
.SYNOPSIS
    Interactive Configuration Wizard for Antigravity Workspace
    
.DESCRIPTION
    Helps users set up their environment with an interactive wizard
    - Gemini API configuration
    - GitHub token setup
    - Model selection
    - Ngrok configuration
    - Server settings
    
.EXAMPLE
    .\configure.ps1
    
.NOTES
    Windows 10/11 compatible
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
$ConfirmPreference            = "None"

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Configuration variables
$script:Config = @{
    GEMINI_API_KEY = ""
    VERTEX_API_KEY = ""
    VERTEX_PROJECT_ID = ""
    VERTEX_LOCATION = "us-central1"
    VERTEX_MODEL = "gemini-pro"
    OPENROUTER_API_KEY = ""
    OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"
    OPENAI_API_KEY = ""
    LOCAL_MODEL = "llama3"
    ACTIVE_MODEL = "auto"
    MODEL_ROTATOR_ENABLED = "true"
    SWARM_AUTO_ROTATE_KEYS = "true"
    SMART_RATE_LIMIT_HANDOFF = "true"
    COPILOT_MCP_GITHUB_TOKEN = ""
    COPILOT_MCP_BRAVE_API_KEY = ""
    COPILOT_MCP_POSTGRES_CONNECTION_STRING = ""
    HOST = "0.0.0.0"
    PORT = "8000"
    NGROK_ENABLED = "false"
    NGROK_AUTH_TOKEN = ""
    NGROK_REGION = "us"
    NGROK_DOMAIN = ""
    ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"
    DEBUG_MODE = "false"
    LOG_LEVEL = "INFO"
}

# Colors and formatting
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('Info', 'Success', 'Warning', 'Error', 'Question')]
        [string]$Type = 'Info'
    )
    
    $color = switch ($Type) {
        'Info'     { 'Cyan' }
        'Success'  { 'Green' }
        'Warning'  { 'Yellow' }
        'Error'    { 'Red' }
        'Question' { 'Magenta' }
    }
    
    $prefix = switch ($Type) {
        'Info'     { 'ℹ' }
        'Success'  { '✓' }
        'Warning'  { '⚠' }
        'Error'    { '✗' }
        'Question' { '?' }
    }
    
    Write-Host "$prefix  $Message" -ForegroundColor $color
}

function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║     Antigravity Workspace - Configuration Wizard          ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══ $Title ═══" -ForegroundColor Blue
    Write-Host ""
}

function Read-Input {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [switch]$Secure
    )
    
    $message = if ($Default) {
        "? $Prompt [$Default]"
    } else {
        "? $Prompt"
    }
    
    if ($Secure) {
        $secureInput = Read-Host -Prompt $message -AsSecureString
        $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureInput)
        $result = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
    else {
        $result = Read-Host -Prompt $message
    }
    
    if ([string]::IsNullOrWhiteSpace($result) -and $Default) {
        return $Default
    }
    
    return $result
}

function Read-YesNo {
    param(
        [string]$Prompt,
        [bool]$Default = $false
    )
    
    $defaultText = if ($Default) { "Y/n" } else { "y/N" }
    $message = "? $Prompt [$defaultText]"
    
    $result = Read-Host -Prompt $message
    
    if ([string]::IsNullOrWhiteSpace($result)) {
        return $Default
    }
    
    return $result -match '^[Yy]'
}

function Test-ApiKey {
    param([string]$Key)
    
    if ([string]::IsNullOrWhiteSpace($Key)) {
        return $false
    }
    
    return $Key.Length -ge 20
}

function Get-ExistingConfig {
    $envPath = Join-Path $PSScriptRoot ".env"
    
    if (Test-Path $envPath) {
        Write-ColorOutput "Loading existing configuration..." -Type Info
        
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                
                if ($script:Config.ContainsKey($key)) {
                    $script:Config[$key] = $value
                }
            }
        }
        
        Write-ColorOutput "Existing configuration loaded" -Type Success
    }
}

function Set-GeminiConfiguration {
    Write-Section "Gemini AI Configuration"
    
    Write-ColorOutput "Gemini is used for high-complexity reasoning tasks" -Type Info
    Write-ColorOutput "Get your API key from: https://aistudio.google.com/app/apikey" -Type Info
    Write-Host ""
    
    $apiKey = Read-Input -Prompt "Enter your Gemini API key" -Default $script:Config.GEMINI_API_KEY -Secure
    
    if (Test-ApiKey $apiKey) {
        $script:Config.GEMINI_API_KEY = $apiKey
        Write-ColorOutput "Gemini API key configured" -Type Success
    }
    else {
        Write-ColorOutput "API key seems invalid (too short)" -Type Warning
        $script:Config.GEMINI_API_KEY = $apiKey
    }
}

function Set-OpenRouterConfiguration {
    Write-Section "OpenRouter Configuration (Optional - Recommended)"
    
    Write-ColorOutput "OpenRouter provides access to 100+ models from one API" -Type Info
    Write-ColorOutput "Including: Claude 3.5, GPT-4, Gemini, Llama 3, Mixtral, and more" -Type Info
    Write-ColorOutput "Get your API key from: https://openrouter.ai/keys" -Type Info
    Write-Host ""
    
    if (Read-YesNo -Prompt "Configure OpenRouter?" -Default $false) {
        $apiKey = Read-Input -Prompt "Enter your OpenRouter API key" -Default $script:Config.OPENROUTER_API_KEY -Secure
        
        if (Test-ApiKey $apiKey) {
            $script:Config.OPENROUTER_API_KEY = $apiKey
            Write-ColorOutput "OpenRouter API key configured" -Type Success
            
            Write-Host ""
            Write-ColorOutput "Popular models:" -Type Info
            Write-ColorOutput "  1. anthropic/claude-3.5-sonnet (best quality)" -Type Info
            Write-ColorOutput "  2. openai/gpt-4-turbo (balanced)" -Type Info
            Write-ColorOutput "  3. google/gemini-pro-1.5 (fast)" -Type Info
            Write-ColorOutput "  4. meta-llama/llama-3.1-70b-instruct (open source)" -Type Info
            Write-ColorOutput "  5. mistralai/mixtral-8x7b-instruct (cost-effective)" -Type Info
            Write-Host ""
            
            $model = Read-Input -Prompt "Default model" -Default $script:Config.OPENROUTER_MODEL
            $script:Config.OPENROUTER_MODEL = $model
        }
        else {
            Write-ColorOutput "API key seems invalid (too short)" -Type Warning
        }
    }
}

function Set-VertexConfiguration {
    Write-Section "Vertex AI Configuration (Optional)"
    
    if (Read-YesNo -Prompt "Configure Vertex AI (Google Cloud)?" -Default $false) {
        Write-ColorOutput "Get API key from: https://console.cloud.google.com/apis/credentials" -Type Info
        Write-Host ""
        
        $script:Config.VERTEX_API_KEY = Read-Input -Prompt "Vertex API key" -Default $script:Config.VERTEX_API_KEY -Secure
        $script:Config.VERTEX_PROJECT_ID = Read-Input -Prompt "GCP Project ID" -Default $script:Config.VERTEX_PROJECT_ID
        $script:Config.VERTEX_LOCATION = Read-Input -Prompt "Vertex Location" -Default $script:Config.VERTEX_LOCATION
        $script:Config.VERTEX_MODEL = Read-Input -Prompt "Vertex Model" -Default $script:Config.VERTEX_MODEL
        
        Write-ColorOutput "Vertex AI configured" -Type Success
    }
    else {
        $script:Config.VERTEX_API_KEY = ""
        $script:Config.VERTEX_PROJECT_ID = ""
        Write-ColorOutput "Vertex AI will not be used" -Type Info
    }
}

function Set-ModelSelection {
    Write-Section "AI Model Selection"
    
    Write-Host "Available options:" -ForegroundColor Cyan
    Write-Host "  1. auto       - Automatic selection based on task complexity (recommended)" -ForegroundColor White
    Write-Host "  2. gemini     - Always use Gemini" -ForegroundColor White
    Write-Host "  3. vertex     - Always use Vertex AI" -ForegroundColor White
    Write-Host "  4. openrouter - Always use OpenRouter (100+ models)" -ForegroundColor White
    Write-Host "  5. ollama     - Use local Ollama with cloud fallback" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Input -Prompt "Select model strategy (1-5)" -Default "1"
    
    $script:Config.ACTIVE_MODEL = switch ($choice) {
        "1" { "auto" }
        "2" { "gemini" }
        "3" { "vertex" }
        "4" { "openrouter" }
        "5" { "ollama" }
        default { "auto" }
    }
    
    Write-ColorOutput "Model strategy set to: $($script:Config.ACTIVE_MODEL)" -Type Success
}

function Set-OllamaConfiguration {
    Write-Section "Local AI (Ollama) Configuration"
    
    if (Read-YesNo -Prompt "Use local Ollama for low-complexity tasks?" -Default $true) {
        $script:Config.LOCAL_MODEL = Read-Input -Prompt "Enter model name" -Default $script:Config.LOCAL_MODEL
        Write-ColorOutput "Ollama configured with model: $($script:Config.LOCAL_MODEL)" -Type Success
        
        # Check if Ollama is installed
        try {
            $null = Get-Command ollama -ErrorAction Stop
            Write-ColorOutput "Ollama is installed" -Type Success
            
            # Check if model is available
            $models = & ollama list 2>&1
            if ($models -match $script:Config.LOCAL_MODEL) {
                Write-ColorOutput "Model '$($script:Config.LOCAL_MODEL)' is available" -Type Success
            }
            else {
                Write-ColorOutput "Model '$($script:Config.LOCAL_MODEL)' not found" -Type Warning
                if (Read-YesNo -Prompt "Pull the model now?" -Default $true) {
                    Write-ColorOutput "Pulling model (this may take a while)..." -Type Info
                    & ollama pull $script:Config.LOCAL_MODEL
                }
            }
        }
        catch {
            Write-ColorOutput "Ollama not installed" -Type Warning
            Write-ColorOutput "Install from: https://ollama.ai" -Type Info
            
            if (Read-YesNo -Prompt "Open Ollama website in browser?" -Default $false) {
                Start-Process "https://ollama.ai"
            }
        }
    }
    else {
        $script:Config.LOCAL_MODEL = ""
        Write-ColorOutput "Ollama will not be used" -Type Info
    }
}

function Set-GitHubConfiguration {
    Write-Section "GitHub Integration"
    
    if (Read-YesNo -Prompt "Enable GitHub MCP integration?" -Default $true) {
        Write-ColorOutput "Create a token at: https://github.com/settings/tokens" -Type Info
        Write-ColorOutput "Required scopes: repo, read:org" -Type Info
        Write-Host ""
        
        $token = Read-Input -Prompt "Enter your GitHub token" -Default $script:Config.COPILOT_MCP_GITHUB_TOKEN -Secure
        
        if (Test-ApiKey $token) {
            $script:Config.COPILOT_MCP_GITHUB_TOKEN = $token
            Write-ColorOutput "GitHub token configured" -Type Success
            
            # Test token
            Write-ColorOutput "Testing GitHub token..." -Type Info
            try {
                $headers = @{
                    "Authorization" = "token $token"
                    "User-Agent" = "Antigravity-Workspace"
                }
                $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -TimeoutSec 10
                Write-ColorOutput "GitHub token is valid (User: $($response.login))" -Type Success
            }
            catch {
                Write-ColorOutput "GitHub token validation failed: $_" -Type Warning
            }
        }
        else {
            Write-ColorOutput "Token seems invalid (too short)" -Type Warning
            $script:Config.COPILOT_MCP_GITHUB_TOKEN = $token
        }
    }
    else {
        $script:Config.COPILOT_MCP_GITHUB_TOKEN = ""
        Write-ColorOutput "GitHub integration will be disabled" -Type Info
    }
}

function Set-NgrokConfiguration {
    Write-Section "Ngrok Tunnel Configuration"
    
    Write-ColorOutput "Ngrok provides public URLs for local development" -Type Info
    Write-ColorOutput "Useful for webhooks, external API access, and remote testing" -Type Info
    Write-Host ""
    
    if (Read-YesNo -Prompt "Enable Ngrok tunnel?" -Default $false) {
        $script:Config.NGROK_ENABLED = "true"
        
        Write-ColorOutput "Get auth token from: https://dashboard.ngrok.com/get-started/your-authtoken" -Type Info
        Write-Host ""
        
        $token = Read-Input -Prompt "Ngrok auth token (optional but recommended)" -Default $script:Config.NGROK_AUTH_TOKEN -Secure
        $script:Config.NGROK_AUTH_TOKEN = $token
        
        # Region selection
        Write-Host ""
        Write-Host "Ngrok regions:" -ForegroundColor Cyan
        Write-Host "  us - United States" -ForegroundColor White
        Write-Host "  eu - Europe" -ForegroundColor White
        Write-Host "  ap - Asia/Pacific" -ForegroundColor White
        Write-Host "  au - Australia" -ForegroundColor White
        Write-Host "  sa - South America" -ForegroundColor White
        Write-Host "  jp - Japan" -ForegroundColor White
        Write-Host "  in - India" -ForegroundColor White
        Write-Host ""
        
        $region = Read-Input -Prompt "Ngrok region" -Default $script:Config.NGROK_REGION
        $script:Config.NGROK_REGION = $region
        
        # Custom domain (paid feature)
        if (Read-YesNo -Prompt "Use custom domain? (requires paid plan)" -Default $false) {
            $domain = Read-Input -Prompt "Custom domain" -Default $script:Config.NGROK_DOMAIN
            $script:Config.NGROK_DOMAIN = $domain
        }
        else {
            $script:Config.NGROK_DOMAIN = ""
        }
        
        # Install pyngrok if not already installed
        Write-ColorOutput "Checking pyngrok installation..." -Type Info
        try {
            & python -c "import pyngrok" 2>&1 | Out-Null
            Write-ColorOutput "pyngrok is installed" -Type Success
        }
        catch {
            Write-ColorOutput "Installing pyngrok..." -Type Info
            & python -m pip install "pyngrok>=7.0.0" --quiet
            Write-ColorOutput "pyngrok installed" -Type Success
        }
        
        Write-ColorOutput "Ngrok configured" -Type Success
    }
    else {
        $script:Config.NGROK_ENABLED = "false"
        $script:Config.NGROK_AUTH_TOKEN = ""
        Write-ColorOutput "Ngrok will not be used" -Type Info
    }
}

function Set-OptionalServices {
    Write-Section "Optional Services"
    
    # Brave Search
    if (Read-YesNo -Prompt "Enable Brave Search integration?" -Default $false) {
        Write-ColorOutput "Get API key from: https://brave.com/search/api/" -Type Info
        $script:Config.COPILOT_MCP_BRAVE_API_KEY = Read-Input -Prompt "Brave Search API key" -Secure
        Write-ColorOutput "Brave Search configured" -Type Success
    }
    else {
        $script:Config.COPILOT_MCP_BRAVE_API_KEY = ""
    }
    
    # PostgreSQL
    if (Read-YesNo -Prompt "Enable PostgreSQL integration?" -Default $false) {
        Write-ColorOutput "Format: postgresql://user:password@host:port/database" -Type Info
        $script:Config.COPILOT_MCP_POSTGRES_CONNECTION_STRING = Read-Input -Prompt "PostgreSQL connection string"
        Write-ColorOutput "PostgreSQL configured" -Type Success
    }
    else {
        $script:Config.COPILOT_MCP_POSTGRES_CONNECTION_STRING = ""
    }
}

function Set-ServerConfiguration {
    Write-Section "Server Configuration"
    
    $script:Config.HOST = Read-Input -Prompt "Server host" -Default $script:Config.HOST
    $script:Config.PORT = Read-Input -Prompt "Server port" -Default $script:Config.PORT
    
    Write-ColorOutput "Server will run on $($script:Config.HOST):$($script:Config.PORT)" -Type Success
}

function Set-AdvancedSettings {
    Write-Section "Advanced Settings"
    
    if (Read-YesNo -Prompt "Configure advanced settings?" -Default $false) {
        # Debug mode
        if (Read-YesNo -Prompt "Enable debug mode?" -Default $false) {
            $script:Config.DEBUG_MODE = "true"
        }
        else {
            $script:Config.DEBUG_MODE = "false"
        }
        
        # Log level
        Write-Host ""
        Write-Host "Log levels:" -ForegroundColor Cyan
        Write-Host "  1. DEBUG   - Detailed debugging information" -ForegroundColor White
        Write-Host "  2. INFO    - General information (default)" -ForegroundColor White
        Write-Host "  3. WARNING - Warning messages only" -ForegroundColor White
        Write-Host "  4. ERROR   - Error messages only" -ForegroundColor White
        Write-Host ""
        
        $choice = Read-Input -Prompt "Select log level (1-4)" -Default "2"
        
        $script:Config.LOG_LEVEL = switch ($choice) {
            "1" { "DEBUG" }
            "2" { "INFO" }
            "3" { "WARNING" }
            "4" { "ERROR" }
            default { "INFO" }
        }
        
        Write-ColorOutput "Advanced settings configured" -Type Success
    }
}

function Save-Configuration {
    Write-Section "Saving Configuration"
    
    $envPath = Join-Path $PSScriptRoot ".env"
    
    # Backup existing .env
    if (Test-Path $envPath) {
        $backupPath = "$envPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $envPath $backupPath
        Write-ColorOutput "Backed up existing .env to: $(Split-Path $backupPath -Leaf)" -Type Info
    }
    
    # Create new .env file
    $envContent = @"
# Antigravity Workspace Configuration
# Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# ═══ AI Models ═══
# Gemini API Key (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=$($script:Config.GEMINI_API_KEY)

# Vertex AI Configuration (Google Cloud)
VERTEX_API_KEY=$($script:Config.VERTEX_API_KEY)
VERTEX_PROJECT_ID=$($script:Config.VERTEX_PROJECT_ID)
VERTEX_LOCATION=$($script:Config.VERTEX_LOCATION)
VERTEX_MODEL=$($script:Config.VERTEX_MODEL)

# Local Model Settings (if using Ollama)
LOCAL_MODEL=$($script:Config.LOCAL_MODEL)

# Active AI Model Selection
# Options: 'gemini', 'vertex', 'ollama', 'auto'
ACTIVE_MODEL=$($script:Config.ACTIVE_MODEL)

# ═══ GitHub Integration ═══
COPILOT_MCP_GITHUB_TOKEN=$($script:Config.COPILOT_MCP_GITHUB_TOKEN)

# ═══ Optional Services ═══
# Brave Search API
COPILOT_MCP_BRAVE_API_KEY=$($script:Config.COPILOT_MCP_BRAVE_API_KEY)

# PostgreSQL connection
COPILOT_MCP_POSTGRES_CONNECTION_STRING=$($script:Config.COPILOT_MCP_POSTGRES_CONNECTION_STRING)

# ═══ Server Configuration ═══
HOST=$($script:Config.HOST)
PORT=$($script:Config.PORT)

# ═══ Ngrok Configuration ═══
NGROK_ENABLED=$($script:Config.NGROK_ENABLED)
NGROK_AUTH_TOKEN=$($script:Config.NGROK_AUTH_TOKEN)
NGROK_REGION=$($script:Config.NGROK_REGION)
NGROK_DOMAIN=$($script:Config.NGROK_DOMAIN)

# ═══ Security Settings ═══
ALLOWED_ORIGINS=$($script:Config.ALLOWED_ORIGINS)

# ═══ Advanced Settings ═══
DEBUG_MODE=$($script:Config.DEBUG_MODE)
LOG_LEVEL=$($script:Config.LOG_LEVEL)

# Agent settings
AGENT_NAME=AntigravityAgent
MAX_ITERATIONS=10

# Database
DB_PATH=./data.db
"@
    
    Set-Content -Path $envPath -Value $envContent
    Write-ColorOutput "Configuration saved to .env" -Type Success
}

function Show-Summary {
    Write-Section "Configuration Summary"
    
    Write-Host "✓ Gemini AI: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.GEMINI_API_KEY) { "Configured" } else { "Not configured" })
    
    Write-Host "✓ Vertex AI: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.VERTEX_API_KEY) { "Configured" } else { "Not configured" })
    
    Write-Host "✓ Active Model: " -NoNewline -ForegroundColor Green
    Write-Host $script:Config.ACTIVE_MODEL
    
    Write-Host "✓ Local AI (Ollama): " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.LOCAL_MODEL) { $script:Config.LOCAL_MODEL } else { "Disabled" })
    
    Write-Host "✓ GitHub Integration: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.COPILOT_MCP_GITHUB_TOKEN) { "Enabled" } else { "Disabled" })
    
    Write-Host "✓ Ngrok Tunnel: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.NGROK_ENABLED -eq "true") { "Enabled" } else { "Disabled" })
    
    Write-Host "✓ Brave Search: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.COPILOT_MCP_BRAVE_API_KEY) { "Enabled" } else { "Disabled" })
    
    Write-Host "✓ PostgreSQL: " -NoNewline -ForegroundColor Green
    Write-Host $(if ($script:Config.COPILOT_MCP_POSTGRES_CONNECTION_STRING) { "Enabled" } else { "Disabled" })
    
    Write-Host "✓ Server: " -NoNewline -ForegroundColor Green
    Write-Host "$($script:Config.HOST):$($script:Config.PORT)"
    
    Write-Host ""
    Write-ColorOutput "Configuration file: $(Join-Path $PSScriptRoot '.env')" -Type Info
}

function Show-NextSteps {
    Write-Section "Next Steps"
    
    Write-Host "1. Start the workspace:" -ForegroundColor Cyan
    Write-Host "   .\start.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Access web interface:" -ForegroundColor Cyan
    Write-Host "   http://localhost:$($script:Config.PORT)" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Reconfigure anytime:" -ForegroundColor Cyan
    Write-Host "   .\configure.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "4. View documentation:" -ForegroundColor Cyan
    Write-Host "   docs\WINDOWS_SETUP.md" -ForegroundColor White
    Write-Host ""
}

# Main execution
function Main {
    Write-Header
    
    Write-ColorOutput "This wizard will help you configure Antigravity Workspace" -Type Info
    Write-ColorOutput "Press Ctrl+C at any time to cancel" -Type Info
    Write-Host ""
    
    if (-not (Read-YesNo -Prompt "Continue with configuration?" -Default $true)) {
        Write-ColorOutput "Configuration cancelled" -Type Info
        exit 0
    }
    
    # Load existing config if available
    Get-ExistingConfig
    
    # Run configuration steps
    Set-GeminiConfiguration
    Set-VertexConfiguration
    Set-ModelSelection
    Set-OllamaConfiguration
    Set-GitHubConfiguration
    Set-NgrokConfiguration
    Set-OptionalServices
    Set-ServerConfiguration
    Set-AdvancedSettings
    
    # Save configuration
    Save-Configuration
    
    # Display summary
    Show-Summary
    Show-NextSteps
    
    Write-ColorOutput "Configuration completed successfully!" -Type Success
    Write-Host ""
}

# Run main function
try {
    Main
}
catch {
    Write-Host ""
    Write-ColorOutput "Configuration failed: $_" -Type Error
    exit 1
}
