import logging
import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Constants
# Compute absolute path to the project root (store.py → rag/ → backend/ → project root)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_PERSIST_DIR = os.path.join(_PROJECT_ROOT, "data", "chroma")
DEFAULT_CACHE_TTL = 60
DEFAULT_CACHE_SIZE = 50

try:
    import chromadb
    from chromadb.config import Settings
except Exception as e:
    logger.warning(f"Failed to import chromadb: {e}. Vector capabilities will be disabled.")
    logger.debug("This is likely due to pydantic version conflicts (v1 vs v2). Running in resilience mode.")
    chromadb = None
    Settings = None

class VectorStore:
    def __init__(self, persist_directory: str = DEFAULT_PERSIST_DIR):
        self.persist_directory = Path(persist_directory)
        self._init_successful = False
        
        # Initialize state
        self.client = None
        self.collection = None
        self._query_cache: OrderedDict[str, tuple[Dict[str, Any], float]] = OrderedDict()
        
        # Performance metrics
        self._query_count = 0
        self._cache_hits = 0
        self._add_count = 0
        self._batch_add_count = 0
        
        try:
            # Create directory if it doesn't exist
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB
            if chromadb:
                self.client = chromadb.Client()
                self.collection = self.client.get_or_create_collection(name="knowledge_base")
                self._init_successful = True
                logger.info("VectorStore initialized successfully (in-memory mode)")
            else:
                logger.warning("chromadb module not available - running in resilience mode")
            
            # Configure cache
            self._query_cache_ttl = int(os.getenv("VECTOR_QUERY_CACHE_TTL", str(DEFAULT_CACHE_TTL)))
            self._query_cache_max_size = int(os.getenv("VECTOR_QUERY_CACHE_SIZE", str(DEFAULT_CACHE_SIZE)))
            
            logger.info(f"Query cache initialized: {self._query_cache_max_size} entries")
            
        except Exception as e:
            logger.error(f"VectorStore initialization error: {e}", exc_info=True)
            logger.info("Running without persistent storage (Resilience Mode)")
            # Fallback values are already set via init state

    def _get_query_cache_key(self, query_embeddings: List[List[float]], n_results: int) -> str:
        """Generate cache key for query embeddings."""
        # Hash the first embedding vector and n_results for cache key
        embedding_str = str(query_embeddings[0][:10])  # Use first 10 dimensions
        cache_str = f"{embedding_str}_{n_results}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str], embeddings: List[List[float]] = None):
        """
        Adds documents to the collection. 
        If embeddings are provided, they are used. Otherwise, Chroma's default is used (if configured).
        Since we want to use our LocalClient for embeddings, we should pass them in.
        """
        if not self.collection:
            logger.debug("VectorStore not initialized, skipping document add")
            return
            
        if embeddings:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        else:
            # Fallback to default if no embeddings provided (not recommended if we want specific local model)
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        self._add_count += len(documents)
        logger.info(f"Added {len(documents)} documents to VectorStore (total: {self._add_count})")
    
    def add_documents_batch(self, batch_data: List[tuple[str, Dict[str, Any], str, List[float]]]) -> int:
        """
        Add multiple documents in a single batch operation for better performance.
        
        Args:
            batch_data: List of tuples (document, metadata, id, embedding)
            
        Returns:
            Number of documents successfully added
        """
        if not self.collection:
            logger.debug("VectorStore not initialized, skipping batch add")
            return 0
        
        if not batch_data:
            return 0
        
        try:
            documents, metadatas, ids, embeddings = zip(*batch_data)
            
            self.collection.add(
                documents=list(documents),
                metadatas=list(metadatas),
                ids=list(ids),
                embeddings=list(embeddings)
            )
            
            self._add_count += len(batch_data)
            self._batch_add_count += 1
            logger.info(f"Batch added {len(batch_data)} documents (batch #{self._batch_add_count}, total: {self._add_count})")
            return len(batch_data)
        except Exception as e:
            logger.error(f"Error in batch add: {e}")
            return 0

    def query(self, query_embeddings: List[List[float]], n_results: int = 5, use_cache: bool = True) -> Dict[str, Any]:
        """
        Queries the collection using embeddings with optional caching for better performance.
        
        Args:
            query_embeddings: List of embedding vectors to query with
            n_results: Number of results to return
            use_cache: Whether to use query cache (default: True)
            
        Returns:
            Query results dictionary
        """
        if not self.collection:
            return {"documents": [], "metadatas": [], "ids": []}
        
        self._query_count += 1
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._get_query_cache_key(query_embeddings, n_results)
            
            if cache_key in self._query_cache:
                cached_result, timestamp = self._query_cache[cache_key]
                if time.time() - timestamp < self._query_cache_ttl:
                    self._cache_hits += 1
                    self._query_cache.move_to_end(cache_key)  # LRU update
                    return cached_result
                else:
                    # Expired
                    del self._query_cache[cache_key]
        
        # Perform query
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        
        # Cache result if caching enabled
        if use_cache:
            cache_key = self._get_query_cache_key(query_embeddings, n_results)
            self._query_cache[cache_key] = (results, time.time())
            self._query_cache.move_to_end(cache_key)
            
            # Evict oldest if cache is full
            while len(self._query_cache) > self._query_cache_max_size:
                self._query_cache.popitem(last=False)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        cache_hit_rate = self._cache_hits / self._query_count if self._query_count > 0 else 0.0
        
        return {
            "total_queries": self._query_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "cache_hit_rate_percentage": f"{cache_hit_rate * 100:.2f}%",
            "cache_size": len(self._query_cache),
            "max_cache_size": self._query_cache_max_size,
            "documents_added": self._add_count,
            "batch_operations": self._batch_add_count,
            "collection_count": self.collection.count() if self.collection else 0
        }
    
    def clear_cache(self) -> int:
        """
        Clear query result cache.
        
        Returns:
            Number of entries cleared
        """
        cleared = len(self._query_cache)
        self._query_cache.clear()
        return cleared
