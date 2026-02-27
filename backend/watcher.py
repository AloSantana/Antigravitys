import os
import time
import asyncio
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rag.ingest import IngestionPipeline

logger = logging.getLogger(__name__)

class DropHandler(FileSystemEventHandler):
    def __init__(self, pipeline: IngestionPipeline, loop):
        self.pipeline = pipeline
        self.loop = loop
        # Debouncing mechanism to prevent duplicate processing
        self._pending_tasks = {}
        self._debounce_delay = 2.0  # Wait 2 seconds before processing
        self._last_processed = defaultdict(float)
        self._processing_cooldown = 5.0  # Don't reprocess within 5 seconds
        self._max_retries = 3  # Maximum retries for failed operations

    def on_created(self, event):
        """Handle file/folder creation with debouncing and error handling."""
        if event.is_directory:
            path = event.src_path
            
            try:
                # Validate path exists and is accessible
                if not self._validate_path(path):
                    logger.warning(f"Skipping inaccessible path: {path}")
                    return
                
                current_time = time.time()
                
                # Check if recently processed
                if current_time - self._last_processed[path] < self._processing_cooldown:
                    logger.debug(f"Skipping {path}: Recently processed")
                    return
                
                logger.info(f"New folder detected: {path}")
                
                # Cancel any pending task for this path
                if path in self._pending_tasks:
                    self._pending_tasks[path].cancel()
                
                # Schedule new task with debouncing
                task = asyncio.run_coroutine_threadsafe(
                    self._debounced_process(path),
                    self.loop
                )
                self._pending_tasks[path] = task
                
            except PermissionError:
                logger.error(f"Permission denied accessing: {path}")
            except OSError as e:
                logger.error(f"OS error accessing {path}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error handling creation event for {path}: {e}", exc_info=True)
    
    def on_modified(self, event):
        """Handle file/folder modification with debouncing and error handling."""
        if event.is_directory:
            # Treat modifications as creation events for folders
            try:
                self.on_created(event)
            except Exception as e:
                logger.error(f"Error handling modification event: {e}", exc_info=True)
    
    def _validate_path(self, path: str) -> bool:
        """
        Validate that a path exists and is accessible.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid and accessible, False otherwise
        """
        try:
            path_obj = Path(path)
            
            # Check if path exists
            if not path_obj.exists():
                logger.warning(f"Path does not exist: {path}")
                return False
            
            # Check if we have read permissions
            if not os.access(path, os.R_OK):
                logger.warning(f"No read permission for path: {path}")
                return False
            
            # Check if it's actually a directory
            if not path_obj.is_dir():
                logger.warning(f"Path is not a directory: {path}")
                return False
            
            return True
            
        except PermissionError:
            logger.error(f"Permission denied validating path: {path}")
            return False
        except OSError as e:
            logger.error(f"OS error validating path {path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating path {path}: {e}")
            return False
    
    async def _debounced_process(self, path: str, retry_count: int = 0):
        """
        Process a folder after debounce delay with retry logic.
        
        Args:
            path: Path to process
            retry_count: Current retry attempt
        """
        try:
            # Wait for debounce period
            await asyncio.sleep(self._debounce_delay)
            
            # Double-check path is still valid (may have been deleted)
            if not self._validate_path(path):
                logger.warning(f"Path no longer valid, skipping processing: {path}")
                if path in self._pending_tasks:
                    del self._pending_tasks[path]
                return
            
            # Mark as processed
            self._last_processed[path] = time.time()
            
            # Process the folder
            logger.info(f"Processing folder after debounce: {path}")
            
            try:
                await self.pipeline.process_folder(path)
                logger.info(f"Successfully processed folder: {path}")
                
            except PermissionError as e:
                logger.error(f"Permission denied processing {path}: {e}")
                # Don't retry permission errors
                
            except FileNotFoundError as e:
                logger.warning(f"File not found during processing {path}: {e}")
                # File was deleted during processing - this is ok
                
            except OSError as e:
                logger.error(f"OS error processing {path}: {e}")
                # Retry on OS errors (might be temporary)
                if retry_count < self._max_retries:
                    logger.info(f"Retrying processing of {path} (attempt {retry_count + 1}/{self._max_retries})")
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    await self._debounced_process(path, retry_count + 1)
                else:
                    logger.error(f"Failed to process {path} after {self._max_retries} retries")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing {path}: {e}", exc_info=True)
                # Retry on unexpected errors
                if retry_count < self._max_retries:
                    logger.info(f"Retrying processing of {path} (attempt {retry_count + 1}/{self._max_retries})")
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    await self._debounced_process(path, retry_count + 1)
                else:
                    logger.error(f"Failed to process {path} after {self._max_retries} retries")
            
            # Cleanup
            if path in self._pending_tasks:
                del self._pending_tasks[path]
                
        except asyncio.CancelledError:
            logger.info(f"Processing cancelled for {path}")
            raise  # Re-raise to properly handle cancellation
            
        except Exception as e:
            logger.error(f"Critical error in debounced processing for {path}: {e}", exc_info=True)
            # Cleanup on critical error
            if path in self._pending_tasks:
                del self._pending_tasks[path]

class Watcher:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.pipeline = IngestionPipeline(watch_dir)
        self.observer: Optional[Observer] = None
        self._is_running = False
        self._event_handler: Optional[DropHandler] = None

    def start(self):
        """Start the file watcher with error handling."""
        if self._is_running:
            logger.warning("Watcher already running")
            return
        
        try:
            # Validate watch directory
            watch_path = Path(self.watch_dir)
            if not watch_path.exists():
                logger.warning(f"Watch directory does not exist, creating: {self.watch_dir}")
                watch_path.mkdir(parents=True, exist_ok=True)
            
            if not os.access(self.watch_dir, os.R_OK):
                logger.error(f"No read permission for watch directory: {self.watch_dir}")
                raise PermissionError(f"Cannot read watch directory: {self.watch_dir}")
            
            # Initialize observer and handler
            loop = asyncio.get_running_loop()
            self._event_handler = DropHandler(self.pipeline, loop)
            self.observer = Observer()
            self.observer.schedule(self._event_handler, self.watch_dir, recursive=False)
            self.observer.start()
            self._is_running = True
            logger.info(f"Watcher started on {self.watch_dir}")
            
        except PermissionError as e:
            logger.error(f"Permission denied starting watcher: {e}")
            raise
        except OSError as e:
            logger.error(f"OS error starting watcher: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start watcher: {e}", exc_info=True)
            raise

    def stop(self):
        """Stop the file watcher with proper cleanup."""
        if not self._is_running:
            logger.debug("Watcher not running, nothing to stop")
            return
        
        try:
            logger.info("Stopping watcher...")
            
            if self.observer:
                self.observer.stop()
                # Wait for observer thread with timeout
                self.observer.join(timeout=5.0)
                
                if self.observer.is_alive():
                    logger.warning("Watcher observer thread did not stop cleanly")
            
            self._is_running = False
            logger.info("Watcher stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping watcher: {e}", exc_info=True)
            # Still mark as not running even if there was an error
            self._is_running = False
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._is_running
    
    def is_healthy(self) -> bool:
        """
        Check if watcher is healthy and responsive.
        
        Returns:
            True if watcher is running and observer is alive
        """
        try:
            if not self._is_running:
                return False
            
            if not self.observer:
                return False
            
            # Check if observer thread is alive
            return self.observer.is_alive()
            
        except Exception as e:
            logger.error(f"Error checking watcher health: {e}")
            return False
