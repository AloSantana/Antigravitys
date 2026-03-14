"""
Per-agent Memory Workspace with session compaction.

Each agent gets an isolated :class:`MemoryWorkspace` that persists
conversation history to disk and automatically compacts old entries
into a rolling summary when the history grows beyond a configurable
threshold.

Example::

    from src.memory_workspace import workspace_manager

    ws = workspace_manager.get_workspace("my-agent")
    ws.add("user", "Hello!")
    ws.add("assistant", "Hi there!")
    await ws.auto_compact()
    ws.save()

    results = ws.search("hello")
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MemoryEntry:
    """A single entry in the conversation history.

    Attributes:
        role: Speaker role, e.g. ``"user"`` or ``"assistant"``.
        content: Text content of the message.
        timestamp: UTC timestamp when the entry was created.
        metadata: Arbitrary key/value pairs attached to this entry.
    """

    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a JSON-compatible dictionary."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MemoryEntry":
        """Deserialise from a dictionary produced by :meth:`to_dict`.

        Args:
            d: Source dictionary.

        Returns:
            A new :class:`MemoryEntry` instance.
        """
        ts_raw = d.get("timestamp")
        if isinstance(ts_raw, str):
            try:
                ts = datetime.fromisoformat(ts_raw)
            except ValueError:
                ts = datetime.now(timezone.utc)
        elif isinstance(ts_raw, datetime):
            ts = ts_raw
        else:
            ts = datetime.now(timezone.utc)

        return cls(
            role=d.get("role", "unknown"),
            content=d.get("content", ""),
            timestamp=ts,
            metadata=d.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------

class MemoryWorkspace:
    """Per-agent persistent memory with automatic compaction.

    History is written to ``{workspace_dir}/{agent_id}.json`` on every
    :meth:`save` call.

    Args:
        agent_id: Unique identifier for the agent that owns this workspace.
        workspace_dir: Directory under which workspace files are stored.
        max_history: Absolute upper bound on stored entries (older entries
            are evicted when this limit is hit during :meth:`compact`).
        compaction_threshold: :meth:`auto_compact` will trigger compaction
            once the history length reaches this value.
    """

    def __init__(
        self,
        agent_id: str,
        workspace_dir: str = ".memory",
        max_history: int = 100,
        compaction_threshold: int = 80,
    ) -> None:
        self.agent_id = agent_id
        self.workspace_dir = workspace_dir
        self.max_history = max_history
        self.compaction_threshold = compaction_threshold

        self._history: List[MemoryEntry] = []
        self._summary: str = ""

        # Attempt to load existing workspace from disk
        self.load()

    # ------------------------------------------------------------------
    # Path helper
    # ------------------------------------------------------------------

    @property
    def _file_path(self) -> str:
        """Absolute path to the workspace JSON file."""
        return os.path.join(self.workspace_dir, f"{self.agent_id}.json")

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """Append a new entry to the workspace history.

        Args:
            role: Speaker role (e.g. ``"user"``, ``"assistant"``).
            content: Message content.
            metadata: Optional metadata dictionary.

        Returns:
            The newly created :class:`MemoryEntry`.
        """
        entry = MemoryEntry(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self._history.append(entry)
        return entry

    def get_history(
        self, last_n: Optional[int] = None
    ) -> List[MemoryEntry]:
        """Return history entries, optionally limited to the most recent *last_n*.

        Args:
            last_n: When provided, return only the last *last_n* entries.

        Returns:
            List of :class:`MemoryEntry` objects (oldest first).
        """
        if last_n is not None:
            return list(self._history[-last_n:])
        return list(self._history)

    def get_summary(self) -> str:
        """Return the current compaction summary string.

        Returns:
            Summary text, or an empty string if none has been created yet.
        """
        return self._summary

    def update_summary(self, summary: str) -> None:
        """Replace the compaction summary.

        Args:
            summary: New summary text.
        """
        self._summary = summary

    # ------------------------------------------------------------------
    # Compaction
    # ------------------------------------------------------------------

    def _default_summarizer(self, entries: List[MemoryEntry]) -> str:
        """Built-in fallback summarizer.

        Concatenates the first five entries into a short pipe-delimited
        string.

        Args:
            entries: Entries to summarise.

        Returns:
            Summary string.
        """
        parts = [
            f"{e.role}: {e.content[:100]}"
            for e in entries[:5]
        ]
        return " | ".join(parts)

    def compact(
        self,
        summarizer_fn: Optional[Callable[[List[MemoryEntry]], str]] = None,
    ) -> str:
        """Compact old history entries into a rolling summary.

        Entries beyond the most recent ``compaction_threshold`` items are
        summarised and removed.  The resulting summary is prepended to any
        existing summary text.

        Args:
            summarizer_fn: Optional callable that receives a list of
                :class:`MemoryEntry` objects and returns a summary string.
                Defaults to :meth:`_default_summarizer`.

        Returns:
            The updated summary string.
        """
        if len(self._history) < self.compaction_threshold:
            return self._summary

        # Determine split point: keep the most recent entries
        keep_count = self.compaction_threshold // 2
        old_entries = self._history[:-keep_count]
        recent_entries = self._history[-keep_count:]

        summarizer = summarizer_fn or self._default_summarizer
        new_summary = summarizer(old_entries)

        if self._summary:
            self._summary = f"{self._summary}\n\n[Compacted]: {new_summary}"
        else:
            self._summary = new_summary

        self._history = recent_entries
        logger.debug(
            "Workspace '%s' compacted %d entries into summary",
            self.agent_id,
            len(old_entries),
        )
        return self._summary

    def auto_compact(
        self,
        summarizer_fn: Optional[Callable[[List[MemoryEntry]], str]] = None,
    ) -> bool:
        """Check the compaction threshold and compact if needed.

        Args:
            summarizer_fn: Optional custom summarizer (see :meth:`compact`).

        Returns:
            ``True`` if compaction was performed, ``False`` otherwise.
        """
        if len(self._history) >= self.compaction_threshold:
            self.compact(summarizer_fn=summarizer_fn)
            return True
        return False

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist the current workspace state to disk as JSON."""
        os.makedirs(self.workspace_dir, exist_ok=True)
        payload = {
            "agent_id": self.agent_id,
            "summary": self._summary,
            "history": [e.to_dict() for e in self._history],
        }
        try:
            with open(self._file_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.error(
                "Failed to save workspace '%s' to %s: %s",
                self.agent_id,
                self._file_path,
                exc,
            )

    def load(self) -> None:
        """Load workspace state from disk (no-op if file does not exist)."""
        if not os.path.exists(self._file_path):
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)

            self._summary = payload.get("summary", "")
            raw_history = payload.get("history", [])
            self._history = [
                MemoryEntry.from_dict(e) for e in raw_history
            ]
            logger.debug(
                "Loaded workspace '%s' (%d entries)",
                self.agent_id,
                len(self._history),
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Could not load workspace '%s' from %s: %s – starting fresh",
                self.agent_id,
                self._file_path,
                exc,
            )
            self._history = []
            self._summary = ""

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear all history entries and the summary (in-memory only)."""
        self._history.clear()
        self._summary = ""

    def search(
        self, query: str, top_k: int = 5
    ) -> List[MemoryEntry]:
        """Simple keyword search over entry content.

        Args:
            query: Search string (case-insensitive substring match).
            top_k: Maximum number of results to return.

        Returns:
            Up to *top_k* matching entries (most recent first).
        """
        query_lower = query.lower()
        matches = [
            e for e in reversed(self._history)
            if query_lower in e.content.lower()
        ]
        return matches[:top_k]


# ---------------------------------------------------------------------------
# Workspace manager
# ---------------------------------------------------------------------------

class WorkspaceManager:
    """Factory and registry for :class:`MemoryWorkspace` instances.

    Ensures that a single workspace object is created per agent ID and
    reused across calls.

    Example::

        manager = WorkspaceManager(workspace_dir="/tmp/workspaces")
        ws = manager.get_workspace("agent-42")
    """

    def __init__(self, workspace_dir: str = ".memory") -> None:
        self.workspace_dir = workspace_dir
        self._workspaces: Dict[str, MemoryWorkspace] = {}

    def get_workspace(self, agent_id: str) -> MemoryWorkspace:
        """Return the workspace for *agent_id*, creating it if necessary.

        Args:
            agent_id: Unique agent identifier.

        Returns:
            The :class:`MemoryWorkspace` for the given agent.
        """
        if agent_id not in self._workspaces:
            self._workspaces[agent_id] = MemoryWorkspace(
                agent_id=agent_id,
                workspace_dir=self.workspace_dir,
            )
        return self._workspaces[agent_id]

    def list_workspaces(self) -> List[str]:
        """Return agent IDs of all workspaces known to this manager.

        Includes both in-memory and on-disk workspaces.

        Returns:
            Sorted list of agent ID strings.
        """
        # Collect IDs from in-memory cache
        ids = set(self._workspaces.keys())

        # Also scan the workspace directory for persisted files
        if os.path.isdir(self.workspace_dir):
            for filename in os.listdir(self.workspace_dir):
                if filename.endswith(".json"):
                    ids.add(filename[:-5])

        return sorted(ids)

    def delete_workspace(self, agent_id: str) -> bool:
        """Delete a workspace both from memory and disk.

        Args:
            agent_id: Unique agent identifier.

        Returns:
            ``True`` if the workspace existed (in memory or on disk) and was
            removed, ``False`` if it was not found.
        """
        removed = False

        # Remove from in-memory cache
        if agent_id in self._workspaces:
            del self._workspaces[agent_id]
            removed = True

        # Remove persisted file
        file_path = os.path.join(self.workspace_dir, f"{agent_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed = True
            except OSError as exc:
                logger.error(
                    "Failed to delete workspace file %s: %s", file_path, exc
                )

        return removed


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Global default workspace manager.
workspace_manager: WorkspaceManager = WorkspaceManager()
