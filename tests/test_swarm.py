"""
Comprehensive tests for the swarm system.

Tests:
- MessageBus communication
- SwarmOrchestrator coordination
- RouterAgent delegation
- Worker agents (Coder, Reviewer, Researcher)
- Agent capabilities
- Multi-agent workflows
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.swarm import Message, MessageBus, SwarmOrchestrator
from src.agents.router_agent import RouterAgent
from src.agents.coder_agent import CoderAgent
from src.agents.reviewer_agent import ReviewerAgent
from src.agents.researcher_agent import ResearcherAgent


# =============================================================================
# Message Tests
# =============================================================================

class TestMessage:
    """Test Message dataclass."""
    
    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            sender="User",
            content="Hello, world!"
        )
        
        assert msg.sender == "User"
        assert msg.content == "Hello, world!"
        assert isinstance(msg.timestamp, datetime)
        assert msg.metadata == {}
    
    def test_message_with_metadata(self):
        """Test creating a message with metadata."""
        metadata = {"priority": "high", "type": "query"}
        msg = Message(
            sender="Agent",
            content="Processing...",
            metadata=metadata
        )
        
        assert msg.metadata == metadata
        assert msg.metadata["priority"] == "high"
    
    def test_message_with_custom_timestamp(self):
        """Test message with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        msg = Message(
            sender="System",
            content="Test",
            timestamp=custom_time
        )
        
        assert msg.timestamp == custom_time


# =============================================================================
# MessageBus Tests
# =============================================================================

class TestMessageBus:
    """Test MessageBus functionality."""
    
    def test_message_bus_initialization(self):
        """Test MessageBus initialization."""
        bus = MessageBus()
        
        assert bus.messages == []
    
    def test_send_message(self):
        """Test sending a message to the bus."""
        bus = MessageBus()
        
        msg = bus.send("User", "Test message")
        
        assert isinstance(msg, Message)
        assert msg.sender == "User"
        assert msg.content == "Test message"
        assert len(bus.messages) == 1
    
    def test_send_message_with_metadata(self):
        """Test sending a message with metadata."""
        bus = MessageBus()
        
        metadata = {"tool": "search", "confidence": 0.95}
        msg = bus.send("Agent", "Search results", metadata)
        
        assert msg.metadata == metadata
        assert len(bus.messages) == 1
    
    def test_send_multiple_messages(self):
        """Test sending multiple messages."""
        bus = MessageBus()
        
        bus.send("User", "Message 1")
        bus.send("Agent", "Response 1")
        bus.send("User", "Message 2")
        
        assert len(bus.messages) == 3
    
    def test_get_all_messages(self):
        """Test getting all messages."""
        bus = MessageBus()
        
        bus.send("User", "Message 1")
        bus.send("Agent", "Response 1")
        
        messages = bus.get_all_messages()
        
        assert len(messages) == 2
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Response 1"
        
        # Should return a copy
        messages.append(Message(sender="Test", content="Test"))
        assert len(bus.messages) == 2  # Original unchanged
    
    def test_get_context_for(self):
        """Test getting context for an agent."""
        bus = MessageBus()
        
        for i in range(15):
            bus.send("User", f"Message {i}")
        
        # Get last 10 messages
        context = bus.get_context_for("Agent", last_n=10)
        
        assert len(context) == 10
        assert context[0].content == "Message 5"
        assert context[-1].content == "Message 14"
    
    def test_get_context_for_with_fewer_messages(self):
        """Test getting context when there are fewer messages than requested."""
        bus = MessageBus()
        
        bus.send("User", "Message 1")
        bus.send("Agent", "Response 1")
        
        context = bus.get_context_for("Agent", last_n=10)
        
        # Should return all messages
        assert len(context) == 2
    
    def test_clear_messages(self):
        """Test clearing all messages."""
        bus = MessageBus()
        
        bus.send("User", "Message 1")
        bus.send("Agent", "Response 1")
        
        bus.clear()
        
        assert len(bus.messages) == 0
    
    def test_message_ordering(self):
        """Test that messages maintain chronological order."""
        bus = MessageBus()
        
        messages = []
        for i in range(5):
            msg = bus.send("User", f"Message {i}")
            messages.append(msg)
        
        all_messages = bus.get_all_messages()
        
        for i in range(len(all_messages) - 1):
            assert all_messages[i].timestamp <= all_messages[i + 1].timestamp


# =============================================================================
# RouterAgent Tests
# =============================================================================

class TestRouterAgent:
    """Test RouterAgent functionality."""
    
    def test_router_agent_initialization(self):
        """Test RouterAgent initialization."""
        router = RouterAgent()
        
        assert router.name == "Router"
        assert router.role == "Task Analysis & Delegation"
        assert router.worker_agents == {}
    
    def test_register_worker(self):
        """Test registering worker agents."""
        router = RouterAgent()
        coder = CoderAgent()
        
        router.register_worker(coder)
        
        assert "Coder" in router.worker_agents
        assert router.worker_agents["Coder"] == coder
    
    def test_register_multiple_workers(self):
        """Test registering multiple workers."""
        router = RouterAgent()
        coder = CoderAgent()
        reviewer = ReviewerAgent()
        researcher = ResearcherAgent()
        
        router.register_worker(coder)
        router.register_worker(reviewer)
        router.register_worker(researcher)
        
        assert len(router.worker_agents) == 3
    
    @pytest.mark.asyncio
    async def test_execute_creates_delegation_plan(self):
        """Test that execute creates a delegation plan."""
        router = RouterAgent()
        
        result = await router.execute("Write a Python function to sort a list")
        
        assert result["success"] is True
        assert "delegation_plan" in result
        assert isinstance(result["delegation_plan"], dict)
        assert len(result["delegation_plan"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_coding_task(self):
        """Test analyzing a coding task."""
        router = RouterAgent()
        
        result = await router.execute("Implement a function to calculate fibonacci")
        
        assert "Coder" in result["delegation_plan"]
    
    @pytest.mark.asyncio
    async def test_analyze_review_task(self):
        """Test analyzing a review task."""
        router = RouterAgent()
        
        result = await router.execute("Review the code for security issues")
        
        assert "Reviewer" in result["delegation_plan"]
    
    @pytest.mark.asyncio
    async def test_analyze_research_task(self):
        """Test analyzing a research task."""
        router = RouterAgent()
        
        result = await router.execute("Research best practices for API design")
        
        assert "Researcher" in result["delegation_plan"]
    
    @pytest.mark.asyncio
    async def test_analyze_complex_task(self):
        """Test analyzing a complex task requiring multiple agents."""
        router = RouterAgent()
        
        task = "Research Python best practices, implement a solution, and review it"
        result = await router.execute(task)
        
        # Should involve multiple agents
        assert len(result["delegation_plan"]) >= 2
    
    @pytest.mark.asyncio
    async def test_analyze_generic_task(self):
        """Test analyzing a generic task without specific keywords."""
        router = RouterAgent()
        
        result = await router.execute("Help me with this project")
        
        # Should delegate to all agents as fallback
        assert "Coder" in result["delegation_plan"]
        assert "Reviewer" in result["delegation_plan"]
        assert "Researcher" in result["delegation_plan"]
    
    @pytest.mark.asyncio
    async def test_synthesize_results(self):
        """Test synthesizing results from workers."""
        router = RouterAgent()
        
        worker_results = {
            "Coder": {
                "success": True,
                "output": "Implementation complete"
            },
            "Reviewer": {
                "success": True,
                "output": "Code looks good"
            }
        }
        
        synthesis = await router.synthesize_results(worker_results)
        
        assert synthesis["success"] is True
        assert "synthesis" in synthesis
        assert "Coder" in synthesis["synthesis"]
        assert "Reviewer" in synthesis["synthesis"]
        assert synthesis["worker_count"] == 2
    
    @pytest.mark.asyncio
    async def test_synthesize_with_failure(self):
        """Test synthesizing results when some workers fail."""
        router = RouterAgent()
        
        worker_results = {
            "Coder": {
                "success": True,
                "output": "Done"
            },
            "Reviewer": {
                "success": False,
                "output": "Found issues"
            }
        }
        
        synthesis = await router.synthesize_results(worker_results)
        
        assert synthesis["success"] is False  # Not all successful
    
    def test_get_capabilities(self):
        """Test getting router capabilities."""
        router = RouterAgent()
        router.register_worker(CoderAgent())
        
        capabilities = router.get_capabilities()
        
        assert "Router" in capabilities
        assert "Task Analysis" in capabilities
        assert "Registered workers" in capabilities


# =============================================================================
# Worker Agent Tests
# =============================================================================

class TestCoderAgent:
    """Test CoderAgent functionality."""
    
    def test_coder_agent_initialization(self):
        """Test CoderAgent initialization."""
        coder = CoderAgent()
        
        assert coder.name == "Coder"
        assert "Code" in coder.role
        assert coder.history == []
    
    @pytest.mark.asyncio
    async def test_coder_execute(self):
        """Test CoderAgent execution."""
        coder = CoderAgent()
        
        result = await coder.execute("Write a hello world function")
        
        assert "success" in result
        assert "output" in result
    
    def test_coder_capabilities(self):
        """Test CoderAgent capabilities."""
        coder = CoderAgent()
        
        capabilities = coder.get_capabilities()
        
        assert "Coder" in capabilities
        assert isinstance(capabilities, str)


class TestReviewerAgent:
    """Test ReviewerAgent functionality."""
    
    def test_reviewer_agent_initialization(self):
        """Test ReviewerAgent initialization."""
        reviewer = ReviewerAgent()
        
        assert reviewer.name == "Reviewer"
        assert "Review" in reviewer.role
    
    @pytest.mark.asyncio
    async def test_reviewer_execute(self):
        """Test ReviewerAgent execution."""
        reviewer = ReviewerAgent()
        
        result = await reviewer.execute("Review this code for issues")
        
        assert "success" in result
        assert "output" in result
    
    def test_reviewer_capabilities(self):
        """Test ReviewerAgent capabilities."""
        reviewer = ReviewerAgent()
        
        capabilities = reviewer.get_capabilities()
        
        assert "Reviewer" in capabilities


class TestResearcherAgent:
    """Test ResearcherAgent functionality."""
    
    def test_researcher_agent_initialization(self):
        """Test ResearcherAgent initialization."""
        researcher = ResearcherAgent()
        
        assert researcher.name == "Researcher"
        assert "Research" in researcher.role
    
    @pytest.mark.asyncio
    async def test_researcher_execute(self):
        """Test ResearcherAgent execution."""
        researcher = ResearcherAgent()
        
        result = await researcher.execute("Research Python decorators")
        
        assert "success" in result
        assert "output" in result
    
    def test_researcher_capabilities(self):
        """Test ResearcherAgent capabilities."""
        researcher = ResearcherAgent()
        
        capabilities = researcher.get_capabilities()
        
        assert "Researcher" in capabilities


# =============================================================================
# BaseAgent Tests
# =============================================================================

class TestBaseAgent:
    """Test BaseAgent functionality."""
    
    def test_base_agent_history(self):
        """Test agent history tracking."""
        coder = CoderAgent()
        
        task = "Write a function"
        result = {"success": True, "output": "Done"}
        
        coder.add_to_history(task, result)
        
        history = coder.get_history()
        assert len(history) == 1
        assert history[0]["task"] == task
        assert history[0]["result"] == result
    
    def test_base_agent_reset_history(self):
        """Test resetting agent history."""
        coder = CoderAgent()
        
        coder.add_to_history("Task 1", {"success": True})
        coder.add_to_history("Task 2", {"success": True})
        
        coder.reset_history()
        
        assert len(coder.get_history()) == 0


# =============================================================================
# SwarmOrchestrator Tests
# =============================================================================

class TestSwarmOrchestrator:
    """Test SwarmOrchestrator functionality."""
    
    def test_swarm_orchestrator_initialization(self):
        """Test SwarmOrchestrator initialization."""
        swarm = SwarmOrchestrator()
        
        assert isinstance(swarm.message_bus, MessageBus)
        assert isinstance(swarm.router, RouterAgent)
        assert isinstance(swarm.coder, CoderAgent)
        assert isinstance(swarm.reviewer, ReviewerAgent)
        assert isinstance(swarm.researcher, ResearcherAgent)
        
        # Check agent registry
        assert "Router" in swarm.agents
        assert "Coder" in swarm.agents
        assert "Reviewer" in swarm.agents
        assert "Researcher" in swarm.agents
    
    @pytest.mark.asyncio
    async def test_execute_simple_task(self):
        """Test executing a simple task through the swarm."""
        swarm = SwarmOrchestrator()
        
        result = await swarm.execute("Write a hello world function", verbose=False)
        
        assert result["success"] is not None
        assert "task" in result
        assert "delegation_plan" in result
        assert "worker_results" in result
        assert "synthesis" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_message_bus(self):
        """Test that execution uses message bus."""
        swarm = SwarmOrchestrator()
        
        await swarm.execute("Test task", verbose=False)
        
        messages = swarm.message_bus.get_all_messages()
        
        # Should have messages from user, router, and workers
        assert len(messages) > 0
        assert any(msg.sender == "User" for msg in messages)
        assert any(msg.sender == "Router" for msg in messages)
    
    @pytest.mark.asyncio
    async def test_execute_creates_delegation_plan(self):
        """Test that execute creates a delegation plan."""
        swarm = SwarmOrchestrator()
        
        result = await swarm.execute("Implement and review a function", verbose=False)
        
        assert "delegation_plan" in result
        assert isinstance(result["delegation_plan"], dict)
        assert len(result["delegation_plan"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_runs_workers(self):
        """Test that workers are executed."""
        swarm = SwarmOrchestrator()
        
        result = await swarm.execute("Write code", verbose=False)
        
        assert "worker_results" in result
        assert len(result["worker_results"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_synthesizes_results(self):
        """Test that results are synthesized."""
        swarm = SwarmOrchestrator()
        
        result = await swarm.execute("Test task", verbose=False)
        
        assert "synthesis" in result
        assert isinstance(result["synthesis"], str)
    
    @pytest.mark.asyncio
    async def test_execute_verbose_mode(self):
        """Test execute in verbose mode."""
        swarm = SwarmOrchestrator()
        
        # Should not raise errors
        result = await swarm.execute("Test task", verbose=True)
        
        assert result is not None
    
    def test_get_message_log(self):
        """Test getting message log."""
        swarm = SwarmOrchestrator()
        
        swarm.message_bus.send("User", "Test message")
        
        log = swarm.get_message_log()
        
        assert len(log) == 1
        assert log[0]["sender"] == "User"
        assert log[0]["content"] == "Test message"
        assert "timestamp" in log[0]
        assert "metadata" in log[0]
    
    def test_reset_swarm(self):
        """Test resetting swarm state."""
        swarm = SwarmOrchestrator()
        
        swarm.message_bus.send("User", "Test")
        swarm.coder.add_to_history("Task", {"result": "Done"})
        
        swarm.reset()
        
        assert len(swarm.message_bus.get_all_messages()) == 0
        assert len(swarm.coder.get_history()) == 0
    
    def test_get_agent_capabilities(self):
        """Test getting capabilities of all agents."""
        swarm = SwarmOrchestrator()
        
        capabilities = swarm.get_agent_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "Router" in capabilities
        assert "Coder" in capabilities
        assert "Reviewer" in capabilities
        assert "Researcher" in capabilities


# =============================================================================
# Integration Tests
# =============================================================================

class TestSwarmIntegration:
    """Integration tests for the swarm system."""
    
    @pytest.mark.asyncio
    async def test_full_swarm_workflow(self):
        """Test a complete swarm workflow."""
        swarm = SwarmOrchestrator()
        
        task = "Write a Python function to calculate factorial"
        
        result = await swarm.execute(task, verbose=False)
        
        # Verify complete workflow
        assert result["success"] is not None
        assert result["task"] == task
        assert len(result["delegation_plan"]) > 0
        assert len(result["worker_results"]) > 0
        assert result["synthesis"]
        assert result["message_count"] > 0
        
        # Verify message flow
        messages = swarm.get_message_log()
        assert len(messages) > 0
        assert messages[0]["sender"] == "User"
    
    @pytest.mark.asyncio
    async def test_multiple_task_execution(self):
        """Test executing multiple tasks in sequence."""
        swarm = SwarmOrchestrator()
        
        tasks = [
            "Write a hello world function",
            "Review the code",
            "Research Python best practices"
        ]
        
        for task in tasks:
            result = await swarm.execute(task, verbose=False)
            assert result["success"] is not None
        
        # Message log should contain all tasks
        messages = swarm.get_message_log()
        assert len(messages) > len(tasks)
    
    @pytest.mark.asyncio
    async def test_task_with_all_agents(self):
        """Test a task that uses all available agents."""
        swarm = SwarmOrchestrator()
        
        task = "Research Python decorators, implement an example, and review it"
        
        result = await swarm.execute(task, verbose=False)
        
        # Should involve multiple agents
        assert len(result["delegation_plan"]) >= 2
        assert len(result["worker_results"]) >= 2
    
    @pytest.mark.asyncio
    async def test_context_passing_between_agents(self):
        """Test that context is passed between agents."""
        swarm = SwarmOrchestrator()
        
        # Execute task
        await swarm.execute("Test task", verbose=False)
        
        # Workers should have received context
        messages = swarm.message_bus.get_all_messages()
        assert len(messages) > 0


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestSwarmEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_task(self):
        """Test handling empty task."""
        swarm = SwarmOrchestrator()
        
        result = await swarm.execute("", verbose=False)
        
        # Should handle gracefully
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_very_long_task(self):
        """Test handling very long task description."""
        swarm = SwarmOrchestrator()
        
        long_task = "Write code " * 1000
        
        result = await swarm.execute(long_task, verbose=False)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_task_with_unknown_agent(self):
        """Test handling delegation to non-existent agent."""
        swarm = SwarmOrchestrator()
        
        # Manually create delegation plan with unknown agent
        with patch.object(swarm.router, 'execute') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "delegation_plan": {
                    "UnknownAgent": "Do something"
                }
            }
            
            result = await swarm.execute("Test", verbose=False)
            
            # Should handle gracefully
            assert result is not None
    
    def test_message_bus_with_large_metadata(self):
        """Test message bus with large metadata."""
        bus = MessageBus()
        
        large_metadata = {"data": "x" * 10000}
        msg = bus.send("Agent", "Test", large_metadata)
        
        assert msg.metadata == large_metadata
    
    @pytest.mark.asyncio
    async def test_unicode_in_task(self):
        """Test handling Unicode characters in task."""
        swarm = SwarmOrchestrator()
        
        task = "Write code for 日本語処理"
        
        result = await swarm.execute(task, verbose=False)
        
        assert result["task"] == task


# =============================================================================
# Performance Tests
# =============================================================================

class TestSwarmPerformance:
    """Test swarm system performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_message_bus_scalability(self):
        """Test message bus with many messages."""
        bus = MessageBus()
        
        # Add many messages
        for i in range(1000):
            bus.send("Agent", f"Message {i}")
        
        assert len(bus.messages) == 1000
        
        # Get context should still be fast
        context = bus.get_context_for("Agent", last_n=10)
        assert len(context) == 10
    
    @pytest.mark.asyncio
    async def test_swarm_reset_performance(self):
        """Test that reset clears everything efficiently."""
        swarm = SwarmOrchestrator()
        
        # Add many messages
        for i in range(100):
            swarm.message_bus.send("Agent", f"Message {i}")
        
        swarm.reset()
        
        assert len(swarm.message_bus.get_all_messages()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
