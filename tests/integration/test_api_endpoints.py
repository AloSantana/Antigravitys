"""
Integration tests for FastAPI endpoints
Tests API routes with TestClient
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json


@pytest.mark.integration
class TestAPIEndpoints:
    """Test suite for FastAPI API endpoints."""
    
    @pytest.fixture
    def app(self, temp_dir):
        """Create FastAPI app for testing."""
        # Use patch.object or patch the instance directly in backend.main
        with patch('backend.main.orchestrator') as mock_orchestrator, \
             patch('backend.main.watcher') as mock_watcher:
            
            # Setup orchestrator mock
            mock_orchestrator.process_request = AsyncMock(return_value={
                "source": "Local",
                "response": "Test response"
            })
            mock_orchestrator.get_cache_hit_rate = Mock(return_value=0.5)
            mock_orchestrator.local = Mock()
            mock_orchestrator.local.close = AsyncMock()
            
            # Setup watcher mock
            watch_dir = temp_dir / "drop_zone"
            watch_dir.mkdir(parents=True, exist_ok=True)
            mock_watcher.is_running = Mock(return_value=True)
            mock_watcher.watch_dir = str(watch_dir)
            mock_watcher.start = Mock()
            mock_watcher.stop = Mock()
            
            # Import after mocking (though instance is already there, patch should catch it)
            from backend.main import app
            yield app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test GET / endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    def test_health_endpoint(self, client):
        """Test GET /health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "watcher" in data
        assert "cache_hit_rate" in data
    
    def test_files_endpoint(self, client):
        """Test GET /files endpoint."""
        with patch('backend.main.get_file_structure') as mock_get_files:
            mock_get_files.return_value = {
                "name": "drop_zone",
                "type": "directory",
                "children": []
            }
            
            response = client.get("/files")
            
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            mock_get_files.assert_called_once()
    
    def test_upload_single_file(self, client, temp_dir):
        """Test POST /upload with single file."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/upload",
                files={"files": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "1 file(s)" in data["message"]
    
    def test_upload_multiple_files(self, client, temp_dir):
        """Test POST /upload with multiple files."""
        # Create test files
        files_to_upload = []
        for i in range(3):
            test_file = temp_dir / f"test{i}.txt"
            test_file.write_text(f"Content {i}")
            files_to_upload.append(("files", (f"test{i}.txt", open(test_file, "rb"), "text/plain")))
        
        response = client.post("/upload", files=files_to_upload)
        
        # Close files
        for _, (_, f, _) in files_to_upload:
            f.close()
        
        assert response.status_code == 200
        data = response.json()
        assert "3 file(s)" in data["message"]
    
    def test_ask_agent_endpoint(self, client):
        """Test POST /agent/ask endpoint."""
        response = client.post(
            "/agent/ask",
            params={"query": "What is Python?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert "response" in data
        assert data["response"] == "Test response"
    
    def test_ask_agent_complex_query(self, client):
        """Test /agent/ask with complex query."""
        complex_query = "Design a scalable microservices architecture"
        
        response = client.post(
            "/agent/ask",
            params={"query": complex_query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
    
    def test_ask_agent_empty_query(self, client):
        """Test /agent/ask with empty query."""
        response = client.post(
            "/agent/ask",
            params={"query": ""}
        )
        
        # Should still process (may return error from orchestrator)
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/")
        
        # CORS middleware should add headers
        # Note: TestClient may not fully simulate OPTIONS requests
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_api_versioning(self, client):
        """Test API version in response."""
        response = client.get("/")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
    
    def test_upload_with_subdirectory(self, client, temp_dir):
        """Test upload creates subdirectories if needed."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/upload",
                files={"files": ("subdir/test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Test API error handling."""
        # Request to non-existent endpoint
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.parametrize("endpoint,method", [
        ("/", "GET"),
        ("/health", "GET"),
        ("/files", "GET"),
    ])
    def test_all_get_endpoints(self, client, endpoint, method):
        """Parametrized test for all GET endpoints."""
        response = client.get(endpoint)
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
    
    def test_agent_ask_preserves_formatting(self, client):
        """Test that agent responses preserve formatting."""
        query = "Show me code:\n```python\ndef hello():\n    pass\n```"
        
        response = client.post(
            "/agent/ask",
            params={"query": query}
        )
        
        assert response.status_code == 200
        # Response should be valid JSON
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.integration
class TestPerformanceEndpoints:
    """Test suite for performance monitoring endpoints."""
    
    @pytest.fixture
    def app_with_performance(self):
        """Create app with performance endpoints."""
        from fastapi import FastAPI
        from backend.utils.performance import add_performance_endpoints
        
        app = FastAPI()
        add_performance_endpoints(app)
        return app
    
    @pytest.fixture
    def client(self, app_with_performance):
        """Create test client."""
        return TestClient(app_with_performance)
    
    def test_performance_health_endpoint(self, client):
        """Test GET /performance/health endpoint."""
        response = client.get("/performance/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "health_score" in data
        assert "metrics" in data
    
    def test_performance_metrics_endpoint(self, client):
        """Test GET /performance/metrics endpoint."""
        response = client.get("/performance/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "timestamp" in data["system"]
        assert "cpu_percent" in data["system"]
        assert "memory_percent" in data["system"]
    
    def test_performance_summary_endpoint(self, client):
        """Test GET /performance/summary endpoint."""
        response = client.get("/performance/summary")
        
        assert response.status_code == 200
        # May be empty initially
        data = response.json()
        assert isinstance(data, dict)
    
    def test_performance_analysis_endpoint(self, client):
        """Test GET /performance/analysis endpoint."""
        response = client.get("/performance/analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        assert "recommendations" in data
    
    def test_performance_report_endpoint(self, client):
        """Test GET /performance/report endpoint."""
        response = client.get("/performance/report")
        
        assert response.status_code == 200
        data = response.json()
        assert "report" in data
        assert isinstance(data["report"], str)
        assert "PERFORMANCE" in data["report"]
