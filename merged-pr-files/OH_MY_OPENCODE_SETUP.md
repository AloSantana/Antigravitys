# Oh-My-OpenCode Setup Guide

This guide walks you through installing and configuring oh-my-opencode for the Antigravity workspace.

## Prerequisites

### 1. Install OpenCode

Oh-my-opencode is a plugin for OpenCode, so OpenCode must be installed first.

**For Linux/macOS:**
```bash
curl -fsSL https://opencode.ai/install.sh | sh
```

**For Windows:**
```powershell
irm https://opencode.ai/install.ps1 | iex
```

**Verify Installation:**
```bash
opencode --version  # Should be 1.0.150 or higher
```

If OpenCode is not available via the install script, you can install it via npm:
```bash
npm install -g opencode
```

## Installation

### Automated Installation (Recommended)

The easiest way to install oh-my-opencode is to paste the following prompt into an LLM agent (Claude Code, OpenCode, etc.):

```
Install and configure oh-my-opencode by following the instructions here:
https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/dev/docs/guide/installation.md
```

The agent will:
1. Ask about your subscriptions (Claude, ChatGPT, Gemini, GitHub Copilot, etc.)
2. Run the installer with appropriate flags
3. Configure authentication
4. Verify the setup

### Manual Installation

If you prefer to install manually, run:

```bash
npx oh-my-opencode install --no-tui
```

You'll be prompted for your subscriptions. Answer the questions to configure the appropriate models.

## Configuration

### Subscription-Based Installation

The installer will ask about your subscriptions to determine which models to use:

#### 1. Claude Subscription
- **No subscription**: `--claude=no`
- **Claude Pro/Max**: `--claude=yes`
- **Claude Max20 (20x mode)**: `--claude=max20`

#### 2. OpenAI/ChatGPT Subscription
- **No subscription**: `--openai=no` (default)
- **ChatGPT Plus**: `--openai=yes` (enables GPT-5.2 for Oracle agent)

#### 3. Gemini Models
- **No integration**: `--gemini=no`
- **Using Gemini**: `--gemini=yes`

#### 4. GitHub Copilot
- **No subscription**: `--copilot=no`
- **Has subscription**: `--copilot=yes`

#### 5. OpenCode Zen
- **No access**: `--opencode-zen=no` (default)
- **Has access**: `--opencode-zen=yes`

#### 6. Z.ai Coding Plan
- **No subscription**: `--zai-coding-plan=no` (default)
- **Has subscription**: `--zai-coding-plan=yes`

### Example Installation Commands

**All native subscriptions:**
```bash
npx oh-my-opencode install --no-tui --claude=max20 --openai=yes --gemini=yes --copilot=no
```

**Claude only:**
```bash
npx oh-my-opencode install --no-tui --claude=yes --gemini=no --copilot=no
```

**GitHub Copilot only:**
```bash
npx oh-my-opencode install --no-tui --claude=no --gemini=no --copilot=yes
```

**Using Bun (faster):**
```bash
bunx oh-my-opencode install --no-tui --claude=yes --openai=no --gemini=no --copilot=no
```

## Authentication

After installation, you need to authenticate with your chosen providers.

### Anthropic (Claude)

```bash
opencode auth login
# Select Provider: Anthropic
# Select Login method: Claude Pro/Max
# Follow OAuth flow in browser
```

### Google Gemini (with Antigravity OAuth)

First, ensure the `opencode-antigravity-auth` plugin is installed. The installer should have added it, but you can verify in `~/.config/opencode/opencode.json`:

```json
{
  "plugin": [
    "oh-my-opencode",
    "opencode-antigravity-auth@latest"
  ]
}
```

Then authenticate:

```bash
opencode auth login
# Select Provider: Google
# Select Login method: OAuth with Google (Antigravity)
# Complete sign-in in browser
```

### GitHub Copilot

```bash
opencode auth login
# Select: GitHub
# Authenticate via OAuth
```

## Verification

After installation and authentication:

```bash
# Check OpenCode version
opencode --version  # Should be 1.0.150 or higher

# Check plugin configuration
cat ~/.config/opencode/opencode.json | grep oh-my-opencode

# Test OpenCode
opencode
```

## Agent Models

Oh-my-opencode comes with several specialized agents:

### Main Agents

| Agent | Default Model | Role |
|-------|--------------|------|
| **Sisyphus** | Claude Opus 4.6 / Kimi K2.5 / GLM 5 | Main orchestrator, drives tasks to completion |
| **Hephaestus** | GPT-5.3-codex | Autonomous deep worker, explores and executes |
| **Prometheus** | Claude Opus 4.6 / Kimi K2.5 | Strategic planner, interview mode |
| **Oracle** | GPT-5.2 | Architecture and debugging specialist |
| **Momus** | GPT-5.2 | High-accuracy code reviewer |

### Utility Agents

| Agent | Default Model | Role |
|-------|--------------|------|
| **Explore** | MiniMax M2.5 Free / Grok Code Fast | Fast codebase search |
| **Librarian** | MiniMax M2.5 Free / Gemini Flash | Documentation search |
| **Multimodal Looker** | Kimi K2.5 | Vision and screenshot analysis |
| **Atlas** | Kimi K2.5 | Todo orchestrator |
| **Metis** | Claude Opus | Plan review |

## Customization

### Model Configuration

To override agent models, create or edit `~/.config/opencode/oh-my-opencode.json`:

```json
{
  "agents": {
    "sisyphus": { "model": "kimi-for-coding/k2p5" },
    "prometheus": { "model": "openai/gpt-5.2" },
    "oracle": { "model": "anthropic/claude-opus-4-6" }
  }
}
```

### Gemini with Antigravity

If using `opencode-antigravity-auth`, configure models:

```json
{
  "agents": {
    "multimodal-looker": { "model": "google/antigravity-gemini-3-flash" }
  }
}
```

**Available Antigravity models:**
- `google/antigravity-gemini-3-pro` (variants: `low`, `high`)
- `google/antigravity-gemini-3-flash` (variants: `minimal`, `low`, `medium`, `high`)
- `google/antigravity-claude-sonnet-4-6`
- `google/antigravity-claude-sonnet-4-6-thinking` (variants: `low`, `max`)
- `google/antigravity-claude-opus-4-5-thinking` (variants: `low`, `max`)

## Usage

### Basic Usage

Start OpenCode and type `ultrawork` (or `ulw`) to activate the full agent system:

```bash
opencode
# In the prompt:
> ultrawork: Implement user authentication with JWT tokens
```

### Planner Mode

Press **Tab** to enter Prometheus planner mode for strategic planning:

```bash
opencode
# Press Tab
# Answer interview questions
# Run /start-work to execute
```

### Commands

- `ultrawork` or `ulw` - Activate all agents, autonomous completion
- `/ulw-loop` - Ralph loop mode (doesn't stop until 100% done)
- `/init-deep` - Generate hierarchical AGENTS.md files for better context
- `/start-work` - Execute a Prometheus plan

## Integration with Antigravity

Oh-my-opencode is fully compatible with the Antigravity workspace:

1. **MCP Servers**: All existing MCP servers in `opencode.json` work with oh-my-opencode
2. **Custom Agents**: Antigravity's custom agents (`.github/agents/*.agent.md`) can coexist
3. **Skills**: Claude Code skills are compatible
4. **Hooks**: All hooks and commands work unchanged

## Troubleshooting

### OpenCode not found
```bash
# Check PATH
echo $PATH | grep opencode

# Reinstall OpenCode
curl -fsSL https://opencode.ai/install.sh | sh

# Or via npm
npm install -g opencode
```

### Plugin not loading
```bash
# Check plugin registration
cat ~/.config/opencode/opencode.json | jq '.plugin'

# Reinstall plugin
npx oh-my-opencode install --no-tui --claude=yes
```

### Authentication issues
```bash
# Clear auth and retry
rm -rf ~/.config/opencode/auth

# Re-authenticate
opencode auth login
```

### Model errors
```bash
# Check available models
opencode models list

# Update plugin
npm update -g oh-my-opencode
```

## Provider Priority

When multiple providers are available, oh-my-opencode uses this priority:

```
Native (anthropic/, openai/, google/)
  → Kimi for Coding
  → GitHub Copilot
  → Venice
  → OpenCode Zen
  → Z.ai Coding Plan
```

## Next Steps

1. **Star the repository** if you find it helpful: https://github.com/code-yeongyu/oh-my-opencode
2. **Read the overview guide**: https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/dev/docs/guide/overview.md
3. **Join the Discord**: https://discord.gg/PUwSMR9XNk
4. **Explore agent skills**: https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/dev/docs/guide/agent-model-matching.md

## References

- [Installation Guide](https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/dev/docs/guide/installation.md)
- [Overview Guide](https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/dev/docs/guide/overview.md)
- [GitHub Repository](https://github.com/code-yeongyu/oh-my-opencode)
- [OpenCode Documentation](https://opencode.ai/docs/)
