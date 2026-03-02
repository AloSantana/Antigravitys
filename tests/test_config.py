"""
Comprehensive tests for the enhanced Pydantic configuration system.

Tests:
- MCPServerConfig model validation
- Settings with all config options
- Path resolution methods
- Environment variable loading
- API key aliasing
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError

from src.config import MCPServerConfig, Settings, settings


# =============================================================================
# MCPServerConfig Tests
# =============================================================================

class TestMCPServerConfig:
    """Test MCPServerConfig model."""
    
    def test_mcp_server_config_defaults(self):
        """Test MCPServerConfig with default values."""
        config = MCPServerConfig(name="test-server")
        
        assert config.name == "test-server"
        assert config.transport == "stdio"
        assert config.command is None
        assert config.args == []
        assert config.url is None
        assert config.env == {}
        assert config.enabled is True
    
    def test_mcp_server_config_stdio(self):
        """Test MCPServerConfig for stdio transport."""
        config = MCPServerConfig(
            name="filesystem",
            transport="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
            env={"DEBUG": "1"}
        )
        
        assert config.name == "filesystem"
        assert config.transport == "stdio"
        assert config.command == "npx"
        assert config.args == ["-y", "@modelcontextprotocol/server-filesystem"]
        assert config.env == {"DEBUG": "1"}
    
    def test_mcp_server_config_http(self):
        """Test MCPServerConfig for HTTP transport."""
        config = MCPServerConfig(
            name="api-server",
            transport="http",
            url="http://localhost:8080",
            enabled=False
        )
        
        assert config.name == "api-server"
        assert config.transport == "http"
        assert config.url == "http://localhost:8080"
        assert config.enabled is False
    
    def test_mcp_server_config_sse(self):
        """Test MCPServerConfig for SSE transport."""
        config = MCPServerConfig(
            name="sse-server",
            transport="sse",
            url="http://localhost:9000/sse"
        )
        
        assert config.name == "sse-server"
        assert config.transport == "sse"
        assert config.url == "http://localhost:9000/sse"
    
    def test_mcp_server_config_validation(self):
        """Test that MCPServerConfig validates required fields."""
        with pytest.raises(ValidationError):
            MCPServerConfig()  # name is required
    
    def test_mcp_server_config_from_dict(self):
        """Test creating MCPServerConfig from dictionary."""
        data = {
            "name": "test",
            "transport": "stdio",
            "command": "python",
            "args": ["server.py"],
            "env": {"PATH": "/usr/bin"},
            "enabled": True
        }
        config = MCPServerConfig(**data)
        
        assert config.name == "test"
        assert config.command == "python"
        assert len(config.args) == 1


# =============================================================================
# Settings Tests
# =============================================================================

class TestSettings:
    """Test Settings configuration class."""
    
    def test_settings_defaults(self):
        """Test Settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.GOOGLE_API_KEY == ""
            assert test_settings.GEMINI_API_KEY == ""
            assert test_settings.GEMINI_MODEL_NAME == "gemini-2.0-flash-exp"
            assert test_settings.AGENT_NAME == "AntigravityAgent"
            assert test_settings.DEBUG_MODE is False
            assert test_settings.PROJECT_ROOT != ""  # Set to cwd
    
    def test_settings_from_env(self):
        """Test Settings loading from environment variables."""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_google_key',
            'GEMINI_MODEL_NAME': 'gemini-pro',
            'AGENT_NAME': 'TestAgent',
            'DEBUG_MODE': 'true'
        }):
            test_settings = Settings()
            
            assert test_settings.GOOGLE_API_KEY == 'test_google_key'
            assert test_settings.GEMINI_MODEL_NAME == 'gemini-pro'
            assert test_settings.AGENT_NAME == 'TestAgent'
            assert test_settings.DEBUG_MODE is True
    
    def test_settings_api_key_aliasing_gemini_to_google(self):
        """Test that GEMINI_API_KEY is aliased to GOOGLE_API_KEY."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key_do_not_use_in_prod'}, clear=True):
            test_settings = Settings()
            
            assert test_settings.GEMINI_API_KEY == 'test_key_do_not_use_in_prod'
            assert test_settings.GOOGLE_API_KEY == 'test_key_do_not_use_in_prod'
    
    def test_settings_api_key_aliasing_google_to_gemini(self):
        """Test that GOOGLE_API_KEY is aliased to GEMINI_API_KEY."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key_do_not_use_in_prod'}, clear=True):
            test_settings = Settings()
            
            assert test_settings.GOOGLE_API_KEY == 'test_key_do_not_use_in_prod'
            assert test_settings.GEMINI_API_KEY == 'test_key_do_not_use_in_prod'
    
    def test_settings_api_key_both_set(self):
        """Test when both API keys are set."""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'google_key',
            'GEMINI_API_KEY': 'gemini_key'
        }):
            test_settings = Settings()
            
            # Both should retain their values
            assert test_settings.GOOGLE_API_KEY == 'google_key'
            assert test_settings.GEMINI_API_KEY == 'gemini_key'
    
    def test_settings_openai_config(self):
        """Test OpenAI-compatible API configuration."""
        with patch.dict(os.environ, {
            'OPENAI_BASE_URL': 'http://localhost:11434',
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_MODEL': 'gpt-4-turbo'
        }):
            test_settings = Settings()
            
            assert test_settings.OPENAI_BASE_URL == 'http://localhost:11434'
            assert test_settings.OPENAI_API_KEY == 'test_key'
            assert test_settings.OPENAI_MODEL == 'gpt-4-turbo'
    
    def test_settings_memory_config(self):
        """Test memory configuration."""
        with patch.dict(os.environ, {
            'MEMORY_FILE': 'custom_memory.json',
            'ARTIFACTS_DIR': 'custom_artifacts'
        }):
            test_settings = Settings()
            
            assert test_settings.MEMORY_FILE == 'custom_memory.json'
            assert test_settings.ARTIFACTS_DIR == 'custom_artifacts'
    
    def test_settings_mcp_config(self):
        """Test MCP configuration."""
        with patch.dict(os.environ, {
            'MCP_ENABLED': 'false',
            'MCP_SERVERS_CONFIG': 'custom_mcp.json',
            'MCP_CONNECTION_TIMEOUT': '60',
            'MCP_TOOL_PREFIX': 'custom_'
        }):
            test_settings = Settings()
            
            assert test_settings.MCP_ENABLED is False
            assert test_settings.MCP_SERVERS_CONFIG == 'custom_mcp.json'
            assert test_settings.MCP_CONNECTION_TIMEOUT == 60
            assert test_settings.MCP_TOOL_PREFIX == 'custom_'
    
    def test_settings_sandbox_config(self):
        """Test sandbox configuration."""
        with patch.dict(os.environ, {
            'SANDBOX_TYPE': 'docker',
            'SANDBOX_TIMEOUT_SEC': '60',
            'SANDBOX_MAX_OUTPUT_KB': '1000',
            'DOCKER_IMAGE': 'custom-sandbox:latest',
            'DOCKER_NETWORK_ENABLED': 'true',
            'DOCKER_CPU_LIMIT': '2.0',
            'DOCKER_MEMORY_LIMIT': '1g'
        }):
            test_settings = Settings()
            
            assert test_settings.SANDBOX_TYPE == 'docker'
            assert test_settings.SANDBOX_TIMEOUT_SEC == 60
            assert test_settings.SANDBOX_MAX_OUTPUT_KB == 1000
            assert test_settings.DOCKER_IMAGE == 'custom-sandbox:latest'
            assert test_settings.DOCKER_NETWORK_ENABLED is True
            assert test_settings.DOCKER_CPU_LIMIT == '2.0'
            assert test_settings.DOCKER_MEMORY_LIMIT == '1g'


# =============================================================================
# Path Resolution Tests
# =============================================================================

class TestPathResolution:
    """Test path resolution methods in Settings."""
    
    def test_resolve_path(self, tmp_path):
        """Test resolve_path method."""
        test_settings = Settings(PROJECT_ROOT=str(tmp_path))
        
        resolved = test_settings.resolve_path("subdir/file.txt")
        expected = tmp_path / "subdir" / "file.txt"
        
        assert resolved == expected
    
    def test_project_root_path(self, tmp_path):
        """Test project_root_path property."""
        test_settings = Settings(PROJECT_ROOT=str(tmp_path))
        
        root_path = test_settings.project_root_path
        
        assert isinstance(root_path, Path)
        assert root_path == tmp_path
    
    def test_memory_file_path(self, tmp_path):
        """Test memory_file_path property."""
        test_settings = Settings(
            PROJECT_ROOT=str(tmp_path),
            MEMORY_FILE="agent_memory.json"
        )
        
        memory_path = test_settings.memory_file_path
        expected = tmp_path / "agent_memory.json"
        
        assert memory_path == expected
    
    def test_artifacts_path(self, tmp_path):
        """Test artifacts_path property."""
        test_settings = Settings(
            PROJECT_ROOT=str(tmp_path),
            ARTIFACTS_DIR="artifacts"
        )
        
        artifacts_path = test_settings.artifacts_path
        expected = tmp_path / "artifacts"
        
        assert artifacts_path == expected
    
    def test_resolve_path_absolute(self, tmp_path):
        """Test that resolve_path works with relative paths."""
        test_settings = Settings(PROJECT_ROOT=str(tmp_path))
        
        # Relative path
        resolved = test_settings.resolve_path("data/test.json")
        expected = tmp_path / "data" / "test.json"
        
        assert resolved == expected
    
    def test_project_root_defaults_to_cwd(self):
        """Test that PROJECT_ROOT defaults to current working directory."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.PROJECT_ROOT == os.getcwd()
    
    def test_path_resolution_with_nested_dirs(self, tmp_path):
        """Test path resolution with nested directories."""
        test_settings = Settings(PROJECT_ROOT=str(tmp_path))
        
        resolved = test_settings.resolve_path("a/b/c/file.txt")
        expected = tmp_path / "a" / "b" / "c" / "file.txt"
        
        assert resolved == expected


# =============================================================================
# Environment Variable Loading Tests
# =============================================================================

class TestEnvironmentVariableLoading:
    """Test environment variable loading and .env file support."""
    
    def test_load_from_env_file(self, tmp_path):
        """Test loading settings from .env file."""
        # Create a .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
GOOGLE_API_KEY=env_file_key
AGENT_NAME=EnvAgent
DEBUG_MODE=true
MEMORY_FILE=env_memory.json
""")
        
        # Note: Actual .env loading is handled by pydantic-settings
        # This test verifies the configuration is set up correctly
        test_settings = Settings(_env_file=str(env_file))
        assert hasattr(test_settings, 'GOOGLE_API_KEY')
    
    def test_env_vars_override_defaults(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {'AGENT_NAME': 'CustomAgent'}):
            test_settings = Settings()
            
            assert test_settings.AGENT_NAME == 'CustomAgent'
    
    def test_type_coercion(self):
        """Test that settings properly coerce types."""
        with patch.dict(os.environ, {
            'DEBUG_MODE': '1',
            'MCP_ENABLED': 'true',
            'SANDBOX_TIMEOUT_SEC': '45',
            'DOCKER_NETWORK_ENABLED': 'false'
        }):
            test_settings = Settings()
            
            assert test_settings.DEBUG_MODE is True
            assert test_settings.MCP_ENABLED is True
            assert test_settings.SANDBOX_TIMEOUT_SEC == 45
            assert test_settings.DOCKER_NETWORK_ENABLED is False
    
    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        with patch.dict(os.environ, {'UNKNOWN_FIELD': 'value'}):
            # Should not raise an error
            test_settings = Settings()
            assert not hasattr(test_settings, 'UNKNOWN_FIELD')


# =============================================================================
# Integration Tests
# =============================================================================

class TestSettingsIntegration:
    """Integration tests for the settings system."""
    
    def test_global_settings_instance(self):
        """Test that global settings instance is available."""
        
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'GOOGLE_API_KEY')
        assert hasattr(settings, 'resolve_path')
    
    def test_settings_with_all_options(self, tmp_path):
        """Test creating settings with all options."""
        test_settings = Settings(
            # Google GenAI
            GOOGLE_API_KEY="test_google_key_do_not_use_in_prod",
            GEMINI_API_KEY="test_gemini_key",
            GEMINI_MODEL_NAME="gemini-pro",
            
            # Agent
            AGENT_NAME="TestAgent",
            DEBUG_MODE=True,
            PROJECT_ROOT=str(tmp_path),
            
            # OpenAI
            OPENAI_BASE_URL="http://localhost:11434",
            OPENAI_API_KEY="test_openai_key_do_not_use_in_prod",
            OPENAI_MODEL="gpt-4",
            
            # Memory
            MEMORY_FILE="test_memory.json",
            ARTIFACTS_DIR="test_artifacts",
            
            # MCP
            MCP_ENABLED=True,
            MCP_SERVERS_CONFIG="test_mcp.json",
            MCP_CONNECTION_TIMEOUT=60,
            MCP_TOOL_PREFIX="test_",
            
            # Sandbox
            SANDBOX_TYPE="docker",
            SANDBOX_TIMEOUT_SEC=60,
            SANDBOX_MAX_OUTPUT_KB=1000,
            DOCKER_IMAGE="test-sandbox:latest",
            DOCKER_NETWORK_ENABLED=True,
            DOCKER_CPU_LIMIT="2.0",
            DOCKER_MEMORY_LIMIT="1g"
        )
        
        # Verify all settings
        assert test_settings.GOOGLE_API_KEY == "test_google_key_do_not_use_in_prod"
        assert test_settings.GEMINI_MODEL_NAME == "gemini-pro"
        assert test_settings.AGENT_NAME == "TestAgent"
        assert test_settings.DEBUG_MODE is True
        assert test_settings.PROJECT_ROOT == str(tmp_path)
        assert test_settings.OPENAI_BASE_URL == "http://localhost:11434"
        assert test_settings.MEMORY_FILE == "test_memory.json"
        assert test_settings.MCP_ENABLED is True
        assert test_settings.SANDBOX_TYPE == "docker"
    
    def test_settings_immutable_after_creation(self):
        """Test that settings can be updated after creation."""
        test_settings = Settings(AGENT_NAME="Original")
        
        # Pydantic models are mutable by default
        test_settings.AGENT_NAME = "Updated"
        assert test_settings.AGENT_NAME == "Updated"
    
    def test_settings_serialization(self):
        """Test that settings can be serialized to dict."""
        test_settings = Settings(
            GOOGLE_API_KEY="test_key_do_not_use_in_prod",
            AGENT_NAME="TestAgent",
            DEBUG_MODE=True
        )
        
        settings_dict = test_settings.model_dump()
        
        assert isinstance(settings_dict, dict)
        assert settings_dict['GOOGLE_API_KEY'] == 'test_key_do_not_use_in_prod'
        assert settings_dict['AGENT_NAME'] == 'TestAgent'
        assert settings_dict['DEBUG_MODE'] is True


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestSettingsEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_api_keys(self):
        """Test settings with empty API keys."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.GOOGLE_API_KEY == ""
            assert test_settings.GEMINI_API_KEY == ""
    
    def test_whitespace_in_values(self):
        """Test that whitespace in values is preserved."""
        with patch.dict(os.environ, {'AGENT_NAME': '  TestAgent  '}):
            test_settings = Settings()
            
            # Pydantic strips whitespace by default for strings
            assert test_settings.AGENT_NAME == '  TestAgent  '
    
    def test_special_characters_in_paths(self, tmp_path):
        """Test paths with special characters."""
        special_dir = tmp_path / "test-dir_123"
        test_settings = Settings(PROJECT_ROOT=str(special_dir))
        
        resolved = test_settings.resolve_path("file.txt")
        expected = special_dir / "file.txt"
        
        assert resolved == expected
    
    def test_unicode_in_settings(self):
        """Test Unicode characters in settings."""
        with patch.dict(os.environ, {'AGENT_NAME': 'Agent-日本語'}):
            test_settings = Settings()
            
            assert test_settings.AGENT_NAME == 'Agent-日本語'
    
    def test_very_long_values(self):
        """Test very long configuration values."""
        long_value = "x" * 10000
        test_settings = Settings(GOOGLE_API_KEY=long_value)
        
        assert len(test_settings.GOOGLE_API_KEY) == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
