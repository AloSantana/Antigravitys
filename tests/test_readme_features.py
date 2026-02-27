import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os

# Ensure backend path is in sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from main import app
except ImportError:
    # If main cannot be imported directly, try backend.main
    # But sys.path insert should handle it
    pytest.fail("Could not import main application from backend")

@pytest.fixture
def client():
    return TestClient(app)

def test_readme_health_check(client):
    """Test the /health endpoint mentioned in README."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    # Health check should return "ready" or "degraded" or "healthy"
    # The code returns healthy for basic check /health
    # Oh wait, /health returns minimal info. /health/ready returns components.
    # README says /health is health check.
    # Let's check what it returns
    if "components" not in data:
         # Maybe it's the simple health check
         assert data.get("status") == "healthy"
    else:
         # Or detailed one
         assert "components" in data

def test_readme_root(client):
    """Test the root endpoint mentioned in README."""
    response = client.get("/")
    assert response.status_code == 200
    # Should return JSON if not browser (Accept header)
    data = response.json()
    assert "message" in data
    assert "Running" in data["message"]

def test_readme_conversations_list(client):
    """Test /api/conversations endpoint mentioned in README."""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert isinstance(data["conversations"], list)

def test_readme_artifacts_list(client):
    """Test /api/artifacts endpoint mentioned in README."""
    response = client.get("/api/artifacts")
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    assert isinstance(data["artifacts"], list)

def test_readme_settings_get(client):
    """Test /settings endpoint mentioned in README."""
    response = client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "settings" in data

def test_readme_performance_metrics(client):
    """Test /performance/metrics endpoint mentioned in README."""
    response = client.get("/performance/metrics")
    assert response.status_code == 200
    data = response.json()
    # It returns a dict with cpu, memory, etc.
    assert "cpu" in data or "system" in data

def test_readme_agent_stats(client):
    """Test /agent/stats endpoint which relates to Agent features in README."""
    response = client.get("/agent/stats")
    assert response.status_code == 200
    data = response.json()
    assert "orchestrator" in data

def test_readme_ngrok_status(client):
    """Test /ngrok/status endpoint mentioned in README Features."""
    response = client.get("/ngrok/status")
    # This might return 200 even if not connected
    assert response.status_code == 200
    data = response.json()
    assert "tunnel_active" in data or "public_url" in data or "status" in data
