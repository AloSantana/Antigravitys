#!/bin/bash
# Oh-My-OpenCode Installation Script for Antigravity Workspace
# This script helps install and configure oh-my-opencode

set -e

echo "========================================="
echo "  Oh-My-OpenCode Installation Helper"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if OpenCode is installed
echo -e "${YELLOW}Step 1: Checking OpenCode installation...${NC}"
if command -v opencode &> /dev/null; then
    OPENCODE_VERSION=$(opencode --version 2>&1 || echo "unknown")
    echo -e "${GREEN}✓ OpenCode is installed: $OPENCODE_VERSION${NC}"
else
    echo -e "${RED}✗ OpenCode is not installed${NC}"
    echo ""
    echo "OpenCode must be installed first. Please install it using one of these methods:"
    echo ""
    echo "  Linux/macOS:"
    echo "    curl -fsSL https://opencode.ai/install.sh | sh"
    echo ""
    echo "  Windows:"
    echo "    irm https://opencode.ai/install.ps1 | iex"
    echo ""
    echo "  Via npm:"
    echo "    npm install -g opencode"
    echo ""
    echo "After installing OpenCode, run this script again."
    exit 1
fi

# Check Node.js/npm
echo ""
echo -e "${YELLOW}Step 2: Checking Node.js/npm installation...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    echo "npm is required to install oh-my-opencode."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ npm is installed: $(npm --version)${NC}"

# Check for npx
if ! command -v npx &> /dev/null; then
    echo -e "${RED}✗ npx is not available${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npx is available${NC}"

# Check for bunx (optional but faster)
echo ""
echo -e "${YELLOW}Step 3: Checking for Bun (optional, but faster)...${NC}"
if command -v bunx &> /dev/null; then
    echo -e "${GREEN}✓ Bun is installed: $(bunx --version)${NC}"
    INSTALLER="bunx"
else
    echo -e "${YELLOW}ℹ Bun is not installed (optional, will use npx)${NC}"
    INSTALLER="npx"
fi

# Interactive subscription questions
echo ""
echo "========================================="
echo "  Subscription Configuration"
echo "========================================="
echo ""
echo "The installer needs to know which AI provider subscriptions you have."
echo "This determines which models will be used for different agents."
echo ""

read -p "Do you have a Claude Pro/Max Subscription? (y/n/max20): " CLAUDE_SUB
case "$CLAUDE_SUB" in
    max20) CLAUDE_FLAG="--claude=max20" ;;
    y|yes|Y|YES) CLAUDE_FLAG="--claude=yes" ;;
    *) CLAUDE_FLAG="--claude=no" ;;
esac

read -p "Do you have an OpenAI/ChatGPT Plus Subscription? (y/n): " OPENAI_SUB
case "$OPENAI_SUB" in
    y|yes|Y|YES) OPENAI_FLAG="--openai=yes" ;;
    *) OPENAI_FLAG="--openai=no" ;;
esac

read -p "Will you integrate Gemini models? (y/n): " GEMINI_SUB
case "$GEMINI_SUB" in
    y|yes|Y|YES) GEMINI_FLAG="--gemini=yes" ;;
    *) GEMINI_FLAG="--gemini=no" ;;
esac

read -p "Do you have a GitHub Copilot Subscription? (y/n): " COPILOT_SUB
case "$COPILOT_SUB" in
    y|yes|Y|YES) COPILOT_FLAG="--copilot=yes" ;;
    *) COPILOT_FLAG="--copilot=no" ;;
esac

read -p "Do you have access to OpenCode Zen? (y/n): " ZEN_SUB
case "$ZEN_SUB" in
    y|yes|Y|YES) ZEN_FLAG="--opencode-zen=yes" ;;
    *) ZEN_FLAG="--opencode-zen=no" ;;
esac

read -p "Do you have a Z.ai Coding Plan subscription? (y/n): " ZAI_SUB
case "$ZAI_SUB" in
    y|yes|Y|YES) ZAI_FLAG="--zai-coding-plan=yes" ;;
    *) ZAI_FLAG="--zai-coding-plan=no" ;;
esac

# Build installation command
INSTALL_CMD="$INSTALLER oh-my-opencode install --no-tui $CLAUDE_FLAG $OPENAI_FLAG $GEMINI_FLAG $COPILOT_FLAG"
if [ "$ZEN_FLAG" = "--opencode-zen=yes" ]; then
    INSTALL_CMD="$INSTALL_CMD $ZEN_FLAG"
fi
if [ "$ZAI_FLAG" = "--zai-coding-plan=yes" ]; then
    INSTALL_CMD="$INSTALL_CMD $ZAI_FLAG"
fi

# Show installation command
echo ""
echo "========================================="
echo "  Installation Command"
echo "========================================="
echo ""
echo "The following command will be executed:"
echo ""
echo "  $INSTALL_CMD"
echo ""
read -p "Proceed with installation? (y/n): " PROCEED

if [ "$PROCEED" != "y" ] && [ "$PROCEED" != "Y" ] && [ "$PROCEED" != "yes" ] && [ "$PROCEED" != "YES" ]; then
    echo "Installation cancelled."
    exit 0
fi

# Run installation
echo ""
echo -e "${YELLOW}Step 4: Installing oh-my-opencode...${NC}"
$INSTALL_CMD

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ oh-my-opencode installed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Installation failed${NC}"
    exit 1
fi

# Verify installation
echo ""
echo -e "${YELLOW}Step 5: Verifying installation...${NC}"
if [ -f "$HOME/.config/opencode/opencode.json" ]; then
    if grep -q "oh-my-opencode" "$HOME/.config/opencode/opencode.json"; then
        echo -e "${GREEN}✓ oh-my-opencode is registered in opencode.json${NC}"
    else
        echo -e "${YELLOW}⚠ oh-my-opencode may not be registered correctly${NC}"
    fi
else
    echo -e "${YELLOW}⚠ opencode.json not found at expected location${NC}"
fi

# Next steps
echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure authentication for your providers:"
echo ""

if [ "$CLAUDE_FLAG" != "--claude=no" ]; then
    echo "   Anthropic (Claude):"
    echo "     opencode auth login"
    echo "     # Select: Anthropic → Claude Pro/Max"
    echo ""
fi

if [ "$GEMINI_FLAG" = "--gemini=yes" ]; then
    echo "   Google Gemini (Antigravity):"
    echo "     opencode auth login"
    echo "     # Select: Google → OAuth with Google (Antigravity)"
    echo ""
fi

if [ "$COPILOT_FLAG" = "--copilot=yes" ]; then
    echo "   GitHub Copilot:"
    echo "     opencode auth login"
    echo "     # Select: GitHub → Authenticate via OAuth"
    echo ""
fi

echo "2. Test OpenCode:"
echo "     opencode"
echo ""
echo "3. Try the ultrawork command:"
echo "     > ultrawork: Implement user authentication"
echo ""
echo "4. Read the documentation:"
echo "     docs/OH_MY_OPENCODE_SETUP.md"
echo ""
echo "5. Star the repository if you find it helpful:"
echo "     https://github.com/code-yeongyu/oh-my-opencode"
echo ""
echo "For more information, visit:"
echo "  https://github.com/code-yeongyu/oh-my-opencode"
echo ""
