"""
Integration tests for RAG pipeline
Tests end-to-end RAG workflow: ingest → store → query
"""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
@pytest.mark.asyncio
class TestRAGPipeline:
    """Test suite for complete RAG pipeline."""
    
    async def test_complete_rag_workflow(self, temp_dir, mock_local_client, mock_vector_store):
        """Test complete RAG workflow: ingest, store, query."""
        from backend.rag.ingest import IngestionPipeline
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):

            
            # Create test documents
            (temp_dir / "doc1.md").write_text("# Document 1\nPython is great")
            (temp_dir / "doc2.py").write_text("def hello(): return 'world'")
            
            # Ingest documents
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            await pipeline.process_folder(str(temp_dir))
            
            # Verify documents were embedded and stored
            assert mock_local_client.embed.call_count >= 2
            assert mock_vector_store.add_documents_batch.call_count >= 2
            
            # Query the store
            query_embedding = [0.1] * 768
            results = mock_vector_store.query([query_embedding], n_results=5)
            
            assert results is not None
            assert 'documents' in results
    
    async def test_rag_with_orchestrator(self, temp_dir, mock_local_client, mock_vector_store):
        """Test RAG integration with orchestrator."""
        from backend.agent.orchestrator import Orchestrator
        with patch('backend.agent.orchestrator.LocalClient', return_value=mock_local_client), \
             patch('backend.agent.orchestrator.GeminiClient') as MockGemini, \
             patch('backend.agent.orchestrator.VectorStore', return_value=mock_vector_store):
            
            mock_gemini = AsyncMock()
            mock_gemini.generate = AsyncMock(return_value="Gemini response")
            mock_gemini.embed = AsyncMock(return_value=[0.1] * 768)
            MockGemini.return_value = mock_gemini

            
            # Setup mock store to return results
            mock_vector_store.query.return_value = {
                'documents': [['Python is a programming language', 'FastAPI is a web framework']],
                'metadatas': [[{'source': 'doc1.md'}, {'source': 'doc2.md'}]],
            }
            
            orchestrator = Orchestrator()
            
            # Force complexity to high to trigger RAG
            with patch.object(orchestrator, '_assess_complexity', return_value="high"):
                response = await orchestrator.process_request("Detailed analysis of Python features")
            
            # Should use RAG context
            assert 'response' in response
            mock_gemini.embed.assert_called()
    
    async def test_rag_handles_empty_results(self, temp_dir, mock_local_client, mock_vector_store):
        """Test RAG pipeline handles empty query results."""
        from backend.agent.orchestrator import Orchestrator
        with patch('backend.agent.orchestrator.LocalClient', return_value=mock_local_client), \
             patch('backend.agent.orchestrator.GeminiClient') as MockGemini, \
             patch('backend.agent.orchestrator.VectorStore', return_value=mock_vector_store):
            
            mock_gemini = AsyncMock()
            mock_gemini.generate = AsyncMock(return_value="Gemini response")
            MockGemini.return_value = mock_gemini

            
            # Empty results
            mock_vector_store.query.return_value = {
                'documents': [[]],
                'metadatas': [[]],
            }
            
            orchestrator = Orchestrator()
            response = await orchestrator.process_request("Query with no results")
            
            # Should still complete
            assert 'response' in response
    
    async def test_rag_with_large_documents(self, temp_dir, mock_local_client, mock_vector_store):
        """Test RAG pipeline with large documents."""
        from backend.rag.ingest import IngestionPipeline
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):

            
            # Create large document
            large_content = "Large document content. " * 500  # ~10KB
            (temp_dir / "large.txt").write_text(large_content)
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            await pipeline.process_folder(str(temp_dir))
            
            # Should be chunked
            # Verify multiple chunks were created
            embed_call_count = mock_local_client.embed.call_count
            assert embed_call_count >= 2  # Should create multiple chunks
    
    async def test_rag_concurrent_ingestion(self, temp_dir, mock_local_client, mock_vector_store):
        """Test concurrent document ingestion."""
        from backend.rag.ingest import IngestionPipeline
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):

            
            # Create many documents
            for i in range(20):
                (temp_dir / f"doc{i}.txt").write_text(f"Document {i} content")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            pipeline._batch_size = 5
            
            await pipeline.process_folder(str(temp_dir))
            
            # All should be processed
            assert mock_local_client.embed.call_count == 20


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgentOrchestration:
    """Test suite for multi-agent coordination."""
    
    async def test_orchestrator_routing_decision(self, mock_local_client):
        """Test orchestrator makes correct routing decisions."""
        with patch('backend.agent.orchestrator.LocalClient', return_value=mock_local_client), \
             patch('backend.agent.orchestrator.GeminiClient') as MockGemini, \
             patch('backend.agent.orchestrator.VectorStore'), \
             patch.dict('os.environ', {'ACTIVE_MODEL': 'auto'}):
            
            mock_gemini = AsyncMock()
            mock_gemini.generate = AsyncMock(return_value="Gemini response")
            MockGemini.return_value = mock_gemini
            
            from backend.agent.orchestrator import Orchestrator
            
            orchestrator = Orchestrator()
            # Ensure model is auto
            orchestrator.active_model = "auto"
            
            # High complexity → Gemini
            response = await orchestrator.process_request("Design a complex architecture")
            assert response['source'] in ('Gemini', 'Vertex AI')
            
            # Low complexity → Gemini (Local fallback disabled in auto mode)
            mock_local_client.generate.reset_mock()
            response = await orchestrator.process_request("Hello")
            assert response['source'] in ('Gemini', 'Vertex AI')
    
    async def test_orchestrator_fallback_mechanism(self, mock_local_client):
        """Test orchestrator falls back correctly."""
        with patch('backend.agent.orchestrator.LocalClient', return_value=mock_local_client), \
             patch('backend.agent.orchestrator.GeminiClient') as MockGemini, \
             patch('backend.agent.orchestrator.VectorStore'):
            
            # Local fails
            mock_local_client.generate = AsyncMock(return_value="Error: Could not connect")
            
            mock_gemini = AsyncMock()
            mock_gemini.generate = AsyncMock(return_value="Fallback response")
            MockGemini.return_value = mock_gemini
            
            from backend.agent.orchestrator import Orchestrator
            
            orchestrator = Orchestrator()
            response = await orchestrator.process_request("Simple task")
            
            # Should fallback to Gemini
            assert response['source'] == 'Gemini'
            assert response['response'] == 'Fallback response'
