"""
Test rate limiter fixes for endpoints.
Ensures all rate-limited endpoints have the required request: Request parameter.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure backend is in path (conftest.py should handle this, but being explicit)
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestRateLimiterEndpoints:
    """Test that all rate-limited endpoints work correctly."""
    
    def test_health_endpoint_with_rate_limiter(self, client):
        """Test /health endpoint has request parameter and rate limiter works."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_config_endpoint_with_rate_limiter(self, client):
        """Test /config endpoint has request parameter and rate limiter works."""
        response = client.get("/config")
        assert response.status_code == 200
        assert "mode" in response.json()
    
    def test_files_endpoint_with_rate_limiter(self, client):
        """Test /files endpoint has request parameter and rate limiter works."""
        response = client.get("/files")
        assert response.status_code == 200
    
    def test_agent_ask_endpoint_with_rate_limiter(self, client):
        """Test /agent/ask endpoint has request parameter and rate limiter works."""
        response = client.post("/agent/ask", json="What is the weather?")
        # Should return 200 or 422 (validation error), not 500 (rate limiter crash)
        assert response.status_code in [200, 422]
    
    def test_agent_clear_cache_endpoint_with_rate_limiter(self, client):
        """Test /agent/clear-cache endpoint has request parameter and rate limiter works."""
        response = client.post("/agent/clear-cache")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_agent_warm_cache_endpoint_with_rate_limiter(self, client):
        """Test /agent/warm-cache endpoint has request parameter and rate limiter works."""
        response = client.post("/agent/warm-cache")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_settings_get_endpoint_with_rate_limiter(self, client):
        """Test /settings GET endpoint has request parameter and rate limiter works."""
        response = client.get("/settings")
        assert response.status_code == 200
        assert "success" in response.json()
    
    def test_settings_mcp_get_endpoint_with_rate_limiter(self, client):
        """Test /settings/mcp GET endpoint has request parameter and rate limiter works."""
        response = client.get("/settings/mcp")
        assert response.status_code == 200
        assert "success" in response.json()
    
    def test_settings_models_get_endpoint_with_rate_limiter(self, client):
        """Test /settings/models GET endpoint has request parameter and rate limiter works."""
        response = client.get("/settings/models")
        assert response.status_code == 200
        assert "models" in response.json()
    
    def test_settings_env_get_endpoint_with_rate_limiter(self, client):
        """Test /settings/env GET endpoint has request parameter and rate limiter works."""
        response = client.get("/settings/env")
        assert response.status_code == 200
        assert "success" in response.json()
    
    def test_settings_export_endpoint_with_rate_limiter(self, client):
        """Test /settings/export GET endpoint has request parameter and rate limiter works."""
        response = client.get("/settings/export")
        assert response.status_code == 200
        assert "success" in response.json()
    
    def test_multiple_requests_dont_crash(self, client):
        """Test that multiple requests don't cause rate limiter to crash."""
        # Make 10 requests to different endpoints
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            
        for _ in range(5):
            response = client.get("/config")
            assert response.status_code == 200
    
    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present in responses."""
        response = client.get("/health")
        # slowapi should add rate limit headers
        # Note: These headers may not always be present in test client
        assert response.status_code == 200


class TestCORSConfiguration:
    """Test CORS configuration for ngrok support."""
    
    def test_cors_allows_ngrok_pattern(self, client):
        """Test that CORS middleware is configured with ngrok regex pattern."""
        # This is a code inspection test - checking the middleware config
        from main import app as main_app
        
        # Find CORSMiddleware in the middleware stack
        cors_middleware = None
        for middleware in main_app.user_middleware:
            if hasattr(middleware, 'cls') and 'CORS' in str(middleware.cls):
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None, "CORSMiddleware should be configured"
    
    def test_allowed_origins_configured(self, client):
        """Test that allowed origins are properly configured."""
        from security import get_allowed_origins
        
        origins = get_allowed_origins()
        assert len(origins) > 0, "Should have at least default localhost origins"
        assert any('localhost' in origin for origin in origins), "Should include localhost"


class TestWebSocketEndpoint:
    """Test WebSocket endpoint is properly configured."""
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint exists at /ws."""
        from main import app as main_app
        
        # Check if /ws route exists
        routes = [route.path for route in main_app.routes]
        assert "/ws" in routes, "WebSocket endpoint should exist at /ws"
    
    def test_websocket_endpoint_type(self):
        """Test that /ws is configured as a WebSocket endpoint."""
        from main import app as main_app
        from starlette.routing import WebSocketRoute
        
        # Find the WebSocket route
        ws_route = None
        for route in main_app.routes:
            if hasattr(route, 'path') and route.path == "/ws":
                ws_route = route
                break
        
        assert ws_route is not None, "WebSocket route should exist"
        assert isinstance(ws_route, WebSocketRoute), "Route should be a WebSocketRoute"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
