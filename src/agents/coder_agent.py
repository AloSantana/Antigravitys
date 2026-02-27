"""
Coder agent specialized in writing and refactoring code.
"""

from typing import Dict, Any, Optional

from .base_agent import BaseAgent


class CoderAgent(BaseAgent):
    """
    Coder agent specialized in code implementation and refactoring.
    
    Capabilities:
    - Write new code
    - Refactor existing code
    - Fix bugs
    - Implement features
    """
    
    def __init__(self):
        super().__init__(name="Coder", role="Code Implementation")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a coding task.
        
        Args:
            task: Coding task description
            context: Optional context (e.g., existing code, requirements)
            
        Returns:
            Result with generated/modified code
        """
        # Extract relevant context
        existing_code = context.get("existing_code", "") if context else ""
        language = context.get("language", "python") if context else "python"
        
        # Simulate code generation (in real implementation, would use LLM)
        output = self._generate_code_response(task, existing_code, language)
        
        result = {
            "success": True,
            "output": output,
            "language": language,
            "task_type": self._classify_task(task)
        }
        
        self.add_to_history(task, result)
        return result
    
    def _classify_task(self, task: str) -> str:
        """Classify the type of coding task."""
        task_lower = task.lower()
        
        if "bug" in task_lower or "fix" in task_lower:
            return "bug_fix"
        elif "refactor" in task_lower:
            return "refactoring"
        elif "implement" in task_lower or "create" in task_lower or "write" in task_lower:
            return "implementation"
        else:
            return "general"
    
    def _generate_code_response(self, task: str, existing_code: str, language: str) -> str:
        """
        Generate a code response (placeholder for LLM integration).
        
        In a real implementation, this would call the LLM to generate actual code.
        """
        task_type = self._classify_task(task)
        
        response_parts = [
            f"Coder Agent: Processing coding task of type '{task_type}'",
            f"Language: {language}",
            "",
            "Task Analysis:",
            f"- {task}",
            ""
        ]
        
        if existing_code:
            response_parts.append("Existing Code Context:")
            response_parts.append(f"```{language}")
            response_parts.append(existing_code[:200] + "..." if len(existing_code) > 200 else existing_code)
            response_parts.append("```")
            response_parts.append("")
        
        response_parts.extend([
            "Proposed Solution:",
            "```" + language,
            "# Implementation would go here",
            "# This is a placeholder - in production, would use LLM to generate actual code",
            "def solution():",
            f"    # Task: {task[:50]}...",
            "    pass",
            "```",
            "",
            "Implementation Notes:",
            "- Code follows best practices",
            "- Includes error handling",
            "- Documented with docstrings"
        ])
        
        return "\n".join(response_parts)
    
    def get_capabilities(self) -> str:
        """Get coder agent capabilities."""
        capabilities = [
            f"{self.name} ({self.role})",
            "- Implements new features and functions",
            "- Fixes bugs in existing code",
            "- Refactors code for better quality",
            "- Supports multiple languages (Python, JavaScript, etc.)",
            "- Follows coding best practices"
        ]
        return "\n".join(capabilities)
