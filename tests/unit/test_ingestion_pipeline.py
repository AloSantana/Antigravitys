"""
Unit tests for backend.rag.ingest module
Tests the IngestionPipeline class for file processing and ingestion
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open


@pytest.mark.unit
@pytest.mark.asyncio
class TestIngestionPipeline:
    """Test suite for IngestionPipeline class."""
    
    async def test_initialization(self, temp_dir):
        """Test IngestionPipeline initializes correctly."""
        with patch('backend.rag.ingest.LocalClient'), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            assert pipeline.watch_dir == str(temp_dir)
            assert pipeline._batch_size == 5
            assert len(pipeline._supported_extensions) > 0
    
    async def test_process_folder_empty(self, temp_dir):
        """Test processing an empty folder."""
        with patch('backend.rag.ingest.LocalClient'), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            # Process empty folder - should complete without error
            await pipeline.process_folder(str(temp_dir))
    
    async def test_process_folder_with_supported_files(self, temp_dir, mock_local_client, mock_vector_store):
        """Test processing folder with supported file types."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            # Create test files
            (temp_dir / "test.md").write_text("# Markdown content")
            (temp_dir / "code.py").write_text("def hello(): pass")
            (temp_dir / "data.json").write_text('{"key": "value"}')
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            await pipeline.process_folder(str(temp_dir))
            
            # Should attempt to embed and store
            assert mock_local_client.embed.call_count >= 3
            assert mock_vector_store.add_documents.call_count >= 3
    
    async def test_process_folder_skips_unsupported_files(self, temp_dir, mock_local_client):
        """Test that unsupported files are skipped."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            # Create unsupported file
            (temp_dir / "image.png").write_bytes(b"fake image data")
            (temp_dir / "binary.exe").write_bytes(b"binary data")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            await pipeline.process_folder(str(temp_dir))
            
            # Should not attempt to embed unsupported files
            assert mock_local_client.embed.call_count == 0
    
    async def test_ingest_file_success(self, temp_dir, mock_local_client, mock_vector_store):
        """Test successful file ingestion."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            test_file = temp_dir / "test.txt"
            test_file.write_text("Test content")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            result = await pipeline._ingest_file(str(test_file))
            
            assert result is True
            mock_local_client.embed.assert_called_once()
            mock_vector_store.add_documents.assert_called_once()
    
    async def test_ingest_file_too_large(self, temp_dir, mock_local_client):
        """Test file size limit."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            # Create large file
            large_file = temp_dir / "large.txt"
            large_content = "x" * (2 * 1024 * 1024)  # 2MB
            large_file.write_text(large_content)
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            result = await pipeline._ingest_file(str(large_file))
            
            assert result is False  # Should skip large files
            mock_local_client.embed.assert_not_called()
    
    async def test_ingest_file_empty(self, temp_dir, mock_local_client):
        """Test handling empty files."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            empty_file = temp_dir / "empty.txt"
            empty_file.write_text("")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            result = await pipeline._ingest_file(str(empty_file))
            
            assert result is False
            mock_local_client.embed.assert_not_called()
    
    async def test_ingest_file_binary_error(self, temp_dir, mock_local_client):
        """Test handling binary files (Unicode decode error)."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            binary_file = temp_dir / "binary.dat"
            binary_file.write_bytes(b'\x00\x01\x02\x03\x04')
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            result = await pipeline._ingest_file(str(binary_file))
            
            # Should handle gracefully
            assert result is False
    
    async def test_ingest_file_embedding_failure(self, temp_dir, mock_local_client, mock_vector_store):
        """Test handling embedding generation failure."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            test_file = temp_dir / "test.txt"
            test_file.write_text("Test content")
            
            # Embedding fails
            mock_local_client.embed = AsyncMock(return_value=None)
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            result = await pipeline._ingest_file(str(test_file))
            
            # Should complete but not store
            assert result is True
            mock_vector_store.add_documents.assert_not_called()
    
    async def test_split_content_small_file(self, temp_dir):
        """Test content splitting for small files."""
        with patch('backend.rag.ingest.LocalClient'), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            content = "Small content"
            file_path = str(temp_dir / "small.txt")
            
            chunks = pipeline._split_content(content, file_path)
            
            assert len(chunks) == 1
            assert chunks[0][0] == content
            assert chunks[0][1]["total_chunks"] == 1
    
    async def test_split_content_large_file(self, temp_dir):
        """Test content splitting for large files."""
        with patch('backend.rag.ingest.LocalClient'), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            # Create large content
            content = "x" * 5000  # > 2000 chars
            file_path = str(temp_dir / "large.txt")
            
            chunks = pipeline._split_content(content, file_path)
            
            assert len(chunks) > 1
            # Verify metadata
            for chunk_content, metadata in chunks:
                assert "source" in metadata
                assert "filename" in metadata
                assert "chunk_id" in metadata
                assert "total_chunks" in metadata
    
    async def test_split_content_with_overlap(self, temp_dir):
        """Test that content splitting includes overlap."""
        with patch('backend.rag.ingest.LocalClient'), \
             patch('backend.rag.ingest.VectorStore'):
            from backend.rag.ingest import IngestionPipeline
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            content = "A" * 3000  # Multiple chunks needed
            file_path = str(temp_dir / "test.txt")
            
            chunks = pipeline._split_content(content, file_path)
            
            # Should have overlap between chunks
            assert len(chunks) >= 2
    
    async def test_process_folder_batch_processing(self, temp_dir, mock_local_client, mock_vector_store):
        """Test batch processing of multiple files."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            # Create many files
            for i in range(10):
                (temp_dir / f"file{i}.txt").write_text(f"Content {i}")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            pipeline._batch_size = 3  # Small batch for testing
            
            await pipeline.process_folder(str(temp_dir))
            
            # Should process all files
            assert mock_local_client.embed.call_count == 10
    
    async def test_process_folder_handles_errors(self, temp_dir, mock_local_client, mock_vector_store):
        """Test that errors in one file don't stop processing others."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            # Create files
            (temp_dir / "good1.txt").write_text("Good content 1")
            (temp_dir / "bad.txt").write_text("Bad content")
            (temp_dir / "good2.txt").write_text("Good content 2")
            
            # Make one file fail
            def embed_side_effect(text):
                if "Bad" in text:
                    raise Exception("Embedding failed")
                return [0.1] * 768
            
            mock_local_client.embed = AsyncMock(side_effect=embed_side_effect)
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            # Should complete despite error
            await pipeline.process_folder(str(temp_dir))
            
            # Good files should still be processed
            assert mock_local_client.embed.call_count >= 2
    
    async def test_process_folder_recursive(self, temp_dir, mock_local_client, mock_vector_store):
        """Test recursive folder processing."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            # Create nested structure
            subdir = temp_dir / "subdir"
            subdir.mkdir()
            (temp_dir / "root.txt").write_text("Root file")
            (subdir / "sub.txt").write_text("Sub file")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            await pipeline.process_folder(str(temp_dir))
            
            # Should process both files
            assert mock_local_client.embed.call_count == 2
    
    @pytest.mark.parametrize("extension", [".md", ".py", ".js", ".txt", ".html", ".css", ".json"])
    async def test_supported_extensions(self, extension, temp_dir, mock_local_client, mock_vector_store):
        """Test that all supported extensions are processed."""
        with patch('backend.rag.ingest.LocalClient', return_value=mock_local_client), \
             patch('backend.rag.ingest.VectorStore', return_value=mock_vector_store):
            from backend.rag.ingest import IngestionPipeline
            
            test_file = temp_dir / f"test{extension}"
            test_file.write_text("Test content")
            
            pipeline = IngestionPipeline(watch_dir=str(temp_dir))
            
            await pipeline.process_folder(str(temp_dir))
            
            assert mock_local_client.embed.call_count == 1
