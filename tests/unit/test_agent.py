"""
Unit tests for src.agent module
Tests the GeminiAgent class
"""

import pytest
from unittest.mock import patch, MagicMock


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
            
            assert "<thought>" in result
            assert "Task Analysis" in result
    
    @pytest.mark.asyncio
    async def test_act_method(self, mock_settings):
        """Test the act method."""
        mock_mem = MagicMock()
        mock_mem.get_context_window.return_value = []
        mock_mem.get_history.return_value = []

        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_mem), \
             patch('time.sleep'):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_mem
            
            result = await agent.act("Test task")
            
            # Should add entries to memory (user input + assistant response)
            assert mock_mem.add_entry.call_count == 2
            assert "Test task" in result
    
    def test_reflect_method(self, mock_settings):
        """Test the reflect method."""
        mock_mem = MagicMock()
        mock_mem.get_history.return_value = [
            {"role": "user", "content": "Task 1"},
            {"role": "assistant", "content": "Response 1"}
        ]

        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_mem):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_mem
            
            # Should not raise error
            agent.reflect()
            
            mock_mem.get_history.assert_called_once()
    
    def test_run_method(self, mock_settings):
        """Test the run method (full workflow)."""
        mock_mem = MagicMock()
        mock_mem.get_context_window.return_value = []
        mock_mem.get_history.return_value = []

        with patch('src.agent.settings', mock_settings), \
             patch('src.agent.MemoryManager', return_value=mock_mem), \
             patch('time.sleep'):
            from src.agent import GeminiAgent
            
            agent = GeminiAgent()
            agent.memory = mock_mem
            
            # Should execute full workflow
            agent.run("Test task")
            
            # Verify memory operations
            assert mock_mem.add_entry.call_count >= 2
            assert mock_mem.get_history.called
    
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
