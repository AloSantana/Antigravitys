"""
Shared pytest fixtures for all tests
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from typing import Dict, Any, List, Generator
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# =============================================================================
# Session Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


# =============================================================================
# File System Fixtures
# =============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file with sample content."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("Test content for testing purposes.")
    return file_path


@pytest.fixture
def test_py_file(temp_dir: Path) -> Path:
    """Create a test Python file."""
    file_path = temp_dir / "test_module.py"
    content = '''"""Test module."""

def hello_world():
    """Return greeting."""
    return "Hello, World!"

class TestClass:
    """Test class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def drop_zone_dir(temp_dir: Path) -> Path:
    """Create a mock drop_zone directory."""
    drop_zone = temp_dir / "drop_zone"
    drop_zone.mkdir()
    
    # Create some test files
    (drop_zone / "test.md").write_text("# Test Document\n\nSome content.")
    (drop_zone / "code.py").write_text("def test():\n    pass")
    
    return drop_zone


# =============================================================================
# Mock Client Fixtures
# =============================================================================

@pytest.fixture
def mock_local_client():
    """Mock LocalClient for testing."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Mocked local response")
    client.embed = AsyncMock(return_value=[0.1] * 768)  # Mock embedding vector
    client.close = AsyncMock()
    client.base_url = "http://localhost:11434"
    client.model = "llama3.2"
    return client


@pytest.fixture
def mock_gemini_client():
    """Mock GeminiClient for testing."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Mocked Gemini response")
    client.embed = AsyncMock(return_value=[0.2] * 768)  # Mock embedding vector
    client.model = MagicMock()
    client.embed_model = "models/embedding-001"
    return client


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for testing."""
    store = Mock()
    store.add_documents = Mock()
    store.add_documents_batch = Mock()
    store.query = Mock(return_value={
        'documents': [['Context document 1', 'Context document 2']],
        'metadatas': [[{'source': 'test.txt'}, {'source': 'test2.txt'}]],
        'ids': [['id1', 'id2']],
        'distances': [[0.1, 0.2]]
    })
    store.collection = Mock()
    return store


# =============================================================================
# Agent and Orchestrator Fixtures
# =============================================================================

@pytest.fixture
def mock_orchestrator(mock_local_client, mock_gemini_client, mock_vector_store):
    """Mock Orchestrator with all dependencies."""
    with patch('backend.agent.orchestrator.LocalClient', return_value=mock_local_client), \
         patch('backend.agent.orchestrator.GeminiClient', return_value=mock_gemini_client), \
         patch('backend.agent.orchestrator.VectorStore', return_value=mock_vector_store):
        
        from backend.agent.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        orchestrator.local = mock_local_client
        orchestrator.gemini = mock_gemini_client
        orchestrator.store = mock_vector_store
        return orchestrator


@pytest.fixture
def mock_agent_manager(temp_dir):
    """Mock AgentManager with test agents."""
    from backend.agent.manager import AgentManager
    
    # Create test agent directory
    agents_dir = temp_dir / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    
    # Create a test agent file
    agent_content = """# Test Agent

## Agent Metadata
- **Name**: test-agent
- **Type**: Custom Agent
- **Expertise**: Testing
- **Priority**: high

## Purpose
This is a test agent for testing purposes.

## Core Responsibilities
1. **Testing**: Test the system
2. **Validation**: Validate functionality

## Available Tools
- bash: Execute commands
- edit: Edit files
"""
    (agents_dir / "test-agent.agent.md").write_text(agent_content)
    
    manager = AgentManager(agents_dir=str(agents_dir))
    return manager


# =============================================================================
# Memory and Config Fixtures
# =============================================================================

@pytest.fixture
def mock_memory_manager(temp_dir):
    """Mock MemoryManager for testing."""
    memory_file = temp_dir / "test_memory.json"
    
    with patch('src.memory.settings') as mock_settings:
        mock_settings.MEMORY_FILE = str(memory_file)
        from src.memory import MemoryManager
        return MemoryManager(memory_file=str(memory_file))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from src.config import Settings
    import os
    
    settings = Settings(
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"),
        GEMINI_MODEL_NAME="gemini-2.0-flash-exp",
        AGENT_NAME="TestAgent",
        DEBUG_MODE=True,
        MEMORY_FILE="test_memory.json"
    )
    return settings


# =============================================================================
# FastAPI Fixtures
# =============================================================================

@pytest.fixture
def mock_app():
    """Create a mock FastAPI application for testing."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "Test API"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


@pytest.fixture
def test_client(mock_app):
    """Create a TestClient for the FastAPI app."""
    from fastapi.testclient import TestClient
    return TestClient(mock_app)


# =============================================================================
# RAG Pipeline Fixtures
# =============================================================================

@pytest.fixture
def mock_ingestion_pipeline(mock_local_client, mock_vector_store, temp_dir):
    """Mock IngestionPipeline for testing."""
    with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
         patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
        
        from backend.rag.ingest import IngestionPipeline
        pipeline = IngestionPipeline(watch_dir=str(temp_dir))
        pipeline.local_llm = mock_local_client
        pipeline.store = mock_vector_store
        return pipeline


# =============================================================================
# Performance Monitoring Fixtures
# =============================================================================

@pytest.fixture
def mock_performance_monitor(temp_dir):
    """Mock PerformanceMonitor for testing."""
    metrics_file = temp_dir / "test_metrics.json"
    
    from backend.utils.performance import PerformanceMonitor
    monitor = PerformanceMonitor(metrics_file=str(metrics_file))
    return monitor


# =============================================================================
# WebSocket Fixtures
# =============================================================================

@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing."""
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    test_env = {
        'GEMINI_API_KEY': 'test_gemini_key',
        'LOCAL_MODEL': 'llama3.2',
        'DEBUG_MODE': 'true',
    }
    
    os.environ.update(test_env)
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_request_data() -> Dict[str, Any]:
    """Sample request data for testing."""
    return {
        "simple": "What is Python?",
        "complex": "Design a scalable microservices architecture for an e-commerce platform with high availability",
        "code": "Write a function to calculate fibonacci numbers",
        "long": "Explain " + "test " * 100,  # Long request
    }


@pytest.fixture
def sample_embeddings() -> List[List[float]]:
    """Sample embeddings for testing."""
    return [
        [0.1, 0.2, 0.3] * 256,  # 768 dimensions
        [0.4, 0.5, 0.6] * 256,
        [0.7, 0.8, 0.9] * 256,
    ]


@pytest.fixture
def sample_documents() -> List[str]:
    """Sample documents for RAG testing."""
    return [
        "Python is a high-level programming language.",
        "FastAPI is a modern web framework for Python.",
        "Machine learning involves training models on data.",
        "Docker containers provide isolated environments.",
        "Git is a version control system."
    ]


# =============================================================================
# Helper Functions
# =============================================================================

@pytest.fixture
def create_test_files():
    """Factory fixture to create multiple test files."""
    def _create_files(directory: Path, files: Dict[str, str]):
        """
        Create multiple test files in a directory.
        
        Args:
            directory: Directory to create files in
            files: Dict mapping filenames to content
        """
        for filename, content in files.items():
            file_path = directory / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
    
    return _create_files


# =============================================================================
# Cleanup Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically cleanup after each test."""
    yield
    # Cleanup code here if needed
    pass


# =============================================================================
# Markers and Skips
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_ollama: mark test as requiring Ollama"
    )
    config.addinivalue_line(
        "markers", "requires_gemini: mark test as requiring Gemini API"
    )


# =============================================================================
# Collection Hooks
# =============================================================================

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    skip_slow = pytest.mark.skip(reason="Slow test, run with --runslow")
    
    for item in items:
        if "slow" in item.keywords and not config.getoption("--runslow", default=False):
            item.add_marker(skip_slow)
