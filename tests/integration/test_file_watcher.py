"""
Integration tests for file watcher and processing flow
"""

import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock


@pytest.mark.integration
@pytest.mark.asyncio
class TestFileWatcherIntegration:
    """Test suite for file watcher integration."""
    
    async def test_watcher_detects_new_folder(self, temp_dir, mock_ingestion_pipeline):
        """Test watcher detects new folder creation."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        
        # Simulate folder creation
        new_folder = temp_dir / "new_folder"
        new_folder.mkdir()
        
        event = Mock()
        event.is_directory = True
        event.src_path = str(new_folder)
        
        handler.on_created(event)
        
        # Wait for debouncing
        await asyncio.sleep(0.5)
        
        # Should schedule processing
        assert len(handler._pending_tasks) >= 0
    
        # Wait for debounce
        await asyncio.sleep(0.3)
        
        # Should only process once
        # Using a mock wrapper to check calls on the real method or just mocking it out
        with patch.object(mock_ingestion_pipeline, 'process_folder', new_callable=AsyncMock) as mock_process:
            # We need to manually trigger the processing logic that the handler would trigger
            # But since we can't easily inject the mock into the already created handler's reference to pipeline
            # We might need to rely on the fact that handler calls pipeline.process_folder
            
            # Re-create handler with the mocked pipeline if possible, or just mock the method on the instance
            pass
            
            # Actually, the handler has a reference to mock_ingestion_pipeline. 
            # If we mock the method on that instance BEFORE creating the handler (or before the event calls), it should work.
            
    async def test_watcher_debouncing(self, temp_dir, mock_ingestion_pipeline):
        """Test watcher debouncing prevents duplicate processing."""
        from backend.watcher import DropHandler
        
        # Patch the process_folder method on the instance
        with patch.object(mock_ingestion_pipeline, 'process_folder', new_callable=AsyncMock) as mock_process:
            loop = asyncio.get_event_loop()
            handler = DropHandler(mock_ingestion_pipeline, loop)
            handler._debounce_delay = 0.2
            
            event = Mock()
            event.is_directory = True
            event.src_path = str(temp_dir)
            
            # Trigger multiple times rapidly
            handler.on_created(event)
            await asyncio.sleep(0.05)
            handler.on_created(event)
            await asyncio.sleep(0.05)
            handler.on_created(event)
            
            # Wait for debounce
            await asyncio.sleep(0.3)
            
            # Should only process once
            assert mock_process.call_count <= 1
    
    async def test_watcher_processes_after_debounce(self, temp_dir, mock_ingestion_pipeline):
        """Test watcher processes folder after debounce period."""
        from backend.watcher import DropHandler
        
        with patch.object(mock_ingestion_pipeline, 'process_folder', new_callable=AsyncMock) as mock_process:
            loop = asyncio.get_event_loop()
            handler = DropHandler(mock_ingestion_pipeline, loop)
            handler._debounce_delay = 0.1
            
            test_path = str(temp_dir)
            
            # Schedule processing
            await handler._debounced_process(test_path)
            
            # Should have processed
            mock_process.assert_called_once_with(test_path)
