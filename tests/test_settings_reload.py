"""
Tests for settings reload and model switching functionality.

Tests environment reload, model selection, and orchestrator reinitialization.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from settings_manager import SettingsManager
from agent.orchestrator import Orchestrator


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    temp_dir = tempfile.mkdtemp()
    env_file = Path(temp_dir) / ".env"
    
    # Create initial .env content
    env_content = """
# AI Models
GEMINI_API_KEY=test_gemini_key
VERTEX_API_KEY=test_vertex_key
LOCAL_MODEL=llama3
ACTIVE_MODEL=auto

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    env_file.write_text(env_content)
    
    yield env_file
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def settings_manager_with_temp_env(temp_env_file):
    """Create a settings manager with temporary .env file."""
    manager = SettingsManager(env_file=str(temp_env_file))
    return manager


class TestSettingsReload:
    """Test environment reload functionality."""
    
    def test_reload_environment_no_changes(self, settings_manager_with_temp_env):
        """Test reloading environment when nothing has changed."""
        result = settings_manager_with_temp_env.reload_environment()
        
        assert result["success"] is True
        assert len(result["changes"]) == 0
    
    def test_reload_environment_model_change(self, settings_manager_with_temp_env, temp_env_file):
        """Test reloading environment after model change."""
        # Modify .env file
        env_content = temp_env_file.read_text()
        env_content = env_content.replace("ACTIVE_MODEL=auto", "ACTIVE_MODEL=gemini")
        temp_env_file.write_text(env_content)
        
        # Reload
        result = settings_manager_with_temp_env.reload_environment()
        
        assert result["success"] is True
        assert len(result["changes"]) > 0
        
        # Check that ACTIVE_MODEL change was detected
        model_change = next((c for c in result["changes"] if c["variable"] == "ACTIVE_MODEL"), None)
        assert model_change is not None
        assert model_change["old_value"] == "auto"
        assert model_change["new_value"] == "gemini"
    
    def test_reload_environment_api_key_change(self, settings_manager_with_temp_env, temp_env_file):
        """Test reloading environment after API key change."""
        # Modify .env file
        env_content = temp_env_file.read_text()
        env_content = env_content.replace("GEMINI_API_KEY=test_gemini_key", "GEMINI_API_KEY=new_gemini_key")
        temp_env_file.write_text(env_content)
        
        # Reload
        result = settings_manager_with_temp_env.reload_environment()
        
        assert result["success"] is True
        
        # Check that API key change was detected (but value is redacted)
        key_change = next((c for c in result["changes"] if c["variable"] == "GEMINI_API_KEY"), None)
        assert key_change is not None
        assert key_change["new_value"] == "***REDACTED***"


class TestModelSelection:
    """Test model selection and validation."""
    
    def test_set_active_model_valid(self, settings_manager_with_temp_env):
        """Test setting active model to a valid value."""
        result = settings_manager_with_temp_env.set_active_model("gemini")
        
        assert result["success"] is True
        assert result["active_model"] == "gemini"
    
    def test_set_active_model_invalid(self, settings_manager_with_temp_env):
        """Test setting active model to an invalid value."""
        result = settings_manager_with_temp_env.set_active_model("invalid_model")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_available_models(self, settings_manager_with_temp_env):
        """Test getting list of available models."""
        models = settings_manager_with_temp_env.get_available_models()
        
        assert len(models) > 0
        
        # Check that all expected models are present
        model_ids = [m["id"] for m in models]
        assert "gemini" in model_ids
        assert "vertex" in model_ids
        assert "ollama" in model_ids
    
    def test_model_configuration_status(self, settings_manager_with_temp_env):
        """Test that model configuration status is reported correctly."""
        models = settings_manager_with_temp_env.get_available_models()
        
        # Gemini should be configured (has API key)
        gemini = next(m for m in models if m["id"] == "gemini")
        assert gemini["configured"] is True
        
        # Ollama doesn't require a key, so should always be configured
        ollama = next(m for m in models if m["id"] == "ollama")
        assert ollama["configured"] is True


class TestOrchestratorReinitialize:
    """Test orchestrator reinitialization."""
    
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "ACTIVE_MODEL": "auto"
    })
    def test_orchestrator_init_with_active_model(self):
        """Test that orchestrator initializes with active model from env."""
        orchestrator = Orchestrator()
        
        assert orchestrator.active_model == "auto"
    
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "ACTIVE_MODEL": "gemini"
    })
    def test_orchestrator_reinitialize(self):
        """Test orchestrator reinitialization."""
        orchestrator = Orchestrator()
        assert orchestrator.active_model == "gemini"
        
        # Change environment
        os.environ["ACTIVE_MODEL"] = "vertex"
        
        # Reinitialize
        orchestrator.reinitialize()
        
        # Should have new model
        assert orchestrator.active_model == "vertex"
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_orchestrator_cache_cleared_on_reinit(self):
        """Test that cache is cleared when orchestrator is reinitialized."""
        orchestrator = Orchestrator()
        
        # Add something to cache
        orchestrator._response_cache["test_key"] = ({"response": "test"}, 12345)
        assert len(orchestrator._response_cache) > 0
        
        # Reinitialize
        orchestrator.reinitialize()
        
        # Cache should be cleared
        assert len(orchestrator._response_cache) == 0


class TestModelRouting:
    """Test that model selection actually routes requests correctly."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "ACTIVE_MODEL": "gemini"
    })
    async def test_explicit_gemini_routing(self):
        """Test that ACTIVE_MODEL=gemini routes to Gemini."""
        orchestrator = Orchestrator()
        
        # Mock the delegate methods to return coroutines
        async def mock_gemini(*args, **kwargs):
            return {"source": "Gemini", "response": "test"}
        
        async def mock_vertex(*args, **kwargs):
            return {"source": "Vertex AI", "response": "test"}
        
        async def mock_local(*args, **kwargs):
            return {"source": "Local", "response": "test"}
        
        orchestrator._delegate_to_gemini = Mock(side_effect=mock_gemini)
        orchestrator._delegate_to_vertex = Mock(side_effect=mock_vertex)
        orchestrator._delegate_to_local = Mock(side_effect=mock_local)
        
        # Mock embed and RAG
        async def mock_embed(*args, **kwargs):
            return []
        
        orchestrator.local.embed = Mock(side_effect=mock_embed)
        orchestrator.store.query = Mock(return_value=None)
        
        # Process request
        await orchestrator.process_request("test request")
        
        # Should have called Gemini delegate
        orchestrator._delegate_to_gemini.assert_called_once()
        orchestrator._delegate_to_vertex.assert_not_called()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "ACTIVE_MODEL": "vertex"
    })
    async def test_explicit_vertex_routing(self):
        """Test that ACTIVE_MODEL=vertex routes to Vertex AI."""
        orchestrator = Orchestrator()
        
        # Mock the delegate methods to return coroutines
        async def mock_gemini(*args, **kwargs):
            return {"source": "Gemini", "response": "test"}
        
        async def mock_vertex(*args, **kwargs):
            return {"source": "Vertex AI", "response": "test"}
        
        async def mock_local(*args, **kwargs):
            return {"source": "Local", "response": "test"}
        
        orchestrator._delegate_to_gemini = Mock(side_effect=mock_gemini)
        orchestrator._delegate_to_vertex = Mock(side_effect=mock_vertex)
        orchestrator._delegate_to_local = Mock(side_effect=mock_local)
        
        # Mock embed and RAG
        async def mock_embed(*args, **kwargs):
            return []
        
        orchestrator.local.embed = Mock(side_effect=mock_embed)
        orchestrator.store.query = Mock(return_value=None)
        
        # Process request
        await orchestrator.process_request("test request")
        
        # Should have called Vertex delegate
        orchestrator._delegate_to_vertex.assert_called_once()
        orchestrator._delegate_to_gemini.assert_not_called()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "ACTIVE_MODEL": "ollama"
    })
    async def test_explicit_ollama_routing(self):
        """Test that ACTIVE_MODEL=ollama routes to local LLM."""
        orchestrator = Orchestrator()
        
        # Mock the delegate methods to return coroutines
        async def mock_gemini(*args, **kwargs):
            return {"source": "Gemini", "response": "test"}
        
        async def mock_vertex(*args, **kwargs):
            return {"source": "Vertex AI", "response": "test"}
        
        async def mock_local(*args, **kwargs):
            return {"source": "Local", "response": "success"}
        
        orchestrator._delegate_to_gemini = Mock(side_effect=mock_gemini)
        orchestrator._delegate_to_vertex = Mock(side_effect=mock_vertex)
        orchestrator._delegate_to_local = Mock(side_effect=mock_local)
        
        # Mock embed and RAG
        async def mock_embed(*args, **kwargs):
            return []
        
        orchestrator.local.embed = Mock(side_effect=mock_embed)
        orchestrator.store.query = Mock(return_value=None)
        
        # Process request
        await orchestrator.process_request("test request")
        
        # Should have called Local delegate
        orchestrator._delegate_to_local.assert_called_once()


class TestEnvironmentPropagation:
    """Test that environment changes propagate correctly."""
    
    def test_settings_to_orchestrator_propagation(self, settings_manager_with_temp_env, temp_env_file):
        """Test that settings changes propagate to orchestrator."""
        # Create orchestrator
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key", "ACTIVE_MODEL": "auto"}):
            orchestrator = Orchestrator()
            assert orchestrator.active_model == "auto"
        
        # Change setting via settings manager
        settings_manager_with_temp_env.set_active_model("gemini")
        
        # Reload environment
        settings_manager_with_temp_env.reload_environment()
        
        # Reinitialize orchestrator
        orchestrator.reinitialize()
        
        # Should have new model
        assert orchestrator.active_model == "gemini"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
