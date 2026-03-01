$servers = @(
  "@modelcontextprotocol/server-filesystem",
  "@modelcontextprotocol/server-git",
  "@modelcontextprotocol/server-memory",
  "@modelcontextprotocol/server-sequential-thinking",
  "@modelcontextprotocol/server-fetch",
  "@modelcontextprotocol/server-time",
  "@github/mcp-server",
  "@playwright/mcp",
  "@upstash/context7-mcp",
  "@brave/brave-search-mcp-server",
  "chrome-devtools-mcp",
  "firecrawl-mcp",
  "exa-mcp-server",
  "mcp-server-docker",
  "agentops-mcp"
)

$markdown = "# MCP Servers Status`n`n| Server | Status |`n|---|---|`n"

foreach ($server in $servers) {
    Write-Host "Checking $server..."
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "npx.cmd"
    $pinfo.RedirectStandardError = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $pinfo.Arguments = "-y $server --help"
    $p.Start() | Out-Null
    $p.WaitForExit(5000) | Out-Null
    
    if (-not $p.HasExited) {
        $p.Kill()
        $status = "✅ Active"
    } else {
        if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 1 -or $p.ExitCode -eq 2) {
            $status = "✅ Installed"
        } else {
            $err = $p.StandardError.ReadToEnd()
            $status = "❌ Failed (Exit: $($p.ExitCode))"
        }
    }
    $markdown += "| $server | $status |`n"
}

$markdown | Out-File -FilePath "$PSScriptRoot\..\docs\MCP_STATUS.md" -Encoding utf8
Write-Host "Done. Results written to docs\MCP_STATUS.md"
