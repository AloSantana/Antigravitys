"""
Context Fusion Engine for Antigravity Workspace
Cross-session intelligence that surfaces relevant past conversations and knowledge.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ContextFusionEngine:
    """
    Cross-session intelligence engine that retrieves relevant context
    from past conversations and the RAG vector store.
    
    Combines:
    - Conversation history search (SQLite full-text)
    - RAG vector store semantic search (ChromaDB)
    - Relevance scoring and merging
    """

    # Max tokens of injected context to avoid prompt bloat
    MAX_CONTEXT_TOKENS = 2000
    # Approximate chars per token
    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        conversation_manager=None,
        vector_store=None,
        embedding_fn=None,
    ):
        """
        Args:
            conversation_manager: ConversationManager instance for history search
            vector_store: VectorStore instance for semantic search
            embedding_fn: Async callable that takes str -> List[float] for embeddings
        """
        self.conversation_manager = conversation_manager
        self.vector_store = vector_store
        self.embedding_fn = embedding_fn
        self._cache: Dict[str, Any] = {}

    def get_relevant_context(
        self,
        query: str,
        limit: int = 5,
        exclude_conversation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant past context from all available sources.
        
        Args:
            query: The user's current query
            limit: Max results to return
            exclude_conversation_id: Skip this conversation (usually the current one)
            
        Returns:
            List of { source, content, score, metadata } dicts sorted by relevance
        """
        results = []

        # Source 1: Conversation history (SQLite full-text search)
        results.extend(
            self._search_conversations(query, limit, exclude_conversation_id)
        )

        # Source 2: RAG vector store (semantic search) — sync wrapper
        results.extend(self._search_vector_store_sync(query, limit))

        # Deduplicate by content similarity
        results = self._deduplicate(results)

        # Sort by score descending and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    async def get_relevant_context_async(
        self,
        query: str,
        limit: int = 5,
        exclude_conversation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Async version that can use embedding_fn for vector search.
        """
        results = []

        # Source 1: Conversation history
        results.extend(
            self._search_conversations(query, limit, exclude_conversation_id)
        )

        # Source 2: RAG vector store (async with embeddings)
        results.extend(await self._search_vector_store_async(query, limit))

        results = self._deduplicate(results)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def build_augmented_prompt(
        self,
        query: str,
        context_items: Optional[List[Dict[str, Any]]] = None,
        agent_context: str = "",
    ) -> str:
        """
        Build a prompt augmented with relevant past context.
        
        Args:
            query: The user's current query
            context_items: Pre-fetched context items (if None, fetches automatically)
            agent_context: Optional agent system prompt to prepend
            
        Returns:
            Augmented prompt string
        """
        if context_items is None:
            context_items = self.get_relevant_context(query, limit=3)

        if not context_items:
            if agent_context:
                return f"{agent_context}\n\nUser Request: {query}"
            return query

        # Build context section within token budget
        max_chars = self.MAX_CONTEXT_TOKENS * self.CHARS_PER_TOKEN
        context_parts = []
        total_chars = 0

        for item in context_items:
            snippet = item["content"]
            if total_chars + len(snippet) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 100:
                    snippet = snippet[:remaining] + "..."
                else:
                    break
            context_parts.append(
                f"[{item['source']}] {snippet}"
            )
            total_chars += len(snippet)

        context_block = "\n\n".join(context_parts)

        parts = []
        if agent_context:
            parts.append(agent_context)
        parts.append(f"Relevant Past Context:\n{context_block}")
        parts.append(f"User Request: {query}")

        return "\n\n".join(parts)

    def index_conversation(self, conversation_id: str) -> bool:
        """
        Index a completed conversation into the RAG vector store for future retrieval.
        
        Args:
            conversation_id: ID of the conversation to index
            
        Returns:
            True if indexed successfully
        """
        if not self.conversation_manager or not self.vector_store:
            logger.warning("Cannot index: missing conversation_manager or vector_store")
            return False

        try:
            messages = self.conversation_manager.get_messages(conversation_id)
            if not messages:
                return False

            # Build document chunks from conversation
            documents = []
            metadatas = []
            ids = []

            for i, msg in enumerate(messages):
                content = msg.get("content", "")
                if not content or len(content) < 20:
                    continue

                doc_id = f"conv_{conversation_id}_{i}"
                documents.append(content)
                metadatas.append({
                    "source": "conversation",
                    "conversation_id": conversation_id,
                    "role": msg.get("role", "unknown"),
                    "timestamp": msg.get("timestamp", ""),
                    "message_index": i,
                })
                ids.append(doc_id)

            if documents:
                self.vector_store.add_documents(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
                logger.info(
                    f"Indexed {len(documents)} messages from conversation {conversation_id}"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to index conversation {conversation_id}: {e}")

        return False

    # ── Private Methods ──────────────────────────────────────────

    def _search_conversations(
        self,
        query: str,
        limit: int,
        exclude_conversation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search conversation history via ConversationManager."""
        if not self.conversation_manager:
            return []

        try:
            results = self.conversation_manager.search_conversations(query)
            items = []

            for conv in results[:limit]:
                conv_id = conv.get("id", "")
                if conv_id == exclude_conversation_id:
                    continue

                # Use title + last messages as content
                title = conv.get("title", "")
                preview = conv.get("preview", conv.get("last_message", ""))
                content = f"{title}: {preview}" if title else preview

                if content:
                    # Simple relevance: keyword overlap ratio
                    query_words = set(query.lower().split())
                    content_words = set(content.lower().split())
                    overlap = len(query_words & content_words)
                    score = overlap / max(len(query_words), 1) * 0.7  # Cap at 0.7

                    items.append({
                        "source": "conversation_history",
                        "content": content[:500],
                        "score": round(score, 3),
                        "metadata": {
                            "conversation_id": conv_id,
                            "title": title,
                        },
                    })

            return items

        except Exception as e:
            logger.error(f"Conversation search failed: {e}")
            return []

    def _search_vector_store_sync(
        self, query: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Synchronous vector store search (no embeddings, returns empty if unavailable)."""
        # Without an embedding function, we can't do vector search synchronously
        return []

    async def _search_vector_store_async(
        self, query: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Async vector store search using embedding function."""
        if not self.vector_store or not self.embedding_fn:
            return []

        try:
            query_embedding = await self.embedding_fn(query)
            if not query_embedding:
                return []

            raw_results = self.vector_store.query(
                query_embeddings=[query_embedding], n_results=limit
            )

            if not raw_results or not raw_results.get("documents"):
                return []

            items = []
            documents = raw_results["documents"][0]
            distances = raw_results.get("distances", [[]])[0]
            metadatas = raw_results.get("metadatas", [[]])[0]

            for i, doc in enumerate(documents):
                # ChromaDB returns distances; convert to similarity score
                distance = distances[i] if i < len(distances) else 1.0
                score = max(0, 1.0 - distance)

                meta = metadatas[i] if i < len(metadatas) else {}

                items.append({
                    "source": "vector_store",
                    "content": doc[:500],
                    "score": round(score, 3),
                    "metadata": meta,
                })

            return items

        except Exception as e:
            logger.error(f"Vector store search failed: {e}")
            return []

    def _deduplicate(
        self, items: List[Dict[str, Any]], threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Remove near-duplicate results based on content overlap."""
        if len(items) <= 1:
            return items

        unique = [items[0]]
        for item in items[1:]:
            is_dup = False
            item_words = set(item["content"].lower().split())

            for existing in unique:
                existing_words = set(existing["content"].lower().split())
                if not item_words or not existing_words:
                    continue
                overlap = len(item_words & existing_words) / max(
                    min(len(item_words), len(existing_words)), 1
                )
                if overlap >= threshold:
                    is_dup = True
                    break

            if not is_dup:
                unique.append(item)

        return unique
