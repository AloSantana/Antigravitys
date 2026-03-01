# MCP Servers Catalog — Antigravity Workspace
> Last updated: March 2026 | Focus: Agents, Multi-Agents, Gemini CLI, OpenCode/Crush, Antigravity

This catalog documents curated MCP (Model Context Protocol) servers organized by category, with special focus on seamless agent-to-agent communication, multi-agent orchestration, and integration with Gemini CLI / OpenCode (Crush) / Antigravity workflows.

---

## Table of Contents
1. [🧠 Core / Official MCP Servers](#core--official)
2. [🤖 Coding Agents](#coding-agents)
3. [🔗 Aggregators & Multi-Agent Hubs](#aggregators--multi-agent-hubs)
4. [🌐 Web & Browser Automation](#web--browser-automation)
5. [🔍 Search & Data Extraction](#search--data-extraction)
6. [💬 Communication & Collaboration](#communication--collaboration)
7. [🗄️ Databases & Storage](#databases--storage)
8. [☁️ Cloud Platforms](#cloud-platforms)
9. [🛠️ Developer Tools](#developer-tools)
10. [🧠 Knowledge & Memory](#knowledge--memory)
11. [🔄 Version Control](#version-control)
12. [🤖 AI Model Bridges](#ai-model-bridges)
13. [📦 Code Execution & Sandboxes](#code-execution--sandboxes)
14. [📊 Monitoring & Observability](#monitoring--observability)
15. [🔒 Security](#security)
16. [🎨 Media & Creative](#media--creative)
17. [📋 Productivity & Workspace](#productivity--workspace)

---

## Core / Official

These are reference implementations from the MCP steering group — stable, production-tested.

| # | Server | Package | Description | Transport |
|---|--------|---------|-------------|-----------|
| 1 | **Filesystem** | `@modelcontextprotocol/server-filesystem` | Secure file operations with configurable access controls | stdio |
| 2 | **Git** | `@modelcontextprotocol/server-git` | Read, search, and manipulate Git repositories | stdio |
| 3 | **Memory** | `@modelcontextprotocol/server-memory` | Knowledge graph-based persistent memory system | stdio |
| 4 | **Sequential Thinking** | `@modelcontextprotocol/server-sequential-thinking` | Dynamic problem-solving through reflective thought sequences | stdio |
| 5 | **Fetch** | `@modelcontextprotocol/server-fetch` | Web content fetching and conversion for efficient LLM use | stdio |
| 6 | **Time** | `@modelcontextprotocol/server-time` | Time and timezone conversion capabilities | stdio |
| 7 | **SQLite** | `@modelcontextprotocol/server-sqlite` | Database interaction and business intelligence | stdio |
| 8 | **Brave Search** | `brave-search-mcp-server` (official by Brave) | Web and local search using Brave's Search API | stdio |
| 9 | **GitHub** | `@github/mcp-server` | Repository management, file ops, GitHub API integration | stdio |
| 10 | **Playwright** | `@playwright/mcp` (Microsoft) | Browser automation with Playwright — official Microsoft server | stdio/SSE |

---

## Coding Agents

MCP servers specifically designed to enhance AI coding agent capabilities, code generation, and software development workflows.

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 11 | **Context7** | `@upstash/context7-mcp` | Up-to-date library docs injected into LLM context. Essential for code accuracy. | TS | ☁️ |
| 12 | **DeepWiki** | `devin/deepwiki` | Remote MCP providing AI-powered codebase context, Q&A over any repo | TS | ☁️ |
| 13 | **Mermaid MCP** | `@narasimhaponnada/mermaid-mcp-server` | AI-powered diagram generation (22+ types: flowchart, sequence, ER, class) | TS | 🏠☁️ |
| 14 | **agent smith** | `jpoindexter/agentsmith` | Auto-generate AGENTS.md from your codebase | TS | 🏠 |
| 15 | **Next.js DevTools** | `vercel/next-devtools-mcp` | Next.js development tools and utilities for AI coding assistants | TS | 🏠 |
| 16 | **Chrome DevTools** | `chromedevtools/chrome-devtools-mcp` | Control and inspect live Chrome browser from Gemini/Claude/Copilot/Cursor | TS | 🏠 |
| 17 | **XcodeBuildMCP** | `cameroncooke/xcodebuildmcp` | Scaffold, build, run, test iOS/macOS apps; UI automation, screenshots | Python | 🍎 |
| 18 | **Shadcn** | `npx shadcn mcp` | shadcn/ui components integration for AI coding | TS | 🏠 |
| 19 | **21st.dev Magic** | `21st-dev/magic-mcp` | Create UI components inspired by top 21st.dev design engineers | TS | ☁️ |
| 20 | **Python Analysis** | `mcp_server_python_analysis` | Run mypy, analyze complexity, find imports, get definitions | Python | 🏠 |
| 21 | **Claude Skills** | `K-Dense-AI/claude-skills-mcp` | Intelligent search to let every model use Claude Agent Skills natively | Python | ☁️🏠 |
| 22 | **Roundtable** | `askbudi/roundtable` | Meta-MCP unifying Codex, Claude Code, Cursor, Gemini through auto-discovery | TS | ☁️🏠 |

---

## Aggregators & Multi-Agent Hubs

These servers are critical for multi-agent architectures — they aggregate, proxy, and orchestrate multiple MCP servers or AI agents.

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 23 | **1mcp/agent** | `1mcp-app/agent` | Unified MCP server aggregating multiple servers into one | TS | ☁️🏠 |
| 24 | **MetaMCP** | `metatool-ai/metatool-app` | Middleware MCP with GUI to manage all MCP connections | TS | ☁️🏠 |
| 25 | **MCPJungle** | `duaraghav8/MCPJungle` | Self-hosted MCP server registry for enterprise AI agents | Go | 🏠 |
| 26 | **Magg** | `sitbon/magg` | Meta-MCP hub — AI can autonomously discover, install, orchestrate servers | Python | ☁️🏠 |
| 27 | **PluggedIn MCP Proxy** | `VeriTeknik/pluggedin-mcp-proxy` | Combines multiple MCP servers with visibility, debugging, and discovery | TS | 🏠 |
| 28 | **Neurolink** | `juspay/neurolink` | Enterprise edge platform unifying 12 AI providers, multi-agent orchestration, HITL workflows | TS | ☁️🏠 |
| 29 | **NCP** | `portel-dev/ncp` | Orchestrates entire MCP ecosystem with intelligent discovery, reduces token overhead | TS | ☁️🏠 |
| 30 | **A-Team MCP** | `ariekogan/ateam-mcp` | Build, validate, deploy multi-agent solutions on ADAS platform | TS | ☁️🏠 |
| 31 | **Aganium** | `Aganium/agenium` | Bridge MCP servers to agent:// network — DNS-like identity, discovery, trust | TS | ☁️ |
| 32 | **MCGravity** | `tigranbs/mcgravity` | Proxy/load-balancer for multiple MCP servers (like Nginx for MCP) | TS | 🏠 |
| 33 | **MCP Gateway** | `ViperJuice/mcp-gateway` | Meta-server with progressive disclosure and dynamic 25+ server provisioning | Python | 🏠 |
| 34 | **Pipedream** | `PipedreamHQ/pipedream` | Connect 2,500+ APIs with 8,000+ prebuilt tools for agents | TS | ☁️🏠 |
| 35 | **Forage** | `isaac-levine/forage` | Self-improving tool discovery — searches registries, installs MCP as subprocesses | TS | 🏠 |
| 36 | **AgentNet** | `oxgeneral/agentnet` | Agent-to-agent referral network with bilateral trust, credit economy | Python | ☁️ |
| 37 | **Prolink** | `edgarriba/prolink` | Agent-to-agent marketplace middleware — MCP-native discovery, negotiation, transactions | Python | ☁️🏠 |
| 38 | **HashNet MCP** | `hashgraph-online/hashnet-mcp-js` | Discover, register, chat with AI agents on Hashgraph network | TS | ☁️ |
| 39 | **Open MCP** | `wegotdocs/open-mcp` | Turn any web API into an MCP server in 10 seconds | TS | 🏠 |
| 40 | **MCPDiscovery** | `particlefuture/MCPDiscovery` | MCP of MCPs — automatic discovery and configure servers locally | Python | ☁️🏠 |
| 41 | **WayStation** | `waystation-ai/mcp` | Connect Claude Desktop/MCP hosts to Notion, Slack, Monday, etc. in 90 seconds | TS | ☁️ |
| 42 | **MCPX (Lunar)** | `TheLunarCompany/lunar/mcpx` | Production-ready gateway for MCP at scale — tool discovery, access control, usage tracking | TS | 🏠☁️ |
| 43 | **MCP Bundles** | `thinkchainai/mcpbundles` | Custom bundles of tools with OAuth/API keys, one server across thousands of integrations | TS | ☁️ |

---

## Web & Browser Automation

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 44 | **Playwright (MS)** | `@playwright/mcp` | Microsoft's official Playwright-based browser automation | TS | 🏠 |
| 45 | **Puppeteer** | `@anthropic/server-puppeteer` | Browser automation and web scraping via Puppeteer | TS | 🏠 |
| 46 | **Browserbase** | `@browserbase/mcp-server-browserbase` | Cloud browser interactions — navigation, data extraction, form filling | TS | ☁️ |
| 47 | **BrowserMCP** | `browsermcp/mcp` | Automate local Chrome browser | TS | 🏠 |
| 48 | **Firecrawl MCP** | `firecrawl/firecrawl-mcp-server` | Powerful web scraping and search for LLM clients | TS | ☁️🏠 |
| 49 | **AgentQL** | `tinyfish-io/agentql-mcp` | Structured data from unstructured web for AI agents | TS | ☁️ |
| 50 | **Bright Data** | `brightdata/brightdata-mcp` | Discover, extract, interact with the web — automated access across public internet | TS | ☁️ |
| 51 | **YT-DLP** | `mcp-server-yt-dlp` | Download videos, get info, list formats, extract audio | TS | 🏠 |
| 52 | **Browser Use RS** | `BB-fat/browser-use-rs` | Lightweight browser automation in Rust, zero dependencies | Rust | 🏠 |

---

## Search & Data Extraction

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 53 | **Exa** | `exa-labs/exa-mcp-server` | AI-native search engine via Exa API | TS | ☁️ |
| 54 | **Brave Search** | `brave/brave-search-mcp-server` | Web + local search using Brave Search API | TS | ☁️ |
| 55 | **Algolia** | `algolia/mcp` | Provision, configure, and query Algolia search indices | TS | ☁️ |
| 56 | **MindsDB** | `mindsdb/mindsdb` | Connect and unify data across platforms and databases | Python | ☁️🏠 |
| 57 | **AnyQuery** | `julien040/anyquery` | Query 40+ apps with SQL; connects to PostgreSQL, MySQL, SQLite | Go | 🏠☁️ |
| 58 | **Alpha Vantage** | `mcp.alphavantage.co` | Financial market data: stocks, ETFs, forex, crypto, commodities | TS | ☁️ |
| 59 | **Kaggle MCP** | `kaggle.com/docs/mcp` | Datasets, models, competitions, notebooks, benchmarks | TS | ☁️ |

---

## Communication & Collaboration

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 60 | **Slack** | `zencoderai/slack-mcp-server` | Channel management and messaging (Zencoder-maintained fork) | TS | ☁️ |
| 61 | **ActionKit (Paragon)** | `useparagon/paragon-mcp` | 130+ SaaS integrations: Slack, Salesforce, Gmail via Paragon | TS | ☁️ |
| 62 | **Synter Ads** | `jshorwitz/synter-mcp-server` | Cross-platform ad management: Google, Meta, LinkedIn, Reddit, TikTok | TS | ☁️ |
| 63 | **WayStation** | `waystation-ai/mcp` | Notion, Slack, Monday, Airtable connections in 90 seconds | TS | ☁️ |

---

## Databases & Storage

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 64 | **SQLite** | `@modelcontextprotocol/server-sqlite` | SQLite database interaction and business intelligence | TS | 🏠 |
| 65 | **PostgreSQL** | `mcp-server-postgres` | Read/write database access with schema inspection | TS | 🏠☁️ |
| 66 | **Redis** | `@modelcontextprotocol/server-redis` (archived) | Interact with Redis key-value stores | TS | 🏠 |
| 67 | **Supabase** | `supabase-community/supabase-mcp` | Database, auth, edge functions via Supabase platform | TS | ☁️ |
| 68 | **Aiven** | `Aiven-Open/mcp-aiven` | PostgreSQL, Kafka, ClickHouse, OpenSearch via Aiven | TS | ☁️ |
| 69 | **MindsDB** | `mindsdb/mindsdb` | Unified data layer across 40+ data sources | Python | ☁️🏠 |

---

## Cloud Platforms

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 70 | **Cloudflare** | `cloudflare/mcp-server-cloudflare` | Deploy, configure Workers/KV/R2/D1 on Cloudflare | TS | ☁️ |
| 71 | **Docker** | `mcp-server-docker` | Container management: list, create, run, stop, build, pull | TS | 🏠 |
| 72 | **Google MCP** | `google/mcp` | Collection of Google's official MCP servers (Workspace, Cloud) | TS | ☁️ |
| 73 | **AWS KB Retrieval** | (archived) `aws-kb-retrieval-server` | Retrieval from AWS Knowledge Base using Bedrock Agent Runtime | TS | ☁️ |

---

## Developer Tools

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 74 | **AgentOps** | `AgentOps-AI/agentops-mcp` | Observability and tracing for AI agents | TS | ☁️ |
| 75 | **AgentRPC** | `agentrpc/agentrpc` | Connect any function in any language across network boundaries | TS | ☁️🏠 |
| 76 | **Sentry** | (archived) `sentry-mcp` | Retrieve and analyze issues from Sentry.io | TS | ☁️ |
| 77 | **Scout Monitoring** | `scoutapm.com/mcp` | Performance and error data for AI assistants | TS | ☁️ |
| 78 | **E2B** | `e2b-dev/mcp-server` | Run code in secure sandboxes hosted by E2B | TS | ☁️ |
| 79 | **2slides** | `2slides/2slides-mcp` | Convert content to slides/PPT via AI | TS | ☁️ |

---

## Knowledge & Memory

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 80 | **Memory** | `@modelcontextprotocol/server-memory` | Knowledge graph persistent memory with entity/relation graph | TS | 🏠 |
| 81 | **Agentset** | `agentset-ai/mcp-server` | RAG for your knowledge base via Agentset.ai | TS | ☁️ |
| 82 | **Context7** | `@upstash/context7-mcp` | Inject up-to-date library documentation into prompts | TS | ☁️ |
| 83 | **RAGMap** | `khalidsaidi/ragmap` | RAG-focused subregistry to discover retrieval-capable MCP servers | TS | ☁️🏠 |
| 84 | **MapRag** | `khalidsaidi/ragmap` | Discovery and routing to retrieval-capable servers | TS | ☁️🏠 |

---

## Version Control

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 85 | **Git** | `@modelcontextprotocol/server-git` | Full git operations: status, diff, commit, log, branch | TS | 🏠 |
| 86 | **GitHub** | `@github/mcp-server` | Repository management, issues, PRs, search, file ops | TS | ☁️🏠 |
| 87 | **GitLab** | (archived) `server-gitlab` | GitLab API, project management | TS | ☁️ |

---

## AI Model Bridges

These servers bridge different AI models/providers into your MCP environment — essential for multi-model agent setups.

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 88 | **Gemini Bridge** | `jaspertvdm/mcp-server-gemini-bridge` | Bridge to Google Gemini API (Pro, Flash models) | Python | ☁️ |
| 89 | **Ollama Bridge** | `jaspertvdm/mcp-server-ollama-bridge` | Bridge to local Ollama server (Llama, Mistral, Qwen) | Python | 🏠 |
| 90 | **OpenAI Bridge** | `jaspertvdm/mcp-server-openai-bridge` | Bridge to OpenAI API (GPT-4, GPT-4o) | Python | ☁️ |
| 91 | **Grok MCP** | `merterbak/Grok-MCP` | xAI Grok API with agentic tool calling, image generation, vision | Python | ☁️ |
| 92 | **MiniMax MCP** | `minimax-ai/minimax-mcp` | Text-to-Speech, image and video generation via MiniMax | TS | ☁️ |
| 93 | **BlockRun** | `blockrunai/blockrun-mcp` | Access 30+ AI models (GPT-5, Claude, Gemini, Grok, DeepSeek) pay-per-use | TS | ☁️ |
| 94 | **OpenAI Image** | `SureScaleAI/openai-gpt-image-mcp` | OpenAI GPT image generation/editing | TS | ☁️ |
| 95 | **Imagen3** | `hamflx/imagen3-mcp` | Image generation using Google Imagen 3.0 API | TS | 🏠 |

---

## Code Execution & Sandboxes

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 96 | **E2B** | `e2b-dev/mcp-server` | Secure cloud sandboxes for code execution | TS | ☁️ |
| 97 | **Docker** | `mcp-server-docker` | Docker containers as sandboxes for code execution | TS | 🏠 |
| 98 | **ComfyPilot** | `ConstantineB6/comfy-pilot` | ComfyUI control for AI agents: view, edit, run image generation workflows | Python | 🏠 |

---

## Monitoring & Observability

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 99 | **AgentOps** | `AgentOps-AI/agentops-mcp` | Full observability and tracing for AI agent debugging | TS | ☁️ |
| 100 | **Scout** | `scoutapm.com/mcp` | Performance and error monitoring for AI assistants | TS | ☁️ |

---

## Security

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 101 | **Sentry** | (archived) `sentry-mcp` | Error tracking and security issue analysis | TS | ☁️ |

---

## Media & Creative

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 102 | **MiniMax** | `minimax-ai/minimax-mcp` | Text-to-Speech, image, video generation | TS | ☁️ |
| 103 | **Imagen3** | `hamflx/imagen3-mcp` | High-quality image generation with Google Imagen 3.0 | TS | 🏠 |
| 104 | **Fal AI** | `raveenb/fal-mcp-server` | Generate images, videos, music via Fal.ai (FLUX, SD, MusicGen) | Python | ☁️ |
| 105 | **DaVinci Resolve** | `samuelgursky/davinci-resolve-mcp` | Video editing, color grading, media management | Python | 🏠 |
| 106 | **REAPER DAW** | `TwelveTake-Studios/reaper-mcp` | AI control of REAPER DAW: mixing, mastering, MIDI, 129 tools | Python | 🏠 |
| 107 | **Blender** | `ahujasid/blender-mcp` | MCP server for working with Blender 3D | Python | 🏠 |
| 108 | **Agent Media** | `yuvalsuede/agent-media` | AI video and image generation across 7 models (Kling, Veo, Sora, Flux, Grok) | TS | ☁️ |

---

## Productivity & Workspace

| # | Server | Package / Repo | Description | Language | Type |
|---|--------|----------------|-------------|----------|------|
| 109 | **Google Workspace** | `google/mcp` | Google Drive, Docs, Sheets, Calendar, Gmail | TS | ☁️ |
| 110 | **Notion** | (via WayStation) | Full Notion workspace integration | TS | ☁️ |
| 111 | **ActionKit** | `useparagon/paragon-mcp` | 130+ SaaS apps: Slack, Salesforce, GitHub, Gmail, Jira | TS | ☁️ |
| 112 | **Anki MCP** | `anki-mcp/anki-mcp-desktop` | Interact with Anki spaced repetition flashcards | TS | 🏠 |

---

## Priority Servers for Antigravity / Gemini CLI / OpenCode Integration

The following 20 servers provide the best foundation for seamless agent-to-agent and multi-agent chat integration:

```
Priority A — Already in Antigravity (verify/update):
  1. filesystem        — Core file operations
  2. git               — Version control
  3. github            — GitHub integration  
  4. memory            — Persistent context across agents
  5. sequential-thinking — Deep reasoning chains
  6. fetch             — Web content retrieval
  7. sqlite            — Local structured data
  8. brave-search      — Web search
  9. docker            — Container management
 10. playwright        — Browser automation (use MS official)
 11. puppeteer         — Browser automation (legacy)
 12. time              — Time operations

Priority B — Add for enhanced agent workflows:
 13. context7          — Up-to-date library docs
 14. e2b               — Secure code execution sandboxes
 15. agentops          — Agent observability/tracing
 16. mcp-server-gemini-bridge — Gemini model access
 17. mcp-server-ollama-bridge — Local model access
 18. metatool-app      — GUI to manage all MCP servers
 19. pluggedin-mcp-proxy — Combine multiple servers
 20. exa               — AI-native search
```

---

## Notes

- **OpenCode / Crush**: Use `mcpServers` key in `.opencode.json` with `type: "stdio"` | `type: "sse"` format
- **Gemini CLI**: Configured via `~/.gemini/settings.json` or `GEMINI_MCP_*` environment variables  
- **Antigravity**: Configured via `.github/copilot/mcp.json` (Copilot) and `.agent/mcp_config.json` (agents)
- **Transport Types**: `stdio` (most common), `sse` (HTTP streaming), `http` (REST-based)

---

*Sources: [modelcontextprotocol.io/registry](https://registry.modelcontextprotocol.io), [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers), [mcpservers.org](https://mcpservers.org), direct GitHub research (March 2026)*
