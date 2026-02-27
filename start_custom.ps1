
# Custom startup script
$envPath = ".\.env"
$envExamplePath = ".\.env.example"

if (-not (Test-Path $envPath)) {
    Write-Host "Creating .env from example..."
    Copy-Item $envExamplePath $envPath
}

# Read content as array of lines
$lines = Get-Content $envPath
$newLines = @()
$keysToUpdate = @{
    "NGROK_ENABLED" = "true"
    "ACTIVE_MODEL" = "auto"
    "DEBUG_MODE" = "true"
    "LOG_LEVEL" = "DEBUG"
}
$foundKeys = @{}

foreach ($line in $lines) {
    $updated = $false
    foreach ($key in $keysToUpdate.Keys) {
        if ($line -match "^$key=") {
            $newLines += "$key=$($keysToUpdate[$key])"
            $foundKeys[$key] = $true
            $updated = $true
            break
        }
    }
    if (-not $updated) {
        $newLines += $line
    }
}

# Add missing keys
foreach ($key in $keysToUpdate.Keys) {
    if (-not $foundKeys.ContainsKey($key)) {
        $newLines += "$key=$($keysToUpdate[$key])"
    }
}

$newLines | Set-Content $envPath
Write-Host "Configuration updated."

# Run start script
.\start.ps1
