"""
Router agent for task analysis and delegation.
"""

import re
from typing import Dict, Any, Optional

from .base_agent import BaseAgent


class RouterAgent(BaseAgent):
    """
    Router agent that analyzes tasks and delegates to appropriate worker agents.
    
    Responsibilities:
    - Analyze incoming tasks
    - Determine which specialist agents are needed
    - Create delegation plans
    - Synthesize results from workers
    """
    
    def __init__(self):
        super().__init__(name="Router", role="Task Analysis & Delegation")
        self.worker_agents = {}
    
    def register_worker(self, agent: BaseAgent):
        """Register a worker agent."""
        self.worker_agents[agent.name] = agent
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze task and create delegation plan.
        
        Args:
            task: Task description
            context: Optional context
            
        Returns:
            Delegation plan with agent assignments
        """
        # Analyze the task and determine which agents are needed
        delegation_plan = self._analyze_task(task)
        
        result = {
            "success": True,
            "delegation_plan": delegation_plan,
            "task": task,
            "agents_needed": list(delegation_plan.keys())
        }
        
        self.add_to_history(task, result)
        return result
    
    def _analyze_task(self, task: str) -> Dict[str, str]:
        """
        Analyze task and create delegation plan.
        
        Returns:
            Dictionary mapping agent names to their specific sub-tasks
        """
        task_lower = task.lower()
        delegation = {}
        
        # Keyword-based delegation logic
        # Coding tasks
        if any(kw in task_lower for kw in ["code", "implement", "write", "function", "class", "fix bug", "refactor"]):
            delegation["Coder"] = self._extract_coder_task(task)
        
        # Review tasks
        if any(kw in task_lower for kw in ["review", "check", "validate", "security", "quality", "test"]):
            delegation["Reviewer"] = self._extract_reviewer_task(task)
        
        # Research tasks
        if any(kw in task_lower for kw in ["research", "investigate", "analyze", "find", "search", "learn", "documentation"]):
            delegation["Researcher"] = self._extract_researcher_task(task)
        
        # If no specific keywords found, default to all agents
        if not delegation:
            delegation["Coder"] = f"Implement: {task}"
            delegation["Reviewer"] = f"Review: {task}"
            delegation["Researcher"] = f"Research: {task}"
        
        return delegation
    
    def _extract_coder_task(self, task: str) -> str:
        """Extract coding-specific task."""
        # Look for DELEGATION format
        match = re.search(r'CODER:\s*([^\n]+)', task, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return task
    
    def _extract_reviewer_task(self, task: str) -> str:
        """Extract review-specific task."""
        # Look for DELEGATION format
        match = re.search(r'REVIEWER:\s*([^\n]+)', task, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return task
    
    def _extract_researcher_task(self, task: str) -> str:
        """Extract research-specific task."""
        # Look for DELEGATION format
        match = re.search(r'RESEARCHER:\s*([^\n]+)', task, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return task
    
    async def synthesize_results(self, worker_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize results from multiple worker agents.
        
        Args:
            worker_results: Dictionary mapping agent names to their results
            
        Returns:
            Synthesized final result
        """
        # Combine all worker outputs
        combined_output = []
        all_successful = True
        
        for agent_name, result in worker_results.items():
            if not result.get("success", False):
                all_successful = False
            
            combined_output.append(f"\n=== {agent_name} ===")
            combined_output.append(result.get("output", "No output"))
        
        synthesis = {
            "success": all_successful,
            "synthesis": "\n".join(combined_output),
            "worker_count": len(worker_results),
            "workers": list(worker_results.keys())
        }
        
        return synthesis
    
    def get_capabilities(self) -> str:
        """Get router agent capabilities."""
        capabilities = [
            f"{self.name} ({self.role})",
            "- Analyzes tasks and determines required specialists",
            "- Delegates to worker agents (Coder, Reviewer, Researcher)",
            "- Synthesizes results from multiple agents",
            f"- Registered workers: {', '.join(self.worker_agents.keys()) if self.worker_agents else 'None'}"
        ]
        return "\n".join(capabilities)
