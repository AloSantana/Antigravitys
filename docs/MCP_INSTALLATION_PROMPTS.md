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

---

## 🤖 OpenCode & Multi-Agent Optimized MCP Servers

> Top 10 MCP servers specifically optimized for OpenCode/Crush terminal workflows and multi-agent coordination. Each prompt is fully self-contained — paste into any AI coding assistant to install and configure from scratch.

---

### 1. Taskmaster AI — Multi-Agent Task Orchestration

```
You are setting up the Taskmaster AI MCP server for this Antigravity project. This is the most important MCP server for multi-agent workflows — it replaces ad-hoc task state with a persistent, queryable task backlog.

INSTALL AND CONFIGURE:

Step 1 — Verify npx access:
  npx --yes task-master-ai --version
  (Expected: version number printed; if error check Node 18+ with: node --version)

Step 2 — Add to .github/copilot/mcp.json under "mcpServers":
  "taskmaster-ai": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "--package=task-master-ai", "task-master-ai"],
    "env": {
      "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
      "OPENAI_API_KEY": "${OPENAI_API_KEY}"
    },
    "tools": ["get_tasks", "next_task", "set_task_status", "add_task", "expand_task", "analyze_project_complexity", "update_task", "get_task"]
  }

Step 3 — Add to opencode.json mcpServers section (OpenCode/Crush format):
  "taskmaster-ai": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "--package=task-master-ai", "task-master-ai"],
    "env": {
      "ANTHROPIC_API_KEY": "REPLACE_WITH_ANTHROPIC_KEY",
      "OPENAI_API_KEY": "REPLACE_WITH_OPENAI_KEY"
    }
  }

Step 4 — Add to .env file (at least one AI key required):
  ANTHROPIC_API_KEY=sk-ant-...    # Preferred — used for task parsing
  OPENAI_API_KEY=sk-...           # Fallback if Anthropic unavailable

Step 5 — Create initial task list from this project's README:
  Use the get_tasks tool to check if any tasks exist.
  If empty, use add_task to create 3 sample tasks:
  - "Set up MCP servers" (priority: high)
  - "Test multi-agent swarm" (priority: medium)  
  - "Document agent workflows" (priority: low)

Step 6 — Verify the multi-agent loop works:
  Call next_task to get the highest-priority unblocked task.
  Call set_task_status to mark it "in-progress".
  Call set_task_status again to mark it "done".
  Call next_task again — it should return the next task.

The full autonomous agent loop is: RouterAgent calls next_task → delegates to CoderAgent → CoderAgent calls set_task_status("done") → loop continues until all tasks complete.
```

---

### 2. Chroma MCP — Semantic Vector Memory for Agents

```
You are setting up the Chroma MCP server for semantic codebase search and agent RAG memory. This fills the critical vector search gap — the existing Memory MCP handles structured knowledge graphs, Chroma handles semantic recall over unstructured content.

INSTALL AND CONFIGURE:

Step 1 — Install via pip/uvx (Python server):
  pip install chroma-mcp
  OR (no install needed with uvx):
  uvx chroma-mcp --help
  (Expected: help text shown; if missing Python: python --version must be 3.10+)

Step 2 — Add to .github/copilot/mcp.json under "mcpServers":
  "chroma": {
    "type": "stdio",
    "command": "uvx",
    "args": ["chroma-mcp", "--mode", "embedded", "--data-dir", "./.chroma"],
    "tools": ["chroma_create_collection", "chroma_add_documents", "chroma_query_documents", "chroma_get_document", "chroma_list_collections", "chroma_delete_collection"]
  }

Step 3 — Add to opencode.json mcpServers section:
  "chroma": {
    "type": "stdio",
    "command": "uvx",
    "args": ["chroma-mcp", "--mode", "embedded", "--data-dir", "./.chroma"]
  }

  NOTE: Embedded mode stores data in ./.chroma directory — add ".chroma/" to .gitignore

Step 4 — Add .chroma/ to .gitignore:
  echo ".chroma/" >> .gitignore

Step 5 — Test semantic indexing:
  Use chroma_create_collection with name "codebase" to create a collection.
  Use chroma_add_documents to add 3 documents:
    - doc1: id="readme", content="This is the Antigravity AI workspace", metadata={"type": "docs"}
    - doc2: id="backend", content="FastAPI Python backend with agent orchestration", metadata={"type": "code"}
    - doc3: id="mcp", content="MCP servers for AI agent capabilities", metadata={"type": "config"}
  Use chroma_query_documents with query="agent memory" to verify semantic search works.
  Expected: doc1 and doc3 should rank highest.

Step 6 — For remote ChromaDB (optional):
  Change args to: ["chroma-mcp", "--mode", "http"]
  Add env: {"CHROMA_HOST": "localhost", "CHROMA_PORT": "8000"}
  Start ChromaDB: docker run -p 8000:8000 chromadb/chroma

Verify: chroma_list_collections returns the "codebase" collection. Semantic search works for agent RAG memory.
```

---

### 3. Tavily MCP — AI-Optimized Search for Agent RAG Pipelines

```
You are setting up the Tavily MCP server for AI-optimized web search. Unlike Brave Search (real-time news) or Exa (neural discovery), Tavily returns pre-cleaned, LLM-ready content specifically designed for RAG pipelines and agent context injection.

INSTALL AND CONFIGURE:

Step 1 — Get a free Tavily API key:
  Go to: https://app.tavily.com → Sign up → Copy API key (starts with tvly-)
  Free tier: 1,000 searches/month — sufficient for development use

Step 2 — Verify package:
  npx -y @tavily/mcp --help
  (Expected: help text; requires Node 18+)

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "tavily": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@tavily/mcp"],
    "env": {
      "TAVILY_API_KEY": "${TAVILY_API_KEY}"
    },
    "tools": ["tavily_search", "tavily_extract"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "tavily": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@tavily/mcp"],
    "env": {
      "TAVILY_API_KEY": "REPLACE_WITH_TAVILY_KEY"
    }
  }

Step 5 — Add to .env:
  TAVILY_API_KEY=tvly-...

Step 6 — Test both key tools:
  a) Search: Use tavily_search with query="MCP server stdio transport protocol 2025"
     Expected: 5-10 structured results with clean snippets (not raw HTML)
  b) Extract: Use tavily_extract with url="https://modelcontextprotocol.io/docs"
     Expected: Clean markdown content from the MCP docs page

Step 7 — Compare with Brave/Exa to understand positioning:
  - tavily_search: best for factual lookups, returns pre-processed content
  - brave_web_search: best for real-time news and local results
  - exa search: best for neural/semantic discovery of similar content

Verify: Both tavily_search and tavily_extract return clean, LLM-ready text (not HTML) that can be directly passed as context to agents.
```

---

### 4. Neon MCP — Serverless Postgres with Database Branching

```
You are setting up the Neon MCP server for serverless Postgres with agent-safe database branching. The key differentiator from standard Postgres MCP: agents can fork a database branch, run destructive migrations safely, then merge or discard.

INSTALL AND CONFIGURE:

Step 1 — Get a free Neon API key:
  Go to: https://console.neon.tech → Account Settings → API Keys → Create
  Free tier: 10 projects, 3GB storage — sufficient for multi-agent state

Step 2 — Verify package:
  npx -y @neondatabase/mcp-server-neon --help

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "neon": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@neondatabase/mcp-server-neon"],
    "env": {
      "NEON_API_KEY": "${NEON_API_KEY}"
    },
    "tools": ["neon_run_sql", "neon_create_project", "neon_create_branch", "neon_describe_table_schema", "neon_list_projects", "neon_delete_branch"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "neon": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@neondatabase/mcp-server-neon"],
    "env": {
      "NEON_API_KEY": "REPLACE_WITH_NEON_KEY"
    }
  }

Step 5 — Add to .env:
  NEON_API_KEY=...

Step 6 — Create and test a project:
  a) Call neon_list_projects — should show any existing projects
  b) Call neon_create_project with name="antigravity-agents" — creates a new Postgres cluster
  c) Note the project_id from the response
  d) Call neon_run_sql:
     project_id: <from step c>
     sql: "CREATE TABLE agent_state (id SERIAL PRIMARY KEY, agent_name TEXT, task TEXT, status TEXT, created_at TIMESTAMP DEFAULT NOW());"
  e) Call neon_run_sql: "INSERT INTO agent_state (agent_name, task, status) VALUES ('coder-agent', 'implement auth', 'in-progress');"
  f) Call neon_run_sql: "SELECT * FROM agent_state;" — verify row exists

Step 7 — Test the critical branching feature:
  a) Call neon_create_branch with project_id=<id> name="agent-experiment"
  b) On the branch, run a destructive migration:
     neon_run_sql with branch_id=<branch_id>: "DROP TABLE agent_state;" (safe — only affects the branch!)
  c) Verify main branch still has data: neon_run_sql without branch_id: "SELECT * FROM agent_state;"
  d) Call neon_delete_branch to clean up the test branch

Verify: The agent_state table exists on the main branch. Branching creates isolated contexts. The branching workflow enables agents to test schema changes safely before applying to production.
```

---

### 5. OpenRouter MCP — 200+ Model Access for Multi-Agent Routing

```
You are setting up the OpenRouter MCP server for unified access to 200+ AI models. This enables heterogeneous multi-agent setups where different agents use different models optimized for their tasks (RouterAgent: fast Gemini Flash; CoderAgent: Claude 3.5 Sonnet; ReviewerAgent: GPT-4o).

INSTALL AND CONFIGURE:

Step 1 — Get a free OpenRouter API key:
  Go to: https://openrouter.ai/keys → Create Key
  Free models available (no credit card for many models)
  Top models for agents: anthropic/claude-3.5-sonnet, google/gemini-2.5-pro, openai/gpt-4o, meta-llama/llama-3.3-70b-instruct (free)

Step 2 — Verify package:
  npx -y openrouter-mcp --help

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "openrouter": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "openrouter-mcp"],
    "env": {
      "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}"
    },
    "tools": ["chat_completion", "list_models", "get_model_info"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "openrouter": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "openrouter-mcp"],
    "env": {
      "OPENROUTER_API_KEY": "REPLACE_WITH_OPENROUTER_KEY"
    }
  }

Step 5 — Add to .env:
  OPENROUTER_API_KEY=sk-or-v1-...

Step 6 — Test model listing and routing:
  a) Call list_models — should return 200+ available models with pricing
  b) Find a free model: look for models with "free" in the ID or pricing=$0
  c) Call chat_completion:
     model: "meta-llama/llama-3.3-70b-instruct:free"
     messages: [{"role": "user", "content": "List 3 best practices for multi-agent AI systems. Be brief."}]
  d) Verify response is coherent and returned in under 10 seconds

Step 7 — Set up multi-agent model routing strategy:
  Add to .env for role-based model selection:
  AGENT_ROUTER_MODEL=google/gemini-flash-1.5         # Fast, cheap for routing
  AGENT_CODER_MODEL=anthropic/claude-3.5-sonnet      # Best for code generation
  AGENT_REVIEWER_MODEL=openai/gpt-4o                 # Best for analysis
  AGENT_RESEARCHER_MODEL=meta-llama/llama-3.3-70b-instruct:free  # Free, good for research

  In the SwarmOrchestrator, agents can call openrouter chat_completion with their assigned model rather than hardcoded Gemini/Anthropic keys — enabling cost optimization and fallback logic.

Verify: chat_completion with a free model returns a valid response. list_models shows available models with cost info. The routing strategy is documented in .env.
```

---

### 6. Upstash MCP — Redis Cache + QStash Message Queue for Agents

```
You are setting up the Upstash MCP server for cross-session agent state (Redis) and async agent-to-agent messaging (QStash). This enables coordination patterns impossible with the in-process Memory MCP.

INSTALL AND CONFIGURE:

Step 1 — Create free Upstash account:
  Go to: https://console.upstash.com → Sign up
  Create a Redis database: Console → Redis → Create Database
    - Name: "antigravity-agents"
    - Region: closest to your location
    - Free tier: 10k commands/day
  Create a QStash account: Console → QStash → Get Started
    - Free tier: 500 messages/day

Step 2 — Get credentials:
  Redis: REST URL and REST Token (from database details page)
  QStash: Token from QStash dashboard

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "upstash": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@upstash/mcp-server"],
    "env": {
      "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
      "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}",
      "QSTASH_TOKEN": "${QSTASH_TOKEN}"
    },
    "tools": ["redis_get", "redis_set", "redis_del", "redis_hset", "redis_hget", "qstash_publish", "qstash_list_queues"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "upstash": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@upstash/mcp-server"],
    "env": {
      "UPSTASH_REDIS_REST_URL": "REPLACE_WITH_URL",
      "UPSTASH_REDIS_REST_TOKEN": "REPLACE_WITH_TOKEN",
      "QSTASH_TOKEN": "REPLACE_WITH_QSTASH_TOKEN"
    }
  }

Step 5 — Add to .env:
  UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
  UPSTASH_REDIS_REST_TOKEN=AX...
  QSTASH_TOKEN=eyJ...

Step 6 — Test Redis for agent state:
  a) Call redis_set: key="current-task", value="implement authentication", ex=3600
  b) Call redis_get: key="current-task" → Expected: "implement authentication"
  c) Test distributed locking: redis_set key="agent-lock:auth.py" value="coder-agent-1" ex=60 nx=true
  d) Try locking again: redis_set key="agent-lock:auth.py" value="coder-agent-2" ex=60 nx=true
     Expected: null (lock already held — prevents concurrent file editing!)
  e) Call redis_del: key="agent-lock:auth.py" to release the lock

Step 7 — Test QStash for async messaging:
  a) Call qstash_publish:
     url: "https://httpbin.org/post"
     body: {"task": "review-auth-code", "agent": "reviewer-agent", "file": "backend/auth.py"}
     Expected: Returns messageId
  b) Call qstash_list_queues to see pending messages

Verify: Redis get/set persists between tool calls. Distributed locking prevents concurrent agent file access. QStash publishes messages that can trigger agent endpoints.
```

---

### 7. Qdrant MCP — Production Vector Database for Agent Memory

```
You are setting up the Qdrant MCP server as a production vector database for semantic agent memory. Choose Qdrant over Chroma when you need: advanced filtering on metadata, hybrid (dense + sparse) search, or production-scale deployments.

INSTALL AND CONFIGURE:

Step 1 — Choose deployment mode:
  Option A (Local Docker, recommended for dev):
    docker run -d -p 6333:6333 qdrant/qdrant
    QDRANT_URL=http://localhost:6333
    No API key needed.
  Option B (Qdrant Cloud, free tier):
    Go to: https://cloud.qdrant.io → Create Cluster (free: 1GB)
    Get URL (ends in :6333) and API Key from dashboard

Step 2 — Install Python package:
  pip install mcp-server-qdrant
  OR: uvx mcp-server-qdrant --help

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "qdrant": {
    "type": "stdio",
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
      "QDRANT_URL": "${QDRANT_URL}",
      "QDRANT_API_KEY": "${QDRANT_API_KEY}",
      "COLLECTION_NAME": "antigravity-agent-memory",
      "EMBEDDING_PROVIDER": "fastembed"
    },
    "tools": ["qdrant-store", "qdrant-find"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "qdrant": {
    "type": "stdio",
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
      "QDRANT_URL": "http://localhost:6333",
      "COLLECTION_NAME": "antigravity-agent-memory",
      "EMBEDDING_PROVIDER": "fastembed"
    }
  }

Step 5 — Add to .env:
  QDRANT_URL=http://localhost:6333
  QDRANT_API_KEY=                       # Leave empty for local Docker
  EMBEDDING_PROVIDER=fastembed          # Local embeddings, no API cost

Step 6 — Test semantic storage and retrieval:
  a) Call qdrant-store:
     information: "The Antigravity backend uses FastAPI with async endpoints. Authentication is JWT-based with Pydantic models for validation."
     metadata: {"agent": "coder-agent", "file": "backend/main.py", "timestamp": "2026-03-01"}
  b) Call qdrant-store again:
     information: "The MCP server configuration is stored in .github/copilot/mcp.json and .agent/mcp_config.json"
     metadata: {"agent": "coder-agent", "file": ".github/copilot/mcp.json"}
  c) Call qdrant-find:
     query: "authentication implementation"
     Expected: First stored document should rank highest
  d) Call qdrant-find:
     query: "MCP configuration files"
     Expected: Second stored document should rank highest

Step 7 — Agent memory isolation pattern:
  For multi-agent setups, use different COLLECTION_NAME per agent:
  - coder-agent: COLLECTION_NAME=coder-memory
  - reviewer-agent: COLLECTION_NAME=reviewer-memory
  - shared: COLLECTION_NAME=shared-memory
  All agents can read shared-memory but write only to their own collection.

Verify: qdrant-store saves documents. qdrant-find returns semantically relevant results. The fastembed provider works without any API key.
```

---

### 8. Linear MCP — Sprint & Issue Tracking for Agent Coordination

```
You are setting up the Linear MCP server for issue tracking and sprint management in multi-agent workflows. Agents create bugs they find, update issue status as code lands, and coordinate work via sprint boards.

INSTALL AND CONFIGURE:

Step 1 — Get Linear API key (free for personal use):
  Go to: https://linear.app → Settings → API → Personal API Keys → Create key
  Name: "Antigravity Agents"
  Scopes: read, write (for issue creation/updates)

Step 2 — Verify package:
  npx -y linear-mcp-server --help

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "linear": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "linear-mcp-server"],
    "env": {
      "LINEAR_API_KEY": "${LINEAR_API_KEY}"
    },
    "tools": ["list_issues", "create_issue", "update_issue", "search_issues", "list_projects", "get_issue"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "linear": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "linear-mcp-server"],
    "env": {
      "LINEAR_API_KEY": "REPLACE_WITH_LINEAR_KEY"
    }
  }

Step 5 — Add to .env:
  LINEAR_API_KEY=lin_api_...

Step 6 — Test core operations:
  a) Call list_projects → shows all Linear projects (create one in Linear UI first if empty)
  b) Call create_issue:
     title: "Implement Taskmaster AI MCP integration"
     description: "Add task-master-ai MCP server for multi-agent task orchestration. See docs/MCP_INSTALLATION_PROMPTS.md for setup instructions."
     priority: 2 (high)
     Note the issue ID from the response (e.g., "ENG-42")
  c) Call get_issue with the ID from step b → verify details
  d) Call update_issue: set status to "In Progress"
  e) Call search_issues: query="MCP" → should return the created issue
  f) Call update_issue: set status to "Done" to close the test issue

Step 7 — Multi-agent integration pattern:
  ReviewerAgent workflow:
    1. list_issues (status="Backlog", assignee=me) → get assigned work
    2. update_issue (status="In Progress") → signal work started
    3. [perform code review]
    4. create_issue (if bug found): title="Bug: {description}", priority=urgent
    5. update_issue (status="Done") → close completed ticket

Verify: list_issues returns project issues. create_issue creates a real ticket visible in Linear UI. update_issue changes status. search_issues finds issues by keyword.
```

---

### 9. Notion MCP (Official) — Knowledge Base & Auto-Documentation

```
You are setting up the official Notion MCP server (@notionhq/notion-mcp-server). This is the direct official server — NOT via WayStation proxy. Agents use it to read project knowledge bases and auto-generate documentation.

INSTALL AND CONFIGURE:

Step 1 — Create a Notion Integration:
  Go to: https://www.notion.so/my-integrations → New Integration
  Name: "Antigravity Agents"
  Capabilities: Read content, Update content, Insert content
  Copy the "Internal Integration Token" (starts with secret_)

Step 2 — Share pages with the integration:
  In Notion, open any page you want agents to access.
  Click ··· menu → Connections → Connect to "Antigravity Agents"
  IMPORTANT: Agents can ONLY access pages explicitly shared with the integration

Step 3 — Verify package:
  npx -y @notionhq/notion-mcp-server --help

Step 4 — Add to .github/copilot/mcp.json under "mcpServers":
  "notion": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
      "NOTION_API_KEY": "${NOTION_API_KEY}"
    },
    "tools": ["search", "retrieve_page", "create_page", "update_page", "query_database", "append_blocks"]
  }

Step 5 — Add to opencode.json mcpServers section:
  "notion": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
      "NOTION_API_KEY": "REPLACE_WITH_NOTION_KEY"
    }
  }

Step 6 — Add to .env:
  NOTION_API_KEY=secret_...

Step 7 — Test all key operations:
  a) Call search: query="Antigravity" → should return shared pages containing that word
  b) Create a test page: call create_page:
     parent: {"type": "workspace"}  
     title: "Agent Session Log — 2026-03-01"
     content: "# Agent Session\n\nThis page was created by the Antigravity MCP agent.\n\n## Tasks Completed\n- Set up Notion MCP server\n- Verified read/write access"
  c) Note the page ID from the response
  d) Call retrieve_page with the ID → verify content matches
  e) Call append_blocks to add a note: "## Status\nAll MCP servers configured successfully."
  f) Call update_page to change the title: "Agent Session Log — 2026-03-01 ✅"

Step 8 — Auto-documentation workflow:
  After each major coding session, the RouterAgent should call create_page with:
  - Session summary (what was built)
  - Architecture decisions made
  - Open questions for next session
  This creates an automatic "engineering log" in Notion from every agent session.

Verify: search finds shared pages. create_page creates a real page visible in Notion. retrieve_page reads content. append_blocks adds to existing pages.
```

---

### 10. Daytona MCP — Persistent Sandboxes for Multi-Session Agent Work

```
You are setting up the Daytona MCP server for persistent development environment sandboxes. Unlike E2B (ephemeral — resets each execution), Daytona workspaces survive between sessions. A CoderAgent's environment with installed dependencies and in-progress files persists until you explicitly stop it.

INSTALL AND CONFIGURE:

Step 1 — Choose deployment:
  Option A (Daytona Cloud, recommended):
    Sign up: https://app.daytona.io → Create account
    Get API key: Profile → API Keys → Generate
  Option B (Self-hosted, fully private):
    docker run -d --name daytona-server \
      -p 3986:3986 \
      daytonaio/daytona-server
    API_KEY=none, SERVER_URL=http://localhost:3986

Step 2 — Install Daytona CLI (needed for workspace bootstrap):
  # macOS/Linux:
  curl -sfL https://download.daytona.io/daytona/install.sh | sh
  # Windows: see https://www.daytona.io/docs/installation/installation
  daytona version

Step 3 — Add to .github/copilot/mcp.json under "mcpServers":
  "daytona": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@daytona/mcp"],
    "env": {
      "DAYTONA_API_KEY": "${DAYTONA_API_KEY}",
      "DAYTONA_SERVER_URL": "${DAYTONA_SERVER_URL}"
    },
    "tools": ["daytona_workspace_create", "daytona_code_execute", "daytona_file_write", "daytona_file_read", "daytona_workspace_stop", "daytona_workspace_list"]
  }

Step 4 — Add to opencode.json mcpServers section:
  "daytona": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@daytona/mcp"],
    "env": {
      "DAYTONA_API_KEY": "REPLACE_WITH_DAYTONA_KEY",
      "DAYTONA_SERVER_URL": "https://app.daytona.io"
    }
  }

Step 5 — Add to .env:
  DAYTONA_API_KEY=dt-...
  DAYTONA_SERVER_URL=https://app.daytona.io

Step 6 — Create and test a workspace:
  a) Call daytona_workspace_create:
     repository_url: "https://github.com/AloSantana/Antigravitys"
     name: "antigravity-dev"
     Expected: Returns workspace_id after ~30 seconds
  b) Call daytona_workspace_list → should show "antigravity-dev" workspace
  c) Call daytona_code_execute:
     workspace_id: <from step a>
     command: "python --version && pip list | grep fastapi"
     Expected: Python version + FastAPI if installed
  d) Call daytona_file_write:
     workspace_id: <from step a>
     path: "/workspace/test-agent-output.txt"
     content: "This file was created by an AI agent via Daytona MCP"
  e) Call daytona_file_read:
     workspace_id: <from step a>
     path: "/workspace/test-agent-output.txt"
     Expected: The text written in step d

Step 7 — Multi-agent workflow with persistent environments:
  CoderAgent pattern:
    1. daytona_workspace_create (once per feature branch)
    2. daytona_code_execute: "git checkout -b feature/new-auth"
    3. daytona_file_write: write generated code files
    4. daytona_code_execute: "pytest tests/ -v" to run tests
    5. daytona_code_execute: "git commit -am 'feat: implement auth'" to commit
    6. daytona_workspace_stop when feature is complete (preserves state)
    7. Next session: workspace resumes with all changes intact

  KEY DIFFERENCE from E2B: E2B resets between calls. Daytona workspace in step 6 still has all your agent's installed packages, git history, and file changes when you come back tomorrow.

Verify: daytona_workspace_create returns a workspace_id. daytona_code_execute runs commands in the sandbox. daytona_file_write and daytona_file_read work for agent-generated code persistence.
```

---

## Complete opencode.json with All 10 New Servers

```
Configure the opencode.json file in this project to include all 10 new OpenCode-optimized MCP servers. Read the current .opencode.json or opencode.json file, then add the mcpServers configuration.

TARGET STATE of opencode.json:
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow",
  "mcpServers": {
    "taskmaster-ai": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    },
    "chroma": {
      "type": "stdio",
      "command": "uvx",
      "args": ["chroma-mcp", "--mode", "embedded", "--data-dir", "./.chroma"]
    },
    "tavily": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@tavily/mcp"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    },
    "neon": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@neondatabase/mcp-server-neon"],
      "env": {
        "NEON_API_KEY": "${NEON_API_KEY}"
      }
    },
    "openrouter": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "openrouter-mcp"],
      "env": {
        "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}"
      }
    },
    "upstash": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/mcp-server"],
      "env": {
        "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
        "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}",
        "QSTASH_TOKEN": "${QSTASH_TOKEN}"
      }
    },
    "qdrant": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "${QDRANT_URL}",
        "QDRANT_API_KEY": "${QDRANT_API_KEY}",
        "COLLECTION_NAME": "antigravity-agent-memory",
        "EMBEDDING_PROVIDER": "fastembed"
      }
    },
    "linear": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "linear-mcp-server"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    },
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    },
    "daytona": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@daytona/mcp"],
      "env": {
        "DAYTONA_API_KEY": "${DAYTONA_API_KEY}",
        "DAYTONA_SERVER_URL": "${DAYTONA_SERVER_URL}"
      }
    }
  }
}

Steps to apply:
1. Read the current opencode.json file
2. Replace its entire contents with the TARGET STATE above
3. Verify the JSON is valid
4. Run: node -e "JSON.parse(require('fs').readFileSync('opencode.json', 'utf8')); console.log('JSON valid ✅')"

After updating opencode.json, also add the new environment variables to .env.example:
  # === OpenCode & Multi-Agent MCP Servers ===
  ANTHROPIC_API_KEY=sk-ant-...              # Taskmaster AI (required)
  TAVILY_API_KEY=tvly-...                    # Tavily AI search
  NEON_API_KEY=...                           # Neon serverless Postgres
  OPENROUTER_API_KEY=sk-or-v1-...           # OpenRouter multi-model
  UPSTASH_REDIS_REST_URL=https://...         # Upstash Redis
  UPSTASH_REDIS_REST_TOKEN=AX...            # Upstash Redis token
  QSTASH_TOKEN=eyJ...                        # Upstash QStash queue
  QDRANT_URL=http://localhost:6333           # Qdrant vector DB
  QDRANT_API_KEY=                            # Leave empty for local Qdrant
  LINEAR_API_KEY=lin_api_...                 # Linear issue tracking
  NOTION_API_KEY=secret_...                  # Notion knowledge base
  DAYTONA_API_KEY=dt-...                     # Daytona dev sandboxes
  DAYTONA_SERVER_URL=https://app.daytona.io # Daytona server URL

Report: Confirm opencode.json is valid JSON with 10 new mcpServers entries. Confirm .env.example has the new variables.
```

---

*These prompts are optimized for Antigravity Workspace Template — March 2026*
*Sources: Official MCP documentation, GitHub repositories, community testing*
