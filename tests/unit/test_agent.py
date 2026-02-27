"""
Unit tests for src.agent module
Tests the GeminiAgent class
"""

import pytest
from unittest.mock import patch


@pytest.mark.unit
class TestGeminiAgent:
    """Test suite for GeminiAgent class."""
    
    def test_agent_initialization(self, mock_settings):
        """Test GeminiAgent initializes correctly."""
        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager') as MockMemory:
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            
            assert agent.settings == mock_settings
            MockMemory.assert_called_once()
            assert agent.memory is not None
    
    def test_think_method(self, mock_settings):
        """Test the think method."""
        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager'), \
             patch('time.sleep'):  # Mock sleep to speed up test
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            
            result = agent.think("Test task")
            
            assert result == "Plan formulated."
    
    def test_act_method(self, mock_settings, mock_memory_manager):
        """Test the act method."""
        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_memory_manager), \
             patch('time.sleep'):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_memory_manager
            
            result = agent.act("Test task")
            
            # Should add entries to memory
            assert mock_memory_manager.add_entry.call_count == 2
            assert "completed" in result.lower()
    
    def test_reflect_method(self, mock_settings, mock_memory_manager):
        """Test the reflect method."""
        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_memory_manager):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_memory_manager
            mock_memory_manager.get_history.return_value = [
                {"role": "user", "content": "Task 1"},
                {"role": "assistant", "content": "Response 1"}
            ]
            
            # Should not raise error
            agent.reflect()
            
            mock_memory_manager.get_history.assert_called_once()
    
    def test_run_method(self, mock_settings, mock_memory_manager):
        """Test the run method (full workflow)."""
        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_memory_manager), \
             patch('time.sleep'):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_memory_manager
            mock_memory_manager.get_history.return_value = []
            
            # Should execute full workflow
            agent.run("Test task")
            
            # Verify memory operations
            assert mock_memory_manager.add_entry.call_count >= 2
            assert mock_memory_manager.get_history.called
    
    def test_agent_with_different_settings(self):
        """Test agent with various settings configurations."""
        from src.config import Settings
        from src.agent import GeminiAgent
        
        test_settings = Settings(
            GOOGLE_API_KEY="test_key",
            GEMINI_MODEL_NAME="custom-model",
            AGENT_NAME="CustomAgent",
            DEBUG_MODE=True
        )
        
        with patch('src.agent.settings', test_settings), \
             patch('src.agent.MemoryManager'):
            agent = GeminiAgent()
            
            assert agent.settings.AGENT_NAME == "CustomAgent"
            assert agent.settings.GEMINI_MODEL_NAME == "custom-model"
            assert agent.settings.DEBUG_MODE is True
