"""
Conversation History Manager

Manages conversation persistence using SQLite database.
Supports CRUD operations, search, export, and pagination.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import uuid

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation history with SQLite backend."""

    def __init__(self, db_path: str = "conversations.db"):
        """
        Initialize conversation manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"ConversationManager initialized with database: {db_path}")

    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        title TEXT,
                        agent_type TEXT,
                        metadata TEXT
                    )
                """)
                
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        conversation_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                    ON messages(conversation_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
                    ON conversations(updated_at DESC)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_agent_type 
                    ON conversations(agent_type)
                """)
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    def create_conversation(
        self,
        title: str,
        agent_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            title: Conversation title
            agent_type: Type of agent used
            metadata: Additional metadata
            
        Returns:
            Created conversation data
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversations (id, created_at, updated_at, title, agent_type, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conversation_id,
                        timestamp,
                        timestamp,
                        title,
                        agent_type,
                        json.dumps(metadata or {})
                    )
                )
                conn.commit()
                
                logger.info(f"Created conversation: {conversation_id}")
                
                return {
                    "id": conversation_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "title": title,
                    "agent_type": agent_type,
                    "metadata": metadata or {},
                    "message_count": 0
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to create conversation: {e}", exc_info=True)
            raise

    def get_conversation(
        self,
        conversation_id: str,
        include_messages: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            include_messages: Whether to include messages
            
        Returns:
            Conversation data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get conversation
                cursor.execute(
                    """
                    SELECT * FROM conversations WHERE id = ?
                    """,
                    (conversation_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"Conversation not found: {conversation_id}")
                    return None
                
                conversation = dict(row)
                conversation["metadata"] = json.loads(conversation["metadata"] or "{}")
                
                # Get message count
                cursor.execute(
                    """
                    SELECT COUNT(*) as count FROM messages WHERE conversation_id = ?
                    """,
                    (conversation_id,)
                )
                conversation["message_count"] = cursor.fetchone()["count"]
                
                # Get messages if requested
                if include_messages:
                    cursor.execute(
                        """
                        SELECT * FROM messages 
                        WHERE conversation_id = ? 
                        ORDER BY timestamp ASC
                        """,
                        (conversation_id,)
                    )
                    messages = []
                    for msg_row in cursor.fetchall():
                        msg = dict(msg_row)
                        msg["metadata"] = json.loads(msg["metadata"] or "{}")
                        messages.append(msg)
                    conversation["messages"] = messages
                
                return conversation
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}", exc_info=True)
            raise

    def list_conversations(
        self,
        skip: int = 0,
        limit: int = 20,
        agent_type: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List conversations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            agent_type: Filter by agent type
            
        Returns:
            Tuple of (conversations list, total count)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build query
                where_clause = ""
                params: List[Any] = []
                
                if agent_type:
                    where_clause = "WHERE agent_type = ?"
                    params.append(agent_type)
                
                # Get total count
                cursor.execute(
                    f"SELECT COUNT(*) as count FROM conversations {where_clause}",
                    params
                )
                total = cursor.fetchone()["count"]
                
                # Get conversations
                params.extend([limit, skip])
                cursor.execute(
                    f"""
                    SELECT c.*, COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    {where_clause}
                    GROUP BY c.id
                    ORDER BY c.updated_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    params
                )
                
                conversations = []
                for row in cursor.fetchall():
                    conv = dict(row)
                    conv["metadata"] = json.loads(conv["metadata"] or "{}")
                    conversations.append(conv)
                
                logger.info(f"Listed {len(conversations)} conversations (total: {total})")
                return conversations, total
                
        except sqlite3.Error as e:
            logger.error(f"Failed to list conversations: {e}", exc_info=True)
            raise

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'agent')
            content: Message content
            metadata: Additional metadata
            
        Returns:
            Created message data
            
        Raises:
            sqlite3.Error: If database operation fails
            ValueError: If role is invalid or conversation not found
        """
        if role not in ("user", "agent"):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'agent'")
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verify conversation exists
                cursor.execute(
                    "SELECT id FROM conversations WHERE id = ?",
                    (conversation_id,)
                )
                if not cursor.fetchone():
                    raise ValueError(f"Conversation not found: {conversation_id}")
                
                # Insert message
                cursor.execute(
                    """
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message_id,
                        conversation_id,
                        role,
                        content,
                        timestamp,
                        json.dumps(metadata or {})
                    )
                )
                
                # Update conversation timestamp
                cursor.execute(
                    """
                    UPDATE conversations SET updated_at = ? WHERE id = ?
                    """,
                    (timestamp, conversation_id)
                )
                
                conn.commit()
                
                logger.info(f"Added message to conversation {conversation_id}")
                
                return {
                    "id": message_id,
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp,
                    "metadata": metadata or {}
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to add message: {e}", exc_info=True)
            raise

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages (cascade should handle this, but be explicit)
                cursor.execute(
                    "DELETE FROM messages WHERE conversation_id = ?",
                    (conversation_id,)
                )
                
                # Delete conversation
                cursor.execute(
                    "DELETE FROM conversations WHERE id = ?",
                    (conversation_id,)
                )
                
                deleted = cursor.rowcount > 0
                conn.commit()
                
                if deleted:
                    logger.info(f"Deleted conversation: {conversation_id}")
                else:
                    logger.warning(f"Conversation not found for deletion: {conversation_id}")
                
                return deleted
                
        except sqlite3.Error as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}", exc_info=True)
            raise

    def search_conversations(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search conversations by title or message content.
        
        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (matching conversations, total count)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                search_pattern = f"%{query}%"
                
                # Get total count
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT c.id) as count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.title LIKE ? OR m.content LIKE ?
                    """,
                    (search_pattern, search_pattern)
                )
                total = cursor.fetchone()["count"]
                
                # Get matching conversations
                cursor.execute(
                    """
                    SELECT DISTINCT c.*, COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.title LIKE ? OR c.id IN (
                        SELECT conversation_id FROM messages WHERE content LIKE ?
                    )
                    GROUP BY c.id
                    ORDER BY c.updated_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (search_pattern, search_pattern, limit, skip)
                )
                
                conversations = []
                for row in cursor.fetchall():
                    conv = dict(row)
                    conv["metadata"] = json.loads(conv["metadata"] or "{}")
                    conversations.append(conv)
                
                logger.info(f"Found {len(conversations)} conversations matching '{query}'")
                return conversations, total
                
        except sqlite3.Error as e:
            logger.error(f"Failed to search conversations: {e}", exc_info=True)
            raise

    def export_conversation_markdown(self, conversation_id: str) -> str:
        """
        Export conversation as Markdown format.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Markdown formatted conversation
            
        Raises:
            ValueError: If conversation not found
        """
        conversation = self.get_conversation(conversation_id, include_messages=True)
        
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Build Markdown
        lines = [
            f"# {conversation['title']}",
            "",
            f"**Created:** {conversation['created_at']}",
            f"**Updated:** {conversation['updated_at']}",
        ]
        
        if conversation.get("agent_type"):
            lines.append(f"**Agent:** {conversation['agent_type']}")
        
        lines.extend(["", "---", ""])
        
        # Add messages
        for msg in conversation.get("messages", []):
            role_label = "🧑 User" if msg["role"] == "user" else "🤖 Agent"
            lines.extend([
                f"## {role_label}",
                f"*{msg['timestamp']}*",
                "",
                msg["content"],
                "",
                "---",
                ""
            ])
        
        markdown = "\n".join(lines)
        logger.info(f"Exported conversation {conversation_id} to Markdown")
        return markdown

    def update_conversation_title(
        self,
        conversation_id: str,
        title: str
    ) -> bool:
        """
        Update conversation title.
        
        Args:
            conversation_id: Conversation ID
            title: New title
            
        Returns:
            True if updated, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                timestamp = datetime.utcnow().isoformat()
                
                cursor.execute(
                    """
                    UPDATE conversations 
                    SET title = ?, updated_at = ? 
                    WHERE id = ?
                    """,
                    (title, timestamp, conversation_id)
                )
                
                updated = cursor.rowcount > 0
                conn.commit()
                
                if updated:
                    logger.info(f"Updated conversation title: {conversation_id}")
                else:
                    logger.warning(f"Conversation not found for update: {conversation_id}")
                
                return updated
                
        except sqlite3.Error as e:
            logger.error(f"Failed to update conversation title: {e}", exc_info=True)
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Total conversations
                cursor.execute("SELECT COUNT(*) as count FROM conversations")
                total_conversations = cursor.fetchone()["count"]
                
                # Total messages
                cursor.execute("SELECT COUNT(*) as count FROM messages")
                total_messages = cursor.fetchone()["count"]
                
                # Conversations by agent type
                cursor.execute("""
                    SELECT agent_type, COUNT(*) as count 
                    FROM conversations 
                    WHERE agent_type IS NOT NULL
                    GROUP BY agent_type
                """)
                by_agent = {row["agent_type"]: row["count"] for row in cursor.fetchall()}
                
                # Recent activity
                cursor.execute("""
                    SELECT DATE(updated_at) as date, COUNT(*) as count
                    FROM conversations
                    WHERE updated_at >= date('now', '-7 days')
                    GROUP BY DATE(updated_at)
                    ORDER BY date DESC
                """)
                recent_activity = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "by_agent_type": by_agent,
                    "recent_activity": recent_activity
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get statistics: {e}", exc_info=True)
            raise

    def close(self) -> None:
        """Close database connection. (SQLite auto-closes, but kept for consistency)"""
        logger.info("ConversationManager closed")
