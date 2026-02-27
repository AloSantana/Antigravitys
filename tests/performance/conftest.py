import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.main import app, limiter

@pytest.fixture
def client():
    """Create a TestClient with rate limits disabled."""
    # Disable rate limits for performance testing
    limiter.enabled = False
    
    with TestClient(app) as client:
        yield client
    
    # Re-enable after tests (optional, but good practice)
    limiter.enabled = True
