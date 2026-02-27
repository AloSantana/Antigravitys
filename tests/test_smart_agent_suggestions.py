"""
Tests for Smart Agent Suggestions (Feature E)
Tests the enhanced AgentManager.suggest_agents() and /api/agents/suggest endpoint.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agent.manager import AgentManager, AgentMetadata


@pytest.fixture
def manager(tmp_path):
    """Create an AgentManager with a temporary agents directory."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    # Create a few mock agent files
    agent_defs = {
        "debug-detective": {
            "type": "Debugging Agent",
            "expertise": "Bug hunting and root cause analysis",
            "capabilities": ["Debugging", "Error Analysis"],
            "tools": ["debugger", "profiler"]
        },
        "full-stack-developer": {
            "type": "Development Agent",
            "expertise": "Full-stack web development",
            "capabilities": ["Frontend", "Backend", "Database"],
            "tools": ["editor", "terminal"]
        },
        "testing-stability-expert": {
            "type": "Testing Agent",
            "expertise": "QA and test automation",
            "capabilities": ["Unit Testing", "E2E Testing"],
            "tools": ["pytest", "playwright"]
        },
        "performance-optimizer": {
            "type": "Performance Agent",
            "expertise": "Performance tuning",
            "capabilities": ["Profiling", "Optimization"],
            "tools": ["profiler", "benchmark"]
        },
        "code-reviewer": {
            "type": "Review Agent",
            "expertise": "Code quality and security",
            "capabilities": ["Code Review", "Security Audit"],
            "tools": ["linter", "scanner"]
        },
    }

    for name, meta in agent_defs.items():
        content = f"""# {name}

## Agent Metadata
- **Name**: {name}
- **Type**: {meta['type']}
- **Expertise**: {meta['expertise']}
- **Priority**: high

## Purpose
{meta['expertise']}

## Core Responsibilities
{chr(10).join(f"{i+1}. **{c}**: Description" for i, c in enumerate(meta['capabilities']))}

## Available Tools
{chr(10).join(f"- {t}: description" for t in meta['tools'])}

## End
"""
        (agents_dir / f"{name}.agent.md").write_text(content, encoding="utf-8")

    return AgentManager(agents_dir=str(agents_dir))


class TestSuggestAgents:
    """Test the suggest_agents() method."""

    def test_returns_suggestions_for_debugging_task(self, manager):
        suggestions = manager.suggest_agents("I have a bug in my code that crashes")
        assert len(suggestions) > 0
        agent_names = [s['agent_name'] for s in suggestions]
        assert 'debug-detective' in agent_names

    def test_returns_suggestions_for_testing_task(self, manager):
        suggestions = manager.suggest_agents("Write unit tests for the auth module")
        assert len(suggestions) > 0
        agent_names = [s['agent_name'] for s in suggestions]
        assert 'testing-stability-expert' in agent_names

    def test_returns_suggestions_for_performance_task(self, manager):
        suggestions = manager.suggest_agents("The API is slow and has high latency")
        assert len(suggestions) > 0
        agent_names = [s['agent_name'] for s in suggestions]
        assert 'performance-optimizer' in agent_names

    def test_returns_suggestions_for_review_task(self, manager):
        suggestions = manager.suggest_agents("Review my code for security vulnerabilities")
        assert len(suggestions) > 0
        agent_names = [s['agent_name'] for s in suggestions]
        assert 'code-reviewer' in agent_names

    def test_returns_suggestions_for_fullstack_task(self, manager):
        suggestions = manager.suggest_agents("Build a REST API with database and frontend")
        assert len(suggestions) > 0
        agent_names = [s['agent_name'] for s in suggestions]
        assert 'full-stack-developer' in agent_names

    def test_confidence_scores_are_valid(self, manager):
        suggestions = manager.suggest_agents("debug this error traceback crash")
        for s in suggestions:
            assert 0 <= s['confidence'] <= 100
            assert isinstance(s['confidence'], int)

    def test_auto_select_flag(self, manager):
        """High confidence should set auto_select=True."""
        suggestions = manager.suggest_agents("debug this error traceback crash bug fix broken")
        if suggestions and suggestions[0]['confidence'] >= 80:
            assert suggestions[0]['auto_select'] is True

    def test_limit_parameter(self, manager):
        suggestions = manager.suggest_agents("build and test a REST API with database", limit=2)
        assert len(suggestions) <= 2

    def test_min_confidence_filter(self, manager):
        suggestions = manager.suggest_agents("help me with something", min_confidence=90)
        for s in suggestions:
            assert s['confidence'] >= 90

    def test_empty_query_returns_empty(self, manager):
        assert manager.suggest_agents("") == []
        assert manager.suggest_agents("ab") == []
        assert manager.suggest_agents(None) == []

    def test_suggestion_structure(self, manager):
        suggestions = manager.suggest_agents("fix a bug in my code")
        if suggestions:
            s = suggestions[0]
            assert 'agent_name' in s
            assert 'confidence' in s
            assert 'reason' in s
            assert 'auto_select' in s
            assert 'expertise' in s
            assert 'loaded' in s

    def test_suggestions_are_sorted_by_confidence(self, manager):
        suggestions = manager.suggest_agents("build and test and review and fix bugs")
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i]['confidence'] >= suggestions[i + 1]['confidence']

    def test_loaded_flag_reflects_agent_availability(self, manager):
        suggestions = manager.suggest_agents("debug this error", limit=5)
        for s in suggestions:
            if s['agent_name'] in manager.agents:
                assert s['loaded'] is True


class TestRecommendAgentBackwardCompat:
    """Ensure recommend_agent() still works after refactoring."""

    def test_returns_agent_for_api_task(self, manager):
        result = manager.recommend_agent("Create a REST API endpoint")
        assert result is not None
        assert isinstance(result, AgentMetadata)

    def test_returns_agent_for_debug_task(self, manager):
        result = manager.recommend_agent("Fix this crash bug error")
        assert result is not None
        assert result.name == 'debug-detective'

    def test_returns_agent_for_test_task(self, manager):
        result = manager.recommend_agent("Write comprehensive tests")
        assert result is not None
        assert result.name == 'testing-stability-expert'

    def test_returns_none_for_gibberish(self, manager):
        result = manager.recommend_agent("xyzzy foobar bazzle")
        assert result is None

    def test_returns_none_for_empty(self, manager):
        result = manager.recommend_agent("")
        assert result is None


class TestScoreAgents:
    """Test the internal _score_agents() method."""

    def test_scores_are_sorted_descending(self, manager):
        scored = manager._score_agents("build an api and test it and debug errors")
        if len(scored) > 1:
            for i in range(len(scored) - 1):
                assert scored[i]['confidence'] >= scored[i + 1]['confidence']

    def test_strong_keywords_boost_score(self, manager):
        """Strong keywords should produce higher confidence."""
        weak = manager._score_agents("fix something")
        strong = manager._score_agents("debug the root cause of the stack trace")
        
        weak_debug = next((s for s in weak if s['name'] == 'debug-detective'), None)
        strong_debug = next((s for s in strong if s['name'] == 'debug-detective'), None)
        
        if weak_debug and strong_debug:
            assert strong_debug['confidence'] >= weak_debug['confidence']

    def test_no_matches_returns_empty(self, manager):
        scored = manager._score_agents("zzzzz qqqqq wwwww")
        assert scored == []
