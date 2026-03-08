"""
Router agent for task analysis and delegation.
"""

import re
from typing import Dict, Any, Optional, Tuple

from .base_agent import BaseAgent


# Keyword sets used for routing decisions
_CODER_KEYWORDS = frozenset([
    "code", "implement", "write", "function", "class", "fix bug", "refactor",
    "program", "script", "algorithm", "api", "endpoint", "module", "library",
    "debug", "compile", "build", "feature", "method",
])

_REVIEWER_KEYWORDS = frozenset([
    "review", "check", "validate", "security", "quality", "test", "audit",
    "lint", "static analysis", "vulnerability", "best practices", "verify",
    "inspect", "assess", "evaluate",
])

_RESEARCHER_KEYWORDS = frozenset([
    "research", "investigate", "analyze", "find", "search", "learn",
    "documentation", "explore", "compare", "benchmark", "survey", "study",
    "understand", "look up", "what is", "how does",
])


class RouterAgent(BaseAgent):
    """
    Router agent that analyzes tasks and delegates to appropriate worker agents.
    
    Responsibilities:
    - Analyze incoming tasks using keyword and heuristic scoring
    - Determine which specialist agents are needed (with confidence scores)
    - Create delegation plans
    - Synthesize results from workers
    """
    
    def __init__(self):
        super().__init__(name="Router", role="Task Analysis & Delegation")
        self.worker_agents: Dict[str, BaseAgent] = {}
    
    def register_worker(self, agent: BaseAgent) -> None:
        """Register a worker agent."""
        self.worker_agents[agent.name] = agent
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze task and create delegation plan.
        
        Args:
            task: Task description
            context: Optional context
            
        Returns:
            Delegation plan with agent assignments and routing confidence
        """
        delegation_plan, confidence_scores = self._analyze_task(task)
        
        result = {
            "success": True,
            "delegation_plan": delegation_plan,
            "task": task,
            "agents_needed": list(delegation_plan.keys()),
            "confidence_scores": confidence_scores,
            "execution_time_ms": 0.0,
        }
        
        self.add_to_history(task, result)
        return result
    
    def _score_task(self, task: str) -> Dict[str, int]:
        """
        Score a task for each worker type based on keyword frequency.

        Returns:
            Mapping of agent name to score (0 = no match).
        """
        task_lower = task.lower()
        words = set(re.findall(r"\w+", task_lower))
        bigrams = {
            f"{a} {b}"
            for a, b in zip(task_lower.split(), task_lower.split()[1:])
        }
        tokens = words | bigrams

        scores: Dict[str, int] = {
            "Coder": len(tokens & _CODER_KEYWORDS),
            "Reviewer": len(tokens & _REVIEWER_KEYWORDS),
            "Researcher": len(tokens & _RESEARCHER_KEYWORDS),
        }
        return scores

    def _analyze_task(self, task: str) -> Tuple[Dict[str, str], Dict[str, float]]:
        """
        Analyze task and create delegation plan with confidence scores.
        
        Returns:
            Tuple of (delegation_plan, confidence_scores)
            delegation_plan: Dict mapping agent names to their specific sub-tasks
            confidence_scores: Dict mapping agent names to routing confidence [0,1]
        """
        scores = self._score_task(task)
        total = sum(scores.values()) or 1  # avoid div-by-zero

        delegation: Dict[str, str] = {}
        confidence: Dict[str, float] = {}

        for agent_name, score in scores.items():
            if score > 0:
                delegation[agent_name] = self._extract_agent_task(agent_name, task)
                confidence[agent_name] = round(score / total, 3)

        # If no specific keywords found, delegate to all agents equally
        if not delegation:
            delegation = {
                "Coder": f"Implement: {task}",
                "Reviewer": f"Review: {task}",
                "Researcher": f"Research: {task}",
            }
            confidence = {"Coder": 0.333, "Reviewer": 0.333, "Researcher": 0.333}
        
        return delegation, confidence
    
    def _extract_agent_task(self, agent_name: str, task: str) -> str:
        """Extract the sub-task string for a given agent."""
        tag = agent_name.upper()
        match = re.search(rf"{tag}:\s*([^\n]+)", task, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        prefixes = {
            "Coder": "Implement",
            "Reviewer": "Review",
            "Researcher": "Research",
        }
        return f"{prefixes.get(agent_name, 'Handle')}: {task}"

    # ------------------------------------------------------------------
    # Legacy helpers kept for backward compatibility
    # ------------------------------------------------------------------

    def _extract_coder_task(self, task: str) -> str:
        return self._extract_agent_task("Coder", task)

    def _extract_reviewer_task(self, task: str) -> str:
        return self._extract_agent_task("Reviewer", task)

    def _extract_researcher_task(self, task: str) -> str:
        return self._extract_agent_task("Researcher", task)

    async def synthesize_results(self, worker_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize results from multiple worker agents.
        
        Args:
            worker_results: Dictionary mapping agent names to their results
            
        Returns:
            Synthesized final result with combined output and timing summary
        """
        combined_output = []
        all_successful = True
        total_worker_time_ms: float = 0.0
        
        for agent_name, result in worker_results.items():
            if not result.get("success", False):
                all_successful = False
            
            elapsed = result.get("execution_time_ms", 0.0)
            total_worker_time_ms += elapsed
            combined_output.append(f"\n=== {agent_name} ({elapsed} ms) ===")
            combined_output.append(result.get("output", "No output"))
        
        synthesis = {
            "success": all_successful,
            "synthesis": "\n".join(combined_output),
            "worker_count": len(worker_results),
            "workers": list(worker_results.keys()),
            "total_worker_time_ms": round(total_worker_time_ms, 2),
        }
        
        return synthesis
    
    def get_capabilities(self) -> str:
        """Get router agent capabilities."""
        capabilities = [
            f"{self.name} ({self.role})",
            "- Analyzes tasks using keyword scoring and confidence estimates",
            "- Delegates to worker agents (Coder, Reviewer, Researcher)",
            "- Dispatches workers in parallel for maximum throughput",
            "- Synthesizes results from multiple agents",
            f"- Registered workers: {', '.join(self.worker_agents.keys()) if self.worker_agents else 'None'}"
        ]
        return "\n".join(capabilities)

