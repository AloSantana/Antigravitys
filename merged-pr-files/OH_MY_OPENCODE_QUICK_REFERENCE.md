# Oh-My-OpenCode Quick Reference

Quick reference for using oh-my-opencode in the Antigravity workspace.

## Quick Start

```bash
# Start OpenCode
opencode

# Use ultrawork for autonomous task completion
> ultrawork: Implement user authentication with JWT tokens

# Or use the short alias
> ulw: Add rate limiting to the API
```

## Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `ultrawork` | `ulw` | Activate all agents for autonomous task completion |
| `/ulw-loop` | - | Ralph loop mode (doesn't stop until 100% done) |
| `/init-deep` | - | Generate hierarchical AGENTS.md files |
| `/start-work` | - | Execute a Prometheus plan |
| **Tab** | - | Enter Prometheus planner mode |

## Agents

### Main Agents

| Agent | Model | When to Use |
|-------|-------|-------------|
| **Sisyphus** | Claude Opus 4.6 / Kimi K2.5 / GLM 5 | Main orchestrator, use for complex multi-step tasks |
| **Hephaestus** | GPT-5.3-codex | Autonomous deep work, research + implementation |
| **Prometheus** | Claude Opus 4.6 / Kimi K2.5 | Strategic planning before execution |
| **Oracle** | GPT-5.2 | Architecture decisions, debugging complex issues |
| **Momus** | GPT-5.2 | High-accuracy code review |

### Utility Agents

| Agent | Model | When to Use |
|-------|-------|-------------|
| **Explore** | MiniMax M2.5 Free / Grok | Fast codebase search and grep |
| **Librarian** | MiniMax M2.5 Free / Gemini Flash | Documentation and reference lookup |
| **Multimodal Looker** | Kimi K2.5 | Screenshots, UI analysis, images |
| **Atlas** | Kimi K2.5 | Todo management and orchestration |
| **Metis** | Claude Opus | Plan review and gap analysis |

## Common Workflows

### 1. Fast Feature Development
```bash
> ultrawork: Implement dark mode toggle with persistence
```
The agent will:
- Plan the architecture
- Implement the feature end-to-end
- Create tests
- Review for security/quality
- Document the changes

### 2. Strategic Planning First
```bash
# Press Tab to enter planner mode
Prometheus will interview you, create a detailed plan
# Then run:
> /start-work
```

### 3. Deep Research + Implementation
```bash
> ultrawork: Research and implement GraphQL subscriptions for real-time updates
```
Hephaestus will research patterns and implement autonomously.

### 4. Code Review
```bash
> Ask Momus to review backend/main.py for security issues
```

### 5. Documentation Search
```bash
> Ask Librarian to find FastAPI WebSocket examples
```

## Key Features

### 🪄 Ultrawork
Just type `ultrawork` or `ulw` followed by your task. The system:
- Automatically selects the right agents
- Runs specialists in parallel
- Doesn't stop until 100% complete
- Handles errors and retries

### 🔗 Hash-Anchored Edit Tool
Every line edit is content-hash validated. Zero stale-line errors.

### 🛠️ LSP + AST-Grep Integration
- Workspace-wide rename
- Pre-build diagnostics
- AST-aware code rewrites

### 🧠 Background Agents
Fire 5+ specialists in parallel. Results when ready.

### 📚 Built-in MCPs
- **Exa**: Web search
- **Context7**: Official documentation
- **Grep.app**: GitHub code search

### 🔁 Ralph Loop
Self-referential loop that doesn't stop until task is 100% done.

### ✅ Todo Enforcer
Agent goes idle? System yanks it back. Task gets done.

### 💬 Comment Checker
No AI slop in comments. Code reads professionally.

### 🖥️ Tmux Integration
Full interactive terminal support (REPLs, debuggers, TUIs).

## Model Selection

### When to Use Claude Models
- Complex orchestration
- Multi-step planning
- Following detailed instructions
- Template-based work

### When to Use GPT Models
- Architecture decisions
- Explicit reasoning
- Principle-driven work
- Research + deep analysis

### When to Use Lightweight Models
- Fast search/grep
- Documentation lookup
- Simple queries
- No need for intelligence

## Configuration

### Agent Model Override
Create/edit `~/.config/opencode/oh-my-opencode.json`:

```json
{
  "agents": {
    "sisyphus": { "model": "kimi-for-coding/k2p5" },
    "oracle": { "model": "openai/gpt-5.2" }
  }
}
```

### Gemini with Antigravity
```json
{
  "agents": {
    "multimodal-looker": {
      "model": "google/antigravity-gemini-3-flash",
      "variant": "high"
    }
  }
}
```

### Feature Toggles
```json
{
  "features": {
    "intent_gate": true,
    "hash_anchored_edit": true,
    "lsp_integration": true,
    "background_agents": true,
    "todo_enforcer": true,
    "comment_checker": true,
    "tmux_integration": true
  }
}
```

## Tips & Best Practices

### 1. Let Agents Work in Parallel
`ultrawork` automatically parallelizes. Don't micromanage.

### 2. Use Planner for Complex Work
Press Tab for Prometheus interview mode. Better planning = better results.

### 3. Trust the Ralph Loop
`/ulw-loop` won't stop until done. Great for large refactors.

### 4. Don't Override Explore/Librarian
They use lightweight models intentionally. Speed > intelligence for search.

### 5. Sisyphus Works Best with Claude Opus
Other models work, but Opus gives the best orchestration.

### 6. Use Hephaestus for Autonomous Work
Give a goal, not a recipe. He explores and figures it out.

## Authentication

### Anthropic (Claude)
```bash
opencode auth login
# Select: Anthropic → Claude Pro/Max
```

### Google Gemini (Antigravity)
```bash
opencode auth login
# Select: Google → OAuth with Google (Antigravity)
```

### GitHub Copilot
```bash
opencode auth login
# Select: GitHub → OAuth
```

## Troubleshooting

### Plugin Not Loading
```bash
cat ~/.config/opencode/opencode.json | grep oh-my-opencode
# Should show: "oh-my-opencode@latest"
```

### Model Errors
```bash
opencode models list
# Check available models
```

### Authentication Issues
```bash
rm -rf ~/.config/opencode/auth
opencode auth login
```

### Performance Issues
Check if too many agents are running:
```json
{
  "settings": {
    "parallel_agent_limit": 3
  }
}
```

## Integration with Antigravity

### Works With Existing Setup
- All MCP servers in `opencode.json`
- Custom agents in `.github/agents/`
- Skills and hooks
- Plugins

### Coexistence
Oh-my-opencode agents work alongside Antigravity's custom agents.

### Priority
Use oh-my-opencode for:
- Fast autonomous work (`ultrawork`)
- Strategic planning (Prometheus)
- Deep research (Hephaestus)

Use Antigravity agents for:
- Specialized domain work
- Custom workflows
- Repository-specific tasks

## Resources

- [Installation Guide](OH_MY_OPENCODE_SETUP.md)
- [GitHub Repository](https://github.com/code-yeongyu/oh-my-opencode)
- [Discord Community](https://discord.gg/PUwSMR9XNk)
- [OpenCode Documentation](https://opencode.ai/docs/)

## Example Prompts

```bash
# Feature implementation
> ultrawork: Add pagination to the user list endpoint

# Refactoring
> ulw: Refactor the authentication module to use dependency injection

# Bug fixing
> ultrawork: Fix the race condition in the WebSocket handler

# Performance
> ulw: Optimize database queries in the analytics dashboard

# Documentation
> Ask Librarian: Find FastAPI middleware examples

# Code review
> Ask Momus to review backend/agent/orchestrator.py

# Research
> ultrawork: Research and implement Redis caching for session management

# Planning
[Press Tab]
Prometheus: What are you trying to build?
You: A real-time notification system
[Prometheus creates detailed plan]
> /start-work
```

## Support

- **Documentation**: See [OH_MY_OPENCODE_SETUP.md](OH_MY_OPENCODE_SETUP.md)
- **Issues**: https://github.com/code-yeongyu/oh-my-opencode/issues
- **Discord**: https://discord.gg/PUwSMR9XNk
- **Antigravity Issues**: https://github.com/AloSantana/Antigravitys/issues
