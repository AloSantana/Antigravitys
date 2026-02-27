"""
Base classes for sandbox code execution.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ExecutionResult:
    """Result of code execution in a sandbox."""
    
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    truncated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "error": self.error,
            "truncated": self.truncated,
            "metadata": self.metadata
        }


class CodeSandbox(ABC):
    """
    Abstract base class for code execution sandboxes.
    
    Implementations must provide secure, isolated code execution
    with timeout and resource limits.
    """
    
    @abstractmethod
    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code in the sandbox.
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            timeout: Execution timeout in seconds
            working_dir: Working directory for execution
            
        Returns:
            ExecutionResult with output and status
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Clean up sandbox resources."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if sandbox is available and properly configured."""
        pass
