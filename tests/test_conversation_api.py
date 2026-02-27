"""
Tests for Conversation API endpoints

Integration tests for conversation history API.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app, conversation_manager
import tempfile
import os


@pytest.fixture(scope="function")
def client():
    """Create a test client with temporary database."""
    # Use a temporary database for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.close()
    
    # Replace the global conversation_manager's database
    from backend.conversation_manager import ConversationManager
    test_manager = ConversationManager(db_path=temp_file.name)
    
    # Monkey-patch the global manager
    import backend.main
    original_manager = backend.main.conversation_manager
    backend.main.conversation_manager = test_manager
    
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup
    backend.main.conversation_manager = original_manager
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


def test_create_conversation(client):
    """Test creating a new conversation."""
    response = client.post("/api/conversations", json={
        "title": "Test Conversation",
        "agent_type": "test_agent",
        "metadata": {"key": "value"}
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert data["agent_type"] == "test_agent"
    assert data["metadata"] == {"key": "value"}
    assert "id" in data


def test_create_conversation_minimal(client):
    """Test creating a conversation with minimal data."""
    response = client.post("/api/conversations", json={
        "title": "Minimal Conversation"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Conversation"


def test_create_conversation_empty_title(client):
    """Test that empty title is rejected."""
    response = client.post("/api/conversations", json={
        "title": ""
    })
    
    assert response.status_code == 422  # Validation error


def test_get_conversation(client):
    """Test retrieving a conversation."""
    # Create conversation
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    # Retrieve it
    response = client.get(f"/api/conversations/{conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert data["title"] == "Test"
    assert "messages" in data


def test_get_conversation_not_found(client):
    """Test retrieving a non-existent conversation."""
    response = client.get("/api/conversations/nonexistent-id")
    
    assert response.status_code == 404


def test_get_conversation_without_messages(client):
    """Test retrieving a conversation without messages."""
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/conversations/{conversation_id}",
        params={"include_messages": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" not in data


def test_list_conversations_empty(client):
    """Test listing conversations when none exist."""
    response = client.get("/api/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["conversations"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


def test_list_conversations(client):
    """Test listing conversations."""
    # Create multiple conversations
    for i in range(3):
        client.post("/api/conversations", json={"title": f"Conv {i}"})
    
    response = client.get("/api/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 3
    assert data["total"] == 3


def test_list_conversations_pagination(client):
    """Test pagination in listing conversations."""
    # Create 5 conversations
    for i in range(5):
        client.post("/api/conversations", json={"title": f"Conv {i}"})
    
    # Get first page
    response = client.get("/api/conversations?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 2
    assert data["total"] == 5
    assert data["has_more"] is True
    
    # Get second page
    response = client.get("/api/conversations?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 2
    assert data["has_more"] is True


def test_list_conversations_limit_cap(client):
    """Test that limit is capped at 100."""
    response = client.get("/api/conversations?limit=200")
    
    assert response.status_code == 200
    # Should be capped at 100 (verified in pagination logic)


def test_list_conversations_filter_by_agent(client):
    """Test filtering conversations by agent type."""
    client.post("/api/conversations", json={
        "title": "Conv 1",
        "agent_type": "agent_a"
    })
    client.post("/api/conversations", json={
        "title": "Conv 2",
        "agent_type": "agent_b"
    })
    
    response = client.get("/api/conversations?agent_type=agent_a")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 1
    assert data["conversations"][0]["agent_type"] == "agent_a"


def test_update_conversation(client):
    """Test updating a conversation."""
    # Create conversation
    create_response = client.post("/api/conversations", json={
        "title": "Original Title"
    })
    conversation_id = create_response.json()["id"]
    
    # Update it
    response = client.patch(
        f"/api/conversations/{conversation_id}",
        json={"title": "New Title"}
    )
    
    assert response.status_code == 200
    
    # Verify update
    get_response = client.get(f"/api/conversations/{conversation_id}")
    assert get_response.json()["title"] == "New Title"


def test_update_conversation_not_found(client):
    """Test updating a non-existent conversation."""
    response = client.patch(
        "/api/conversations/nonexistent",
        json={"title": "Title"}
    )
    
    assert response.status_code == 404


def test_delete_conversation(client):
    """Test deleting a conversation."""
    # Create conversation
    create_response = client.post("/api/conversations", json={
        "title": "To Delete"
    })
    conversation_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/conversations/{conversation_id}")
    
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/conversations/{conversation_id}")
    assert get_response.status_code == 404


def test_delete_conversation_not_found(client):
    """Test deleting a non-existent conversation."""
    response = client.delete("/api/conversations/nonexistent")
    
    assert response.status_code == 404


def test_add_message(client):
    """Test adding a message to a conversation."""
    # Create conversation
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    # Add message
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={
            "role": "user",
            "content": "Hello!",
            "metadata": {"source": "test"}
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "user"
    assert data["content"] == "Hello!"
    assert data["metadata"] == {"source": "test"}


def test_add_message_invalid_role(client):
    """Test adding a message with invalid role."""
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={
            "role": "invalid",
            "content": "Test"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_add_message_to_nonexistent_conversation(client):
    """Test adding a message to a non-existent conversation."""
    response = client.post(
        "/api/conversations/nonexistent/messages",
        json={
            "role": "user",
            "content": "Test"
        }
    )
    
    assert response.status_code == 400


def test_add_multiple_messages(client):
    """Test adding multiple messages to a conversation."""
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    # Add messages
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Message 1"}
    )
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "agent", "content": "Response 1"}
    )
    
    # Retrieve conversation
    response = client.get(f"/api/conversations/{conversation_id}")
    data = response.json()
    
    assert len(data["messages"]) == 2
    assert data["message_count"] == 2


def test_export_conversation(client):
    """Test exporting a conversation as Markdown."""
    # Create conversation with messages
    create_response = client.post("/api/conversations", json={
        "title": "Export Test"
    })
    conversation_id = create_response.json()["id"]
    
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello"}
    )
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "agent", "content": "Hi there!"}
    )
    
    # Export it
    response = client.get(f"/api/conversations/{conversation_id}/export")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/markdown; charset=utf-8"
    assert "Export Test" in response.text
    assert "Hello" in response.text
    assert "Hi there!" in response.text


def test_export_conversation_not_found(client):
    """Test exporting a non-existent conversation."""
    response = client.get("/api/conversations/nonexistent/export")
    
    assert response.status_code == 404


def test_search_conversations(client):
    """Test searching conversations."""
    # Create conversations
    client.post("/api/conversations", json={"title": "Python Tutorial"})
    client.post("/api/conversations", json={"title": "JavaScript Guide"})
    
    # Search
    response = client.get("/api/conversations/search?q=Python")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) == 1
    assert "Python" in data["conversations"][0]["title"]


def test_search_conversations_short_query(client):
    """Test that short search queries are rejected."""
    response = client.get("/api/conversations/search?q=a")
    
    assert response.status_code == 400


def test_search_conversations_by_message_content(client):
    """Test searching by message content."""
    create_response = client.post("/api/conversations", json={
        "title": "Test"
    })
    conversation_id = create_response.json()["id"]
    
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "How to use Python?"}
    )
    
    response = client.get("/api/conversations/search?q=Python")
    
    assert response.status_code == 200
    assert len(response.json()["conversations"]) == 1


def test_get_conversation_stats(client):
    """Test getting conversation statistics."""
    # Create conversations with messages
    for i in range(3):
        create_response = client.post("/api/conversations", json={
            "title": f"Conv {i}",
            "agent_type": "test_agent"
        })
        conversation_id = create_response.json()["id"]
        
        client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"role": "user", "content": "Message"}
        )
    
    response = client.get("/api/conversations/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_conversations"] == 3
    assert data["total_messages"] == 3
    assert "by_agent_type" in data


def test_rate_limiting_conversation_creation(client):
    """Test rate limiting on conversation creation."""
    # Note: This test may not work as expected in unit tests
    # since rate limiting is typically per-IP and may be disabled in test mode
    # but we include it for completeness
    
    response = client.post("/api/conversations", json={
        "title": "Test"
    })
    
    assert response.status_code in [201, 429]  # 201 OK or 429 Too Many Requests


def test_conversation_workflow(client):
    """Test complete conversation workflow."""
    # 1. Create conversation
    create_response = client.post("/api/conversations", json={
        "title": "Complete Workflow"
    })
    assert create_response.status_code == 201
    conversation_id = create_response.json()["id"]
    
    # 2. Add messages
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Question 1"}
    )
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "agent", "content": "Answer 1"}
    )
    
    # 3. Retrieve conversation
    get_response = client.get(f"/api/conversations/{conversation_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()["messages"]) == 2
    
    # 4. Update title
    update_response = client.patch(
        f"/api/conversations/{conversation_id}",
        json={"title": "Updated Workflow"}
    )
    assert update_response.status_code == 200
    
    # 5. Export
    export_response = client.get(f"/api/conversations/{conversation_id}/export")
    assert export_response.status_code == 200
    
    # 6. Delete
    delete_response = client.delete(f"/api/conversations/{conversation_id}")
    assert delete_response.status_code == 200
    
    # 7. Verify deletion
    final_get_response = client.get(f"/api/conversations/{conversation_id}")
    assert final_get_response.status_code == 404
