"""
Reviewer agent specialized in code review and quality assurance.
"""

from typing import Dict, Any, Optional

from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """
    Reviewer agent specialized in code review, security, and quality checks.
    
    Capabilities:
    - Code quality review
    - Security vulnerability detection
    - Best practices validation
    - Performance analysis
    """
    
    def __init__(self):
        super().__init__(name="Reviewer", role="Code Review & Quality Assurance")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a code review task.
        
        Args:
            task: Review task description
            context: Optional context (e.g., code to review)
            
        Returns:
            Review results with findings and recommendations
        """
        # Extract code to review
        code_to_review = context.get("code", "") if context else ""
        review_type = context.get("review_type", "general") if context else "general"
        
        # Perform review
        output = self._perform_review(task, code_to_review, review_type)
        
        result = {
            "success": True,
            "output": output,
            "review_type": review_type,
            "issues_found": self._count_issues(output)
        }
        
        self.add_to_history(task, result)
        return result
    
    def _perform_review(self, task: str, code: str, review_type: str) -> str:
        """
        Perform code review (placeholder for LLM integration).
        
        In a real implementation, this would use an LLM to perform actual code review.
        """
        response_parts = [
            f"Reviewer Agent: Code Review ({review_type})",
            "",
            "Review Task:",
            f"- {task}",
            ""
        ]
        
        if code:
            response_parts.append("Code Under Review:")
            response_parts.append("```")
            response_parts.append(code[:300] + "..." if len(code) > 300 else code)
            response_parts.append("```")
            response_parts.append("")
        
        # Simulate review findings
        response_parts.extend([
            "Review Findings:",
            "",
            "✓ Strengths:",
            "- Code structure is clear",
            "- Naming conventions are consistent",
            "",
            "⚠ Areas for Improvement:",
            "- Add error handling for edge cases",
            "- Include docstrings for public functions",
            "- Consider adding type hints",
            "",
            "Security Considerations:",
            "- Input validation needed",
            "- Consider rate limiting for external calls",
            "",
            "Performance Notes:",
            "- Current implementation is acceptable",
            "- Consider caching for repeated operations",
            "",
            "Recommendations:",
            "1. Add comprehensive error handling",
            "2. Improve documentation",
            "3. Add unit tests",
            "4. Consider edge cases"
        ])
        
        return "\n".join(response_parts)
    
    def _count_issues(self, review_output: str) -> int:
        """Count issues found in review (simplified)."""
        # Count lines with warning indicators
        return review_output.count("⚠") + review_output.count("- Consider") + review_output.count("- Add")
    
    def get_capabilities(self) -> str:
        """Get reviewer agent capabilities."""
        capabilities = [
            f"{self.name} ({self.role})",
            "- Reviews code for quality and correctness",
            "- Identifies security vulnerabilities",
            "- Validates best practices compliance",
            "- Provides actionable recommendations",
            "- Analyzes performance implications"
        ]
        return "\n".join(capabilities)
