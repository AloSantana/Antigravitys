"""
Structured Debug Logger for Antigravity Workspace.

Provides comprehensive debugging and logging capabilities:
- JSON-formatted log entries for easy parsing
- Request/response lifecycle tracking
- Performance metrics and timing
- Failed request detection
- Missing data detection (RAG context, embeddings)
- Export to JSON and CSV formats
"""

import os
import json
import logging
import csv
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# Compute absolute path to the project root (debug_logger.py → utils/ → backend/ → project root)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")


class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class DebugLogger:
    """
    Structured debug logger for tracking requests, responses, and system events.
    
    Features:
    - JSON-formatted logs (one per line in .jsonl file)
    - Request/response lifecycle tracking
    - Performance metrics (latency, cache hits, etc.)
    - Failed request tracking
    - Missing data detection (RAG, embeddings)
    - Export to JSON and CSV formats
    - Filtering by severity, model, time range
    """
    
    def __init__(self, log_dir: str = DEFAULT_LOG_DIR, log_file: str = "debug.jsonl"):
        """
        Initialize the debug logger.
        
        Args:
            log_dir: Directory for log files
            log_file: Name of the log file
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        self.log_level = os.getenv("DEBUG_LOG_LEVEL", "INFO")
        self.max_log_size_mb = int(os.getenv("DEBUG_MAX_LOG_SIZE_MB", "100"))
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Request tracking
        self._active_requests: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Debug logger initialized: {self.log_file}")
    
    def _write_log(self, entry: Dict[str, Any]):
        """
        Write a log entry to the file.
        
        Args:
            entry: Log entry dictionary
        """
        try:
            # Check file size and rotate if needed
            if self.log_file.exists():
                size_mb = self.log_file.stat().st_size / (1024 * 1024)
                if size_mb > self.max_log_size_mb:
                    self._rotate_log()
            
            # Write as JSON line
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        
        except Exception as e:
            logger.error(f"Failed to write debug log: {e}")
    
    def _rotate_log(self):
        """Rotate log file when it gets too large."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.log_dir / f"debug_{timestamp}.jsonl"
            self.log_file.rename(backup_file)
            logger.info(f"Rotated debug log to: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to rotate log: {e}")
    
    def log_request_start(self, request: str, request_id: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Log the start of a request.
        
        Args:
            request: Request text
            request_id: Unique request identifier
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": LogLevel.INFO.value,
            "event": "request_start",
            "request_id": request_id,
            "request": request[:500] if len(request) > 500 else request,  # Truncate long requests
            "request_length": len(request),
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        # Track active request
        self._active_requests[request_id] = {
            "start_time": datetime.now(),
            "request": request,
        }
        
        self._write_log(entry)
    
    def log_request_complete(self, request_id: str, response: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Log the completion of a request.
        
        Args:
            request_id: Unique request identifier
            response: Response dictionary
            metadata: Optional metadata dictionary
        """
        start_data = self._active_requests.get(request_id, {})
        start_time = start_data.get("start_time", datetime.now())
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": LogLevel.INFO.value,
            "event": "request_complete",
            "request_id": request_id,
            "duration_ms": round(duration_ms, 2),
            "model": response.get("model", "unknown"),
            "response_length": len(str(response.get("response", ""))),
            "from_cache": response.get("from_cache", False),
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        # Check for errors in response
        response_text = str(response.get("response", ""))
        if "Error" in response_text or "error" in response_text.lower():
            entry["level"] = LogLevel.ERROR.value
            entry["has_error"] = True
        
        # Clean up tracking
        if request_id in self._active_requests:
            del self._active_requests[request_id]
        
        self._write_log(entry)
    
    def log_info(self, event: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Log an informational message.
        
        Args:
            event: Event type
            message: Log message
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": LogLevel.INFO.value,
            "event": event,
            "message": message,
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._write_log(entry)
    
    def log_warning(self, event: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Log a warning message.
        
        Args:
            event: Event type
            message: Log message
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": LogLevel.WARN.value,
            "event": event,
            "message": message,
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._write_log(entry)
    
    def log_error(self, event: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Log an error message.
        
        Args:
            event: Event type
            message: Log message
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": LogLevel.ERROR.value,
            "event": event,
            "message": message,
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._write_log(entry)
    
    def get_logs(
        self,
        severity: Optional[LogLevel] = None,
        model: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get logs with optional filtering.
        
        Args:
            severity: Filter by log level
            model: Filter by model name
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []
        
        logs = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Apply filters
                        if severity and entry.get("level") != severity.value:
                            continue
                        
                        if model and entry.get("model") != model:
                            continue
                        
                        if start_date:
                            entry_date = entry.get("timestamp", "")
                            if entry_date < start_date:
                                continue
                        
                        if end_date:
                            entry_date = entry.get("timestamp", "")
                            if entry_date > end_date:
                                continue
                        
                        logs.append(entry)
                    
                    except json.JSONDecodeError:
                        continue
            
            # Reverse to show newest first before pagination
            logs.reverse()
            
            # Apply pagination on newest-first list
            if offset:
                logs = logs[offset:]
            if limit:
                logs = logs[:limit]
            
            return logs
        
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
            return []
    
    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """
        Get all failed requests.
        
        Returns:
            List of failed request log entries
        """
        if not self.log_file.exists():
            return []
        
        failed = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Check for errors
                        if (entry.get("level") == LogLevel.ERROR.value or
                            entry.get("has_error", False)):
                            failed.append(entry)
                    
                    except json.JSONDecodeError:
                        continue
            
            # Reverse to show newest first
            failed.reverse()
            
            return failed
        
        except Exception as e:
            logger.error(f"Failed to read failed requests: {e}")
            return []
    
    def get_missing_data_requests(self) -> List[Dict[str, Any]]:
        """
        Get requests where RAG context was empty or embeddings failed.
        
        Returns:
            List of log entries with missing data
        """
        if not self.log_file.exists():
            return []
        
        missing_data = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Check for missing data indicators
                        message = entry.get("message", "")
                        
                        if any(indicator in message.lower() for indicator in [
                            "no context", "empty context", "embedding failed",
                            "rag failed", "no results", "no embeddings"
                        ]):
                            missing_data.append(entry)
                    
                    except json.JSONDecodeError:
                        continue
            
            # Reverse to show newest first
            missing_data.reverse()
            
            return missing_data
        
        except Exception as e:
            logger.error(f"Failed to read missing data requests: {e}")
            return []
    
    def export_logs(
        self,
        format: Literal['json', 'csv'] = 'json',
        severity: Optional[LogLevel] = None,
        model: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Export logs in specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            severity: Filter by log level
            model: Filter by model name
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            Exported data as string
        """
        logs = self.get_logs(severity=severity, model=model, start_date=start_date, end_date=end_date)
        
        if format == 'json':
            return json.dumps(logs, indent=2)
        
        elif format == 'csv':
            if not logs:
                return ""
            
            # Get all unique keys from logs
            fieldnames = set()
            for entry in logs:
                fieldnames.update(entry.keys())
            fieldnames = sorted(fieldnames)
            
            # Convert to CSV using StringIO
            from io import StringIO
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in logs:
                # Flatten nested dictionaries
                flat_entry = {}
                for key, value in entry.items():
                    if isinstance(value, (dict, list)):
                        flat_entry[key] = json.dumps(value)
                    else:
                        flat_entry[key] = value
                writer.writerow(flat_entry)
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_logs(self):
        """Clear all debug logs."""
        try:
            if self.log_file.exists():
                # Backup before clearing
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.log_dir / f"debug_backup_{timestamp}.jsonl"
                self.log_file.rename(backup_file)
                logger.info(f"Logs backed up to: {backup_file}")
            
            # Create new empty log file
            self.log_file.touch()
            logger.info("Debug logs cleared")
        
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            raise


# Global instance
_debug_logger = None


def get_debug_logger() -> DebugLogger:
    """
    Get the global debug logger instance.
    
    Returns:
        DebugLogger instance
    """
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger()
    return _debug_logger
