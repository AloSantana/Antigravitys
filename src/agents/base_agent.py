"""
Base agent class for the multi-agent system.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAgent(ABC):
    """
    Base class for all agents in the swarm system.
    
    All specialized agents inherit from this class and implement
    the execute() method for their specific domain.
    """
    
    def __init__(self, name: str, role: str):
        """
        Initialize the base agent.
        
        Args:
            name: Agent identifier
            role: Agent's role/specialty
        """
        self.name = name
        self.role = role
        self.history: List[Dict[str, Any]] = []
        # Performance metrics
        self.total_tasks: int = 0
        self.successful_tasks: int = 0
        self.failed_tasks: int = 0
        self.total_execution_time: float = 0.0
    
    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task description
            context: Optional context dictionary
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    def add_to_history(self, task: str, result: Dict[str, Any]):
        """Add task and result to agent's history, updating metrics."""
        elapsed = result.get("execution_time_ms", 0.0)
        self.total_tasks += 1
        self.total_execution_time += elapsed
        if result.get("success", False):
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1
        self.history.append({
            "task": task,
            "result": result
        })
    
    def reset_history(self):
        """Clear the agent's history and reset metrics."""
        self.history.clear()
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.total_execution_time = 0.0
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the agent's execution history."""
        return self.history.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.
        
        Returns:
            Dictionary with task counts and average execution time
        """
        avg_time = (
            self.total_execution_time / self.total_tasks
            if self.total_tasks > 0
            else 0.0
        )
        return {
            "name": self.name,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "avg_execution_time_ms": round(avg_time, 2),
            "total_execution_time_ms": round(self.total_execution_time, 2),
        }
    
    def get_capabilities(self) -> str:
        """
        Get a description of the agent's capabilities.
        
        Returns:
            String describing what the agent can do
        """
        return f"{self.name} ({self.role}): Base agent with no specific capabilities defined."

    @staticmethod
    def _timestamp_ms() -> float:
        """Return current time in milliseconds."""
        return time.monotonic() * 1000
