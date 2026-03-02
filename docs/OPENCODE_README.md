# OpenCode Configuration

This directory contains OpenCode-specific configuration files.

## Files

### `oh-my-opencode.json`

Configuration for the [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) plugin.

This file defines:
- **Agent model overrides**: Custom model assignments for specific agents
- **Feature flags**: Enable/disable specific oh-my-opencode features
- **MCP settings**: Built-in MCP server configurations
- **Settings**: Performance and behavior tuning

## Oh-My-OpenCode Plugin

Oh-my-opencode is a batteries-included OpenCode plugin that provides:

- **Multi-model orchestration**: Automatically routes tasks to the best model
- **Specialized agents**: Sisyphus, Hephaestus, Prometheus, Oracle, and more
- **Advanced tooling**: LSP integration, AST-Grep, hash-anchored edits
- **Background execution**: Parallel agent spawning for faster completion
- **Ultrawork mode**: Autonomous task completion with `ulw` command

### Installation

Oh-my-opencode is already configured in the root `opencode.json` file. To complete the setup:

1. Install OpenCode (if not already installed):
   ```bash
   curl -fsSL https://opencode.ai/install.sh | sh
   ```

2. Run the installation script:
   ```bash
   ./install-oh-my-opencode.sh  # Linux/Mac
   # or
   .\install-oh-my-opencode.ps1  # Windows
   ```

3. Authenticate with your providers:
   ```bash
   opencode auth login
   ```

### Configuration

The `oh-my-opencode.json` file contains default settings for the Antigravity workspace.

#### Agent Models

Agents are pre-configured to use optimal models:

- **Sisyphus**: Main orchestrator (Claude Opus / Kimi K2.5 / GLM 5)
- **Hephaestus**: Deep autonomous worker (GPT-5.3-codex)
- **Prometheus**: Strategic planner (Claude Opus / Kimi K2.5)
- **Oracle**: Architecture specialist (GPT-5.2)
- **Explore**: Fast search (MiniMax / Grok)
- **Librarian**: Documentation search (MiniMax / Gemini Flash)
- **Multimodal Looker**: Visual tasks (Antigravity Gemini 3 Flash)

#### Features

All features are enabled by default:

- `intent_gate`: Analyzes user intent before acting
- `hash_anchored_edit`: Content-hash validated edits
- `lsp_integration`: LSP server integration
- `background_agents`: Parallel agent execution
- `todo_enforcer`: Ensures task completion
- `comment_checker`: Prevents AI slop in comments
- `tmux_integration`: Interactive terminal support

#### MCPs

Built-in MCP servers for oh-my-opencode:

- **Exa**: Web search
- **Context7**: Official documentation
- **Grep.app**: GitHub code search

### Customization

To override agent models, edit `oh-my-opencode.json`:

```json
{
  "agents": {
    "sisyphus": {
      "model": "anthropic/claude-opus-4-6"
    },
    "oracle": {
      "model": "openai/gpt-5.2"
    }
  }
}
```

To adjust performance settings:

```json
{
  "settings": {
    "parallel_agent_limit": 3,
    "ralph_loop_max_iterations": 50
  }
}
```

### Documentation

- **Setup Guide**: [docs/OH_MY_OPENCODE_SETUP.md](../docs/OH_MY_OPENCODE_SETUP.md)
- **Quick Reference**: [docs/OH_MY_OPENCODE_QUICK_REFERENCE.md](../docs/OH_MY_OPENCODE_QUICK_REFERENCE.md)
- **GitHub**: https://github.com/code-yeongyu/oh-my-opencode

## Global OpenCode Configuration

The main OpenCode configuration is in the root `opencode.json` file, which includes:

- **Plugin registry**: `oh-my-opencode@latest` and `opencode-antigravity-auth@latest`
- **MCP servers**: 30+ MCP server configurations
- **Permissions**: Auto-approve settings

### Location Priority

OpenCode loads configuration from multiple locations in this order:

1. `~/.config/opencode/opencode.json` (global user config)
2. `./opencode.json` (repository root - this file)
3. `./.opencode/oh-my-opencode.json` (plugin-specific config - this directory)

Settings in later files override earlier ones.

## Compatibility

Oh-my-opencode is fully compatible with:

- **Claude Code**: All hooks, commands, and skills work
- **Antigravity Agents**: Custom agents in `.github/agents/`
- **MCP Servers**: All servers in `opencode.json`
- **Plugins**: Other OpenCode plugins

## Support

For issues or questions:

- **Oh-my-opencode**: https://github.com/code-yeongyu/oh-my-opencode/issues
- **Antigravity**: https://github.com/AloSantana/Antigravitys/issues
- **OpenCode**: https://opencode.ai/docs/
