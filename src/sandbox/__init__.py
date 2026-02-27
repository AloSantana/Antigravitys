"""
Sandbox code execution system for Antigravity Workspace.

Provides secure code execution in isolated environments.
"""

from .base import ExecutionResult, CodeSandbox
from .factory import get_sandbox

__all__ = ["ExecutionResult", "CodeSandbox", "get_sandbox"]
