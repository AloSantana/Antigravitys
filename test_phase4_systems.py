#!/usr/bin/env python3
"""
Quick test script to verify conversation and artifact systems work

Tests the core functionality without requiring full app startup.
"""

import sys
import os
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from conversation_manager import ConversationManager
from artifact_manager import ArtifactManager


def test_conversation_system():
    """Test conversation system basics."""
    print("Testing Conversation System...")
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    try:
        manager = ConversationManager(db_path=temp_db.name)
        
        # Create conversation
        conv = manager.create_conversation(
            title="Test Conversation",
            agent_type="test"
        )
        print(f"✓ Created conversation: {conv['id']}")
        
        # Add messages
        manager.add_message(conv['id'], 'user', 'Hello!')
        manager.add_message(conv['id'], 'agent', 'Hi there!')
        print("✓ Added messages")
        
        # Retrieve conversation
        retrieved = manager.get_conversation(conv['id'])
        assert len(retrieved['messages']) == 2
        print("✓ Retrieved conversation with messages")
        
        # Search
        results, total = manager.search_conversations('Test')
        assert len(results) == 1
        print("✓ Search works")
        
        # Export
        markdown = manager.export_conversation_markdown(conv['id'])
        assert 'Test Conversation' in markdown
        print("✓ Export works")
        
        # Statistics
        stats = manager.get_statistics()
        assert stats['total_conversations'] == 1
        print("✓ Statistics work")
        
        print("✅ Conversation system: ALL TESTS PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Conversation system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


def test_artifact_system():
    """Test artifact system basics."""
    print("Testing Artifact System...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = ArtifactManager(artifacts_dir=temp_dir)
        
        # Store artifact
        content = b"print('Hello, World!')"
        artifact = manager.store_artifact(
            content=content,
            filename="hello.py",
            agent="test"
        )
        print(f"✓ Stored artifact: {artifact['id']}")
        
        # Retrieve artifact
        retrieved = manager.get_artifact(artifact['id'])
        assert retrieved is not None
        print("✓ Retrieved artifact")
        
        # Read content
        read_content = manager.read_artifact_content(artifact['id'])
        assert read_content == content
        print("✓ Read artifact content")
        
        # List artifacts
        artifacts = manager.list_artifacts()
        assert len(artifacts) == 1
        print("✓ List artifacts works")
        
        # Search
        results = manager.search_artifacts('hello')
        assert len(results) == 1
        print("✓ Search works")
        
        # Preview
        preview = manager.export_artifact_preview(artifact['id'])
        assert preview is not None
        print("✓ Preview works")
        
        # Statistics
        stats = manager.get_statistics()
        assert stats['total_count'] == 1
        print("✓ Statistics work")
        
        print("✅ Artifact system: ALL TESTS PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Artifact system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 4: Conversation & Artifact Systems Quick Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_conversation_system())
    results.append(test_artifact_system())
    
    print("=" * 60)
    if all(results):
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
