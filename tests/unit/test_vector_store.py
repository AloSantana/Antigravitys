"""
Unit tests for backend.rag.store module
Tests the VectorStore class for ChromaDB operations
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestVectorStore:
    """Test suite for VectorStore class."""
    
    def test_initialization_success(self, temp_dir):
        """Test VectorStore initializes successfully."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_client = Mock()
            mock_collection = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            persist_dir = str(temp_dir / "chroma")
            store = VectorStore(persist_directory=persist_dir)
            
            assert store.client is not None
            assert store.collection is not None
            mock_client.get_or_create_collection.assert_called_once_with(name="knowledge_base")
    
    def test_initialization_failure(self):
        """Test VectorStore handles initialization failure gracefully."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_chromadb.Client.side_effect = Exception("ChromaDB not available")
            
            store = VectorStore()
            
            assert store.client is None
            assert store.collection is None
    
    def test_add_documents_with_embeddings(self):
        """Test adding documents with embeddings."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            documents = ["Document 1", "Document 2"]
            metadatas = [{"source": "file1.txt"}, {"source": "file2.txt"}]
            ids = ["id1", "id2"]
            embeddings = [[0.1, 0.2], [0.3, 0.4]]
            
            store.add_documents(documents, metadatas, ids, embeddings)
            
            mock_collection.add.assert_called_once_with(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
    
    def test_add_documents_without_embeddings(self):
        """Test adding documents without embeddings (fallback)."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            documents = ["Document 1"]
            metadatas = [{"source": "file1.txt"}]
            ids = ["id1"]
            
            store.add_documents(documents, metadatas, ids, embeddings=None)
            
            mock_collection.add.assert_called_once_with(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def test_add_documents_when_not_initialized(self):
        """Test adding documents when VectorStore is not initialized."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_chromadb.Client.side_effect = Exception("Init failed")
            
            store = VectorStore()
            
            # Should not raise exception
            store.add_documents(["doc"], [{"meta": "data"}], ["id1"], [[0.1]])
            
            # No assertion needed - just verify it doesn't crash
    
    def test_query_success(self):
        """Test querying the vector store."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            expected_results = {
                'documents': [['Doc1', 'Doc2']],
                'metadatas': [[{'source': 'file1'}, {'source': 'file2'}]],
                'ids': [['id1', 'id2']],
                'distances': [[0.1, 0.2]]
            }
            mock_collection.query.return_value = expected_results
            
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            query_embeddings = [[0.1, 0.2, 0.3]]
            results = store.query(query_embeddings, n_results=5)
            
            assert results == expected_results
            mock_collection.query.assert_called_once_with(
                query_embeddings=query_embeddings,
                n_results=5
            )
    
    def test_query_when_not_initialized(self):
        """Test querying when VectorStore is not initialized."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_chromadb.Client.side_effect = Exception("Init failed")
            
            store = VectorStore()
            
            results = store.query([[0.1, 0.2]], n_results=5)
            
            # Should return empty results
            assert results == {"documents": [], "metadatas": [], "ids": []}
    
    def test_query_with_custom_n_results(self):
        """Test querying with custom number of results."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_collection.query.return_value = {
                'documents': [['Doc1', 'Doc2', 'Doc3']],
                'metadatas': [[{}, {}, {}]],
                'ids': [['id1', 'id2', 'id3']]
            }
            
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            results = store.query([[0.1]], n_results=3)
            
            mock_collection.query.assert_called_once_with(
                query_embeddings=[[0.1]],
                n_results=3
            )
    
    def test_multiple_add_documents_calls(self):
        """Test multiple calls to add_documents."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            # Add documents multiple times
            for i in range(3):
                store.add_documents(
                    [f"Doc {i}"],
                    [{"source": f"file{i}"}],
                    [f"id{i}"],
                    [[float(i)]]
                )
            
            assert mock_collection.add.call_count == 3
    
    def test_persistence_directory_creation(self, temp_dir):
        """Test that persistence directory is created."""
        with patch('backend.rag.store.chromadb'):
            from backend.rag.store import VectorStore
            
            persist_dir = temp_dir / "new_chroma_dir"
            
            VectorStore(persist_directory=str(persist_dir))
            
            # Directory should be created
            assert persist_dir.exists()
    
    @pytest.mark.parametrize("n_results", [1, 5, 10, 100])
    def test_query_various_n_results(self, n_results):
        """Test querying with various n_results values."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
            
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            store.query([[0.1]], n_results=n_results)
            
            call_kwargs = mock_collection.query.call_args[1]
            assert call_kwargs['n_results'] == n_results
    
    def test_add_documents_with_large_batch(self):
        """Test adding a large batch of documents."""
        with patch('backend.rag.store.chromadb') as mock_chromadb:
            from backend.rag.store import VectorStore
            
            mock_collection = Mock()
            mock_client = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.Client.return_value = mock_client
            
            store = VectorStore()
            
            # Large batch
            n_docs = 100
            documents = [f"Document {i}" for i in range(n_docs)]
            metadatas = [{"source": f"file{i}"} for i in range(n_docs)]
            ids = [f"id{i}" for i in range(n_docs)]
            embeddings = [[float(i)] for i in range(n_docs)]
            
            store.add_documents(documents, metadatas, ids, embeddings)
            
            mock_collection.add.assert_called_once()
            call_args = mock_collection.add.call_args[1]
            assert len(call_args['documents']) == n_docs
