"""
Multi-agent swarm orchestration system.

Provides a message bus and orchestrator for coordinating multiple agents
in a router-worker pattern.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.agents import RouterAgent, CoderAgent, ReviewerAgent, ResearcherAgent


@dataclass
class Message:
    """Represents a message in the system."""
    sender: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    Central message bus for agent communication.
    
    Maintains a chronological log of all messages and provides
    context retrieval for agents.
    """
    
    def __init__(self):
        self.messages: List[Message] = []
    
    def send(self, sender: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Send a message to the bus.
        
        Args:
            sender: Message sender identifier
            content: Message content
            metadata: Optional metadata dictionary
            
        Returns:
            The created Message object
        """
        message = Message(
            sender=sender,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        return message
    
    def get_all_messages(self) -> List[Message]:
        """Get all messages in chronological order."""
        return self.messages.copy()
    
    def get_context_for(self, agent_name: str, last_n: int = 10) -> List[Message]:
        """
        Get recent message context for an agent.
        
        Args:
            agent_name: Name of the agent requesting context
            last_n: Number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        return self.messages[-last_n:] if len(self.messages) > last_n else self.messages.copy()
    
    def clear(self):
        """Clear all messages from the bus."""
        self.messages.clear()


class SwarmOrchestrator:
    """
    Orchestrates multiple agents in a swarm system.
    
    Uses a router-worker pattern where:
    1. Router agent analyzes tasks and creates delegation plans
    2. Worker agents execute their assigned sub-tasks
    3. Router synthesizes results from all workers
    """
    
    def __init__(self):
        """Initialize the swarm with router and worker agents."""
        self.message_bus = MessageBus()
        
        # Initialize agents
        self.router = RouterAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.researcher = ResearcherAgent()
        
        # Register workers with router
        self.router.register_worker(self.coder)
        self.router.register_worker(self.reviewer)
        self.router.register_worker(self.researcher)
        
        # Agent registry
        self.agents = {
            "Router": self.router,
            "Coder": self.coder,
            "Reviewer": self.reviewer,
            "Researcher": self.researcher
        }
    
    async def execute(self, user_task: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Execute a task using the swarm system.
        
        Process:
        1. User task sent to message bus
        2. Router analyzes and creates delegation plan
        3. Workers execute their assigned sub-tasks
        4. Router synthesizes final results
        
        Args:
            user_task: Task description from user
            verbose: Whether to print progress messages
            
        Returns:
            Final synthesized result
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Swarm Execution Started")
            print(f"{'='*60}")
            print(f"Task: {user_task}\n")
        
        # Step 1: Send user task to message bus
        self.message_bus.send("User", user_task)
        
        # Step 2: Router analyzes task
        if verbose:
            print("→ Router: Analyzing task and creating delegation plan...")
        
        delegation_result = await self.router.execute(user_task)
        delegation_plan = delegation_result.get("delegation_plan", {})
        
        if verbose:
            print(f"  Delegation Plan: {list(delegation_plan.keys())}\n")
        
        self.message_bus.send(
            "Router",
            f"Delegation plan created: {list(delegation_plan.keys())}",
            {"delegation_plan": delegation_plan}
        )
        
        # Step 3: Execute worker tasks
        worker_results = {}
        
        for agent_name, sub_task in delegation_plan.items():
            agent = self.agents.get(agent_name)
            
            if not agent:
                if verbose:
                    print(f"⚠ Warning: Agent '{agent_name}' not found, skipping...")
                continue
            
            if verbose:
                print(f"→ {agent_name}: Executing sub-task...")
                print(f"  Sub-task: {sub_task[:80]}{'...' if len(sub_task) > 80 else ''}")
            
            # Get recent context for the agent
            context_messages = self.message_bus.get_context_for(agent_name)
            context = {
                "recent_messages": [
                    {"sender": msg.sender, "content": msg.content}
                    for msg in context_messages
                ]
            }
            
            # Execute the sub-task
            result = await agent.execute(sub_task, context)
            worker_results[agent_name] = result
            
            # Send result to message bus
            self.message_bus.send(
                agent_name,
                result.get("output", "Task completed"),
                {"success": result.get("success", False)}
            )
            
            if verbose:
                print(f"  ✓ {agent_name} completed\n")
        
        # Step 4: Router synthesizes results
        if verbose:
            print("→ Router: Synthesizing results from all workers...")
        
        synthesis = await self.router.synthesize_results(worker_results)
        
        self.message_bus.send(
            "Router",
            "Final synthesis complete",
            {"synthesis": synthesis}
        )
        
        if verbose:
            print(f"  ✓ Synthesis complete\n")
            print(f"{'='*60}")
            print("Swarm Execution Complete")
            print(f"{'='*60}\n")
        
        # Return final result
        return {
            "success": synthesis.get("success", True),
            "task": user_task,
            "delegation_plan": delegation_plan,
            "worker_results": worker_results,
            "synthesis": synthesis.get("synthesis", ""),
            "workers_used": synthesis.get("workers", []),
            "message_count": len(self.message_bus.get_all_messages())
        }
    
    def get_message_log(self) -> List[Dict[str, Any]]:
        """
        Get the full message log.
        
        Returns:
            List of message dictionaries
        """
        return [
            {
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in self.message_bus.get_all_messages()
        ]
    
    def reset(self):
        """Reset the swarm state (clear message bus and agent histories)."""
        self.message_bus.clear()
        
        for agent in self.agents.values():
            agent.reset_history()
    
    def get_agent_capabilities(self) -> Dict[str, str]:
        """
        Get capabilities of all agents.
        
        Returns:
            Dictionary mapping agent names to their capabilities
        """
        return {
            name: agent.get_capabilities()
            for name, agent in self.agents.items()
        }
