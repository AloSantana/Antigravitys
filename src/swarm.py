"""
Multi-agent swarm orchestration system.

Provides a message bus and orchestrator for coordinating multiple agents
in a router-worker pattern with parallel execution, result caching, and
task prioritization for fast multi-agent workflows.
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Dict, Any, List, Optional, Tuple

from src.agents import RouterAgent, CoderAgent, ReviewerAgent, ResearcherAgent


class TaskPriority(IntEnum):
    """Priority levels for swarm tasks (higher value = higher priority)."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


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
    2. Worker agents execute their assigned sub-tasks **in parallel**
    3. Router synthesizes results from all workers

    Parallel execution (via ``asyncio.gather``) is the primary performance
    improvement over the legacy sequential approach — all worker agents run
    concurrently so total wall-clock time equals the slowest single worker
    rather than the sum of all workers.

    Additionally provides:
    - **Result caching** — identical tasks reuse previous results (TTL-based)
    - **Task prioritization** — ``TaskPriority`` enum controls ordering
    - **Performance metrics** — per-agent and per-swarm timing
    """
    
    # Default cache TTL in seconds
    _CACHE_TTL: int = 300

    def __init__(self, cache_ttl: int = _CACHE_TTL):
        """Initialize the swarm with router and worker agents.
        
        Args:
            cache_ttl: Seconds before a cached result expires (0 = disabled).
        """
        self.message_bus = MessageBus()
        self.cache_ttl = cache_ttl
        # Result cache: task_hash -> (result, expiry_timestamp)
        self._cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        
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

        # Swarm-level execution metrics
        self.total_executions: int = 0
        self.cache_hits: int = 0
        self.total_wall_time_ms: float = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _task_hash(self, task: str) -> str:
        """Return a stable cache key for *task*."""
        return hashlib.sha256(task.encode()).hexdigest()

    def _cache_get(self, task: str) -> Optional[Dict[str, Any]]:
        """Return a cached result or ``None`` if absent / expired."""
        if self.cache_ttl <= 0:
            return None
        key = self._task_hash(task)
        entry = self._cache.get(key)
        if entry and time.monotonic() < entry[1]:
            return entry[0]
        if entry:
            del self._cache[key]
        return None

    def _cache_set(self, task: str, result: Dict[str, Any]) -> None:
        """Store *result* in the cache with a TTL expiry."""
        if self.cache_ttl <= 0:
            return
        key = self._task_hash(task)
        self._cache[key] = (result, time.monotonic() + self.cache_ttl)

    async def _execute_worker(
        self,
        agent_name: str,
        sub_task: str,
        context: Dict[str, Any],
        verbose: bool,
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute a single worker and return ``(agent_name, result)``."""
        agent = self.agents.get(agent_name)
        if not agent:
            if verbose:
                print(f"⚠  Warning: Agent '{agent_name}' not found, skipping...")
            return agent_name, {"success": False, "output": f"Agent '{agent_name}' not registered.", "execution_time_ms": 0.0}
        
        if verbose:
            print(f"→ {agent_name}: Executing sub-task (parallel)...")
            print(f"  Sub-task: {sub_task[:80]}{'...' if len(sub_task) > 80 else ''}")
        
        result = await agent.execute(sub_task, context)
        
        # Record on the message bus (thread-safe because asyncio is single-threaded)
        self.message_bus.send(
            agent_name,
            result.get("output", "Task completed"),
            {"success": result.get("success", False)}
        )
        
        if verbose:
            elapsed = result.get("execution_time_ms", "?")
            print(f"  ✓ {agent_name} completed in {elapsed} ms\n")
        
        return agent_name, result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    
    async def execute(
        self,
        user_task: str,
        verbose: bool = True,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Dict[str, Any]:
        """
        Execute a task using the swarm system with **parallel** worker execution.
        
        Process:
        1. Check result cache — return immediately on hit
        2. Router analyzes task and creates delegation plan
        3. Workers execute their assigned sub-tasks **concurrently**
        4. Router synthesizes final results
        5. Store result in cache for future identical requests
        
        Args:
            user_task: Task description from user
            verbose: Whether to print progress messages
            priority: Task priority level (affects future scheduling)
            
        Returns:
            Final synthesized result
        """
        wall_start = time.monotonic()
        self.total_executions += 1

        if verbose:
            print(f"\n{'='*60}")
            print(f"Swarm Execution Started  [priority={priority.name}]")
            print(f"{'='*60}")
            print(f"Task: {user_task}\n")

        # --- Cache check ---
        cached = self._cache_get(user_task)
        if cached is not None:
            self.cache_hits += 1
            if verbose:
                print("  ⚡ Cache hit — returning cached result\n")
                print(f"{'='*60}")
                print("Swarm Execution Complete (cached)")
                print(f"{'='*60}\n")
            return {**cached, "from_cache": True}
        
        # Step 1: Send user task to message bus
        self.message_bus.send("User", user_task, {"priority": priority.value})
        
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
        
        # Step 3: Build shared context snapshot once (avoid re-reading bus per worker)
        context_messages = self.message_bus.get_context_for("*")
        shared_context = {
            "recent_messages": [
                {"sender": msg.sender, "content": msg.content}
                for msg in context_messages
            ]
        }

        # Step 4: Execute ALL worker tasks in **parallel**
        if verbose:
            print(f"→ Dispatching {len(delegation_plan)} worker(s) in parallel...\n")

        worker_coroutines = [
            self._execute_worker(agent_name, sub_task, shared_context, verbose)
            for agent_name, sub_task in delegation_plan.items()
        ]

        results_list: List[Tuple[str, Dict[str, Any]]] = await asyncio.gather(
            *worker_coroutines, return_exceptions=False
        )
        worker_results: Dict[str, Dict[str, Any]] = dict(results_list)
        
        # Step 5: Router synthesizes results
        if verbose:
            print("→ Router: Synthesizing results from all workers...")
        
        synthesis = await self.router.synthesize_results(worker_results)
        
        self.message_bus.send(
            "Router",
            "Final synthesis complete",
            {"synthesis": synthesis}
        )
        
        if verbose:
            print("  ✓ Synthesis complete\n")

        wall_elapsed_ms = round((time.monotonic() - wall_start) * 1000, 2)
        self.total_wall_time_ms += wall_elapsed_ms

        if verbose:
            print(f"  Wall-clock time: {wall_elapsed_ms} ms")
            print(f"{'='*60}")
            print("Swarm Execution Complete")
            print(f"{'='*60}\n")
        
        result = {
            "success": synthesis.get("success", True),
            "task": user_task,
            "delegation_plan": delegation_plan,
            "worker_results": worker_results,
            "synthesis": synthesis.get("synthesis", ""),
            "workers_used": synthesis.get("workers", []),
            "message_count": len(self.message_bus.get_all_messages()),
            "wall_time_ms": wall_elapsed_ms,
            "from_cache": False,
            "priority": priority.name,
        }

        self._cache_set(user_task, result)
        return result
    
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

    def get_swarm_metrics(self) -> Dict[str, Any]:
        """
        Return swarm-level performance metrics.

        Returns:
            Dictionary with execution counts, cache stats, and per-agent metrics.
        """
        avg_wall = (
            self.total_wall_time_ms / self.total_executions
            if self.total_executions > 0
            else 0.0
        )
        return {
            "total_executions": self.total_executions,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": round(self.cache_hits / self.total_executions, 4) if self.total_executions else 0.0,
            "avg_wall_time_ms": round(avg_wall, 2),
            "total_wall_time_ms": round(self.total_wall_time_ms, 2),
            "agents": {name: agent.get_metrics() for name, agent in self.agents.items()},
        }
    
    def reset(self):
        """Reset the swarm state (clear message bus, agent histories, and cache)."""
        self.message_bus.clear()
        self._cache.clear()
        self.total_executions = 0
        self.cache_hits = 0
        self.total_wall_time_ms = 0.0
        
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

