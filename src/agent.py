import os
import re
import time
import json
import asyncio
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from src.config import settings
from src.memory import MemoryManager

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiAgent:
    """
    Production-grade agent implementing the Think-Act-Reflect cognitive loop.
    
    Features:
    - Context loading from .context/*.md files
    - Zero-config tool discovery from src/tools/
    - MCP tool integration
    - Memory management with summarization
    - Deep Think prompt generation
    - Tool call extraction and execution
    """

    def __init__(self):
        self.settings = settings
        self.memory = MemoryManager()
        self.tools: Dict[str, Callable] = {}
        self.mcp_tools: Dict[str, Callable] = {}
        self.context_files = []
        
        print(f"🤖 Initializing {self.settings.AGENT_NAME} with model {self.settings.GEMINI_MODEL_NAME}...")
        
        # Initialize Gemini client if available
        if GENAI_AVAILABLE and self.settings.GOOGLE_API_KEY:
            self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
            print("✓ Gemini client initialized")
        else:
            self.client = None
            print("⚠ Gemini client not available (running in mock mode)")
        
        # Load context files
        self._load_context()
        
        # Discover and register tools
        self._discover_tools()
        
        # Initialize MCP if enabled
        if self.settings.MCP_ENABLED:
            self._initialize_mcp()
        
        print(f"✓ Agent initialized with {len(self.tools)} tools and {len(self.mcp_tools)} MCP tools")

    def _load_context(self):
        """Load all .md files from .context/ directory."""
        context_dir = self.settings.resolve_path(".context")
        
        if not context_dir.exists():
            print("⚠ No .context directory found")
            return
        
        md_files = list(context_dir.glob("*.md"))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.context_files.append({
                        "name": md_file.name,
                        "content": content
                    })
            except Exception as e:
                print(f"⚠ Failed to load {md_file.name}: {e}")
        
        print(f"✓ Loaded {len(self.context_files)} context files")

    def _discover_tools(self):
        """Dynamically discover and register tools from src/tools/ directory."""
        tools_dir = Path(__file__).parent / "tools"
        
        if not tools_dir.exists():
            print("⚠ No tools directory found")
            return
        
        # Scan for Python files
        tool_files = list(tools_dir.glob("*.py"))
        
        for tool_file in tool_files:
            if tool_file.name.startswith("_") or tool_file.name == "__init__.py":
                continue
            
            try:
                # Import the module
                module_name = f"src.tools.{tool_file.stem}"
                module = importlib.import_module(module_name)
                
                # Find all public functions
                for name, obj in inspect.getmembers(module):
                    if (inspect.isfunction(obj) and 
                        not name.startswith("_") and 
                        obj.__module__ == module_name):
                        
                        self.tools[name] = obj
                        
            except Exception as e:
                print(f"⚠ Failed to load tools from {tool_file.name}: {e}")
        
        print(f"✓ Discovered {len(self.tools)} tools")

    def _initialize_mcp(self):
        """Initialize MCP client and discover MCP tools."""
        try:
            from src.mcp_client import MCPClientManagerSync
            
            mcp_client = MCPClientManagerSync()
            
            if mcp_client.initialize():
                self.mcp_tools = mcp_client.get_all_tools_as_callables()
                print(f"✓ MCP initialized with {len(self.mcp_tools)} tools")
            else:
                print("⚠ MCP initialization failed")
                
        except Exception as e:
            print(f"⚠ MCP initialization error: {e}")

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with context and tools."""
        prompt_parts = []
        
        # Add context files
        if self.context_files:
            prompt_parts.append("# Context\n")
            for ctx_file in self.context_files:
                prompt_parts.append(f"## {ctx_file['name']}\n")
                prompt_parts.append(ctx_file['content'])
                prompt_parts.append("\n")
        
        # Add tool catalog
        if self.tools or self.mcp_tools:
            prompt_parts.append("\n# Available Tools\n")
            
            for tool_name, tool_func in self.tools.items():
                doc = tool_func.__doc__ or "No description available"
                prompt_parts.append(f"- **{tool_name}**: {doc.strip()}\n")
            
            for tool_name, tool_func in self.mcp_tools.items():
                doc = getattr(tool_func, '__doc__', "No description available")
                prompt_parts.append(f"- **{tool_name}**: {doc}\n")
        
        # Add agent directive
        prompt_parts.append("\n# Your Role\n")
        prompt_parts.append(f"You are {self.settings.AGENT_NAME}, an advanced AI agent.\n")
        prompt_parts.append("Use the Think-Act-Reflect pattern:\n")
        prompt_parts.append("1. Think deeply about the task using <thought> tags\n")
        prompt_parts.append("2. Act by calling appropriate tools\n")
        prompt_parts.append("3. Reflect on results and iterate if needed\n")
        
        return "\n".join(prompt_parts)

    def summarize_memory(self) -> str:
        """
        Summarize old messages to fit within context window.
        
        Returns:
            Summary of older interactions (≤120 words)
        """
        history = self.memory.get_history()
        
        if len(history) <= 10:
            return ""  # No need to summarize
        
        # Get older messages (beyond the recent 10)
        old_messages = history[:-10]
        
        # Create a basic summary (in production, would use Gemini)
        summary_parts = []
        for msg in old_messages[:5]:  # First 5 old messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:50]
            summary_parts.append(f"{role}: {content}...")
        
        summary = " | ".join(summary_parts)
        
        # Truncate to approximately 120 words
        words = summary.split()[:120]
        return " ".join(words)

    def _generate_thought(self, task: str) -> str:
        """
        Generate deep think analysis of the task.
        
        Uses the Deep Think prompt pattern from .antigravity/rules.md
        """
        thought_parts = [
            f"\n🤔 <thought>",
            f"Task Analysis: {task}",
            "",
            "Analyzing requirements:",
            "- What is the core objective?",
            "- What information/context do I have?",
            "- What tools are available?",
            "- What are potential edge cases?",
            "",
            f"Available tools: {', '.join(list(self.tools.keys())[:5])}{'...' if len(self.tools) > 5 else ''}",
            "",
            "Execution strategy:",
            "1. Gather necessary information",
            "2. Apply appropriate tools",
            "3. Validate results",
            "4. Provide comprehensive response",
            "</thought>\n"
        ]
        
        return "\n".join(thought_parts)

    def _extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract tool call from agent response.
        
        Supports both JSON format and plain-text Action format:
        - JSON: {"action": "tool_name", "args": {...}}
        - Plain: Action: tool_name(arg1="value", arg2="value")
        
        Returns:
            Dictionary with action and args, or None if no tool call found
        """
        # Try JSON format first
        json_match = re.search(r'\{[^}]*"action"[^}]*\}', text, re.DOTALL)
        if json_match:
            try:
                tool_call = json.loads(json_match.group(0))
                return tool_call
            except json.JSONDecodeError:
                pass
        
        # Try plain-text Action format
        action_match = re.search(r'Action:\s*(\w+)\((.*?)\)', text, re.DOTALL)
        if action_match:
            tool_name = action_match.group(1)
            args_str = action_match.group(2)
            
            # Parse arguments (simplified)
            args = {}
            if args_str.strip():
                # Basic parsing of key=value pairs
                for arg_pair in args_str.split(','):
                    if '=' in arg_pair:
                        key, value = arg_pair.split('=', 1)
                        args[key.strip()] = value.strip().strip('"\'')
            
            return {"action": tool_name, "args": args}
        
        return None

    async def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """
        Execute a tool call.
        
        Args:
            tool_call: Dictionary with 'action' and 'args'
            
        Returns:
            Tool execution result as string
        """
        action = tool_call.get("action", "")
        args = tool_call.get("args", {})
        
        # Check if tool exists
        tool_func = self.tools.get(action) or self.mcp_tools.get(action)
        
        if not tool_func:
            return f"Error: Tool '{action}' not found"
        
        try:
            # Execute tool (handle both sync and async)
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)
            
            return str(result)
            
        except Exception as e:
            return f"Error executing tool '{action}': {str(e)}"

    def think(self, task: str) -> str:
        """
        Deep Think phase: Analyze the task and formulate a plan.
        """
        thought = self._generate_thought(task)
        print(thought)
        return thought

    async def act(self, task: str) -> str:
        """
        Act phase: Execute the task using available tools.
        
        Process:
        1. Record user input to memory
        2. Build system prompt with context
        3. Generate response (with tool calls if needed)
        4. Extract and execute tool calls
        5. Follow up with tool observation
        
        Args:
            task: User task description
            
        Returns:
            Final response
        """
        # Record user input
        self.memory.add_entry("user", task)
        
        # Think about the task
        thought = self.think(task)
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Get memory context window
        context_messages = self.memory.get_context_window(
            system_prompt=system_prompt,
            max_messages=20,
            summarizer=lambda msgs: self.summarize_memory()
        )
        
        # Generate response (mocked if no Gemini client)
        if self.client and GENAI_AVAILABLE:
            # Real Gemini API call would go here
            response = f"(Gemini response for: {task})"
        else:
            # Mock response with tool call
            response = f"""
I'll help you with: {task}

{thought}

Let me use the available tools to accomplish this.

Action: list_mcp_tools()

This will show us what tools are available.
"""
        
        print(f"\n🛠️  Agent Response:\n{response}\n")
        
        # Extract and execute tool calls (max 1 per iteration)
        tool_call = self._extract_tool_call(response)
        
        if tool_call:
            print(f"🔧 Executing tool: {tool_call['action']}")
            tool_result = await self._execute_tool(tool_call)
            print(f"📊 Tool Result: {tool_result[:200]}{'...' if len(str(tool_result)) > 200 else ''}\n")
            
            # Add tool observation to response
            response += f"\n\nTool Result:\n{tool_result}"
        
        # Record assistant response
        self.memory.add_entry("assistant", response)
        
        return response

    def reflect(self):
        """
        Reflect phase: Review past actions and performance.
        
        Analyzes history to identify patterns, successes, and areas for improvement.
        """
        history = self.memory.get_history()
        print(f"\n🧠 Reflecting on {len(history)} past interactions...")
        
        if len(history) > 10:
            print(f"   Memory is growing - consider summarization")
        
        # Future: Add more sophisticated reflection logic
        # - Analyze success/failure patterns
        # - Identify frequently used tools
        # - Learn from mistakes
        
        print(f"   ✓ Reflection complete\n")

    def run(self, task: str):
        """
        Main entry point for the agent.
        
        Executes the full Think-Act-Reflect loop.
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting Task: {task}")
        print(f"{'='*60}\n")
        
        try:
            # Use asyncio for async operations
            result = asyncio.run(self.act(task))
            print(f"\n✅ Result:\n{result}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        
        finally:
            # Always reflect
            self.reflect()
            
            print(f"{'='*60}")
            print(f"✓ Task Complete")
            print(f"{'='*60}\n")

    def shutdown(self):
        """Clean up resources."""
        print("🔄 Shutting down agent...")
        self.memory.save_memory()
        print("✓ Agent shutdown complete")


if __name__ == "__main__":
    # Example usage
    agent = GeminiAgent()
    agent.run("List all available MCP tools")
    agent.shutdown()
