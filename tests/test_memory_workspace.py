"""
Tests for src/memory_workspace.py — per-agent Memory Workspace.

Covers:
- MemoryEntry dataclass + serialisation round-trip
- MemoryWorkspace: add, get_history, get_summary, update_summary
- MemoryWorkspace: compact, auto_compact
- MemoryWorkspace: save/load persistence
- MemoryWorkspace: clear and search
- WorkspaceManager: get_workspace, list_workspaces, delete_workspace
"""

import json
import os
from datetime import datetime
from typing import List

import pytest

from src.memory_workspace import (
    MemoryEntry,
    MemoryWorkspace,
    WorkspaceManager,
    workspace_manager,
)


# ---------------------------------------------------------------------------
# MemoryEntry
# ---------------------------------------------------------------------------

class TestMemoryEntry:
    """Validate MemoryEntry dataclass and (de)serialisation."""

    def test_default_creation(self):
        """MemoryEntry can be created with role and content only."""
        entry = MemoryEntry(role="user", content="Hello!")
        assert entry.role == "user"
        assert entry.content == "Hello!"
        assert isinstance(entry.timestamp, datetime)
        assert entry.metadata == {}

    def test_to_dict(self):
        """to_dict produces a JSON-serialisable dict with all fields."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        entry = MemoryEntry(
            role="assistant",
            content="Hi there",
            timestamp=ts,
            metadata={"token_count": 5},
        )
        d = entry.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Hi there"
        assert d["timestamp"] == ts.isoformat()
        assert d["metadata"] == {"token_count": 5}

    def test_from_dict_round_trip(self):
        """from_dict(to_dict()) recreates an equivalent entry."""
        original = MemoryEntry(
            role="user",
            content="Test message",
            metadata={"source": "test"},
        )
        restored = MemoryEntry.from_dict(original.to_dict())
        assert restored.role == original.role
        assert restored.content == original.content
        assert restored.metadata == original.metadata

    def test_from_dict_handles_missing_timestamp(self):
        """from_dict falls back to utcnow when timestamp is absent."""
        entry = MemoryEntry.from_dict({"role": "user", "content": "hi"})
        assert isinstance(entry.timestamp, datetime)

    def test_from_dict_handles_bad_timestamp(self):
        """from_dict falls back to utcnow for un-parseable timestamp strings."""
        entry = MemoryEntry.from_dict(
            {"role": "user", "content": "hi", "timestamp": "not-a-date"}
        )
        assert isinstance(entry.timestamp, datetime)


# ---------------------------------------------------------------------------
# MemoryWorkspace — basic operations
# ---------------------------------------------------------------------------

class TestMemoryWorkspaceBasic:
    """Test core MemoryWorkspace operations."""

    def test_add_entry(self, tmp_path):
        """add() appends an entry to the history."""
        ws = MemoryWorkspace("agent1", workspace_dir=str(tmp_path))
        entry = ws.add("user", "Hello!")
        assert isinstance(entry, MemoryEntry)
        assert entry.role == "user"
        assert entry.content == "Hello!"
        assert len(ws.get_history()) == 1

    def test_get_history_returns_all(self, tmp_path):
        """get_history() without argument returns all entries."""
        ws = MemoryWorkspace("agent2", workspace_dir=str(tmp_path))
        ws.add("user", "msg1")
        ws.add("assistant", "msg2")
        ws.add("user", "msg3")
        history = ws.get_history()
        assert len(history) == 3

    def test_get_history_last_n(self, tmp_path):
        """get_history(last_n) returns only the n most recent entries."""
        ws = MemoryWorkspace("agent3", workspace_dir=str(tmp_path))
        for i in range(10):
            ws.add("user", f"message {i}")
        recent = ws.get_history(last_n=3)
        assert len(recent) == 3
        assert recent[-1].content == "message 9"

    def test_get_summary_empty_initially(self, tmp_path):
        """A new workspace has an empty summary."""
        ws = MemoryWorkspace("agent4", workspace_dir=str(tmp_path))
        assert ws.get_summary() == ""

    def test_update_summary(self, tmp_path):
        """update_summary sets and retrieves the summary string."""
        ws = MemoryWorkspace("agent5", workspace_dir=str(tmp_path))
        ws.update_summary("Previous session covered X and Y.")
        assert ws.get_summary() == "Previous session covered X and Y."

    def test_clear_resets_history_and_summary(self, tmp_path):
        """clear() empties both history and summary in memory."""
        ws = MemoryWorkspace("agent6", workspace_dir=str(tmp_path))
        ws.add("user", "Something")
        ws.update_summary("Old summary")
        ws.clear()
        assert ws.get_history() == []
        assert ws.get_summary() == ""

    def test_add_with_metadata(self, tmp_path):
        """add() stores metadata on the entry."""
        ws = MemoryWorkspace("agent7", workspace_dir=str(tmp_path))
        entry = ws.add("tool", "result", metadata={"tool_name": "search"})
        assert entry.metadata == {"tool_name": "search"}


# ---------------------------------------------------------------------------
# MemoryWorkspace — search
# ---------------------------------------------------------------------------

class TestMemoryWorkspaceSearch:
    """Test substring search over history."""

    def test_search_finds_matching_entries(self, tmp_path):
        """search() returns entries whose content contains the query."""
        ws = MemoryWorkspace("search1", workspace_dir=str(tmp_path))
        ws.add("user", "Tell me about Python")
        ws.add("assistant", "Python is a programming language")
        ws.add("user", "What about Java?")
        results = ws.search("Python")
        assert len(results) == 2

    def test_search_is_case_insensitive(self, tmp_path):
        """search() matches regardless of case."""
        ws = MemoryWorkspace("search2", workspace_dir=str(tmp_path))
        ws.add("user", "HELLO world")
        results = ws.search("hello")
        assert len(results) == 1

    def test_search_top_k_limit(self, tmp_path):
        """search() respects the top_k limit."""
        ws = MemoryWorkspace("search3", workspace_dir=str(tmp_path))
        for i in range(10):
            ws.add("user", f"keyword message {i}")
        results = ws.search("keyword", top_k=3)
        assert len(results) == 3

    def test_search_no_results(self, tmp_path):
        """search() returns empty list when no entries match."""
        ws = MemoryWorkspace("search4", workspace_dir=str(tmp_path))
        ws.add("user", "unrelated content")
        results = ws.search("xyz_not_found")
        assert results == []

    def test_search_returns_most_recent_first(self, tmp_path):
        """search() returns matching entries most-recent first."""
        ws = MemoryWorkspace("search5", workspace_dir=str(tmp_path))
        ws.add("user", "needle first")
        ws.add("user", "needle second")
        ws.add("user", "needle third")
        results = ws.search("needle")
        assert results[0].content == "needle third"


# ---------------------------------------------------------------------------
# MemoryWorkspace — compaction
# ---------------------------------------------------------------------------

class TestMemoryWorkspaceCompaction:
    """Test compact() and auto_compact() behaviour."""

    def _fill(
        self, ws: MemoryWorkspace, count: int, prefix: str = "msg"
    ) -> None:
        for i in range(count):
            ws.add("user", f"{prefix} {i}")

    def test_compact_not_triggered_below_threshold(self, tmp_path):
        """compact() is a no-op when history is shorter than the threshold."""
        ws = MemoryWorkspace(
            "compact1",
            workspace_dir=str(tmp_path),
            compaction_threshold=10,
        )
        self._fill(ws, 5)
        ws.compact()
        assert len(ws.get_history()) == 5

    def test_compact_reduces_history(self, tmp_path):
        """compact() shortens history once threshold is reached."""
        ws = MemoryWorkspace(
            "compact2",
            workspace_dir=str(tmp_path),
            compaction_threshold=10,
        )
        self._fill(ws, 12)
        original_len = len(ws.get_history())
        ws.compact()
        assert len(ws.get_history()) < original_len

    def test_compact_creates_summary(self, tmp_path):
        """compact() populates the summary string."""
        ws = MemoryWorkspace(
            "compact3",
            workspace_dir=str(tmp_path),
            compaction_threshold=6,
        )
        self._fill(ws, 8)
        ws.compact()
        assert ws.get_summary() != ""

    def test_compact_with_custom_summarizer(self, tmp_path):
        """compact() uses a custom summarizer function when provided."""
        ws = MemoryWorkspace(
            "compact4",
            workspace_dir=str(tmp_path),
            compaction_threshold=4,
        )
        self._fill(ws, 6)

        def custom_summarizer(entries: List[MemoryEntry]) -> str:
            return f"CUSTOM SUMMARY OF {len(entries)} ENTRIES"

        ws.compact(summarizer_fn=custom_summarizer)
        assert "CUSTOM SUMMARY" in ws.get_summary()

    def test_auto_compact_triggers_at_threshold(self, tmp_path):
        """auto_compact() returns True and compacts once threshold is reached."""
        threshold = 5
        ws = MemoryWorkspace(
            "auto1",
            workspace_dir=str(tmp_path),
            compaction_threshold=threshold,
        )
        self._fill(ws, threshold)
        triggered = ws.auto_compact()
        assert triggered is True

    def test_auto_compact_not_triggered_below_threshold(self, tmp_path):
        """auto_compact() returns False when history is below threshold."""
        ws = MemoryWorkspace(
            "auto2",
            workspace_dir=str(tmp_path),
            compaction_threshold=10,
        )
        self._fill(ws, 3)
        triggered = ws.auto_compact()
        assert triggered is False

    def test_compact_accumulates_summaries(self, tmp_path):
        """Running compact twice accumulates summaries."""
        ws = MemoryWorkspace(
            "compact5",
            workspace_dir=str(tmp_path),
            compaction_threshold=4,
        )
        self._fill(ws, 6)
        ws.compact()
        first_summary = ws.get_summary()
        self._fill(ws, 6)
        ws.compact()
        second_summary = ws.get_summary()
        # Second summary should contain the first
        assert first_summary in second_summary


# ---------------------------------------------------------------------------
# MemoryWorkspace — persistence
# ---------------------------------------------------------------------------

class TestMemoryWorkspacePersistence:
    """Test save/load round-trip."""

    def test_save_creates_file(self, tmp_path):
        """save() writes a JSON file to workspace_dir."""
        ws = MemoryWorkspace("persist1", workspace_dir=str(tmp_path))
        ws.add("user", "Hello")
        ws.save()
        expected_file = tmp_path / "persist1.json"
        assert expected_file.exists()

    def test_load_restores_history(self, tmp_path):
        """load() restores previously saved history."""
        ws = MemoryWorkspace("persist2", workspace_dir=str(tmp_path))
        ws.add("user", "Remember me")
        ws.add("assistant", "Of course!")
        ws.update_summary("A nice chat")
        ws.save()

        ws2 = MemoryWorkspace("persist2", workspace_dir=str(tmp_path))
        history = ws2.get_history()
        assert len(history) == 2
        assert history[0].content == "Remember me"
        assert ws2.get_summary() == "A nice chat"

    def test_load_nonexistent_file_starts_fresh(self, tmp_path):
        """load() is a no-op when the file does not exist."""
        ws = MemoryWorkspace("no_file", workspace_dir=str(tmp_path))
        assert ws.get_history() == []
        assert ws.get_summary() == ""

    def test_load_corrupt_file_starts_fresh(self, tmp_path):
        """load() recovers gracefully from a corrupt JSON file."""
        file_path = tmp_path / "corrupt.json"
        file_path.write_text("{this is not valid json", encoding="utf-8")
        ws = MemoryWorkspace("corrupt", workspace_dir=str(tmp_path))
        assert ws.get_history() == []

    def test_save_and_load_with_metadata(self, tmp_path):
        """Metadata is preserved through a save/load cycle."""
        ws = MemoryWorkspace("meta_ws", workspace_dir=str(tmp_path))
        ws.add("tool", "output", metadata={"tool": "calculator", "result": 42})
        ws.save()

        ws2 = MemoryWorkspace("meta_ws", workspace_dir=str(tmp_path))
        entry = ws2.get_history()[0]
        assert entry.metadata["tool"] == "calculator"
        assert entry.metadata["result"] == 42


# ---------------------------------------------------------------------------
# WorkspaceManager
# ---------------------------------------------------------------------------

class TestWorkspaceManager:
    """Test WorkspaceManager factory and lifecycle methods."""

    def test_get_workspace_creates_new(self, tmp_path):
        """get_workspace() creates a workspace for an unknown agent_id."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        ws = manager.get_workspace("agent-new")
        assert isinstance(ws, MemoryWorkspace)
        assert ws.agent_id == "agent-new"

    def test_get_workspace_returns_same_instance(self, tmp_path):
        """get_workspace() returns the same instance on subsequent calls."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        ws1 = manager.get_workspace("agent-cached")
        ws2 = manager.get_workspace("agent-cached")
        assert ws1 is ws2

    def test_list_workspaces_empty(self, tmp_path):
        """list_workspaces() returns empty list when nothing exists."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        assert manager.list_workspaces() == []

    def test_list_workspaces_includes_in_memory(self, tmp_path):
        """list_workspaces() includes workspaces created in memory."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        manager.get_workspace("agent-a")
        manager.get_workspace("agent-b")
        ids = manager.list_workspaces()
        assert "agent-a" in ids
        assert "agent-b" in ids

    def test_list_workspaces_includes_disk_files(self, tmp_path):
        """list_workspaces() discovers persisted workspace files on disk."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        ws = manager.get_workspace("disk-agent")
        ws.save()
        # Create a fresh manager that hasn't loaded anything into memory
        manager2 = WorkspaceManager(workspace_dir=str(tmp_path))
        ids = manager2.list_workspaces()
        assert "disk-agent" in ids

    def test_delete_workspace_removes_from_memory(self, tmp_path):
        """delete_workspace() removes the cached workspace."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        manager.get_workspace("del-agent")
        removed = manager.delete_workspace("del-agent")
        assert removed is True
        # A subsequent get creates a fresh instance
        ws2 = manager.get_workspace("del-agent")
        assert ws2.get_history() == []

    def test_delete_workspace_removes_file(self, tmp_path):
        """delete_workspace() removes the on-disk JSON file."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        ws = manager.get_workspace("file-del")
        ws.add("user", "data")
        ws.save()
        file_path = tmp_path / "file-del.json"
        assert file_path.exists()
        manager.delete_workspace("file-del")
        assert not file_path.exists()

    def test_delete_nonexistent_workspace_returns_false(self, tmp_path):
        """delete_workspace() returns False for unknown agent IDs."""
        manager = WorkspaceManager(workspace_dir=str(tmp_path))
        removed = manager.delete_workspace("ghost-agent")
        assert removed is False

    def test_global_singleton_exists(self):
        """The module-level workspace_manager singleton is accessible."""
        from src.memory_workspace import workspace_manager as wm
        assert isinstance(wm, WorkspaceManager)
