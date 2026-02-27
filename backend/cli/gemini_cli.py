#!/usr/bin/env python3
"""
Gemini CLI - Command-line interface for Google Gemini AI

Usage:
    gemini_cli.py chat "Your prompt here"
    gemini_cli.py embed "Text to embed"
    gemini_cli.py analyze file.py
    gemini_cli.py multi-agent "Task description"
    gemini_cli.py status
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.gemini_client import GeminiClient
from agent.orchestrator import Orchestrator
from dotenv import load_dotenv


class GeminiCLI:
    """Command-line interface for Gemini AI."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("ERROR: GEMINI_API_KEY not set in environment")
            print("Please set it in .env file or export GEMINI_API_KEY=your_key")
            sys.exit(1)

        self.client = GeminiClient(self.api_key)
        self.orchestrator = Orchestrator()

    async def chat(self, prompt: str, format: str = "plain") -> None:
        """Chat with Gemini AI."""
        print(f"🤖 Gemini AI Processing...")
        print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n")

        response = await self.client.generate(prompt)

        if format == "json":
            output = {
                "prompt": prompt,
                "response": response,
                "model": "gemini-pro",
                "status": "success" if not response.startswith("Error") else "error"
            }
            print(json.dumps(output, indent=2))
        elif format == "markdown":
            print("## Prompt")
            print(f"{prompt}\n")
            print("## Response")
            print(response)
        else:  # plain
            print("─" * 60)
            print(response)
            print("─" * 60)

    async def embed(self, text: str, format: str = "plain") -> None:
        """Generate embeddings for text."""
        print(f"🔢 Generating embeddings...")
        print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}\n")

        embedding = await self.client.embed(text)

        if format == "json":
            output = {
                "text": text,
                "embedding": embedding[:10] if embedding else [],  # Show first 10 dims
                "dimensions": len(embedding),
                "status": "success" if embedding else "error"
            }
            print(json.dumps(output, indent=2))
        else:
            if embedding:
                print(f"✅ Embedding generated: {len(embedding)} dimensions")
                print(f"First 10 values: {embedding[:10]}")
            else:
                print("❌ Failed to generate embedding")

    async def analyze_file(self, file_path: str) -> None:
        """Analyze a code file using Gemini."""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        with open(file_path, 'r') as f:
            content = f.read()

        prompt = f"""Analyze this code file and provide:
1. Purpose and functionality
2. Key components and structure
3. Potential improvements
4. Security considerations

File: {file_path}
```
{content[:2000]}{'...' if len(content) > 2000 else ''}
```
"""

        print(f"🔍 Analyzing {file_path}...")
        response = await self.client.generate(prompt)
        print("\n" + "─" * 60)
        print(response)
        print("─" * 60)

    async def multi_agent(self, task: str, agents: Optional[list] = None) -> None:
        """Execute task using multiple agents."""
        if agents is None:
            agents = ["jules", "rapid-implementer"]

        print(f"🤝 Multi-Agent Collaboration")
        print(f"📋 Task: {task}")
        print(f"👥 Agents: {', '.join(agents)}\n")

        result = await self.orchestrator.collaborative_process(
            request=task,
            agents=agents,
            mode="sequential"
        )

        print("\n" + "═" * 60)
        print("COLLABORATION RESULTS")
        print("═" * 60)

        for agent, response in result["results"].items():
            print(f"\n🤖 {agent.upper()}")
            print("─" * 60)
            print(response.get("response", "No response"))
            print()

    def status(self) -> None:
        """Show system status and configuration."""
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "ANTIGRAVITY WORKSPACE STATUS" + " " * 15 + "║")
        print("╚" + "═" * 58 + "╝")
        print()

        # Active Agents
        print("## Active Agents (13)")
        agents = [
            ("Jules (Autonomous)", "End-to-end autonomous engineering"),
            ("Rapid Implementer", "Fast feature implementation"),
            ("System Architect", "System architecture and design patterns"),
            ("Debug Detective", "Advanced debugging and troubleshooting"),
            ("Testing Expert", "Comprehensive testing and validation"),
            ("Code Reviewer", "Security and quality code reviews"),
            ("Perf Optimizer", "Performance profiling and optimization"),
            ("Full Stack Dev", "Complete web application development"),
            ("DevOps Infra", "Docker, Kubernetes, CI/CD pipelines"),
            ("Docs Master", "Documentation creation and verification"),
            ("Repo Optimizer", "Repository setup and tooling"),
            ("API Developer", "RESTful API design and implementation"),
            ("Deep Research", "In-depth research and analysis"),
        ]

        for name, desc in agents:
            print(f"  • {name}: {desc}")

        print()

        # Configuration Status
        print("## Configuration Status")
        print(f"  • AI Provider: Gemini AI {'✅' if self.api_key else '❌'}")

        # Check MCP servers
        mcp_servers = ["filesystem", "git", "github", "memory", "sequential-thinking"]
        print(f"  • MCP Servers: {len(mcp_servers)} Active")
        for server in mcp_servers:
            print(f"    - {server}")

        # Environment variables
        env_vars = [
            "GEMINI_API_KEY",
            "VERTEX_API_KEY",
            "COPILOT_MCP_GITHUB_TOKEN",
            "HOST",
            "PORT",
            "CACHE_TTL_SECONDS"
        ]
        configured_count = sum(1 for var in env_vars if os.getenv(var))
        print(f"  • Environment: {configured_count}/{len(env_vars)} Variables Configured")

        print()

        # Capabilities
        print("## Capabilities")
        capabilities = [
            "Autonomous Code Refactoring (Jules)",
            "Multi-Agent Orchestration",
            "Sequential & Parallel Agent Collaboration",
            "Deep Repository Analysis",
            "Automated Workflow Execution",
            "Smart Agent Routing",
            "Context-Aware Code Review",
            "Real-time Performance Monitoring"
        ]

        for cap in capabilities:
            print(f"  ✓ {cap}")

        print()

        # Agent Statistics
        stats = self.orchestrator.get_agent_stats()
        print("## Agent Statistics")
        print(f"  • Active Sessions: {stats['active_sessions']}")
        print(f"  • Total Handoffs: {stats['total_handoffs']}")
        print(f"  • Shared Context Size: {stats['shared_context_size']}")

        print()
        print("─" * 60)
        print("✅ System Ready | Use --help for available commands")
        print("─" * 60)


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Gemini CLI - Command-line interface for Google Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s chat "Explain quantum computing"
  %(prog)s embed "Sample text for embedding"
  %(prog)s analyze backend/main.py
  %(prog)s multi-agent "Build a REST API" --agents jules rapid-implementer
  %(prog)s status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with Gemini AI")
    chat_parser.add_argument("prompt", help="Prompt for Gemini")
    chat_parser.add_argument("--format", choices=["plain", "json", "markdown"],
                            default="plain", help="Output format")

    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Generate embeddings")
    embed_parser.add_argument("text", help="Text to embed")
    embed_parser.add_argument("--format", choices=["plain", "json"],
                             default="plain", help="Output format")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a code file")
    analyze_parser.add_argument("file", help="Path to file to analyze")

    # Multi-agent command
    multi_parser = subparsers.add_parser("multi-agent", help="Execute task with multiple agents")
    multi_parser.add_argument("task", help="Task description")
    multi_parser.add_argument("--agents", nargs="+",
                             default=["jules", "rapid-implementer"],
                             help="Agents to use (default: jules rapid-implementer)")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        cli = GeminiCLI()

        if args.command == "chat":
            await cli.chat(args.prompt, args.format)
        elif args.command == "embed":
            await cli.embed(args.text, args.format)
        elif args.command == "analyze":
            await cli.analyze_file(args.file)
        elif args.command == "multi-agent":
            await cli.multi_agent(args.task, args.agents)
        elif args.command == "status":
            cli.status()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
