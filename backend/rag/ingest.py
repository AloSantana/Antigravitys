import os
import uuid
import asyncio
import logging
import psutil
from typing import List, Tuple, Optional
from pathlib import Path
from backend.agent.local_client import LocalClient
from .store import VectorStore

logger = logging.getLogger(__name__)

# Configuration from environment
MAX_FILE_SIZE_MB = int(os.getenv("RAG_MAX_FILE_SIZE_MB", "10"))  # Default 10MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_CHUNK_SIZE = int(os.getenv("RAG_MAX_CHUNK_SIZE", "2000"))  # Characters per chunk
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))  # Character overlap
BATCH_SIZE = int(os.getenv("RAG_BATCH_SIZE", "5"))  # Files to process concurrently
MEMORY_WARNING_THRESHOLD_MB = int(os.getenv("RAG_MEMORY_WARNING_MB", "500"))  # Warn if using >500MB
MAX_CONCURRENT_EMBEDDINGS = int(os.getenv("RAG_MAX_CONCURRENT_EMBEDDINGS", "10"))  # Limit concurrent embeddings

class IngestionPipeline:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.local_llm = LocalClient()
        self.store = VectorStore()
        # Batch processing configuration
        self._batch_size = BATCH_SIZE
        self._supported_extensions = {".md", ".py", ".js", ".txt", ".html", ".css", ".json", ".jsx", ".ts", ".tsx"}
        self._process_id = os.getpid()
        # Semaphore for limiting concurrent embeddings to prevent resource exhaustion
        self._embedding_semaphore = asyncio.Semaphore(MAX_CONCURRENT_EMBEDDINGS)
        # Cancellation support
        self._cancel_event = asyncio.Event()
        # Performance tracking
        self._total_files_processed = 0
        self._total_chunks_embedded = 0
        self._total_processing_time = 0.0
        
        logger.info(f"Ingestion Pipeline initialized for: {self.watch_dir}")
        logger.info(f"Configuration: max_file_size={MAX_FILE_SIZE_MB}MB, chunk_size={MAX_CHUNK_SIZE}, batch_size={BATCH_SIZE}, max_concurrent_embeddings={MAX_CONCURRENT_EMBEDDINGS}")
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage of this process in MB."""
        try:
            process = psutil.Process(self._process_id)
            return process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def cancel_processing(self) -> None:
        """Cancel ongoing processing operations."""
        logger.info("Cancellation requested for ingestion pipeline")
        self._cancel_event.set()
    
    def is_cancelled(self) -> bool:
        """Check if processing has been cancelled."""
        return self._cancel_event.is_set()
    
    def get_stats(self) -> dict:
        """Get ingestion pipeline statistics."""
        avg_time = self._total_processing_time / self._total_files_processed if self._total_files_processed > 0 else 0
        return {
            "total_files_processed": self._total_files_processed,
            "total_chunks_embedded": self._total_chunks_embedded,
            "total_processing_time_seconds": self._total_processing_time,
            "average_file_time_seconds": avg_time,
            "memory_usage_mb": self._get_memory_usage_mb()
        }

    async def process_folder(self, folder_path: str):
        """
        Recursively reads files and ingests them in batches for better performance.
        Supports cancellation and enhanced progress tracking.
        
        Args:
            folder_path: Path to folder to process
        """
        logger.info(f"Starting ingestion for folder: {folder_path}")
        folder_start_time = asyncio.get_event_loop().time()
        
        try:
            # Reset cancellation flag
            self._cancel_event.clear()
            
            # Check initial memory usage
            initial_memory = self._get_memory_usage_mb()
            logger.info(f"Initial memory usage: {initial_memory:.1f}MB")
            
            # Validate folder path
            folder = Path(folder_path)
            if not folder.exists():
                logger.warning(f"Folder does not exist: {folder_path}")
                return
            
            if not folder.is_dir():
                logger.warning(f"Path is not a directory: {folder_path}")
                return
            
            # Collect all files to process
            files_to_process = []
            try:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if Path(file).suffix.lower() in self._supported_extensions:
                            file_path = os.path.join(root, file)
                            files_to_process.append(file_path)
            except PermissionError as e:
                logger.error(f"Permission denied accessing folder {folder_path}: {e}")
                return
            except OSError as e:
                logger.error(f"OS error accessing folder {folder_path}: {e}")
                return
            
            if not files_to_process:
                logger.info("No supported files found to ingest")
                return
            
            logger.info(f"Found {len(files_to_process)} files to ingest")
            
            # Process files in batches
            successful = 0
            failed = 0
            skipped = 0
            
            for i in range(0, len(files_to_process), self._batch_size):
                # Check for cancellation
                if self.is_cancelled():
                    logger.warning(f"Processing cancelled at batch {i // self._batch_size + 1}")
                    break
                
                batch = files_to_process[i:i + self._batch_size]
                batch_num = i // self._batch_size + 1
                total_batches = (len(files_to_process) + self._batch_size - 1) // self._batch_size
                progress_pct = (i / len(files_to_process)) * 100
                logger.info(f"Processing batch {batch_num}/{total_batches} ({progress_pct:.1f}% complete, {len(batch)} files)")
                
                # Check memory before processing batch
                current_memory = self._get_memory_usage_mb()
                if current_memory > MEMORY_WARNING_THRESHOLD_MB:
                    logger.warning(f"High memory usage: {current_memory:.1f}MB (threshold: {MEMORY_WARNING_THRESHOLD_MB}MB)")
                
                # Process batch concurrently
                tasks = [self._ingest_file(file_path) for file_path in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count results
                for file_path, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error ingesting {file_path}: {result}")
                        failed += 1
                    elif result is True:
                        successful += 1
                        self._total_files_processed += 1
                    elif result is False:
                        skipped += 1
                    elif result is None:
                        failed += 1
            
            # Log final statistics
            folder_time = asyncio.get_event_loop().time() - folder_start_time
            self._total_processing_time += folder_time
            final_memory = self._get_memory_usage_mb()
            memory_delta = final_memory - initial_memory
            
            logger.info(f"Ingestion complete: {successful} successful, {skipped} skipped, {failed} failed")
            logger.info(f"Total processing time: {folder_time:.2f}s")
            logger.info(f"Average time per file: {folder_time / len(files_to_process):.3f}s")
            logger.info(f"Final memory usage: {final_memory:.1f}MB (delta: {memory_delta:+.1f}MB)")
            
        except Exception as e:
            logger.error(f"Critical error in process_folder: {e}", exc_info=True)

    async def _ingest_file(self, file_path: str) -> Optional[bool]:
        """
        Ingest a single file with optimized error handling and streaming support.
        
        Args:
            file_path: Path to file to ingest
            
        Returns:
            True if successful, False if skipped, None if error
        """
        try:
            # Validate file exists and is accessible
            file_obj = Path(file_path)
            if not file_obj.exists():
                logger.warning(f"File no longer exists: {file_path}")
                return None
            
            if not file_obj.is_file():
                logger.warning(f"Path is not a file: {file_path}")
                return None
            
            # Check file size first (don't read large files into memory)
            try:
                file_size = os.path.getsize(file_path)
            except OSError as e:
                logger.error(f"Cannot get file size for {file_path}: {e}")
                return None
            
            if file_size > MAX_FILE_SIZE_BYTES:
                logger.warning(f"Skipping {file_path}: File too large ({file_size / (1024*1024):.1f}MB > {MAX_FILE_SIZE_MB}MB limit)")
                return False
            
            if file_size == 0:
                logger.debug(f"Skipping empty file: {file_path}")
                return False
            
            # Read file content with multiple encoding attempts
            content = await self._read_file_safely(file_path)
            if content is None:
                return None
            
            if not content.strip():
                logger.debug(f"Skipping file with no content: {file_path}")
                return False

            # For large content, split into chunks
            chunks = self._split_content(content, file_path)
            logger.debug(f"Split {os.path.basename(file_path)} into {len(chunks)} chunks")
            
            # Generate embeddings and store in batch for better performance
            batch_data = []
            embedded_count = 0
            
            # Process chunks with semaphore to limit concurrency
            for chunk_content, chunk_metadata in chunks:
                # Check for cancellation
                if self.is_cancelled():
                    logger.debug(f"File processing cancelled: {file_path}")
                    return None
                
                try:
                    async with self._embedding_semaphore:
                        embedding = await self.local_llm.embed(chunk_content)
                        
                    if not embedding:
                        logger.warning(f"Failed to generate embedding for {chunk_metadata['chunk_id']}")
                        continue
                    
                    # Add to batch
                    batch_data.append((
                        chunk_content,
                        chunk_metadata,
                        str(uuid.uuid4()),
                        embedding
                    ))
                    embedded_count += 1
                    
                except Exception as e:
                    logger.error(f"Error embedding chunk {chunk_metadata['chunk_id']}: {e}")
                    continue
            
            # Store all chunks in one batch operation
            if batch_data:
                try:
                    self.store.add_documents_batch(batch_data)
                    self._total_chunks_embedded += embedded_count
                    logger.info(f"✓ Ingested {os.path.basename(file_path)} ({embedded_count}/{len(chunks)} chunks)")
                    return True
                except Exception as e:
                    logger.error(f"Error batch storing chunks for {file_path}: {e}")
                    return None
            else:
                logger.warning(f"✗ No chunks successfully embedded for {file_path}")
                return None
            
        except PermissionError as e:
            logger.error(f"✗ Permission denied reading {file_path}: {e}")
            return None
        except OSError as e:
            logger.error(f"✗ OS error reading {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"✗ Unexpected error ingesting {file_path}: {e}", exc_info=True)
            return None
    
    async def _read_file_safely(self, file_path: str) -> Optional[str]:
        """
        Safely read file content with multiple encoding attempts and streaming for large files.
        
        Args:
            file_path: Path to file to read
            
        Returns:
            File content as string or None if reading failed
        """
        # Try multiple encodings in order of likelihood
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # Use asyncio to avoid blocking on large file reads
                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(
                    None,
                    self._read_file_with_encoding,
                    file_path,
                    encoding
                )
                
                if content is not None:
                    logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                    return content
                    
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode {file_path} with {encoding}, trying next encoding")
                continue
            except Exception as e:
                logger.error(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        logger.error(f"Failed to read {file_path} with any supported encoding")
        return None
    
    def _read_file_with_encoding(self, file_path: str, encoding: str) -> Optional[str]:
        """
        Read file with specific encoding (blocking operation, should be run in executor).
        
        Args:
            file_path: Path to file
            encoding: Encoding to use
            
        Returns:
            File content or None
        """
        try:
            with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                return f.read()
        except Exception:
            return None
    
    def _split_content(self, content: str, file_path: str) -> List[Tuple[str, dict]]:
        """
        Split large content into chunks for better retrieval with configurable sizes.
        
        Args:
            content: Content to split
            file_path: Source file path for metadata
            
        Returns:
            List of (chunk_content, metadata) tuples
        """
        # If content is small, return as single chunk
        if len(content) <= MAX_CHUNK_SIZE:
            return [(content, {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "chunk_id": f"{file_path}:0",
                "chunk_num": 0,
                "total_chunks": 1,
                "chunk_size": len(content)
            })]
        
        # Split into chunks with overlap for context preservation
        chunks = []
        
        for i in range(0, len(content), MAX_CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = content[i:i + MAX_CHUNK_SIZE]
            chunk_num = i // (MAX_CHUNK_SIZE - CHUNK_OVERLAP)
            
            chunks.append((chunk, {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "chunk_id": f"{file_path}:{chunk_num}",
                "chunk_num": chunk_num,
                "total_chunks": -1,  # Will update after
                "chunk_size": len(chunk)
            }))
        
        # Update total_chunks in metadata
        total = len(chunks)
        for _, metadata in chunks:
            metadata["total_chunks"] = total
        
        return chunks
