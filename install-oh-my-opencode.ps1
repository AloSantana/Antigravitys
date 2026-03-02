# Oh-My-OpenCode Installation Script for Antigravity Workspace (Windows)
# This script helps install and configure oh-my-opencode on Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Oh-My-OpenCode Installation Helper" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check OpenCode installation
Write-Host "Step 1: Checking OpenCode installation..." -ForegroundColor Yellow
$opencodeInstalled = Get-Command opencode -ErrorAction SilentlyContinue

if ($opencodeInstalled) {
    try {
        $opencodeVersion = & opencode --version 2>&1
        Write-Host "✓ OpenCode is installed: $opencodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "✓ OpenCode is installed" -ForegroundColor Green
    }
} else {
    Write-Host "✗ OpenCode is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "OpenCode must be installed first. Please install it using:"
    Write-Host ""
    Write-Host "  irm https://opencode.ai/install.ps1 | iex" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Or via npm:"
    Write-Host "    npm install -g opencode" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing OpenCode, run this script again."
    exit 1
}

# Step 2: Check npm
Write-Host ""
Write-Host "Step 2: Checking Node.js/npm installation..." -ForegroundColor Yellow
$npmInstalled = Get-Command npm -ErrorAction SilentlyContinue

if (-not $npmInstalled) {
    Write-Host "✗ npm is not installed" -ForegroundColor Red
    Write-Host "npm is required to install oh-my-opencode."
    Write-Host "Please install Node.js from https://nodejs.org/"
    exit 1
}

$npmVersion = & npm --version
Write-Host "✓ npm is installed: $npmVersion" -ForegroundColor Green

$npxInstalled = Get-Command npx -ErrorAction SilentlyContinue
if (-not $npxInstalled) {
    Write-Host "✗ npx is not available" -ForegroundColor Red
    exit 1
}
Write-Host "✓ npx is available" -ForegroundColor Green

# Step 3: Check for Bun (optional)
Write-Host ""
Write-Host "Step 3: Checking for Bun (optional, but faster)..." -ForegroundColor Yellow
$bunInstalled = Get-Command bunx -ErrorAction SilentlyContinue

if ($bunInstalled) {
    try {
        $bunVersion = & bunx --version
        Write-Host "✓ Bun is installed: $bunVersion" -ForegroundColor Green
        $installer = "bunx"
    } catch {
        Write-Host "ℹ Bun check failed, will use npx" -ForegroundColor Yellow
        $installer = "npx"
    }
} else {
    Write-Host "ℹ Bun is not installed (optional, will use npx)" -ForegroundColor Yellow
    $installer = "npx"
}

# Interactive subscription questions
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Subscription Configuration" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The installer needs to know which AI provider subscriptions you have."
Write-Host "This determines which models will be used for different agents."
Write-Host ""

$claudeSub = Read-Host "Do you have a Claude Pro/Max Subscription? (y/n/max20)"
switch ($claudeSub.ToLower()) {
    "max20" { $claudeFlag = "--claude=max20" }
    { $_ -in @("y", "yes") } { $claudeFlag = "--claude=yes" }
    default { $claudeFlag = "--claude=no" }
}

$openaiSub = Read-Host "Do you have an OpenAI/ChatGPT Plus Subscription? (y/n)"
if ($openaiSub -match "^[yY](es)?$") {
    $openaiFlag = "--openai=yes"
} else {
    $openaiFlag = "--openai=no"
}

$geminiSub = Read-Host "Will you integrate Gemini models? (y/n)"
if ($geminiSub -match "^[yY](es)?$") {
    $geminiFlag = "--gemini=yes"
} else {
    $geminiFlag = "--gemini=no"
}

$copilotSub = Read-Host "Do you have a GitHub Copilot Subscription? (y/n)"
if ($copilotSub -match "^[yY](es)?$") {
    $copilotFlag = "--copilot=yes"
} else {
    $copilotFlag = "--copilot=no"
}

$zenSub = Read-Host "Do you have access to OpenCode Zen? (y/n)"
if ($zenSub -match "^[yY](es)?$") {
    $zenFlag = "--opencode-zen=yes"
} else {
    $zenFlag = ""
}

$zaiSub = Read-Host "Do you have a Z.ai Coding Plan subscription? (y/n)"
if ($zaiSub -match "^[yY](es)?$") {
    $zaiFlag = "--zai-coding-plan=yes"
} else {
    $zaiFlag = ""
}

# Build installation command
$installCmd = "$installer oh-my-opencode install --no-tui $claudeFlag $openaiFlag $geminiFlag $copilotFlag"
if ($zenFlag) { $installCmd += " $zenFlag" }
if ($zaiFlag) { $installCmd += " $zaiFlag" }

# Show installation command
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Installation Command" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The following command will be executed:"
Write-Host ""
Write-Host "  $installCmd" -ForegroundColor Yellow
Write-Host ""
$proceed = Read-Host "Proceed with installation? (y/n)"

if ($proceed -notmatch "^[yY](es)?$") {
    Write-Host "Installation cancelled."
    exit 0
}

# Run installation
Write-Host ""
Write-Host "Step 4: Installing oh-my-opencode..." -ForegroundColor Yellow
Invoke-Expression $installCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ oh-my-opencode installed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Installation failed" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Step 5: Verifying installation..." -ForegroundColor Yellow
$configPath = Join-Path $env:USERPROFILE ".config\opencode\opencode.json"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match "oh-my-opencode") {
        Write-Host "✓ oh-my-opencode is registered in opencode.json" -ForegroundColor Green
    } else {
        Write-Host "⚠ oh-my-opencode may not be registered correctly" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ opencode.json not found at expected location" -ForegroundColor Yellow
}

# Next steps
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "1. Configure authentication for your providers:"
Write-Host ""

if ($claudeFlag -ne "--claude=no") {
    Write-Host "   Anthropic (Claude):" -ForegroundColor Yellow
    Write-Host "     opencode auth login"
    Write-Host "     # Select: Anthropic → Claude Pro/Max"
    Write-Host ""
}

if ($geminiFlag -eq "--gemini=yes") {
    Write-Host "   Google Gemini (Antigravity):" -ForegroundColor Yellow
    Write-Host "     opencode auth login"
    Write-Host "     # Select: Google → OAuth with Google (Antigravity)"
    Write-Host ""
}

if ($copilotFlag -eq "--copilot=yes") {
    Write-Host "   GitHub Copilot:" -ForegroundColor Yellow
    Write-Host "     opencode auth login"
    Write-Host "     # Select: GitHub → Authenticate via OAuth"
    Write-Host ""
}

Write-Host "2. Test OpenCode:"
Write-Host "     opencode"
Write-Host ""
Write-Host "3. Try the ultrawork command:"
Write-Host "     > ultrawork: Implement user authentication"
Write-Host ""
Write-Host "4. Read the documentation:"
Write-Host "     docs\OH_MY_OPENCODE_SETUP.md"
Write-Host ""
Write-Host "5. Star the repository if you find it helpful:"
Write-Host "     https://github.com/code-yeongyu/oh-my-opencode"
Write-Host ""
Write-Host "For more information, visit:"
Write-Host "  https://github.com/code-yeongyu/oh-my-opencode"
Write-Host ""
