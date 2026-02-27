"""
Tests for Artifact API endpoints

Integration tests for artifact management API.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
import tempfile
import shutil
import os
import base64


@pytest.fixture(scope="function")
def client():
    """Create a test client with temporary artifacts directory."""
    temp_dir = tempfile.mkdtemp()
    
    # Replace the global artifact_manager's directory
    from backend.artifact_manager import ArtifactManager
    test_manager = ArtifactManager(artifacts_dir=temp_dir)
    
    # Monkey-patch the global manager
    import backend.main
    original_manager = backend.main.artifact_manager
    backend.main.artifact_manager = test_manager
    
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup
    backend.main.artifact_manager = original_manager
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_create_artifact(client):
    """Test creating a new artifact."""
    content = b"print('Hello, World!')"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "hello.py",
        "agent": "test_agent",
        "description": "Test script",
        "metadata": {"language": "python"}
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "hello.py"
    assert data["artifact_type"] == "code"
    assert data["agent"] == "test_agent"
    assert data["description"] == "Test script"
    assert "id" in data


def test_create_artifact_minimal(client):
    """Test creating an artifact with minimal data."""
    content = b"test content"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "test.txt"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.txt"


def test_create_artifact_invalid_base64(client):
    """Test that invalid base64 content is rejected."""
    response = client.post("/api/artifacts", json={
        "content": "not-valid-base64!!!",
        "filename": "test.txt"
    })
    
    assert response.status_code == 400
    assert "Invalid base64" in response.json()["detail"]


def test_create_artifact_file_too_large(client):
    """Test that overly large files are rejected."""
    # Create content larger than allowed
    import backend.main
    max_size = backend.main.artifact_manager.MAX_FILE_SIZE
    large_content = b"x" * (max_size + 1)
    encoded_content = base64.b64encode(large_content).decode("ascii")
    
    response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "large.txt"
    })
    
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_get_artifact(client):
    """Test retrieving an artifact."""
    # Create artifact
    content = b"test content"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    create_response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "test.txt"
    })
    artifact_id = create_response.json()["id"]
    
    # Retrieve it
    response = client.get(f"/api/artifacts/{artifact_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == artifact_id
    assert data["filename"] == "test.txt"


def test_get_artifact_not_found(client):
    """Test retrieving a non-existent artifact."""
    response = client.get("/api/artifacts/nonexistent-id")
    
    assert response.status_code == 404


def test_list_artifacts_empty(client):
    """Test listing artifacts when none exist."""
    response = client.get("/api/artifacts")
    
    assert response.status_code == 200
    data = response.json()
    assert data["artifacts"] == []


def test_list_artifacts(client):
    """Test listing artifacts."""
    # Create multiple artifacts
    for i in range(3):
        content = f"content {i}".encode()
        encoded = base64.b64encode(content).decode("ascii")
        client.post("/api/artifacts", json={
            "content": encoded,
            "filename": f"file{i}.txt"
        })
    
    response = client.get("/api/artifacts")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 3


def test_list_artifacts_pagination(client):
    """Test pagination in listing artifacts."""
    # Create 5 artifacts
    for i in range(5):
        content = f"content {i}".encode()
        encoded = base64.b64encode(content).decode("ascii")
        client.post("/api/artifacts", json={
            "content": encoded,
            "filename": f"file{i}.txt"
        })
    
    # Get first page
    response = client.get("/api/artifacts?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 2
    
    # Get second page
    response = client.get("/api/artifacts?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 2


def test_list_artifacts_filter_by_type(client):
    """Test filtering artifacts by type."""
    # Create different types
    content = base64.b64encode(b"content").decode("ascii")
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "script.py"
    })
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "changes.diff"
    })
    
    response = client.get("/api/artifacts?artifact_type=code")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 1
    assert data["artifacts"][0]["artifact_type"] == "code"


def test_list_artifacts_filter_by_agent(client):
    """Test filtering artifacts by agent."""
    content = base64.b64encode(b"content").decode("ascii")
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "file1.txt",
        "agent": "agent_a"
    })
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "file2.txt",
        "agent": "agent_b"
    })
    
    response = client.get("/api/artifacts?agent=agent_a")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 1
    assert data["artifacts"][0]["agent"] == "agent_a"


def test_download_artifact(client):
    """Test downloading an artifact file."""
    # Create artifact
    content = b"Hello, World!"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    create_response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "hello.txt"
    })
    artifact_id = create_response.json()["id"]
    
    # Download it
    response = client.get(f"/api/artifacts/{artifact_id}/download")
    
    assert response.status_code == 200
    assert response.content == content
    assert "attachment" in response.headers.get("content-disposition", "")


def test_download_artifact_not_found(client):
    """Test downloading a non-existent artifact."""
    response = client.get("/api/artifacts/nonexistent/download")
    
    assert response.status_code == 404


def test_preview_artifact_text(client):
    """Test getting a text artifact preview."""
    # Create text artifact
    content = b"This is a test file"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    create_response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "test.txt"
    })
    artifact_id = create_response.json()["id"]
    
    # Get preview
    response = client.get(f"/api/artifacts/{artifact_id}/preview")
    
    assert response.status_code == 200
    data = response.json()
    assert "preview" in data
    assert "test file" in data["preview"]


def test_preview_artifact_not_found(client):
    """Test preview for non-existent artifact."""
    response = client.get("/api/artifacts/nonexistent/preview")
    
    assert response.status_code == 404


def test_delete_artifact(client):
    """Test deleting an artifact."""
    # Create artifact
    content = base64.b64encode(b"content").decode("ascii")
    create_response = client.post("/api/artifacts", json={
        "content": content,
        "filename": "delete_me.txt"
    })
    artifact_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/artifacts/{artifact_id}")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    get_response = client.get(f"/api/artifacts/{artifact_id}")
    assert get_response.status_code == 404


def test_delete_artifact_not_found(client):
    """Test deleting a non-existent artifact."""
    response = client.delete("/api/artifacts/nonexistent")
    
    assert response.status_code == 404


def test_search_artifacts(client):
    """Test searching artifacts."""
    content = base64.b64encode(b"content").decode("ascii")
    
    # Create artifacts
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "python_script.py"
    })
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "javascript_code.js"
    })
    
    # Search
    response = client.get("/api/artifacts/search?q=python")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["artifacts"]) == 1
    assert "python" in data["artifacts"][0]["filename"].lower()


def test_search_artifacts_short_query(client):
    """Test that short search queries are rejected."""
    response = client.get("/api/artifacts/search?q=a")
    
    assert response.status_code == 400


def test_search_artifacts_by_description(client):
    """Test searching artifacts by description."""
    content = base64.b64encode(b"content").decode("ascii")
    
    client.post("/api/artifacts", json={
        "content": content,
        "filename": "file.txt",
        "description": "Python utility script"
    })
    
    response = client.get("/api/artifacts/search?q=Python")
    
    assert response.status_code == 200
    assert len(response.json()["artifacts"]) == 1


def test_get_artifact_stats(client):
    """Test getting artifact statistics."""
    content = base64.b64encode(b"x" * 100).decode("ascii")
    
    # Create artifacts
    for i in range(3):
        client.post("/api/artifacts", json={
            "content": content,
            "filename": f"file{i}.py",
            "agent": "test_agent"
        })
    
    response = client.get("/api/artifacts/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 3
    assert data["total_size"] == 300
    assert "by_type" in data
    assert "by_agent" in data


def test_cleanup_artifacts(client):
    """Test cleanup of old artifacts."""
    # Note: This test is limited because we can't easily create "old" artifacts
    # in a test environment without mocking timestamps
    
    response = client.post("/api/artifacts/cleanup?days=30")
    
    assert response.status_code == 200
    data = response.json()
    assert "deleted_count" in data


def test_cleanup_artifacts_invalid_days(client):
    """Test that cleanup with invalid days is rejected."""
    response = client.post("/api/artifacts/cleanup?days=0")
    
    assert response.status_code == 400


def test_artifact_workflow(client):
    """Test complete artifact workflow."""
    content = b"Test content for workflow"
    encoded_content = base64.b64encode(content).decode("ascii")
    
    # 1. Create artifact
    create_response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "workflow.py",
        "agent": "test_agent",
        "description": "Workflow test"
    })
    assert create_response.status_code == 201
    artifact_id = create_response.json()["id"]
    
    # 2. Retrieve metadata
    get_response = client.get(f"/api/artifacts/{artifact_id}")
    assert get_response.status_code == 200
    
    # 3. Download content
    download_response = client.get(f"/api/artifacts/{artifact_id}/download")
    assert download_response.status_code == 200
    assert download_response.content == content
    
    # 4. Get preview
    preview_response = client.get(f"/api/artifacts/{artifact_id}/preview")
    assert preview_response.status_code == 200
    
    # 5. Search for it
    search_response = client.get("/api/artifacts/search?q=workflow")
    assert search_response.status_code == 200
    assert len(search_response.json()["artifacts"]) == 1
    
    # 6. Delete
    delete_response = client.delete(f"/api/artifacts/{artifact_id}")
    assert delete_response.status_code == 200
    
    # 7. Verify deletion
    final_get_response = client.get(f"/api/artifacts/{artifact_id}")
    assert final_get_response.status_code == 404


def test_multiple_artifacts_same_filename(client):
    """Test storing multiple artifacts with the same filename."""
    content = base64.b64encode(b"content").decode("ascii")
    
    response1 = client.post("/api/artifacts", json={
        "content": content,
        "filename": "file.py"
    })
    response2 = client.post("/api/artifacts", json={
        "content": content,
        "filename": "file.py"
    })
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["id"] != response2.json()["id"]


def test_artifact_type_detection(client):
    """Test automatic artifact type detection."""
    test_cases = [
        ("script.py", "code"),
        ("changes.diff", "diff"),
        ("test_utils.py", "test"),
        ("screenshot.png", "screenshot"),
        ("report.md", "report"),
    ]
    
    for filename, expected_type in test_cases:
        content = base64.b64encode(b"content").decode("ascii")
        response = client.post("/api/artifacts", json={
            "content": content,
            "filename": filename
        })
        
        assert response.status_code == 201
        assert response.json()["artifact_type"] == expected_type


def test_rate_limiting_artifact_creation(client):
    """Test rate limiting on artifact creation."""
    content = base64.b64encode(b"content").decode("ascii")
    
    response = client.post("/api/artifacts", json={
        "content": content,
        "filename": "test.txt"
    })
    
    assert response.status_code in [201, 429]  # 201 OK or 429 Too Many Requests


def test_unicode_in_artifact(client):
    """Test storing artifacts with Unicode content."""
    content = "Hello 世界 🌍".encode("utf-8")
    encoded_content = base64.b64encode(content).decode("ascii")
    
    response = client.post("/api/artifacts", json={
        "content": encoded_content,
        "filename": "unicode.txt"
    })
    
    assert response.status_code == 201
    artifact_id = response.json()["id"]
    
    # Download and verify
    download_response = client.get(f"/api/artifacts/{artifact_id}/download")
    assert download_response.content.decode("utf-8") == "Hello 世界 🌍"
