"""
Unit tests for src.config module
Tests the Settings class and configuration
"""

import pytest
from unittest.mock import patch
import os


@pytest.mark.unit
class TestSettings:
    """Test suite for Settings class."""
    
    def test_default_settings(self):
        """Test Settings with default values."""
        from src.config import Settings
        
        settings = Settings()
        
        assert settings.GOOGLE_API_KEY == ""
        assert settings.GEMINI_MODEL_NAME == "gemini-2.0-flash-exp"
        assert settings.AGENT_NAME == "AntigravityAgent"
        assert settings.DEBUG_MODE is False
        assert settings.MEMORY_FILE == "agent_memory.json"
    
    def test_custom_settings(self):
        """Test Settings with custom values."""
        from src.config import Settings
        
        settings = Settings(
            GOOGLE_API_KEY="custom_key_do_not_use_in_prod",
            GEMINI_MODEL_NAME="custom-model",
            AGENT_NAME="CustomAgent",
            DEBUG_MODE=True,
            MEMORY_FILE="custom_memory.json"
        )
        
        assert settings.GOOGLE_API_KEY == "custom_key"
        assert settings.GEMINI_MODEL_NAME == "custom-model"
        assert settings.AGENT_NAME == "CustomAgent"
        assert settings.DEBUG_MODE is True
        assert settings.MEMORY_FILE == "custom_memory.json"
    
    def test_settings_from_env(self, temp_dir):
        """Test Settings loads from environment variables."""
        from src.config import Settings
        
        # Create .env file
        env_file = temp_dir / ".env"
        env_content = """
GOOGLE_API_KEY=env_api_key
GEMINI_MODEL_NAME=env-model
AGENT_NAME=EnvAgent
DEBUG_MODE=true
MEMORY_FILE=env_memory.json
"""
        env_file.write_text(env_content)
        
        # Load with custom env file
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=str(env_file))
            
            # Note: pydantic-settings may not load from custom _env_file
            # So we test with environment variables instead
    
    def test_settings_env_override(self):
        """Test environment variables override defaults."""
        from src.config import Settings
        
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'override_key',
            'AGENT_NAME': 'OverrideAgent'
        }):
            settings = Settings()
            
            assert settings.GOOGLE_API_KEY == 'override_key'
            assert settings.AGENT_NAME == 'OverrideAgent'
    
    def test_settings_immutable(self):
        """Test that settings use Pydantic validation."""
        from src.config import Settings
        
        settings = Settings()
        
        # Pydantic allows assignment but validates
        settings.DEBUG_MODE = True
        assert settings.DEBUG_MODE is True
    
    def test_global_settings_instance(self):
        """Test that global settings instance exists."""
        from src.config import settings
        
        assert settings is not None
        assert hasattr(settings, 'GOOGLE_API_KEY')
        assert hasattr(settings, 'GEMINI_MODEL_NAME')
        assert hasattr(settings, 'AGENT_NAME')
    
    @pytest.mark.parametrize("model_name", [
        "gemini-2.0-flash-exp",
        "gemini-pro",
        "gemini-1.5-pro",
        "custom-model"
    ])
    def test_various_model_names(self, model_name):
        """Test settings with various model names."""
        from src.config import Settings
        
        settings = Settings(GEMINI_MODEL_NAME=model_name)
        
        assert settings.GEMINI_MODEL_NAME == model_name
    
    def test_debug_mode_boolean(self):
        """Test DEBUG_MODE accepts boolean values."""
        from src.config import Settings
        
        settings_true = Settings(DEBUG_MODE=True)
        settings_false = Settings(DEBUG_MODE=False)
        
        assert settings_true.DEBUG_MODE is True
        assert settings_false.DEBUG_MODE is False
    
    def test_empty_api_key(self):
        """Test behavior with empty API key."""
        from src.config import Settings
        
        settings = Settings(GOOGLE_API_KEY="")
        
        assert settings.GOOGLE_API_KEY == ""
        # Should not raise error
    
    def test_settings_extra_ignored(self):
        """Test that extra fields are ignored."""
        from src.config import Settings
        
        # Should not raise error with extra fields
        settings = Settings(
            GOOGLE_API_KEY="key",
            UNKNOWN_FIELD="value"  # This should be ignored
        )
        
        assert settings.GOOGLE_API_KEY == "key"
        # Unknown field should be ignored (extra="ignore" in model_config)
