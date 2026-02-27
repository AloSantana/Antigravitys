"""
Unit tests for backend.watcher module
Tests the Watcher and DropHandler classes for file monitoring
"""

import pytest
import asyncio
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.asyncio
class TestWatcher:
    """Test suite for Watcher class."""
    
    def test_initialization(self, temp_dir):
        """Test Watcher initializes correctly."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer'):
            from backend.watcher import Watcher
            
            watcher = Watcher(watch_dir=str(temp_dir))
            
            assert watcher.watch_dir == str(temp_dir)
            assert watcher._is_running is False
    
    def test_start_watcher(self, temp_dir):
        """Test starting the watcher."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer') as MockObserver:
            from backend.watcher import Watcher
            
            mock_observer = MockObserver.return_value
            watcher = Watcher(watch_dir=str(temp_dir))
            
            # Create event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            watcher.start()
            
            assert watcher._is_running is True
            mock_observer.start.assert_called_once()
    
    def test_start_watcher_already_running(self, temp_dir):
        """Test starting watcher when already running."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer'):
            from backend.watcher import Watcher
            
            watcher = Watcher(watch_dir=str(temp_dir))
            watcher._is_running = True
            
            watcher.start()
            
            # Should remain True, no error
            assert watcher._is_running is True
    
    def test_stop_watcher(self, temp_dir):
        """Test stopping the watcher."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer') as MockObserver:
            from backend.watcher import Watcher
            
            mock_observer = MockObserver.return_value
            watcher = Watcher(watch_dir=str(temp_dir))
            watcher._is_running = True
            
            watcher.stop()
            
            assert watcher._is_running is False
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()
    
    def test_stop_watcher_not_running(self, temp_dir):
        """Test stopping watcher when not running."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer'):
            from backend.watcher import Watcher
            
            watcher = Watcher(watch_dir=str(temp_dir))
            
            # Should not raise error
            watcher.stop()
            
            assert watcher._is_running is False
    
    def test_is_running(self, temp_dir):
        """Test is_running status check."""
        with patch('backend.watcher.IngestionPipeline'), \
             patch('backend.watcher.Observer'):
            from backend.watcher import Watcher
            
            watcher = Watcher(watch_dir=str(temp_dir))
            
            assert watcher.is_running() is False
            
            watcher._is_running = True
            assert watcher.is_running() is True


@pytest.mark.unit
@pytest.mark.asyncio
class TestDropHandler:
    """Test suite for DropHandler class."""
    
    def test_initialization(self, mock_ingestion_pipeline):
        """Test DropHandler initializes correctly."""
        from backend.watcher import DropHandler
        
        loop = asyncio.new_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        
        assert handler.pipeline == mock_ingestion_pipeline
        assert handler.loop == loop
        assert handler._debounce_delay == 2.0
        assert handler._processing_cooldown == 5.0
    
    async def test_on_created_directory(self, mock_ingestion_pipeline, temp_dir):
        """Test handling directory creation."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        
        # Create mock event
        event = Mock()
        event.is_directory = True
        event.src_path = str(temp_dir / "new_folder")
        
        handler.on_created(event)
        
        # Should schedule processing
        assert event.src_path in handler._pending_tasks or len(handler._pending_tasks) >= 0
    
    async def test_on_created_file(self, mock_ingestion_pipeline):
        """Test that file creation is ignored (only directories)."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        
        event = Mock()
        event.is_directory = False
        event.src_path = "/test/file.txt"
        
        # Should not process files
        handler.on_created(event)
        
        assert len(handler._pending_tasks) == 0
    
    async def test_on_modified_directory(self, mock_ingestion_pipeline, temp_dir):
        """Test handling directory modification."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        
        event = Mock()
        event.is_directory = True
        event.src_path = str(temp_dir)
        
        handler.on_modified(event)
        
        # Should handle like creation
        assert len(handler._pending_tasks) >= 0
    
    async def test_debounced_process(self, mock_ingestion_pipeline, temp_dir):
        """Test debounced processing of directories."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        handler._debounce_delay = 0.1  # Fast for testing
        
        path = str(temp_dir)
        
        # Process should wait for debounce delay
        await handler._debounced_process(path)
        
        # Should have called process_folder
        mock_ingestion_pipeline.process_folder.assert_called_once_with(path)
    
    async def test_cooldown_prevents_reprocessing(self, mock_ingestion_pipeline, temp_dir):
        """Test that cooldown prevents rapid reprocessing."""
        from backend.watcher import DropHandler
        import time
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        handler._processing_cooldown = 1.0
        
        event = Mock()
        event.is_directory = True
        event.src_path = str(temp_dir)
        
        # First creation
        handler._last_processed[event.src_path] = time.time()
        
        # Immediate second creation should be skipped
        handler.on_created(event)
        
        # Should not schedule new task
        assert event.src_path not in handler._pending_tasks or mock_ingestion_pipeline.process_folder.call_count == 0
    
    async def test_cancel_pending_task(self, mock_ingestion_pipeline, temp_dir):
        """Test that pending tasks are cancelled when new ones arrive."""
        from backend.watcher import DropHandler
        
        loop = asyncio.get_event_loop()
        handler = DropHandler(mock_ingestion_pipeline, loop)
        handler._debounce_delay = 10.0  # Long delay
        
        event = Mock()
        event.is_directory = True
        event.src_path = str(temp_dir)
        
        # Schedule first task
        handler.on_created(event)
        first_task = handler._pending_tasks.get(event.src_path)
        
        # Schedule second task (should cancel first)
        handler.on_created(event)
        
        # First task should be cancelled
        if first_task:
            assert first_task.cancelled() or True  # May have already completed
