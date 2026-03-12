import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    name: str
    transport: str = "stdio"  # stdio, http, sse
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    env: dict = Field(default_factory=dict)
    enabled: bool = True


class Settings(BaseSettings):
    """Application settings managed by Pydantic."""
    
    # Google GenAI Configuration
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""  # Alias for compatibility
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = ""

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "anthropic/claude-sonnet-4-5"
    
    # Agent Configuration
    AGENT_NAME: str = "AntigravityAgent"
    DEBUG_MODE: bool = False
    PROJECT_ROOT: str = ""
    
    # OpenAI-Compatible API Configuration
    OPENAI_BASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # Memory Configuration
    MEMORY_FILE: str = "agent_memory.json"
    ARTIFACTS_DIR: str = "artifacts"
    
    # MCP Configuration
    MCP_ENABLED: bool = True
    MCP_SERVERS_CONFIG: str = "mcp_servers.json"
    MCP_CONNECTION_TIMEOUT: int = 30
    MCP_TOOL_PREFIX: str = "mcp_"
    
    # Sandbox Configuration
    SANDBOX_TYPE: str = "local"  # local or docker
    SANDBOX_TIMEOUT_SEC: int = 30
    SANDBOX_MAX_OUTPUT_KB: int = 500
    DOCKER_IMAGE: str = "antigravity-sandbox:latest"
    DOCKER_NETWORK_ENABLED: bool = False
    DOCKER_CPU_LIMIT: str = "1.0"
    DOCKER_MEMORY_LIMIT: str = "512m"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set PROJECT_ROOT to current working directory if not set
        if not self.PROJECT_ROOT:
            self.PROJECT_ROOT = os.getcwd()
        # Alias GOOGLE_API_KEY to GEMINI_API_KEY if only one is set
        if self.GEMINI_API_KEY and not self.GOOGLE_API_KEY:
            self.GOOGLE_API_KEY = self.GEMINI_API_KEY
        elif self.GOOGLE_API_KEY and not self.GEMINI_API_KEY:
            self.GEMINI_API_KEY = self.GOOGLE_API_KEY
    
    def resolve_path(self, relative_path: str) -> Path:
        """Resolve a path relative to the project root."""
        return Path(self.PROJECT_ROOT) / relative_path
    
    @property
    def project_root_path(self) -> Path:
        """Get the project root as a Path object."""
        return Path(self.PROJECT_ROOT)
    
    @property
    def memory_file_path(self) -> Path:
        """Get the full path to the memory file."""
        return self.resolve_path(self.MEMORY_FILE)
    
    @property
    def artifacts_path(self) -> Path:
        """Get the full path to the artifacts directory."""
        return self.resolve_path(self.ARTIFACTS_DIR)


# Global settings instance
settings = Settings()
