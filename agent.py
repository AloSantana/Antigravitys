"""
Convenience entrypoint so `python agent.py` works from the repo root.

Usage:
    python agent.py "Your task here"
    python agent.py  # Uses default task from AGENT_TASK env var
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agent import GeminiAgent


def main():
    """Main entry point for CLI agent usage."""
    # Get task from command line or environment
    task = " ".join(sys.argv[1:]).strip() or os.environ.get(
        "AGENT_TASK",
        "Help me review the project structure"
    )
    
    # Create and run agent
    agent = GeminiAgent()
    
    try:
        agent.run(task)
    except KeyboardInterrupt:
        print("\n\n⚠ Task interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    finally:
        agent.shutdown()


if __name__ == "__main__":
    main()
