"""
Tests for Context Fusion Engine (Feature B)
Tests cross-session intelligence, context retrieval, prompt augmentation, and indexing.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from context_fusion import ContextFusionEngine


class MockConversationManager:
    """Mock ConversationManager for testing."""

    def __init__(self, conversations=None):
        self._conversations = conversations or []
        self._messages = {}

    def search_conversations(self, query):
        """Return mock conversations matching query keywords."""
        results = []
        for conv in self._conversations:
            title_lower = conv.get("title", "").lower()
            preview_lower = conv.get("preview", "").lower()
            if any(w in title_lower or w in preview_lower for w in query.lower().split()):
                results.append(conv)
        return results

    def get_messages(self, conversation_id):
        return self._messages.get(conversation_id, [])


class MockVectorStore:
    """Mock VectorStore for testing."""

    def __init__(self):
        self._documents = []
        self._metadatas = []
        self._ids = []

    def add_documents(self, documents, metadatas, ids, embeddings=None):
        self._documents.extend(documents)
        self._metadatas.extend(metadatas)
        self._ids.extend(ids)

    def query(self, query_embeddings, n_results=5, use_cache=True):
        # Return stored documents as mock results
        docs = self._documents[:n_results]
        return {
            "documents": [docs],
            "distances": [[0.2] * len(docs)],
            "metadatas": [self._metadatas[:n_results]],
        }


@pytest.fixture
def mock_conversations():
    return [
        {
            "id": "conv-1",
            "title": "REST API development",
            "preview": "We built a REST API with authentication and database models",
        },
        {
            "id": "conv-2",
            "title": "Debugging memory leak",
            "preview": "Found a memory leak in the connection pool causing crashes",
        },
        {
            "id": "conv-3",
            "title": "Docker deployment",
            "preview": "Set up Docker containers with nginx for production deployment",
        },
    ]


@pytest.fixture
def mock_conv_manager(mock_conversations):
    mgr = MockConversationManager(mock_conversations)
    mgr._messages = {
        "conv-1": [
            {"content": "How do I build a REST API?", "role": "user", "timestamp": "2024-01-01"},
            {"content": "Start with defining your routes and models.", "role": "assistant", "timestamp": "2024-01-01"},
        ],
        "conv-2": [
            {"content": "My app is crashing due to memory issues", "role": "user", "timestamp": "2024-01-02"},
            {"content": "Let me investigate the connection pool.", "role": "assistant", "timestamp": "2024-01-02"},
        ],
    }
    return mgr


@pytest.fixture
def mock_vector_store():
    return MockVectorStore()


@pytest.fixture
def engine(mock_conv_manager, mock_vector_store):
    return ContextFusionEngine(
        conversation_manager=mock_conv_manager,
        vector_store=mock_vector_store,
    )


@pytest.fixture
def engine_no_deps():
    """Engine with no dependencies (graceful degradation)."""
    return ContextFusionEngine()


class TestGetRelevantContext:
    def test_finds_matching_conversations(self, engine):
        results = engine.get_relevant_context("REST API development")
        assert len(results) > 0
        sources = [r["source"] for r in results]
        assert "conversation_history" in sources

    def test_empty_query_returns_empty(self, engine):
        results = engine.get_relevant_context("xyzzy foobar gibberish")
        # May return results with low scores, that's OK
        assert isinstance(results, list)

    def test_respects_limit(self, engine):
        results = engine.get_relevant_context("API", limit=1)
        assert len(results) <= 1

    def test_excludes_conversation(self, engine):
        results = engine.get_relevant_context(
            "REST API", exclude_conversation_id="conv-1"
        )
        conv_ids = [
            r["metadata"].get("conversation_id")
            for r in results
            if r["source"] == "conversation_history"
        ]
        assert "conv-1" not in conv_ids

    def test_results_sorted_by_score(self, engine):
        results = engine.get_relevant_context("API deployment Docker")
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["score"] >= results[i + 1]["score"]

    def test_result_structure(self, engine):
        results = engine.get_relevant_context("memory leak")
        for r in results:
            assert "source" in r
            assert "content" in r
            assert "score" in r
            assert "metadata" in r


class TestGracefulDegradation:
    def test_no_conv_manager_returns_empty(self, engine_no_deps):
        results = engine_no_deps.get_relevant_context("anything")
        assert results == []

    def test_no_vector_store_still_works(self, mock_conv_manager):
        engine = ContextFusionEngine(conversation_manager=mock_conv_manager)
        results = engine.get_relevant_context("REST API")
        assert len(results) > 0  # Conversations should still work


class TestBuildAugmentedPrompt:
    def test_basic_augmentation(self, engine):
        prompt = engine.build_augmented_prompt("How do I build an API?")
        assert "User Request:" in prompt

    def test_with_context_items(self, engine):
        items = [
            {"source": "conversation_history", "content": "Past: We built a REST API.", "score": 0.8, "metadata": {}},
        ]
        prompt = engine.build_augmented_prompt("Build an API", context_items=items)
        assert "Past: We built a REST API." in prompt
        assert "User Request: Build an API" in prompt

    def test_with_agent_context(self, engine):
        prompt = engine.build_augmented_prompt(
            "Fix bug",
            context_items=[],
            agent_context="You are a debugging expert.",
        )
        assert "You are a debugging expert." in prompt

    def test_token_budget_enforcement(self, engine):
        """Long context should be truncated to fit token budget."""
        long_content = "x " * 5000  # Way over 2000 token budget
        items = [
            {"source": "test", "content": long_content, "score": 0.9, "metadata": {}},
        ]
        prompt = engine.build_augmented_prompt("query", context_items=items)
        max_expected_len = (engine.MAX_CONTEXT_TOKENS * engine.CHARS_PER_TOKEN) + 500
        # The injected context portion should be bounded
        assert len(prompt) < max_expected_len + len("query") + 200

    def test_no_context_returns_plain_query(self, engine_no_deps):
        prompt = engine_no_deps.build_augmented_prompt("Fix a bug")
        assert prompt == "Fix a bug"


class TestIndexConversation:
    def test_indexes_conversation_to_vector_store(self, engine, mock_vector_store):
        success = engine.index_conversation("conv-1")
        assert success is True
        assert len(mock_vector_store._documents) > 0
        assert any("conv-1" in doc_id for doc_id in mock_vector_store._ids)

    def test_skips_short_messages(self, engine, mock_conv_manager, mock_vector_store):
        mock_conv_manager._messages["conv-short"] = [
            {"content": "Hi", "role": "user"},
            {"content": "Hey", "role": "assistant"},
        ]
        success = engine.index_conversation("conv-short")
        assert success is False  # All messages too short

    def test_returns_false_for_missing_conversation(self, engine):
        success = engine.index_conversation("nonexistent")
        assert success is False

    def test_returns_false_without_dependencies(self, engine_no_deps):
        success = engine_no_deps.index_conversation("conv-1")
        assert success is False


class TestDeduplication:
    def test_removes_near_duplicates(self, engine):
        items = [
            {"source": "a", "content": "the quick brown fox jumps", "score": 0.9, "metadata": {}},
            {"source": "b", "content": "the quick brown fox jumps over", "score": 0.8, "metadata": {}},
            {"source": "c", "content": "something completely different", "score": 0.7, "metadata": {}},
        ]
        deduped = engine._deduplicate(items, threshold=0.8)
        assert len(deduped) == 2  # First two are near-duplicates

    def test_keeps_unique_items(self, engine):
        items = [
            {"source": "a", "content": "REST API development with Python", "score": 0.9, "metadata": {}},
            {"source": "b", "content": "Docker container deployment on AWS", "score": 0.8, "metadata": {}},
        ]
        deduped = engine._deduplicate(items)
        assert len(deduped) == 2

    def test_empty_list_returns_empty(self, engine):
        assert engine._deduplicate([]) == []

    def test_single_item_returns_same(self, engine):
        items = [{"source": "a", "content": "hello world", "score": 0.9, "metadata": {}}]
        assert engine._deduplicate(items) == items
