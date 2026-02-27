"""
Comprehensive tests for the enhanced memory system.

Tests:
- JSON persistence with legacy format support
- Context window management
- Summarization support
- Backward compatibility
- Memory operations (add, get, clear, update)
"""

import json
import pytest

from src.memory import MemoryManager


# =============================================================================
# Basic Memory Operations Tests
# =============================================================================

class TestMemoryBasicOperations:
    """Test basic memory operations."""
    
    def test_memory_manager_initialization(self, tmp_path):
        """Test MemoryManager initialization."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.memory_file == str(memory_file)
        assert manager._memory == {"summary": "", "history": []}
    
    def test_add_entry(self, tmp_path):
        """Test adding entries to memory."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Hello, agent!")
        manager.add_entry("agent", "Hello! How can I help you?")
        
        history = manager.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello, agent!"
        assert history[1]["role"] == "agent"
        assert history[1]["content"] == "Hello! How can I help you?"
    
    def test_add_entry_with_metadata(self, tmp_path):
        """Test adding entries with metadata."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        metadata = {"tool": "search", "confidence": 0.95}
        manager.add_entry("agent", "Found relevant information", metadata)
        
        history = manager.get_history()
        assert len(history) == 1
        assert history[0]["metadata"] == metadata
    
    def test_get_history(self, tmp_path):
        """Test getting full conversation history."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Message 1")
        manager.add_entry("agent", "Response 1")
        manager.add_entry("user", "Message 2")
        
        history = manager.get_history()
        assert len(history) == 3
        assert all(isinstance(entry, dict) for entry in history)
        assert all("role" in entry and "content" in entry for entry in history)
    
    def test_clear_memory(self, tmp_path):
        """Test clearing memory."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Test message")
        manager.update_summary("Test summary")
        
        manager.clear_memory()
        
        assert manager.get_history() == []
        assert manager.get_summary() == ""
        
        # Verify file is updated
        with open(memory_file, 'r') as f:
            data = json.load(f)
        assert data == {"summary": "", "history": []}


# =============================================================================
# Persistence Tests
# =============================================================================

class TestMemoryPersistence:
    """Test memory persistence to JSON files."""
    
    def test_save_memory(self, tmp_path):
        """Test saving memory to file."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Test message")
        manager.save_memory()
        
        # Verify file exists and contains correct data
        assert memory_file.exists()
        with open(memory_file, 'r') as f:
            data = json.load(f)
        
        assert "history" in data
        assert len(data["history"]) == 1
        assert data["history"][0]["content"] == "Test message"
    
    def test_load_memory_new_format(self, tmp_path):
        """Test loading memory from new format (dict with summary and history)."""
        memory_file = tmp_path / "test_memory.json"
        
        # Write new format
        test_data = {
            "summary": "This is a summary",
            "history": [
                {"role": "user", "content": "Hello", "metadata": {}, "timestamp": None}
            ]
        }
        with open(memory_file, 'w') as f:
            json.dump(test_data, f)
        
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.get_summary() == "This is a summary"
        assert len(manager.get_history()) == 1
        assert manager.get_history()[0]["content"] == "Hello"
    
    def test_load_memory_legacy_format(self, tmp_path):
        """Test loading memory from legacy format (list of entries)."""
        memory_file = tmp_path / "test_memory.json"
        
        # Write legacy format (list)
        legacy_data = [
            {"role": "user", "content": "Legacy message 1"},
            {"role": "agent", "content": "Legacy response 1"}
        ]
        with open(memory_file, 'w') as f:
            json.dump(legacy_data, f)
        
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Should convert to new format
        assert manager.get_summary() == ""
        assert len(manager.get_history()) == 2
        assert manager.get_history()[0]["content"] == "Legacy message 1"
    
    def test_load_memory_invalid_json(self, tmp_path):
        """Test loading memory from invalid JSON."""
        memory_file = tmp_path / "test_memory.json"
        
        # Write invalid JSON
        with open(memory_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Should start fresh without crashing
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.get_history() == []
        assert manager.get_summary() == ""
    
    def test_load_memory_unknown_format(self, tmp_path):
        """Test loading memory from unknown format."""
        memory_file = tmp_path / "test_memory.json"
        
        # Write unexpected format (string)
        with open(memory_file, 'w') as f:
            json.dump("unexpected string", f)
        
        # Should start fresh
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.get_history() == []
        assert manager.get_summary() == ""
    
    def test_memory_file_creation(self, tmp_path):
        """Test that memory file is created if it doesn't exist."""
        memory_file = tmp_path / "subdir" / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Test")
        
        # File and directory should be created
        assert memory_file.exists()
        assert memory_file.parent.exists()
    
    def test_persistence_across_instances(self, tmp_path):
        """Test that memory persists across manager instances."""
        memory_file = tmp_path / "test_memory.json"
        
        # First instance
        manager1 = MemoryManager(memory_file=str(memory_file))
        manager1.add_entry("user", "Persisted message")
        manager1.update_summary("Persisted summary")
        
        # Second instance
        manager2 = MemoryManager(memory_file=str(memory_file))
        
        assert len(manager2.get_history()) == 1
        assert manager2.get_history()[0]["content"] == "Persisted message"
        assert manager2.get_summary() == "Persisted summary"


# =============================================================================
# Summary Management Tests
# =============================================================================

class TestMemorySummary:
    """Test memory summary functionality."""
    
    def test_get_summary_empty(self, tmp_path):
        """Test getting summary when empty."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.get_summary() == ""
    
    def test_update_summary(self, tmp_path):
        """Test updating summary."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.update_summary("This is a conversation summary")
        
        assert manager.get_summary() == "This is a conversation summary"
        
        # Verify persistence
        with open(memory_file, 'r') as f:
            data = json.load(f)
        assert data["summary"] == "This is a conversation summary"
    
    def test_update_summary_multiple_times(self, tmp_path):
        """Test updating summary multiple times."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.update_summary("Summary 1")
        manager.update_summary("Summary 2")
        manager.update_summary("Summary 3")
        
        assert manager.get_summary() == "Summary 3"
    
    def test_summary_with_unicode(self, tmp_path):
        """Test summary with Unicode characters."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        summary = "会話の要約: テスト用の文字列 🎉"
        manager.update_summary(summary)
        
        assert manager.get_summary() == summary


# =============================================================================
# Context Window Tests
# =============================================================================

class TestMemoryContextWindow:
    """Test context window management."""
    
    def test_get_context_window_empty(self, tmp_path):
        """Test getting context window when memory is empty."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        context = manager.get_context_window()
        
        assert context == []
    
    def test_get_context_window_with_system_prompt(self, tmp_path):
        """Test getting context window with system prompt."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Hello")
        
        context = manager.get_context_window(system_prompt="You are a helpful assistant")
        
        assert len(context) == 2
        assert context[0]["role"] == "system"
        assert context[0]["content"] == "You are a helpful assistant"
        assert context[1]["role"] == "user"
    
    def test_get_context_window_within_limit(self, tmp_path):
        """Test context window when messages are within limit."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add 5 messages (less than default max_messages=20)
        for i in range(5):
            manager.add_entry("user", f"Message {i}")
        
        context = manager.get_context_window(max_messages=20)
        
        # Should return all messages
        assert len(context) == 5
    
    def test_get_context_window_exceeds_limit(self, tmp_path):
        """Test context window when messages exceed limit."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add 30 messages
        for i in range(30):
            manager.add_entry("user", f"Message {i}")
        
        context = manager.get_context_window(max_messages=20)
        
        # Should return system message with summary + 20 recent messages
        assert len(context) == 21  # 1 summary + 20 recent
        assert context[0]["role"] == "system"
        assert "[Previous conversation summary]" in context[0]["content"]
        
        # Last 20 messages should be recent ones
        assert context[-1]["content"] == "Message 29"
        assert context[-20]["content"] == "Message 10"
    
    def test_get_context_window_with_custom_summarizer(self, tmp_path):
        """Test context window with custom summarizer."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add messages that exceed limit
        for i in range(15):
            manager.add_entry("user", f"Message {i}")
        
        # Custom summarizer
        def custom_summarizer(messages):
            return f"Custom summary of {len(messages)} messages"
        
        context = manager.get_context_window(max_messages=10, summarizer=custom_summarizer)
        
        # Should have summary + 10 recent messages
        assert len(context) == 11
        assert "Custom summary of 5 messages" in context[0]["content"]
    
    def test_get_context_window_default_summarizer(self, tmp_path):
        """Test context window with default summarizer."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add messages
        for i in range(10):
            manager.add_entry("user", f"Message {i}")
        
        context = manager.get_context_window(max_messages=5)
        
        # Should use default summarizer
        assert len(context) == 6  # 1 summary + 5 recent
        assert context[0]["role"] == "system"
        assert "user:" in context[0]["content"]  # Default format
    
    def test_context_window_combines_with_existing_summary(self, tmp_path):
        """Test that context window combines with existing summary."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Set existing summary
        manager.update_summary("Existing summary from previous conversations")
        
        # Add messages that exceed limit
        for i in range(15):
            manager.add_entry("user", f"Message {i}")
        
        context = manager.get_context_window(max_messages=10)
        
        # Summary should contain both old and new
        summary_content = context[0]["content"]
        assert "Existing summary from previous conversations" in summary_content
        assert "[Recent interactions]" in summary_content
    
    def test_context_window_updates_stored_summary(self, tmp_path):
        """Test that context window updates stored summary."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add messages that exceed limit
        for i in range(15):
            manager.add_entry("user", f"Message {i}")
        
        # Initial summary is empty
        assert manager.get_summary() == ""
        
        # Get context window (should create summary)
        manager.get_context_window(max_messages=10)
        
        # Summary should be updated
        assert manager.get_summary() != ""
        assert "user:" in manager.get_summary()


# =============================================================================
# Backward Compatibility Tests
# =============================================================================

class TestMemoryBackwardCompatibility:
    """Test backward compatibility with older memory formats."""
    
    def test_migrate_from_list_to_dict(self, tmp_path):
        """Test automatic migration from list format to dict format."""
        memory_file = tmp_path / "test_memory.json"
        
        # Create legacy list format
        legacy_data = [
            {"role": "user", "content": "Old message 1"},
            {"role": "agent", "content": "Old response 1"}
        ]
        with open(memory_file, 'w') as f:
            json.dump(legacy_data, f)
        
        # Load with new manager
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add new entry
        manager.add_entry("user", "New message")
        
        # Should be in new format
        with open(memory_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "summary" in data
        assert "history" in data
        assert len(data["history"]) == 3
    
    def test_handle_missing_fields_in_entries(self, tmp_path):
        """Test handling entries with missing fields."""
        memory_file = tmp_path / "test_memory.json"
        
        # Create data with minimal fields
        test_data = {
            "summary": "",
            "history": [
                {"role": "user", "content": "Test"},
                # Missing metadata and timestamp - should still work
            ]
        }
        with open(memory_file, 'w') as f:
            json.dump(test_data, f)
        
        manager = MemoryManager(memory_file=str(memory_file))
        history = manager.get_history()
        
        assert len(history) == 1
        assert history[0]["content"] == "Test"
    
    def test_empty_file_handling(self, tmp_path):
        """Test handling empty memory file."""
        memory_file = tmp_path / "test_memory.json"
        memory_file.write_text("")
        
        # Should handle gracefully
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.get_history() == []
        assert manager.get_summary() == ""


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestMemoryEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_long_messages(self, tmp_path):
        """Test handling very long messages."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        long_message = "x" * 100000  # 100KB message
        manager.add_entry("user", long_message)
        
        history = manager.get_history()
        assert len(history[0]["content"]) == 100000
    
    def test_empty_content(self, tmp_path):
        """Test adding entries with empty content."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "")
        
        history = manager.get_history()
        assert len(history) == 1
        assert history[0]["content"] == ""
    
    def test_special_characters_in_content(self, tmp_path):
        """Test content with special characters."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        special_content = "Test\n\t\"quotes\" and 'apostrophes' \\ backslash"
        manager.add_entry("user", special_content)
        
        # Should handle JSON escaping correctly
        history = manager.get_history()
        assert history[0]["content"] == special_content
    
    def test_unicode_content(self, tmp_path):
        """Test content with Unicode characters."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        unicode_content = "Hello 世界 🌍 Привет مرحبا"
        manager.add_entry("user", unicode_content)
        
        history = manager.get_history()
        assert history[0]["content"] == unicode_content
    
    def test_concurrent_access_protection(self, tmp_path):
        """Test that file operations are safe."""
        memory_file = tmp_path / "test_memory.json"
        
        manager1 = MemoryManager(memory_file=str(memory_file))
        manager2 = MemoryManager(memory_file=str(memory_file))
        
        # Both managers operate on same file
        manager1.add_entry("user", "Message 1")
        manager2.add_entry("user", "Message 2")
        
        # Last write wins
        manager2_history = manager2.get_history()
        assert len(manager2_history) == 1
    
    def test_none_memory_file(self):
        """Test using default memory file path."""
        # When no memory_file is provided, it should use the default from settings
        manager = MemoryManager()
        
        # Should have some memory file path (either default or from settings)
        assert manager.memory_file
        assert isinstance(manager.memory_file, str)


# =============================================================================
# Integration Tests
# =============================================================================

class TestMemoryIntegration:
    """Integration tests for memory system."""
    
    def test_full_conversation_flow(self, tmp_path):
        """Test a full conversation flow."""
        memory_file = tmp_path / "conversation.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Conversation flow
        manager.add_entry("user", "Hello!")
        manager.add_entry("agent", "Hi! How can I help you?")
        manager.add_entry("user", "What's the weather?")
        manager.add_entry("agent", "I can't check real-time weather, but I can help with other tasks.")
        manager.add_entry("user", "Thanks!")
        
        # Get context window
        context = manager.get_context_window(
            system_prompt="You are a helpful assistant",
            max_messages=10
        )
        
        assert len(context) == 6  # 1 system + 5 messages
        assert context[0]["role"] == "system"
        assert context[-1]["content"] == "Thanks!"
    
    def test_memory_with_metadata_tracking(self, tmp_path):
        """Test memory with metadata tracking."""
        memory_file = tmp_path / "test_memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add entries with various metadata
        manager.add_entry("user", "Search for Python", {"intent": "search"})
        manager.add_entry("agent", "Found results", {"tool": "search", "count": 10})
        manager.add_entry("user", "Show the first result", {"intent": "display"})
        
        history = manager.get_history()
        
        assert history[0]["metadata"]["intent"] == "search"
        assert history[1]["metadata"]["tool"] == "search"
        assert history[1]["metadata"]["count"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
