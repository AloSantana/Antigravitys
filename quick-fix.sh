#!/usr/bin/env bash
#
# Quick Fix Script for Common Agent Blocking Issues
# Run this to automatically fix common problems
#
# Note: We intentionally do not use 'set -e' here so that best-effort
# fixes (like cache clears or installs) can fail without aborting the script.

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║            Quick Fix for Agent Blocking Issues                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f ".github/copilot/mcp.json" ]; then
    echo "❌ Error: Run this script from the repository root"
    exit 1
fi

echo "This script will attempt to fix common issues that block agents."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FIX 1: Creating .env file if missing..."

# Ensure .env is in .gitignore before creating it
if [ -f .gitignore ]; then
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo ".env" >> .gitignore
        echo "✓ Added .env to .gitignore"
    fi
else
    echo ".env" > .gitignore
    echo "✓ Created .gitignore with .env entry"
fi

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# GitHub Token for MCP servers
export GITHUB_TOKEN=your_github_token_here
export COPILOT_MCP_GITHUB_TOKEN=your_github_token_here

# Optional - Brave Search API (enable brave-search MCP server)
# export BRAVE_API_KEY=your_brave_api_key
# export COPILOT_MCP_BRAVE_API_KEY=your_brave_api_key

# Optional - PostgreSQL (enable postgres MCP server)
# export POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
# export COPILOT_MCP_POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
EOF
    echo "✓ Created .env file with export statements"
    echo "  ⚠ IMPORTANT: Edit .env and add your actual GitHub token!"
    echo "  ⚠ WARNING: Never commit this file - it's already in .gitignore"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "FIX 2: Cleaning npm cache..."
if command -v npm &> /dev/null; then
    npm cache clean --force > /dev/null 2>&1
    echo "✓ npm cache cleaned"
else
    echo "⚠ npm not installed, skipping"
fi

echo ""
echo "FIX 3: Clearing MCP cache..."
# More carefully clean MCP cache
if [ -d "$HOME/.mcp/cache" ]; then
    find "$HOME/.mcp/cache" -mindepth 1 -delete 2>/dev/null || true
fi

# Clean temp mcp files if they exist
find /tmp -maxdepth 1 -name "mcp-*" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✓ MCP cache cleared"

echo ""
echo "FIX 4: Pre-installing essential MCP servers..."
if command -v npx &> /dev/null; then
    echo "  Installing filesystem server..."
    npx -y @modelcontextprotocol/server-filesystem --version > /dev/null 2>&1 || true
    echo "  Installing memory server..."
    npx -y @modelcontextprotocol/server-memory --version > /dev/null 2>&1 || true
    echo "  Installing sequential-thinking server..."
    npx -y @modelcontextprotocol/server-sequential-thinking --version > /dev/null 2>&1 || true
    echo "✓ MCP servers pre-installed"
else
    echo "⚠ npx not available, skipping"
fi

echo ""
echo "FIX 5: Installing Python MCP server (if Python available)..."
if command -v pip3 &> /dev/null; then
    pip3 install --quiet mcp-server-python-analysis 2>/dev/null || pip3 install --user --quiet mcp-server-python-analysis 2>/dev/null || echo "  ⚠ Could not install (may already be installed)"
    echo "✓ Python MCP server installation attempted"
elif command -v pip &> /dev/null; then
    pip install --quiet mcp-server-python-analysis 2>/dev/null || pip install --user --quiet mcp-server-python-analysis 2>/dev/null || echo "  ⚠ Could not install (may already be installed)"
    echo "✓ Python MCP server installation attempted"
else
    echo "⚠ pip not found, skipping"
fi

echo ""
echo "FIX 6: Validating JSON configurations..."
if command -v python3 &> /dev/null; then
    if [ -f ".github/copilot/mcp.json" ]; then
        if python3 -m json.tool < .github/copilot/mcp.json > /dev/null 2>&1; then
            echo "✓ .github/copilot/mcp.json is valid"
        else
            echo "⚠ .github/copilot/mcp.json has invalid JSON"
        fi
    else
        echo "⚠ .github/copilot/mcp.json not found, skipping validation"
    fi
    
    if [ -f ".mcp/config.json" ]; then
        if python3 -m json.tool < .mcp/config.json > /dev/null 2>&1; then
            echo "✓ .mcp/config.json is valid"
        else
            echo "⚠ .mcp/config.json has invalid JSON"
        fi
    else
        echo "⚠ .mcp/config.json not found, skipping validation"
    fi
else
    echo "⚠ Python not available, cannot validate JSON"
fi

echo ""
echo "FIX 7: Updating .gitignore with MCP entries..."
echo "The following entries will be added to .gitignore if not present:"
echo "  - node_modules/"
echo "  - .mcp/cache/"
echo "  - .mcp/logs/"
echo ""
read -p "Update .gitignore with recommended MCP entries? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check write permissions before attempting to modify .gitignore
    if [ -e .gitignore ] && [ ! -w .gitignore ]; then
        echo "⚠ .gitignore is not writable; skipping updates"
    elif [ ! -e .gitignore ] && [ ! -w . ]; then
        echo "⚠ Repository root is not writable; skipping .gitignore creation"
    else
        gitignore_updated=false
        # Use -Fxq for exact line matching (fixed string, whole line, quiet)
        if ! grep -Fxq "node_modules/" .gitignore 2>/dev/null; then
            # Ensure file ends with newline before appending
            [ -f .gitignore ] && [ -n "$(tail -c1 .gitignore 2>/dev/null)" ] && echo "" >> .gitignore
            echo "node_modules/" >> .gitignore
            gitignore_updated=true
        fi
        if ! grep -Fxq ".mcp/cache/" .gitignore 2>/dev/null; then
            [ -f .gitignore ] && [ -n "$(tail -c1 .gitignore 2>/dev/null)" ] && echo "" >> .gitignore
            echo ".mcp/cache/" >> .gitignore
            gitignore_updated=true
        fi
        if ! grep -Fxq ".mcp/logs/" .gitignore 2>/dev/null; then
            [ -f .gitignore ] && [ -n "$(tail -c1 .gitignore 2>/dev/null)" ] && echo "" >> .gitignore
            echo ".mcp/logs/" >> .gitignore
            gitignore_updated=true
        fi
        if [ "$gitignore_updated" = true ]; then
            echo "✓ .gitignore updated with new entries"
        else
            echo "✓ .gitignore already contains all MCP entries"
        fi
    fi
else
    echo "✓ Skipped .gitignore updates"
fi

echo ""
echo "FIX 8: Setting optimal npm configuration..."
if command -v npm &> /dev/null; then
    npm config set fetch-timeout 60000 2>/dev/null || true
    npm config set fetch-retries 3 2>/dev/null || true
    echo "✓ npm configuration optimized"
else
    echo "⚠ npm not available"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FIXES COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your GitHub token:"
echo "     Get token from: https://github.com/settings/tokens"
echo ""
echo "  2. Load environment variables (variables now have 'export'):"
echo "     source .env"
echo ""
echo "  3. Verify setup:"
echo "     ./health-check.sh"
echo ""
echo "  4. Restart your IDE/editor"
echo ""
echo "  5. Try your first agent:"
echo "     @agent:repo-optimizer Analyze this repository structure"
echo ""
echo "If issues persist, see TROUBLESHOOTING.md for detailed help."
