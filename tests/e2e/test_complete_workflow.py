"""
End-to-end tests for complete user workflows
Tests full system integration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path


@pytest.mark.e2e
class TestCompleteWorkflow:
    """Test suite for complete user workflows."""
    
    def test_upload_and_query_workflow(self, temp_dir):
        """Test complete workflow: upload file → process → query."""
        with patch('backend.main.orchestrator') as mock_orchestrator, \
             patch('backend.main.watcher') as mock_watcher:
            
            # Setup mocks
            mock_orchestrator.process_request = AsyncMock(return_value={
                "source": "Local",
                "response": "Information from uploaded document",
                "processing_time_ms": 100
            })
            mock_orchestrator.get_cache_hit_rate = Mock(return_value=0.0)
            mock_orchestrator.local = Mock()
            mock_orchestrator.local.close = AsyncMock()
            
            watch_dir = temp_dir / "drop_zone"
            watch_dir.mkdir(parents=True, exist_ok=True)
            mock_watcher.is_running = Mock(return_value=True)
            mock_watcher.watch_dir = str(watch_dir)
            mock_watcher.start = Mock()
            mock_watcher.stop = Mock()
            
            from backend.main import app
            client = TestClient(app)
            
            # 1. Check health
            response = client.get("/health")
            assert response.status_code == 200
            
            # 2. Upload a file
            test_file = temp_dir / "test_doc.txt"
            test_file.write_text("Important information about Python")
            
            with open(test_file, "rb") as f:
                response = client.post(
                    "/upload",
                    files={"files": ("test_doc.txt", f, "text/plain")}
                )
            
            assert response.status_code == 200
            
            # 3. Query the system
            response = client.post(
                "/agent/ask",
                params={"query": "Tell me about the uploaded document"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "processing_time_ms" in data
    
    def test_system_health_monitoring(self, temp_dir):
        """Test system health monitoring throughout workflow."""
        with patch('backend.main.Orchestrator'), \
             patch('backend.main.Watcher'):
            
            from fastapi import FastAPI
            from backend.utils.performance import add_performance_endpoints
            
            app = FastAPI()
            add_performance_endpoints(app)
            client = TestClient(app)
            
            # Check health multiple times
            for _ in range(3):
                response = client.get("/performance/health")
                assert response.status_code == 200
                data = response.json()
                assert "status" in data
                assert data["status"] in ["healthy", "warning", "critical"]
    
    def test_concurrent_user_requests(self, temp_dir):
        """Test system handles concurrent user requests."""
        with patch('backend.main.orchestrator') as mock_orchestrator, \
             patch('backend.main.watcher'):
            
            mock_orchestrator.process_request = AsyncMock(return_value={
                "source": "Local",
                "response": "Response"
            })
            mock_orchestrator.get_cache_hit_rate = Mock(return_value=0.5)
            mock_orchestrator.local = Mock()
            mock_orchestrator.local.close = AsyncMock()
            
            from backend.main import app
            client = TestClient(app)
            
            # Make multiple concurrent requests
            import concurrent.futures
            
            def make_query(query):
                return client.post("/agent/ask", params={"query": query})
            
            queries = [f"Query {i}" for i in range(10)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_query, q) for q in queries]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            # All should succeed
            assert all(r.status_code == 200 for r in results)
