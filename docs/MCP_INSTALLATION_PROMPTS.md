# MCP Installation & Optimization Prompts
> Use these prompts with OpenCode/Crush, Claude Code, Gemini CLI, or Antigravity to install and configure each MCP server

---

## How to Use These Prompts

Copy any prompt below and paste it into:
- **Gemini CLI**: `gemini -p "PROMPT_TEXT"`
- **OpenCode/Crush**: Start session → paste prompt
- **Claude Code**: `claude -p "PROMPT_TEXT"`
- **Antigravity Chat**: Paste directly into the chat interface

Each prompt is self-contained and will install, configure, and verify the MCP server.

---

## 🧠 Core / Official MCP Servers

### 1. Filesystem MCP Server

```
Install and configure the @modelcontextprotocol/server-filesystem MCP server for this project.

Steps to complete:
1. Run: npx -y @modelcontextprotocol/server-filesystem . --dry-run (to verify it works)
2. Add to .github/copilot/mcp.json under "mcpServers" key:
   "filesystem": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
     "tools": ["read_file", "write_file", "edit_file", "create_directory", "list_directory", "move_file", "search_files", "get_file_info"]
   }
3. Add to .agent/mcp_config.json for agent access
4. Test by asking: "List the files in the docs/ directory"
5. Verify tools: read_file, write_file, edit_file all respond correctly

The server should have access to the current project directory only. Confirm the server is running and list available tools.
```

---

### 2. Memory MCP Server (Knowledge Graph)

```
Install and fully optimize the @modelcontextprotocol/server-memory MCP server for persistent agent memory in this Antigravity workspace.

Steps:
1. Run: npx -y @modelcontextprotocol/server-memory --test (verify installation)
2. Add to .github/copilot/mcp.json:
   "memory": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-memory"],
     "tools": ["create_entities", "create_relations", "add_observations", "delete_entities", "read_graph", "search_nodes", "open_nodes"]
   }
3. Pre-populate the knowledge graph with project context:
   - Create entity: "Antigravity" (type: Project)
   - Create entity: "Gemini" (type: AI_Model)  
   - Create entity: "MCP" (type: Protocol)
   - Add relations between them
4. Test: Create a test entity, search for it, verify persistence

This memory server enables all agents to share a persistent knowledge graph. Confirm all 9 tools are available and the graph is initialized.
```

---

### 3. Sequential Thinking MCP Server

```
Install and configure the @modelcontextprotocol/server-sequential-thinking MCP server for enhanced multi-step reasoning in Antigravity.

Steps:
1. Install: npx -y @modelcontextprotocol/server-sequential-thinking
2. Add to .github/copilot/mcp.json:
   "sequential-thinking": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
     "tools": ["sequentialthinking"]
   }
3. Test with a complex multi-step problem: 
   "Use sequential thinking to plan the architecture for a multi-agent chat system"
4. Verify the thinking chain shows: thoughtNumber, totalThoughts, nextThoughtNeeded fields
5. Configure to use at least 5 thoughts for complex tasks

The sequential thinking server enables dynamic, reflective problem-solving. Verify it outputs structured thinking with proper thought chaining.
```

---

### 4. GitHub MCP Server (Official)

```
Install and configure the @github/mcp-server for full GitHub integration in Antigravity.

Steps:
1. Ensure GITHUB_TOKEN environment variable is set
2. Test: npx -y @github/mcp-server --test
3. Verify in .github/copilot/mcp.json the github entry has GITHUB_TOKEN
4. Add these specific tools: get_file_contents, get_issue, list_issues, create_issue, create_pull_request, search_code, search_repositories, push_files, create_branch, list_commits
5. Test each major operation:
   - search_repositories query:"modelcontextprotocol"
   - list_issues for this repo
   - search_code query:"MCP" in this repo
6. Verify authentication is working with: list_issues owner:"AloSantana" repo:"Antigravitys"

Configure the server with minimal required permissions. The GITHUB_TOKEN should have: repo, read:org, workflow scopes. Confirm all 15 tools are responding.
```

---

## 🤖 Coding Agents

### 5. Context7 MCP Server

```
Install and fully configure the @upstash/context7-mcp server for up-to-date library documentation injection in Antigravity/Gemini CLI/OpenCode.

Steps:
1. Install globally: npm install -g @upstash/context7-mcp
2. Get a free API key from https://upstash.com/context7
3. Add to .agent/mcp_config.json:
   "context7": {
     "command": "npx",
     "args": ["-y", "@upstash/context7-mcp"],
     "env": { "CONTEXT7_API_KEY": "YOUR_KEY" }
   }
4. Add to .github/copilot/mcp.json as well
5. Test: Ask "What are the latest FastAPI async patterns? use context7"
6. Verify it returns current documentation, not training data
7. Test with: "Show me React 19 hooks documentation use context7"

Context7 resolves "use context7" in prompts to inject real-time library docs. Verify the server correctly identifies and injects documentation for: Python, FastAPI, React, TypeScript, LangChain.

Optimal usage: Always add "use context7" at end of coding prompts for accurate, current docs.
```

---

### 6. Playwright MCP Server (Microsoft Official)

```
Install and configure the Microsoft official @playwright/mcp server for AI-controlled browser automation in Antigravity.

Steps:
1. Install: npm install -g @playwright/mcp
2. Install browsers: npx playwright install chromium
3. Add to .github/copilot/mcp.json:
   "playwright": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@playwright/mcp", "--browser", "chromium"],
     "tools": ["browser_navigate", "browser_screenshot", "browser_click", "browser_fill", "browser_snapshot", "browser_wait_for", "browser_type", "browser_select_option"]
   }
4. Test: Navigate to https://example.com and take a screenshot
5. Verify: Click a button, fill a form, take full-page screenshot
6. Configure headless mode for CI: add "--headless" to args

IMPORTANT: Use this server over the legacy puppeteer server. The Microsoft Playwright server provides superior accessibility snapshots (better than screenshots for AI), cross-browser support, and active maintenance.

Test the full flow: navigate → snapshot → click → fill → verify.
```

---

### 7. Mermaid MCP Server

```
Install and configure the @narasimhaponnada/mermaid-mcp-server for AI-powered diagram generation in Antigravity.

Steps:
1. Install: npm install -g @narasimhaponnada/mermaid-mcp-server
2. Add to .github/copilot/mcp.json:
   "mermaid": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@narasimhaponnada/mermaid-mcp-server"],
     "tools": ["generate_diagram", "validate_mermaid", "list_diagram_types"]
   }
3. Test generating diagrams:
   - Flowchart for the Antigravity multi-agent workflow
   - Sequence diagram for MCP server communication
   - ER diagram for the SQLite database schema
4. Export as SVG/PNG
5. Verify all 22+ diagram types are available

Generate a complete system architecture diagram for the Antigravity workspace showing: User → Chat Interface → Agent Orchestrator → MCP Servers → AI Models. Export as SVG and save to docs/architecture-diagram.svg.
```

---

### 8. Chrome DevTools MCP Server

```
Install and configure the chromedevtools/chrome-devtools-mcp server for live Chrome inspection from Gemini/Claude/Copilot.

Steps:
1. Install: npm install -g chrome-devtools-mcp  
2. Ensure Chrome/Chromium is installed
3. Start Chrome with remote debugging: 
   google-chrome --remote-debugging-port=9222 --no-sandbox
4. Add to .github/copilot/mcp.json:
   "chrome-devtools": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "chrome-devtools-mcp"],
     "env": { "CHROME_DEBUG_PORT": "9222" }
   }
5. Test: Inspect the current page, get console logs, execute JavaScript
6. Test: Take a screenshot of the live frontend at http://localhost:8000

This server enables AI agents to directly inspect, debug, and control a live browser session. Test: Get the network requests from the current page and analyze for performance issues.
```

---

## 🔗 Aggregators & Multi-Agent Hubs

### 9. MetaMCP — GUI MCP Manager

```
Install and configure metatool-ai/MetaMCP as the central GUI hub for managing all MCP connections in Antigravity.

Steps:
1. Clone: git clone https://github.com/metatool-ai/metatool-app
2. Install: cd metatool-app && npm install
3. Build: npm run build
4. Start: npm start (runs on http://localhost:3000)
5. Open GUI at http://localhost:3000
6. Import existing MCP config from .github/copilot/mcp.json
7. Add each server through the GUI with proper env variables
8. Export the unified config back to .agent/mcp_config.json
9. Test: Toggle individual servers on/off from GUI
10. Enable the playground for debugging MCP tool calls

MetaMCP provides a visual dashboard to manage all MCP servers with connection status, tool listing, and debugging. Set it up as the primary management interface for Antigravity's MCP ecosystem.

After setup, create a screenshot of the GUI showing all configured servers and their status.
```

---

### 10. Forage — Self-Improving Tool Discovery

```
Install and configure isaac-levine/forage for autonomous MCP server discovery and installation in Antigravity agents.

Steps:
1. Clone: git clone https://github.com/isaac-levine/forage
2. Install: cd forage && npm install && npm run build
3. Add to .github/copilot/mcp.json:
   "forage": {
     "type": "stdio",
     "command": "node",
     "args": ["path/to/forage/dist/index.js"],
     "tools": ["search_tools", "install_server", "list_installed", "load_tool"]
   }
4. Test: Ask Forage to find MCP servers for "web scraping"
5. Verify it searches the MCP registry and installs the best match
6. Test persistence: After restart, verify installed servers are remembered
7. Configure search to prioritize: npm packages, high star count, recent updates

Forage enables agents to self-extend by discovering and installing new MCP servers on-demand. This is critical for adaptive multi-agent workflows. Test the full discovery-install-use cycle.
```

---

### 11. NCP — MCP Ecosystem Orchestrator

```
Install and configure portel-dev/ncp (NCP) as the intelligent MCP orchestration layer for Antigravity's multi-agent system.

Steps:
1. Install: npm install -g @portel/ncp
2. Configure with your existing MCP servers list
3. Add to .agent/mcp_config.json as the primary router
4. Test: Run a complex task that requires multiple MCP servers
5. Verify: NCP auto-selects the right servers with 98%+ accuracy
6. Monitor: Check token overhead reduction (should be <30% of direct access)
7. Enable intelligent discovery for 40+ tool namespace

NCP reduces token overhead in multi-agent workflows by intelligently routing tool calls. Configure it to orchestrate: filesystem, git, github, memory, context7, playwright, fetch as a unified interface.

After setup, compare response quality and speed with/without NCP for a coding task.
```

---

## 🌐 Web & Browser Automation

### 12. Firecrawl MCP Server

```
Install and configure the Firecrawl MCP server for powerful web scraping and search in Antigravity.

Steps:
1. Get API key: https://firecrawl.dev (free tier available)
2. Install: npm install -g firecrawl-mcp
3. Add to .github/copilot/mcp.json:
   "firecrawl": {
     "type": "stdio", 
     "command": "npx",
     "args": ["-y", "firecrawl-mcp"],
     "env": { "FIRECRAWL_API_KEY": "YOUR_API_KEY" },
     "tools": ["scrape", "crawl", "search", "map", "extract"]
   }
4. Test scraping: Scrape https://modelcontextprotocol.io and extract all MCP server listings
5. Test crawling: Crawl the Antigravity docs structure
6. Test search: Search for "MCP server gemini integration"
7. Test extraction: Extract structured data from a GitHub README

Firecrawl provides clean, LLM-ready web content. Verify it correctly handles JavaScript-rendered pages, extracts markdown, and respects rate limits. Test all 5 tools.
```

---

### 13. Exa Search MCP Server

```
Install and configure the Exa AI-native search MCP server for intelligent web research in Antigravity.

Steps:
1. Get API key: https://exa.ai (free credits available)
2. Install: npm install -g exa-mcp-server
3. Add to .github/copilot/mcp.json:
   "exa": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "exa-mcp-server"],
     "env": { "EXA_API_KEY": "YOUR_API_KEY" },
     "tools": ["search", "find_similar", "get_contents", "search_and_contents"]
   }
4. Test neural search: Search for "latest MCP server multi-agent 2025"
5. Test similarity search: Find pages similar to https://modelcontextprotocol.io
6. Test content extraction: Get full content from search results
7. Compare results quality vs Brave Search for code-related queries

Exa is an AI-native search engine that understands semantic meaning better than keyword search. Configure it as the primary research tool for Antigravity's deep-research agent.
```

---

## 🤖 AI Model Bridges

### 14. Gemini Bridge MCP Server

```
Install and configure the mcp-server-gemini-bridge to expose Google Gemini models as MCP tools in Antigravity.

Steps:
1. Clone: git clone https://github.com/jaspertvdm/mcp-server-gemini-bridge
2. Install: cd mcp-server-gemini-bridge && pip install -r requirements.txt
3. Set environment: export GEMINI_API_KEY="your-key"
4. Test: python -m mcp_server_gemini_bridge --test
5. Add to .agent/mcp_config.json:
   "gemini-bridge": {
     "command": "python",
     "args": ["-m", "mcp_server_gemini_bridge"],
     "env": { "GEMINI_API_KEY": "${GEMINI_API_KEY}" }
   }
6. Configure to expose: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash models
7. Test each model with a coding task
8. Set gemini-2.5-flash as default for speed, gemini-2.5-pro for complex tasks

This bridge enables agents to call Gemini models as tools within any MCP-compatible environment. Test multi-model pipeline: use gemini-2.5-flash for planning, gemini-2.5-pro for implementation.
```

---

### 15. Ollama Bridge MCP Server

```
Install and configure the mcp-server-ollama-bridge for local AI model access in Antigravity.

Steps:
1. Ensure Ollama is installed: ollama --version (install from https://ollama.ai if missing)
2. Pull required models: 
   ollama pull llama3.3
   ollama pull mistral
   ollama pull qwen2.5-coder:7b
3. Clone and install bridge:
   git clone https://github.com/jaspertvdm/mcp-server-ollama-bridge
   cd mcp-server-ollama-bridge && pip install -r requirements.txt
4. Test: python -m mcp_server_ollama_bridge --list-models
5. Add to .agent/mcp_config.json:
   "ollama-bridge": {
     "command": "python",
     "args": ["-m", "mcp_server_ollama_bridge"],
     "env": { "OLLAMA_BASE_URL": "http://localhost:11434" }
   }
6. Test: Ask the bridge to analyze a Python file using qwen2.5-coder
7. Configure: Use qwen2.5-coder for code tasks, llama3.3 for general tasks

The Ollama bridge enables private, offline AI model access. This is essential for sensitive codebases. Verify all models respond within 10 seconds for simple queries.
```

---

## 📊 Monitoring & Observability

### 16. AgentOps MCP Server

```
Install and configure AgentOps MCP for full observability and tracing of Antigravity's AI agent workflows.

Steps:
1. Install: npm install -g agentops-mcp
   OR: pip install agentops
2. Get API key: https://agentops.ai (free tier available)
3. Add to .github/copilot/mcp.json:
   "agentops": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "agentops-mcp"],
     "env": { "AGENTOPS_API_KEY": "YOUR_API_KEY" },
     "tools": ["start_session", "end_session", "log_event", "log_error", "get_analytics"]
   }
4. Instrument the Antigravity backend:
   - Add AgentOps tracking to backend/agent/orchestrator.py
   - Add session tracking to backend/agent/manager.py
   - Add error logging to all agent execute() methods
5. Test: Run a multi-agent workflow and view the trace in AgentOps dashboard
6. Set up alerts for: agent failures, high latency (>5s), token overuse

AgentOps provides session replay, cost tracking, and performance analytics for AI agents. Configure it to track all agent interactions in Antigravity. View the dashboard and verify sessions are being logged.
```

---

## ☁️ Cloud & Infrastructure

### 17. Docker MCP Server

```
Install and configure the mcp-server-docker for AI-controlled container management in Antigravity.

Steps:
1. Ensure Docker is running: docker ps
2. Install: npm install -g mcp-server-docker
3. Add to .github/copilot/mcp.json:
   "docker": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "mcp-server-docker"],
     "tools": ["list_containers", "create_container", "run_container", "stop_container", "remove_container", "list_images", "pull_image", "build_image", "run_exec", "get_logs"]
   }
4. Test: List all running containers
5. Test: Pull the python:3.12-slim image
6. Test: Create and run a test container that executes a Python script
7. Test: Get logs from the Antigravity container (if running)
8. Security: Configure to restrict container creation to specific images only

The Docker MCP server enables agents to manage containerized workloads. Test the complete lifecycle: pull → create → run → exec → logs → stop → remove.
```

---

### 18. Cloudflare MCP Server

```
Install and configure the Cloudflare MCP server for Workers, KV, R2, and D1 management in Antigravity.

Steps:
1. Install: npm install -g @cloudflare/mcp-server-cloudflare
2. Get API token: Cloudflare Dashboard → My Profile → API Tokens
3. Add to .github/copilot/mcp.json:
   "cloudflare": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@cloudflare/mcp-server-cloudflare"],
     "env": {
       "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
       "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
     },
     "tools": ["list_workers", "deploy_worker", "get_worker", "list_kv_namespaces", "kv_get", "kv_put", "list_r2_buckets", "d1_query"]
   }
4. Test: List all Workers in your account
5. Test: Deploy a simple "Hello World" Worker
6. Test: Create a KV namespace and put/get a value
7. Optimize: Set up D1 for the Antigravity session storage

Configure Cloudflare MCP for serverless deployment of Antigravity agents. Test deploying a minimal FastAPI wrapper as a Cloudflare Worker.
```

---

## 🗄️ Databases

### 19. Supabase MCP Server

```
Install and configure the Supabase MCP server for database, auth, and edge functions in Antigravity.

Steps:
1. Create a Supabase project at https://supabase.com (free tier)
2. Get: Project URL, anon key, service_role key
3. Install: npm install -g supabase-mcp
4. Add to .github/copilot/mcp.json:
   "supabase": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "supabase-mcp"],
     "env": {
       "SUPABASE_URL": "${SUPABASE_URL}",
       "SUPABASE_ANON_KEY": "${SUPABASE_ANON_KEY}",
       "SUPABASE_SERVICE_ROLE_KEY": "${SUPABASE_SERVICE_ROLE_KEY}"
     },
     "tools": ["query", "insert", "update", "delete", "rpc", "auth_list_users", "storage_list_buckets"]
   }
5. Create tables: agents, sessions, conversations, mcp_configs
6. Test: Insert a test agent record and query it back
7. Enable Row Level Security for agent data isolation
8. Set up realtime subscriptions for live agent status updates

Supabase provides a full Postgres database with auth, realtime, and storage. Configure it as the primary persistent storage for Antigravity's conversation history and agent state.
```

---

## 🔍 Search & Research

### 20. Brave Search MCP Server (Official)

```
Install and configure the official Brave Search MCP server for web and local search in Antigravity.

Steps:
1. Get API key: https://brave.com/search/api/ (free tier: 2000 req/month)
2. Install: npm install -g @brave/brave-search-mcp-server
3. Add to .github/copilot/mcp.json:
   "brave-search": {
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@brave/brave-search-mcp-server"],
     "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" },
     "tools": ["brave_web_search", "brave_local_search", "brave_news_search", "brave_video_search"]
   }
4. Test web search: "latest MCP servers for AI agents 2025"
5. Test news search: "Gemini CLI updates 2025"
6. Test local search: "coffee shops near me" (requires location)
7. Configure: Set default result count to 10, enable safe search

NOTE: The old @modelcontextprotocol/server-brave-search is archived. Use the official @brave/brave-search-mcp-server instead. Update any existing configs.

Verify the new official server works and provides richer results including news, videos, and local search.
```

---

## Complete Setup Prompt (All Priority Servers)

Use this master prompt to set up all priority MCP servers at once:

```
Set up the complete MCP server ecosystem for the Antigravity workspace. Install and configure all priority servers in the correct order.

PHASE 1 — Core Infrastructure (no API keys needed):
1. Verify filesystem server: npx -y @modelcontextprotocol/server-filesystem .
2. Verify git server: npx -y @modelcontextprotocol/server-git --repository .
3. Verify memory server: npx -y @modelcontextprotocol/server-memory
4. Verify sequential-thinking: npx -y @modelcontextprotocol/server-sequential-thinking
5. Verify time server: npx -y @modelcontextprotocol/server-time
6. Verify fetch server: npx -y @modelcontextprotocol/server-fetch
7. Install playwright: npm install -g @playwright/mcp && npx playwright install chromium

PHASE 2 — API-Key Servers (check .env for keys):
8. Configure brave-search with BRAVE_API_KEY
9. Configure github with GITHUB_TOKEN
10. Configure context7 with CONTEXT7_API_KEY (get free at upstash.com/context7)

PHASE 3 — Enhanced Agent Capabilities:
11. Install mermaid: npm install -g @narasimhaponnada/mermaid-mcp-server
12. Configure exa with EXA_API_KEY (get free credits at exa.ai)
13. Install docker server: npm install -g mcp-server-docker

PHASE 4 — Validation:
- Update .github/copilot/mcp.json with all new servers
- Update .agent/mcp_config.json with all new servers
- Run: node -e "const config = require('./.github/copilot/mcp.json'); console.log('Servers:', Object.keys(config.mcpServers))"
- Test each server responds to a basic tool call
- Create docs/MCP_STATUS.md with status of each server

Report: List all installed servers, their status (✅/❌), and any missing API keys.
```

---

## Gemini CLI Specific Setup Prompt

```
Configure all MCP servers specifically for Gemini CLI integration in the Antigravity workspace.

Gemini CLI MCP configuration location: ~/.gemini/settings.json

Steps:
1. Read current ~/.gemini/settings.json (or create if missing)
2. Add mcpServers section with these servers:
   {
     "mcpServers": {
       "filesystem": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
       },
       "git": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/project"]
       },
       "memory": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-memory"]
       },
       "sequential-thinking": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
       },
       "github": {
         "command": "npx",
         "args": ["-y", "@github/mcp-server"],
         "env": { "GITHUB_TOKEN": "REPLACE_WITH_TOKEN" }
       },
       "context7": {
         "command": "npx",
         "args": ["-y", "@upstash/context7-mcp"],
         "env": { "CONTEXT7_API_KEY": "REPLACE_WITH_KEY" }
       },
       "fetch": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch"]
       },
       "brave-search": {
         "command": "npx",
         "args": ["-y", "@brave/brave-search-mcp-server"],
         "env": { "BRAVE_API_KEY": "REPLACE_WITH_KEY" }
       },
       "playwright": {
         "command": "npx",
         "args": ["-y", "@playwright/mcp", "--browser", "chromium", "--headless"]
       }
     }
   }
3. Replace all REPLACE_WITH_* placeholders with actual keys from ~/.gemini/.env or .env
4. Test: gemini -p "List files in the project directory using filesystem MCP"
5. Test: gemini -p "What are the recent commits? use git MCP"
6. Verify each server loads within 3 seconds

Save the configuration and verify Gemini CLI can access all servers. Output a status table for each server.
```

---

## OpenCode/Crush Specific Setup Prompt

```
Configure MCP servers for OpenCode/Crush CLI integration in the Antigravity workspace.

OpenCode/Crush MCP configuration location: ~/.opencode.json or .opencode.json (local)

Steps:
1. Read current ~/.opencode.json (create if missing)
2. Add mcpServers section:
   {
     "mcpServers": {
       "filesystem": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
         "env": []
       },
       "git": {
         "type": "stdio", 
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "."]
       },
       "memory": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-memory"]
       },
       "github": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@github/mcp-server"],
         "env": [{"GITHUB_TOKEN": "TOKEN_HERE"}]
       },
       "context7": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@upstash/context7-mcp"],
         "env": [{"CONTEXT7_API_KEY": "KEY_HERE"}]
       },
       "brave-search": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@brave/brave-search-mcp-server"],
         "env": [{"BRAVE_API_KEY": "KEY_HERE"}]
       },
       "playwright": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@playwright/mcp"]
       },
       "fetch": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch"]
       }
     }
   }
3. Set agents config: Use Gemini 2.5 Pro for coder, Gemini 2.5 Flash for task
4. Test: opencode -p "List project files" 
5. Verify MCP servers load: opencode should show "MCP servers: 8 connected"

NOTE: OpenCode has moved to Crush (charmbracelet/crush). If using Crush, configuration is identical but command is 'crush' instead of 'opencode'.

Save and verify all servers are accessible from OpenCode/Crush.
```

---

*These prompts are optimized for Antigravity Workspace Template — March 2026*
*Sources: Official MCP documentation, GitHub repositories, community testing*
