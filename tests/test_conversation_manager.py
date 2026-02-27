"""
Tests for ConversationManager

Comprehensive test suite for conversation history persistence.
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime
from backend.conversation_manager import ConversationManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def manager(temp_db):
    """Create a ConversationManager instance for testing."""
    return ConversationManager(db_path=temp_db)


def test_init_database(temp_db):
    """Test database initialization."""
    manager = ConversationManager(db_path=temp_db)
    
    # Verify tables exist
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Check conversations table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversations'
        """)
        assert cursor.fetchone() is not None
        
        # Check messages table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='messages'
        """)
        assert cursor.fetchone() is not None


def test_create_conversation(manager):
    """Test creating a new conversation."""
    conversation = manager.create_conversation(
        title="Test Conversation",
        agent_type="test_agent",
        metadata={"key": "value"}
    )
    
    assert "id" in conversation
    assert conversation["title"] == "Test Conversation"
    assert conversation["agent_type"] == "test_agent"
    assert conversation["metadata"] == {"key": "value"}
    assert conversation["message_count"] == 0
    assert "created_at" in conversation
    assert "updated_at" in conversation


def test_create_conversation_minimal(manager):
    """Test creating a conversation with minimal data."""
    conversation = manager.create_conversation(title="Minimal")
    
    assert conversation["title"] == "Minimal"
    assert conversation["agent_type"] is None
    assert conversation["metadata"] == {}


def test_get_conversation(manager):
    """Test retrieving a conversation."""
    # Create conversation
    created = manager.create_conversation(title="Test")
    
    # Retrieve it
    conversation = manager.get_conversation(created["id"])
    
    assert conversation is not None
    assert conversation["id"] == created["id"]
    assert conversation["title"] == "Test"
    assert "messages" in conversation
    assert conversation["messages"] == []


def test_get_conversation_not_found(manager):
    """Test retrieving a non-existent conversation."""
    conversation = manager.get_conversation("nonexistent-id")
    assert conversation is None


def test_get_conversation_without_messages(manager):
    """Test retrieving a conversation without messages."""
    created = manager.create_conversation(title="Test")
    conversation = manager.get_conversation(created["id"], include_messages=False)
    
    assert conversation is not None
    assert "messages" not in conversation
    assert conversation["message_count"] == 0


def test_list_conversations_empty(manager):
    """Test listing conversations when none exist."""
    conversations, total = manager.list_conversations()
    
    assert conversations == []
    assert total == 0


def test_list_conversations(manager):
    """Test listing conversations."""
    # Create multiple conversations
    manager.create_conversation(title="Conversation 1")
    manager.create_conversation(title="Conversation 2")
    manager.create_conversation(title="Conversation 3")
    
    conversations, total = manager.list_conversations()
    
    assert len(conversations) == 3
    assert total == 3
    # Should be ordered by updated_at DESC
    assert conversations[0]["title"] == "Conversation 3"


def test_list_conversations_pagination(manager):
    """Test pagination in listing conversations."""
    # Create 5 conversations
    for i in range(5):
        manager.create_conversation(title=f"Conversation {i}")
    
    # Get first page
    page1, total = manager.list_conversations(skip=0, limit=2)
    assert len(page1) == 2
    assert total == 5
    
    # Get second page
    page2, total = manager.list_conversations(skip=2, limit=2)
    assert len(page2) == 2
    assert page1[0]["id"] != page2[0]["id"]
    
    # Get last page
    page3, total = manager.list_conversations(skip=4, limit=2)
    assert len(page3) == 1


def test_list_conversations_by_agent_type(manager):
    """Test filtering conversations by agent type."""
    manager.create_conversation(title="Conv 1", agent_type="agent_a")
    manager.create_conversation(title="Conv 2", agent_type="agent_b")
    manager.create_conversation(title="Conv 3", agent_type="agent_a")
    
    conversations, total = manager.list_conversations(agent_type="agent_a")
    
    assert len(conversations) == 2
    assert total == 2
    for conv in conversations:
        assert conv["agent_type"] == "agent_a"


def test_add_message(manager):
    """Test adding a message to a conversation."""
    # Create conversation
    conversation = manager.create_conversation(title="Test")
    
    # Add message
    message = manager.add_message(
        conversation_id=conversation["id"],
        role="user",
        content="Hello, world!",
        metadata={"source": "test"}
    )
    
    assert "id" in message
    assert message["conversation_id"] == conversation["id"]
    assert message["role"] == "user"
    assert message["content"] == "Hello, world!"
    assert message["metadata"] == {"source": "test"}
    assert "timestamp" in message


def test_add_message_invalid_role(manager):
    """Test adding a message with invalid role."""
    conversation = manager.create_conversation(title="Test")
    
    with pytest.raises(ValueError, match="Invalid role"):
        manager.add_message(
            conversation_id=conversation["id"],
            role="invalid",
            content="Test"
        )


def test_add_message_invalid_conversation(manager):
    """Test adding a message to non-existent conversation."""
    with pytest.raises(ValueError, match="Conversation not found"):
        manager.add_message(
            conversation_id="nonexistent",
            role="user",
            content="Test"
        )


def test_add_multiple_messages(manager):
    """Test adding multiple messages to a conversation."""
    conversation = manager.create_conversation(title="Test")
    
    # Add messages
    manager.add_message(conversation["id"], "user", "Message 1")
    manager.add_message(conversation["id"], "agent", "Response 1")
    manager.add_message(conversation["id"], "user", "Message 2")
    
    # Retrieve conversation with messages
    retrieved = manager.get_conversation(conversation["id"])
    
    assert len(retrieved["messages"]) == 3
    assert retrieved["messages"][0]["role"] == "user"
    assert retrieved["messages"][1]["role"] == "agent"
    assert retrieved["messages"][2]["role"] == "user"


def test_delete_conversation(manager):
    """Test deleting a conversation."""
    conversation = manager.create_conversation(title="Test")
    
    # Delete it
    deleted = manager.delete_conversation(conversation["id"])
    
    assert deleted is True
    
    # Verify it's gone
    retrieved = manager.get_conversation(conversation["id"])
    assert retrieved is None


def test_delete_conversation_not_found(manager):
    """Test deleting a non-existent conversation."""
    deleted = manager.delete_conversation("nonexistent")
    assert deleted is False


def test_delete_conversation_with_messages(manager):
    """Test that deleting a conversation also deletes its messages."""
    conversation = manager.create_conversation(title="Test")
    manager.add_message(conversation["id"], "user", "Message 1")
    manager.add_message(conversation["id"], "agent", "Response 1")
    
    # Delete conversation
    manager.delete_conversation(conversation["id"])
    
    # Verify messages are also deleted
    with sqlite3.connect(manager.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
            (conversation["id"],)
        )
        count = cursor.fetchone()[0]
        assert count == 0


def test_search_conversations_by_title(manager):
    """Test searching conversations by title."""
    manager.create_conversation(title="Python Tutorial")
    manager.create_conversation(title="JavaScript Guide")
    manager.create_conversation(title="Python Advanced")
    
    results, total = manager.search_conversations("Python")
    
    assert len(results) == 2
    assert total == 2


def test_search_conversations_by_message_content(manager):
    """Test searching conversations by message content."""
    conv1 = manager.create_conversation(title="Conv 1")
    conv2 = manager.create_conversation(title="Conv 2")
    
    manager.add_message(conv1["id"], "user", "How to use Python?")
    manager.add_message(conv2["id"], "user", "JavaScript is great")
    
    results, total = manager.search_conversations("Python")
    
    assert len(results) == 1
    assert results[0]["id"] == conv1["id"]


def test_search_conversations_case_insensitive(manager):
    """Test that search is case-insensitive."""
    manager.create_conversation(title="Python Tutorial")
    
    results, total = manager.search_conversations("python")
    assert len(results) == 1
    
    results, total = manager.search_conversations("PYTHON")
    assert len(results) == 1


def test_search_conversations_pagination(manager):
    """Test pagination in search results."""
    for i in range(5):
        manager.create_conversation(title=f"Test Conversation {i}")
    
    page1, total = manager.search_conversations("Test", skip=0, limit=2)
    assert len(page1) == 2
    assert total == 5
    
    page2, total = manager.search_conversations("Test", skip=2, limit=2)
    assert len(page2) == 2


def test_export_conversation_markdown(manager):
    """Test exporting conversation as Markdown."""
    conversation = manager.create_conversation(title="Test Export")
    manager.add_message(conversation["id"], "user", "Hello!")
    manager.add_message(conversation["id"], "agent", "Hi there!")
    
    markdown = manager.export_conversation_markdown(conversation["id"])
    
    assert "# Test Export" in markdown
    assert "🧑 User" in markdown
    assert "🤖 Agent" in markdown
    assert "Hello!" in markdown
    assert "Hi there!" in markdown


def test_export_conversation_not_found(manager):
    """Test exporting a non-existent conversation."""
    with pytest.raises(ValueError, match="Conversation not found"):
        manager.export_conversation_markdown("nonexistent")


def test_update_conversation_title(manager):
    """Test updating conversation title."""
    conversation = manager.create_conversation(title="Original Title")
    
    updated = manager.update_conversation_title(
        conversation["id"],
        "New Title"
    )
    
    assert updated is True
    
    # Verify update
    retrieved = manager.get_conversation(conversation["id"])
    assert retrieved["title"] == "New Title"


def test_update_conversation_title_not_found(manager):
    """Test updating title of non-existent conversation."""
    updated = manager.update_conversation_title("nonexistent", "Title")
    assert updated is False


def test_get_statistics_empty(manager):
    """Test getting statistics when database is empty."""
    stats = manager.get_statistics()
    
    assert stats["total_conversations"] == 0
    assert stats["total_messages"] == 0
    assert stats["by_agent_type"] == {}
    assert stats["recent_activity"] == []


def test_get_statistics(manager):
    """Test getting conversation statistics."""
    # Create conversations with different agents
    conv1 = manager.create_conversation(title="Conv 1", agent_type="agent_a")
    conv2 = manager.create_conversation(title="Conv 2", agent_type="agent_b")
    conv3 = manager.create_conversation(title="Conv 3", agent_type="agent_a")
    
    # Add some messages
    manager.add_message(conv1["id"], "user", "Message 1")
    manager.add_message(conv1["id"], "agent", "Response 1")
    manager.add_message(conv2["id"], "user", "Message 2")
    
    stats = manager.get_statistics()
    
    assert stats["total_conversations"] == 3
    assert stats["total_messages"] == 3
    assert stats["by_agent_type"]["agent_a"] == 2
    assert stats["by_agent_type"]["agent_b"] == 1


def test_conversation_updated_at_changes(manager):
    """Test that updated_at changes when messages are added."""
    conversation = manager.create_conversation(title="Test")
    original_updated_at = conversation["updated_at"]
    
    import time
    time.sleep(0.1)  # Small delay to ensure timestamp differs
    
    # Add a message
    manager.add_message(conversation["id"], "user", "New message")
    
    # Retrieve conversation
    updated = manager.get_conversation(conversation["id"])
    
    assert updated["updated_at"] > original_updated_at


def test_message_count_accuracy(manager):
    """Test that message_count is accurate."""
    conversation = manager.create_conversation(title="Test")
    
    # Initially 0
    retrieved = manager.get_conversation(conversation["id"])
    assert retrieved["message_count"] == 0
    
    # Add messages
    for i in range(5):
        manager.add_message(conversation["id"], "user", f"Message {i}")
    
    # Should be 5
    retrieved = manager.get_conversation(conversation["id"])
    assert retrieved["message_count"] == 5


def test_concurrent_conversations(manager):
    """Test creating and managing multiple conversations concurrently."""
    conversations = []
    
    # Create 10 conversations
    for i in range(10):
        conv = manager.create_conversation(title=f"Conv {i}")
        conversations.append(conv)
    
    # Add messages to each
    for conv in conversations:
        manager.add_message(conv["id"], "user", f"Message in {conv['title']}")
    
    # Verify all exist and have messages
    for conv in conversations:
        retrieved = manager.get_conversation(conv["id"])
        assert retrieved is not None
        assert len(retrieved["messages"]) == 1


def test_special_characters_in_content(manager):
    """Test handling special characters in conversation data."""
    conversation = manager.create_conversation(
        title="Special: <>&\"'",
        metadata={"key": "value with 'quotes' and \"double quotes\""}
    )
    
    manager.add_message(
        conversation["id"],
        "user",
        "Message with special chars: <script>alert('test')</script>"
    )
    
    retrieved = manager.get_conversation(conversation["id"])
    assert retrieved["title"] == "Special: <>&\"'"
    assert "<script>" in retrieved["messages"][0]["content"]


def test_large_conversation(manager):
    """Test handling a conversation with many messages."""
    conversation = manager.create_conversation(title="Large Conversation")
    
    # Add 100 messages
    for i in range(100):
        role = "user" if i % 2 == 0 else "agent"
        manager.add_message(conversation["id"], role, f"Message {i}")
    
    retrieved = manager.get_conversation(conversation["id"])
    assert len(retrieved["messages"]) == 100
    assert retrieved["message_count"] == 100
