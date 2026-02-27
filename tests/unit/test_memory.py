"""
Unit tests for src.memory module
Tests the MemoryManager class
"""

import pytest
import json


@pytest.mark.unit
class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    def test_initialization_new_file(self, temp_dir):
        """Test MemoryManager creates new memory file."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert manager.memory_file == str(memory_file)
        assert isinstance(manager._memory, list)
        assert len(manager._memory) == 0
    
    def test_initialization_existing_file(self, temp_dir):
        """Test MemoryManager loads existing memory file."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        
        # Create existing memory file
        existing_data = [
            {"role": "user", "content": "Hello", "metadata": {}},
            {"role": "assistant", "content": "Hi", "metadata": {}}
        ]
        memory_file.write_text(json.dumps(existing_data))
        
        manager = MemoryManager(memory_file=str(memory_file))
        
        assert len(manager._memory) == 2
        assert manager._memory == existing_data
    
    def test_initialization_corrupted_file(self, temp_dir):
        """Test MemoryManager handles corrupted JSON file."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "corrupted.json"
        memory_file.write_text("{ invalid json }")
        
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Should start with empty memory
        assert len(manager._memory) == 0
    
    def test_add_entry(self, temp_dir):
        """Test adding entries to memory."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Test message")
        
        assert len(manager._memory) == 1
        assert manager._memory[0]["role"] == "user"
        assert manager._memory[0]["content"] == "Test message"
        assert "metadata" in manager._memory[0]
    
    def test_add_entry_with_metadata(self, temp_dir):
        """Test adding entry with custom metadata."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        metadata = {"timestamp": "2024-01-01", "source": "test"}
        manager.add_entry("assistant", "Response", metadata=metadata)
        
        assert manager._memory[0]["metadata"] == metadata
    
    def test_add_entry_persists(self, temp_dir):
        """Test that add_entry persists to file."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry("user", "Test")
        
        # Verify file exists and contains data
        assert memory_file.exists()
        
        with open(memory_file) as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["content"] == "Test"
    
    def test_get_history(self, temp_dir):
        """Test getting conversation history."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add some entries
        manager.add_entry("user", "Message 1")
        manager.add_entry("assistant", "Response 1")
        manager.add_entry("user", "Message 2")
        
        history = manager.get_history()
        
        assert len(history) == 3
        assert history[0]["content"] == "Message 1"
        assert history[1]["content"] == "Response 1"
        assert history[2]["content"] == "Message 2"
    
    def test_get_history_empty(self, temp_dir):
        """Test getting history when empty."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        history = manager.get_history()
        
        assert history == []
    
    def test_save_memory(self, temp_dir):
        """Test manually saving memory."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add entry without auto-save
        manager._memory.append({"role": "user", "content": "Test", "metadata": {}})
        
        # Manually save
        manager.save_memory()
        
        # Verify saved
        with open(memory_file) as f:
            data = json.load(f)
        
        assert len(data) == 1
    
    def test_clear_memory(self, temp_dir):
        """Test clearing memory."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add entries
        manager.add_entry("user", "Message 1")
        manager.add_entry("assistant", "Response 1")
        
        # Clear
        manager.clear_memory()
        
        assert len(manager._memory) == 0
        
        # Verify file is cleared
        with open(memory_file) as f:
            data = json.load(f)
        
        assert len(data) == 0
    
    def test_multiple_managers_same_file(self, temp_dir):
        """Test multiple managers can share the same file."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "shared.json"
        
        manager1 = MemoryManager(memory_file=str(memory_file))
        manager1.add_entry("user", "From manager 1")
        
        # Create second manager
        manager2 = MemoryManager(memory_file=str(memory_file))
        
        # Should load data from first manager
        assert len(manager2._memory) == 1
        assert manager2._memory[0]["content"] == "From manager 1"
    
    @pytest.mark.parametrize("role", ["user", "assistant", "system"])
    def test_add_entry_various_roles(self, role, temp_dir):
        """Test adding entries with various roles."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        manager.add_entry(role, f"Message from {role}")
        
        assert manager._memory[0]["role"] == role
    
    def test_long_conversation_history(self, temp_dir):
        """Test handling long conversation histories."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        # Add many entries
        for i in range(100):
            manager.add_entry("user", f"Message {i}")
            manager.add_entry("assistant", f"Response {i}")
        
        history = manager.get_history()
        
        assert len(history) == 200
    
    def test_unicode_content(self, temp_dir):
        """Test handling Unicode content."""
        from src.memory import MemoryManager
        
        memory_file = temp_dir / "memory.json"
        manager = MemoryManager(memory_file=str(memory_file))
        
        unicode_content = "Hello 你好 مرحبا здравствуйте 🎉"
        manager.add_entry("user", unicode_content)
        
        # Reload and verify
        manager2 = MemoryManager(memory_file=str(memory_file))
        assert manager2._memory[0]["content"] == unicode_content
