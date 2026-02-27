"""
Multi-agent system using swarm intelligence patterns.

This package provides a router-worker agent architecture for collaborative
task execution.
"""

from .base_agent import BaseAgent
from .router_agent import RouterAgent
from .coder_agent import CoderAgent
from .reviewer_agent import ReviewerAgent
from .researcher_agent import ResearcherAgent

__all__ = [
    "BaseAgent",
    "RouterAgent",
    "CoderAgent",
    "ReviewerAgent",
    "ResearcherAgent"
]
