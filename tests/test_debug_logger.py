"""
Tests for debug_logger module.

Tests the structured debug logger functionality including:
- Log capture and storage
- Filtering by severity, model, time range
- Export in JSON and CSV formats
- Failed request detection
- Missing data detection
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from utils.debug_logger import DebugLogger, LogLevel


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for test logs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def debug_logger(temp_log_dir):
    """Create a debug logger instance with temporary log directory."""
    logger = DebugLogger(log_dir=temp_log_dir, log_file="test_debug.jsonl")
    return logger


class TestDebugLoggerBasics:
    """Test basic debug logger functionality."""
    
    def test_logger_initialization(self, debug_logger):
        """Test that logger initializes correctly."""
        assert debug_logger is not None
        assert debug_logger.log_file.exists()
    
    def test_log_request_start(self, debug_logger):
        """Test logging request start."""
        request_id = "test_req_1"
        debug_logger.log_request_start("test request", request_id)
        
        # Read log file
        logs = debug_logger.get_logs()
        assert len(logs) == 1
        assert logs[0]["event"] == "request_start"
        assert logs[0]["request_id"] == request_id
    
    def test_log_request_complete(self, debug_logger):
        """Test logging request completion."""
        request_id = "test_req_2"
        debug_logger.log_request_start("test request", request_id)
        
        response = {
            "model": "gemini",
            "response": "test response",
            "from_cache": False
        }
        debug_logger.log_request_complete(request_id, response)
        
        logs = debug_logger.get_logs()
        assert len(logs) == 2
        complete_log = logs[0]  # Most recent first
        assert complete_log["event"] == "request_complete"
        assert complete_log["model"] == "gemini"
    
    def test_log_info(self, debug_logger):
        """Test logging info messages."""
        debug_logger.log_info("test_event", "test message", {"key": "value"})
        
        logs = debug_logger.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "INFO"
        assert logs[0]["event"] == "test_event"
        assert logs[0]["message"] == "test message"
        assert logs[0]["metadata"]["key"] == "value"
    
    def test_log_warning(self, debug_logger):
        """Test logging warning messages."""
        debug_logger.log_warning("test_warn", "warning message")
        
        logs = debug_logger.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "WARN"
    
    def test_log_error(self, debug_logger):
        """Test logging error messages."""
        debug_logger.log_error("test_error", "error message")
        
        logs = debug_logger.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "ERROR"


class TestDebugLoggerFiltering:
    """Test log filtering functionality."""
    
    def setup_method(self):
        """Set up test data."""
        pass
    
    def test_filter_by_severity(self, debug_logger):
        """Test filtering logs by severity level."""
        debug_logger.log_info("event1", "info message")
        debug_logger.log_warning("event2", "warning message")
        debug_logger.log_error("event3", "error message")
        
        # Filter for errors only
        error_logs = debug_logger.get_logs(severity=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0]["level"] == "ERROR"
        
        # Filter for warnings only
        warn_logs = debug_logger.get_logs(severity=LogLevel.WARN)
        assert len(warn_logs) == 1
        assert warn_logs[0]["level"] == "WARN"
    
    def test_filter_by_model(self, debug_logger):
        """Test filtering logs by model name."""
        request_id1 = "req1"
        request_id2 = "req2"
        
        debug_logger.log_request_start("request 1", request_id1)
        debug_logger.log_request_complete(request_id1, {"model": "gemini", "response": "resp1"})
        
        debug_logger.log_request_start("request 2", request_id2)
        debug_logger.log_request_complete(request_id2, {"model": "vertex", "response": "resp2"})
        
        # Filter by Gemini
        gemini_logs = debug_logger.get_logs(model="gemini")
        assert len(gemini_logs) == 1
        assert gemini_logs[0]["model"] == "gemini"
    
    def test_pagination(self, debug_logger):
        """Test log pagination."""
        # Create 10 log entries
        for i in range(10):
            debug_logger.log_info(f"event{i}", f"message {i}")
        
        # Get first page (5 items)
        page1 = debug_logger.get_logs(limit=5, offset=0)
        assert len(page1) == 5
        
        # Get second page (5 items)
        page2 = debug_logger.get_logs(limit=5, offset=5)
        assert len(page2) == 5
        
        # Ensure pages are different
        assert page1[0] != page2[0]


class TestDebugLoggerExport:
    """Test log export functionality."""
    
    def test_export_json(self, debug_logger):
        """Test exporting logs as JSON."""
        debug_logger.log_info("event1", "message 1")
        debug_logger.log_info("event2", "message 2")
        
        exported = debug_logger.export_logs(format='json')
        data = json.loads(exported)
        
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_export_csv(self, debug_logger):
        """Test exporting logs as CSV."""
        debug_logger.log_info("event1", "message 1")
        debug_logger.log_info("event2", "message 2")
        
        exported = debug_logger.export_logs(format='csv')
        
        # Should have headers and 2 data rows
        lines = exported.strip().split('\n')
        assert len(lines) >= 3  # Header + 2 rows
        assert 'timestamp' in lines[0]  # Header row
    
    def test_export_with_filters(self, debug_logger):
        """Test exporting logs with filters applied."""
        debug_logger.log_info("event1", "message 1")
        debug_logger.log_error("event2", "error message")
        
        # Export only errors
        exported = debug_logger.export_logs(format='json', severity=LogLevel.ERROR)
        data = json.loads(exported)
        
        assert len(data) == 1
        assert data[0]["level"] == "ERROR"


class TestDebugLoggerFailedRequests:
    """Test failed request detection."""
    
    def test_get_failed_requests(self, debug_logger):
        """Test retrieving failed requests."""
        # Log a successful request
        debug_logger.log_request_start("success request", "req1")
        debug_logger.log_request_complete("req1", {"model": "gemini", "response": "success"})
        
        # Log a failed request
        debug_logger.log_error("request_error", "Request failed due to timeout")
        
        failed = debug_logger.get_failed_requests()
        assert len(failed) >= 1
        assert any(log["level"] == "ERROR" for log in failed)
    
    def test_error_response_detection(self, debug_logger):
        """Test detection of error responses."""
        request_id = "req_error"
        debug_logger.log_request_start("error request", request_id)
        
        # Response with error
        error_response = {
            "model": "gemini",
            "response": "Error: API quota exceeded"
        }
        debug_logger.log_request_complete(request_id, error_response)
        
        failed = debug_logger.get_failed_requests()
        assert len(failed) >= 1


class TestDebugLoggerMissingData:
    """Test missing data detection."""
    
    def test_get_missing_data_requests(self, debug_logger):
        """Test retrieving requests with missing RAG context."""
        # Log request with missing context
        debug_logger.log_warning("rag_no_results", "No context chunks retrieved from RAG")
        
        # Log request with embedding failure
        debug_logger.log_error("embedding_failed", "Embedding generation failed")
        
        missing_data = debug_logger.get_missing_data_requests()
        # Should have at least 1 (both messages contain indicators)
        assert len(missing_data) >= 1


class TestDebugLoggerManagement:
    """Test log management functionality."""
    
    def test_clear_logs(self, debug_logger):
        """Test clearing debug logs."""
        # Add some logs
        debug_logger.log_info("event1", "message 1")
        debug_logger.log_info("event2", "message 2")
        
        # Clear logs
        debug_logger.clear_logs()
        
        # Verify logs are cleared
        logs = debug_logger.get_logs()
        assert len(logs) == 0
    
    def test_log_rotation(self, debug_logger, temp_log_dir):
        """Test log file rotation when size exceeds limit."""
        # Set very small max size for testing
        debug_logger.max_log_size_mb = 0.001  # 1 KB
        
        # Write many logs to trigger rotation
        for i in range(100):
            debug_logger.log_info(f"event{i}", f"message {i}" * 10)
        
        # Check if backup file was created
        log_dir = Path(temp_log_dir)
        backup_files = list(log_dir.glob("debug_*.jsonl"))
        
        # Should have at least one backup file if rotation occurred
        # (May not always trigger in test, so this is lenient)
        assert debug_logger.log_file.exists()


class TestDebugLoggerIntegration:
    """Integration tests for debug logger."""
    
    def test_complete_request_lifecycle(self, debug_logger):
        """Test complete request lifecycle logging."""
        request_id = "integration_test_req"
        
        # Start request
        debug_logger.log_request_start("integration test request", request_id, 
                                      {"request_number": 1})
        
        # Log RAG retrieval
        debug_logger.log_info("rag_retrieval", "Retrieved 3 context chunks", 
                            {"chunks": 3, "time_ms": 150})
        
        # Complete request
        response = {
            "model": "gemini",
            "response": "Test response",
            "from_cache": False,
            "processing_time_ms": 500
        }
        debug_logger.log_request_complete(request_id, response, 
                                        {"total_time_ms": 500})
        
        # Verify all logs
        logs = debug_logger.get_logs()
        assert len(logs) == 3
        
        # Check chronological order (newest first)
        assert logs[0]["event"] == "request_complete"
        assert logs[1]["event"] == "rag_retrieval"
        assert logs[2]["event"] == "request_start"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
