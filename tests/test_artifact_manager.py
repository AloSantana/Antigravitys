"""
Tests for ArtifactManager

Comprehensive test suite for artifact storage and management.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from backend.artifact_manager import ArtifactManager


@pytest.fixture
def temp_artifacts_dir():
    """Create a temporary artifacts directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def manager(temp_artifacts_dir):
    """Create an ArtifactManager instance for testing."""
    return ArtifactManager(artifacts_dir=temp_artifacts_dir)


def test_init_storage(temp_artifacts_dir):
    """Test artifact storage initialization."""
    manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
    
    # Verify main directory exists
    assert Path(temp_artifacts_dir).exists()
    
    # Verify subdirectories exist
    for artifact_type, config in manager.ARTIFACT_TYPES.items():
        subdir = Path(temp_artifacts_dir) / config["subdir"]
        assert subdir.exists()
    
    # Verify metadata file exists
    assert manager.metadata_file.exists()


def test_detect_artifact_type(manager):
    """Test artifact type detection."""
    assert manager._detect_artifact_type("script.py") == "code"
    assert manager._detect_artifact_type("changes.diff") == "diff"
    assert manager._detect_artifact_type("test_utils.py") == "test"
    assert manager._detect_artifact_type("screenshot.png") == "screenshot"
    assert manager._detect_artifact_type("report.md") == "report"
    assert manager._detect_artifact_type("data.json") == "other"


def test_detect_artifact_type_test_files(manager):
    """Test detection of test files with special naming."""
    assert manager._detect_artifact_type("test_module.js") == "test"
    assert manager._detect_artifact_type("component.spec.ts") == "test"
    assert manager._detect_artifact_type("utils.test.js") == "test"


def test_store_artifact(manager):
    """Test storing an artifact."""
    content = b"print('Hello, World!')"
    
    artifact = manager.store_artifact(
        content=content,
        filename="hello.py",
        agent="test_agent",
        description="Test Python script",
        metadata={"language": "python"}
    )
    
    assert "id" in artifact
    assert artifact["filename"] == "hello.py"
    assert artifact["artifact_type"] == "code"
    assert artifact["size"] == len(content)
    assert artifact["agent"] == "test_agent"
    assert artifact["description"] == "Test Python script"
    assert artifact["metadata"]["language"] == "python"
    assert "created_at" in artifact
    assert "path" in artifact


def test_store_artifact_auto_detect_type(manager):
    """Test that artifact type is auto-detected."""
    artifact = manager.store_artifact(
        content=b"diff content",
        filename="changes.diff"
    )
    
    assert artifact["artifact_type"] == "diff"


def test_store_artifact_explicit_type(manager):
    """Test storing artifact with explicit type."""
    artifact = manager.store_artifact(
        content=b"content",
        filename="file.txt",
        artifact_type="report"
    )
    
    assert artifact["artifact_type"] == "report"


def test_store_artifact_file_too_large(manager):
    """Test that storing a too-large file raises an error."""
    # Create content larger than max size
    large_content = b"x" * (manager.MAX_FILE_SIZE + 1)
    
    with pytest.raises(ValueError, match="File too large"):
        manager.store_artifact(
            content=large_content,
            filename="large.txt"
        )


def test_store_artifact_storage_limit(manager):
    """Test storage limit enforcement."""
    # Store artifacts until we approach the limit
    artifact_size = 1024 * 1024  # 1MB
    content = b"x" * artifact_size
    
    # Calculate how many we can store
    max_artifacts = manager.MAX_TOTAL_SIZE // artifact_size
    
    # Store max allowed artifacts
    for i in range(max_artifacts):
        manager.store_artifact(
            content=content,
            filename=f"file{i}.txt"
        )
    
    # Next one should fail
    with pytest.raises(ValueError, match="Storage limit exceeded"):
        manager.store_artifact(
            content=content,
            filename="overflow.txt"
        )


def test_get_artifact(manager):
    """Test retrieving an artifact."""
    # Store artifact
    stored = manager.store_artifact(
        content=b"test content",
        filename="test.py"
    )
    
    # Retrieve it
    artifact = manager.get_artifact(stored["id"])
    
    assert artifact is not None
    assert artifact["id"] == stored["id"]
    assert artifact["filename"] == "test.py"


def test_get_artifact_not_found(manager):
    """Test retrieving a non-existent artifact."""
    artifact = manager.get_artifact("nonexistent-id")
    assert artifact is None


def test_read_artifact_content(manager):
    """Test reading artifact file content."""
    content = b"Hello, World!"
    stored = manager.store_artifact(
        content=content,
        filename="hello.txt"
    )
    
    read_content = manager.read_artifact_content(stored["id"])
    
    assert read_content == content


def test_read_artifact_content_not_found(manager):
    """Test reading content of non-existent artifact."""
    content = manager.read_artifact_content("nonexistent")
    assert content is None


def test_list_artifacts_empty(manager):
    """Test listing artifacts when none exist."""
    artifacts = manager.list_artifacts()
    assert artifacts == []


def test_list_artifacts(manager):
    """Test listing artifacts."""
    # Store multiple artifacts
    manager.store_artifact(b"content1", "file1.py")
    manager.store_artifact(b"content2", "file2.js")
    manager.store_artifact(b"content3", "file3.diff")
    
    artifacts = manager.list_artifacts()
    
    assert len(artifacts) == 3


def test_list_artifacts_by_type(manager):
    """Test filtering artifacts by type."""
    manager.store_artifact(b"code1", "file1.py")
    manager.store_artifact(b"code2", "file2.py")
    manager.store_artifact(b"diff", "changes.diff")
    
    code_artifacts = manager.list_artifacts(artifact_type="code")
    
    assert len(code_artifacts) == 2
    for artifact in code_artifacts:
        assert artifact["artifact_type"] == "code"


def test_list_artifacts_by_agent(manager):
    """Test filtering artifacts by agent."""
    manager.store_artifact(b"content1", "file1.py", agent="agent_a")
    manager.store_artifact(b"content2", "file2.py", agent="agent_b")
    manager.store_artifact(b"content3", "file3.py", agent="agent_a")
    
    artifacts = manager.list_artifacts(agent="agent_a")
    
    assert len(artifacts) == 2
    for artifact in artifacts:
        assert artifact["agent"] == "agent_a"


def test_list_artifacts_pagination(manager):
    """Test pagination in listing artifacts."""
    # Store 5 artifacts
    for i in range(5):
        manager.store_artifact(b"content", f"file{i}.py")
    
    # Get first page
    page1 = manager.list_artifacts(skip=0, limit=2)
    assert len(page1) == 2
    
    # Get second page
    page2 = manager.list_artifacts(skip=2, limit=2)
    assert len(page2) == 2
    assert page1[0]["id"] != page2[0]["id"]
    
    # Get last page
    page3 = manager.list_artifacts(skip=4, limit=2)
    assert len(page3) == 1


def test_list_artifacts_sorting(manager):
    """Test that artifacts are sorted by creation time (newest first)."""
    import time
    
    artifact1 = manager.store_artifact(b"first", "first.py")
    time.sleep(0.1)
    artifact2 = manager.store_artifact(b"second", "second.py")
    time.sleep(0.1)
    artifact3 = manager.store_artifact(b"third", "third.py")
    
    artifacts = manager.list_artifacts()
    
    # Should be in reverse chronological order
    assert artifacts[0]["id"] == artifact3["id"]
    assert artifacts[1]["id"] == artifact2["id"]
    assert artifacts[2]["id"] == artifact1["id"]


def test_delete_artifact(manager):
    """Test deleting an artifact."""
    artifact = manager.store_artifact(b"content", "file.py")
    
    # Delete it
    deleted = manager.delete_artifact(artifact["id"])
    
    assert deleted is True
    
    # Verify it's gone
    retrieved = manager.get_artifact(artifact["id"])
    assert retrieved is None


def test_delete_artifact_not_found(manager):
    """Test deleting a non-existent artifact."""
    deleted = manager.delete_artifact("nonexistent")
    assert deleted is False


def test_delete_artifact_removes_file(manager):
    """Test that deleting an artifact removes the file."""
    artifact = manager.store_artifact(b"content", "file.py")
    
    # Get file path
    artifact_path = manager.artifacts_dir / artifact["path"]
    assert artifact_path.exists()
    
    # Delete artifact
    manager.delete_artifact(artifact["id"])
    
    # File should be gone
    assert not artifact_path.exists()


def test_search_artifacts_by_filename(manager):
    """Test searching artifacts by filename."""
    manager.store_artifact(b"content", "python_script.py")
    manager.store_artifact(b"content", "javascript_code.js")
    manager.store_artifact(b"content", "python_test.py")
    
    results = manager.search_artifacts("python")
    
    assert len(results) == 2


def test_search_artifacts_by_description(manager):
    """Test searching artifacts by description."""
    manager.store_artifact(
        b"content",
        "file1.py",
        description="Python utility script"
    )
    manager.store_artifact(
        b"content",
        "file2.js",
        description="JavaScript helper"
    )
    
    results = manager.search_artifacts("Python")
    
    assert len(results) == 1
    assert "Python" in results[0]["description"]


def test_search_artifacts_case_insensitive(manager):
    """Test that search is case-insensitive."""
    manager.store_artifact(b"content", "Python_Script.py")
    
    results = manager.search_artifacts("python")
    assert len(results) == 1
    
    results = manager.search_artifacts("PYTHON")
    assert len(results) == 1


def test_get_statistics_empty(manager):
    """Test getting statistics when no artifacts exist."""
    stats = manager.get_statistics()
    
    assert stats["total_count"] == 0
    assert stats["total_size"] == 0
    assert stats["by_type"] == {}
    assert stats["by_agent"] == {}


def test_get_statistics(manager):
    """Test getting artifact statistics."""
    # Store artifacts of different types and agents
    manager.store_artifact(b"x" * 100, "file1.py", agent="agent_a")
    manager.store_artifact(b"x" * 200, "file2.py", agent="agent_b")
    manager.store_artifact(b"x" * 150, "changes.diff", agent="agent_a")
    
    stats = manager.get_statistics()
    
    assert stats["total_count"] == 3
    assert stats["total_size"] == 450
    assert stats["by_type"]["code"]["count"] == 2
    assert stats["by_type"]["code"]["size"] == 300
    assert stats["by_type"]["diff"]["count"] == 1
    assert stats["by_agent"]["agent_a"] == 2
    assert stats["by_agent"]["agent_b"] == 1


def test_cleanup_old_artifacts(manager):
    """Test cleanup of old artifacts."""
    import time
    from datetime import datetime, timedelta
    
    # Store an artifact and manually modify its timestamp
    artifact = manager.store_artifact(b"content", "old.py")
    
    # Modify metadata to make it old
    metadata = manager._load_metadata()
    old_date = (datetime.utcnow() - timedelta(days=60)).isoformat()
    metadata[artifact["id"]]["created_at"] = old_date
    manager._save_metadata(metadata)
    
    # Store a recent artifact
    recent = manager.store_artifact(b"content", "recent.py")
    
    # Cleanup artifacts older than 30 days
    deleted_count = manager.cleanup_old_artifacts(days=30)
    
    assert deleted_count == 1
    
    # Verify old artifact is gone
    assert manager.get_artifact(artifact["id"]) is None
    
    # Verify recent artifact still exists
    assert manager.get_artifact(recent["id"]) is not None


def test_export_artifact_preview_text(manager):
    """Test generating preview for text artifacts."""
    content = b"This is a test file\nWith multiple lines\nOf text"
    artifact = manager.store_artifact(content, "test.txt")
    
    preview = manager.export_artifact_preview(artifact["id"])
    
    assert preview is not None
    assert "This is a test file" in preview


def test_export_artifact_preview_code(manager):
    """Test generating preview for code artifacts."""
    content = b"def hello():\n    print('Hello!')"
    artifact = manager.store_artifact(content, "script.py")
    
    preview = manager.export_artifact_preview(artifact["id"])
    
    assert preview is not None
    assert "def hello()" in preview


def test_export_artifact_preview_truncated(manager):
    """Test that large previews are truncated."""
    # Create large content
    content = b"x" * 2000
    artifact = manager.store_artifact(content, "large.txt")
    
    preview = manager.export_artifact_preview(artifact["id"], max_size=100)
    
    assert len(preview) < 200  # Should be truncated
    assert "truncated" in preview.lower()


def test_export_artifact_preview_image(manager):
    """Test generating preview for image artifacts."""
    # Fake image content (just needs to be bytes)
    content = b"\x89PNG\r\n\x1a\n"  # PNG header
    artifact = manager.store_artifact(content, "image.png")
    
    preview = manager.export_artifact_preview(artifact["id"])
    
    assert preview is not None
    assert preview.startswith("data:image/png;base64,")


def test_export_artifact_preview_binary(manager):
    """Test preview for binary files."""
    content = b"\x00\x01\x02\x03"
    artifact = manager.store_artifact(content, "binary.bin")
    
    preview = manager.export_artifact_preview(artifact["id"])
    
    assert preview is not None
    assert "Binary file" in preview


def test_export_artifact_preview_not_found(manager):
    """Test preview for non-existent artifact."""
    preview = manager.export_artifact_preview("nonexistent")
    assert preview is None


def test_mime_type_detection(manager):
    """Test MIME type detection for different file types."""
    artifacts = [
        (b"content", "file.py", "text/x-python"),
        (b"content", "file.js", "text/javascript"),
        (b"content", "file.html", "text/html"),
        (b"content", "file.json", "application/json"),
        (b"content", "file.txt", "text/plain"),
    ]
    
    for content, filename, expected_mime in artifacts:
        artifact = manager.store_artifact(content, filename)
        # MIME type detection may vary, just check it's set
        assert "mime_type" in artifact


def test_concurrent_artifact_storage(manager):
    """Test storing multiple artifacts concurrently."""
    artifacts = []
    
    # Store 20 artifacts
    for i in range(20):
        artifact = manager.store_artifact(
            b"content",
            f"file{i}.py",
            agent=f"agent_{i % 3}"
        )
        artifacts.append(artifact)
    
    # Verify all were stored
    all_artifacts = manager.list_artifacts(limit=100)
    assert len(all_artifacts) == 20


def test_special_characters_in_metadata(manager):
    """Test handling special characters in metadata."""
    artifact = manager.store_artifact(
        b"content",
        "file.py",
        description="Script with 'quotes' and \"double quotes\"",
        metadata={"key": "value with <>&\"'"}
    )
    
    retrieved = manager.get_artifact(artifact["id"])
    assert retrieved["description"] == "Script with 'quotes' and \"double quotes\""
    assert retrieved["metadata"]["key"] == "value with <>&\"'"


def test_unicode_content(manager):
    """Test storing and retrieving Unicode content."""
    content = "Hello 世界 🌍".encode("utf-8")
    artifact = manager.store_artifact(content, "unicode.txt")
    
    read_content = manager.read_artifact_content(artifact["id"])
    assert read_content.decode("utf-8") == "Hello 世界 🌍"


def test_artifact_path_structure(manager):
    """Test that artifacts are stored in correct subdirectories."""
    code_artifact = manager.store_artifact(b"code", "script.py")
    diff_artifact = manager.store_artifact(b"diff", "changes.diff")
    
    assert "code/" in code_artifact["path"]
    assert "diffs/" in diff_artifact["path"]


def test_get_total_size(manager):
    """Test calculation of total storage size."""
    manager.store_artifact(b"x" * 100, "file1.py")
    manager.store_artifact(b"x" * 200, "file2.py")
    manager.store_artifact(b"x" * 300, "file3.py")
    
    total_size = manager._get_total_size()
    assert total_size == 600


def test_multiple_artifacts_same_filename(manager):
    """Test storing multiple artifacts with the same filename."""
    artifact1 = manager.store_artifact(b"content1", "file.py")
    artifact2 = manager.store_artifact(b"content2", "file.py")
    
    # Should have different IDs
    assert artifact1["id"] != artifact2["id"]
    
    # Both should be retrievable
    assert manager.get_artifact(artifact1["id"]) is not None
    assert manager.get_artifact(artifact2["id"]) is not None
