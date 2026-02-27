"""
Base agent class for the multi-agent system.
"""

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
        """Add task and result to agent's history."""
        self.history.append({
            "task": task,
            "result": result
        })
    
    def reset_history(self):
        """Clear the agent's history."""
        self.history.clear()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the agent's execution history."""
        return self.history.copy()
    
    def get_capabilities(self) -> str:
        """
        Get a description of the agent's capabilities.
        
        Returns:
            String describing what the agent can do
        """
        return f"{self.name} ({self.role}): Base agent with no specific capabilities defined."
