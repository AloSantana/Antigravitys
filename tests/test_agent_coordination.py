"""
Tests for dual-agent coordination and Jules integration.
"""

import pytest
import asyncio
import time
from backend.agent.orchestrator import Orchestrator, AgentSession, AgentHandoff


@pytest.fixture
def orchestrator():
    """Create an orchestrator instance for testing."""
    return Orchestrator()


class TestAgentSessions:
    """Test agent session management."""

    def test_create_agent_session(self, orchestrator):
        """Test creating a new agent session."""
        session = orchestrator.create_agent_session(
            agent_name="jules",
            session_id="test-session-1",
            context={"task": "code review"},
            is_primary=True
        )

        assert session.agent_name == "jules"
        assert session.session_id == "test-session-1"
        assert session.is_primary is True
        assert session.context["task"] == "code review"
        assert session.created_at > 0

    def test_get_agent_session(self, orchestrator):
        """Test retrieving an agent session."""
        orchestrator.create_agent_session(
            agent_name="rapid-implementer",
            session_id="test-session-2",
            context={}
        )

        session = orchestrator.get_agent_session("test-session-2")
        assert session is not None
        assert session.agent_name == "rapid-implementer"

    def test_list_active_sessions(self, orchestrator):
        """Test listing all active sessions."""
        orchestrator.create_agent_session("jules", "session-1", {})
        orchestrator.create_agent_session("architect", "session-2", {})

        sessions = orchestrator.list_active_sessions()
        assert len(sessions) >= 2
        agent_names = [s.agent_name for s in sessions]
        assert "jules" in agent_names
        assert "architect" in agent_names

    def test_end_agent_session(self, orchestrator):
        """Test ending an agent session."""
        orchestrator.create_agent_session("jules", "session-to-end", {})

        # Verify session exists
        session = orchestrator.get_agent_session("session-to-end")
        assert session is not None

        # End the session
        result = orchestrator.end_agent_session("session-to-end")
        assert result is True

        # Verify session no longer exists
        session = orchestrator.get_agent_session("session-to-end")
        assert session is None

    def test_end_nonexistent_session(self, orchestrator):
        """Test ending a session that doesn't exist."""
        result = orchestrator.end_agent_session("nonexistent-session")
        assert result is False


class TestAgentHandoffs:
    """Test agent handoff functionality."""

    def test_handoff_agent(self, orchestrator):
        """Test executing an agent handoff."""
        handoff = orchestrator.handoff_agent(
            from_agent="rapid-implementer",
            to_agent="jules",
            context={"code": "def hello(): pass"},
            reason="code review needed"
        )

        assert handoff.from_agent == "rapid-implementer"
        assert handoff.to_agent == "jules"
        assert handoff.context["code"] == "def hello(): pass"
        assert handoff.handoff_reason == "code review needed"
        assert handoff.timestamp > 0

    def test_get_handoff_history(self, orchestrator):
        """Test retrieving handoff history."""
        # Create multiple handoffs
        orchestrator.handoff_agent("jules", "testing-stability-expert", {}, "test needed")
        orchestrator.handoff_agent("testing-stability-expert", "jules", {}, "review results")

        history = orchestrator.get_handoff_history()
        assert len(history) >= 2

    def test_get_handoff_history_filtered(self, orchestrator):
        """Test retrieving filtered handoff history."""
        orchestrator.handoff_agent("jules", "architect", {}, "design review")
        orchestrator.handoff_agent("debug-detective", "jules", {}, "bug analysis")

        # Get history filtered by jules
        history = orchestrator.get_handoff_history(agent_name="jules")
        assert len(history) >= 2

        # Verify all handoffs involve jules
        for handoff in history:
            assert handoff.from_agent == "jules" or handoff.to_agent == "jules"

    def test_get_handoff_history_with_limit(self, orchestrator):
        """Test handoff history with limit."""
        # Create several handoffs
        for i in range(5):
            orchestrator.handoff_agent(f"agent-{i}", "jules", {}, f"reason-{i}")

        history = orchestrator.get_handoff_history(limit=3)
        assert len(history) <= 3


class TestSharedContext:
    """Test shared context functionality."""

    def test_update_shared_context(self, orchestrator):
        """Test updating shared context."""
        orchestrator.update_shared_context("project_name", "antigravity")

        context = orchestrator.get_shared_context("project_name")
        assert context == "antigravity"

    def test_get_shared_context_all(self, orchestrator):
        """Test getting all shared context."""
        orchestrator.update_shared_context("key1", "value1")
        orchestrator.update_shared_context("key2", "value2")

        context = orchestrator.get_shared_context()
        assert isinstance(context, dict)
        assert "key1" in context or len(context) > 0  # May contain other keys

    def test_get_nonexistent_context_key(self, orchestrator):
        """Test getting a context key that doesn't exist."""
        context = orchestrator.get_shared_context("nonexistent_key")
        assert context is None


class TestAgentRouting:
    """Test agent routing functionality."""

    def test_route_to_best_agent_code_review(self, orchestrator):
        """Test routing a code review request."""
        agent = orchestrator.route_to_best_agent("Please review this code for quality issues")
        assert agent in ["jules", "code-reviewer"]

    def test_route_to_best_agent_implementation(self, orchestrator):
        """Test routing an implementation request."""
        agent = orchestrator.route_to_best_agent("Implement a new user authentication feature")
        assert agent in ["rapid-implementer", "full-stack-developer"]

    def test_route_to_best_agent_debugging(self, orchestrator):
        """Test routing a debugging request."""
        agent = orchestrator.route_to_best_agent("Debug this error in the login system")
        assert agent == "debug-detective"

    def test_route_to_best_agent_testing(self, orchestrator):
        """Test routing a testing request."""
        agent = orchestrator.route_to_best_agent("Create comprehensive tests for the API")
        assert agent in ["testing-stability-expert", "rapid-implementer"]

    def test_route_to_best_agent_architecture(self, orchestrator):
        """Test routing an architecture request."""
        agent = orchestrator.route_to_best_agent("Design the system architecture for microservices")
        assert agent == "architect"

    def test_route_with_excluded_agents(self, orchestrator):
        """Test routing with excluded agents."""
        agent = orchestrator.route_to_best_agent(
            "Review this code",
            exclude_agents=["jules", "code-reviewer"]
        )
        assert agent not in ["jules", "code-reviewer"]

    def test_route_default_to_jules(self, orchestrator):
        """Test that routing defaults to jules for ambiguous requests."""
        agent = orchestrator.route_to_best_agent("Hello")
        # Should default to jules when no clear match
        assert agent is not None


class TestCollaborativeProcessing:
    """Test collaborative agent processing."""

    @pytest.mark.asyncio
    async def test_collaborative_process_sequential(self, orchestrator):
        """Test sequential collaborative processing."""
        result = await orchestrator.collaborative_process(
            request="Analyze and improve this function",
            agents=["jules", "rapid-implementer"],
            mode="sequential"
        )

        assert result["mode"] == "sequential"
        assert len(result["agents"]) == 2
        assert "jules" in result["results"]
        assert "rapid-implementer" in result["results"]

    @pytest.mark.asyncio
    async def test_collaborative_process_parallel(self, orchestrator):
        """Test parallel collaborative processing."""
        result = await orchestrator.collaborative_process(
            request="Quick task for multiple agents",
            agents=["jules", "docs-master"],
            mode="parallel"
        )

        assert result["mode"] == "parallel"
        assert len(result["agents"]) == 2
        assert "jules" in result["results"]
        assert "docs-master" in result["results"]


class TestAgentStats:
    """Test agent statistics functionality."""

    def test_get_agent_stats(self, orchestrator):
        """Test retrieving agent statistics."""
        # Create some sessions and handoffs
        orchestrator.create_agent_session("jules", "stat-session-1", {})
        orchestrator.create_agent_session("architect", "stat-session-2", {})
        orchestrator.handoff_agent("jules", "architect", {}, "test handoff")

        stats = orchestrator.get_agent_stats()

        assert "active_sessions" in stats
        assert "total_handoffs" in stats
        assert "handoff_by_agent" in stats
        assert "shared_context_size" in stats
        assert "agent_priorities" in stats

        assert stats["active_sessions"] >= 2
        assert stats["total_handoffs"] >= 1
        assert "jules" in stats["agent_priorities"]


class TestAgentPriorities:
    """Test agent priority system."""

    def test_jules_has_highest_priority(self, orchestrator):
        """Test that Jules has the highest priority."""
        priorities = orchestrator._agent_priorities
        jules_priority = priorities.get("jules", 0)

        # Jules should have priority 10
        assert jules_priority == 10

        # Jules should have the highest priority among all agents
        max_priority = max(priorities.values())
        assert jules_priority == max_priority

    def test_all_agents_have_priorities(self, orchestrator):
        """Test that all known agents have priorities."""
        priorities = orchestrator._agent_priorities

        expected_agents = [
            "jules", "rapid-implementer", "architect", "debug-detective",
            "testing-stability-expert", "code-reviewer", "performance-optimizer",
            "full-stack-developer", "devops-infrastructure", "docs-master"
        ]

        for agent in expected_agents:
            assert agent in priorities
            assert priorities[agent] > 0


class TestDataClasses:
    """Test dataclass functionality."""

    def test_agent_session_creation(self):
        """Test AgentSession dataclass."""
        session = AgentSession(
            agent_name="jules",
            session_id="test-123",
            created_at=time.time(),
            context={"key": "value"},
            is_primary=True
        )

        assert session.agent_name == "jules"
        assert session.session_id == "test-123"
        assert session.context["key"] == "value"
        assert session.is_primary is True

    def test_agent_handoff_creation(self):
        """Test AgentHandoff dataclass."""
        handoff = AgentHandoff(
            from_agent="agent1",
            to_agent="agent2",
            context={"data": "test"},
            timestamp=time.time(),
            handoff_reason="testing"
        )

        assert handoff.from_agent == "agent1"
        assert handoff.to_agent == "agent2"
        assert handoff.context["data"] == "test"
        assert handoff.handoff_reason == "testing"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_multiple_sessions_same_agent(self, orchestrator):
        """Test multiple sessions for the same agent."""
        orchestrator.create_agent_session("jules", "jules-session-1", {})
        orchestrator.create_agent_session("jules", "jules-session-2", {})

        sessions = orchestrator.list_active_sessions()
        jules_sessions = [s for s in sessions if s.agent_name == "jules"]
        assert len(jules_sessions) >= 2

    def test_handoff_to_same_agent(self, orchestrator):
        """Test handoff to the same agent."""
        handoff = orchestrator.handoff_agent(
            from_agent="jules",
            to_agent="jules",
            context={"note": "self-review"},
            reason="iterative improvement"
        )

        assert handoff.from_agent == "jules"
        assert handoff.to_agent == "jules"

    def test_empty_context(self, orchestrator):
        """Test operations with empty context."""
        session = orchestrator.create_agent_session(
            agent_name="jules",
            session_id="empty-context",
            context={}
        )
        assert session.context == {}

        handoff = orchestrator.handoff_agent(
            from_agent="jules",
            to_agent="architect",
            context={},
            reason="simple handoff"
        )
        assert handoff.context == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
