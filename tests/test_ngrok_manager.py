"""
Tests for ngrok_manager module.

Tests the ngrok tunnel management functionality including:
- Tunnel lifecycle (start/stop/restart)
- URL detection and format
- Health monitoring
- Status reporting
- CORS origin generation
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from utils.ngrok_manager import NgrokManager, get_ngrok_manager


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("NGROK_ENABLED", "true")
    monkeypatch.setenv("NGROK_AUTH_TOKEN", "test_token")
    monkeypatch.setenv("NGROK_REGION", "us")
    monkeypatch.setenv("PORT", "8000")


@pytest.fixture
def ngrok_manager_disabled():
    """Create an ngrok manager with disabled mode for testing."""
    with patch.dict(os.environ, {"NGROK_ENABLED": "false"}):
        manager = NgrokManager()
    return manager


@pytest.fixture
def ngrok_manager_enabled(mock_env):
    """Create an ngrok manager with enabled mode for testing."""
    manager = NgrokManager()
    return manager


class TestNgrokManagerInitialization:
    """Test ngrok manager initialization."""
    
    def test_init_disabled(self, ngrok_manager_disabled):
        """Test initialization when ngrok is disabled."""
        assert ngrok_manager_disabled.enabled is False
        assert ngrok_manager_disabled.tunnel is None
        assert ngrok_manager_disabled.public_url is None
    
    def test_init_enabled(self, ngrok_manager_enabled):
        """Test initialization when ngrok is enabled."""
        assert ngrok_manager_enabled.enabled is True
        assert ngrok_manager_enabled.port == 8000
        assert ngrok_manager_enabled.region == "us"
    
    def test_config_from_env(self, mock_env):
        """Test configuration is loaded from environment variables."""
        manager = NgrokManager()
        assert manager.enabled is True
        assert manager.auth_token == "test_token"
        assert manager.region == "us"
        assert manager.port == 8000


class TestNgrokManagerStatus:
    """Test ngrok manager status reporting."""
    
    def test_get_status_disabled(self, ngrok_manager_disabled):
        """Test status when ngrok is disabled."""
        status = ngrok_manager_disabled.get_status()
        
        assert status["enabled"] is False
        assert status["active"] is False
        assert status["public_url"] is None
    
    def test_get_status_enabled_inactive(self, ngrok_manager_enabled):
        """Test status when ngrok is enabled but tunnel is not active."""
        status = ngrok_manager_enabled.get_status()
        
        assert status["enabled"] is True
        assert status["active"] is False
        assert status["healthy"] is False
    
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    def test_get_status_with_active_tunnel(self, ngrok_manager_enabled):
        """Test status when tunnel is active."""
        # Simulate active tunnel
        ngrok_manager_enabled.tunnel = Mock()
        ngrok_manager_enabled.public_url = "https://abc123.ngrok.io"
        ngrok_manager_enabled.is_healthy = True
        
        status = ngrok_manager_enabled.get_status()
        
        assert status["enabled"] is True
        assert status["active"] is True
        assert status["healthy"] is True
        assert status["public_url"] == "https://abc123.ngrok.io"


class TestNgrokManagerURLGeneration:
    """Test URL generation for ngrok tunnels."""
    
    def test_get_public_url_inactive(self, ngrok_manager_enabled):
        """Test getting public URL when tunnel is inactive."""
        url = ngrok_manager_enabled.get_public_url()
        assert url is None
    
    def test_get_public_url_active(self, ngrok_manager_enabled):
        """Test getting public URL when tunnel is active."""
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        ngrok_manager_enabled.is_healthy = True
        
        url = ngrok_manager_enabled.get_public_url()
        assert url == "https://test.ngrok.io"
    
    def test_get_websocket_url_https(self, ngrok_manager_enabled):
        """Test WebSocket URL generation for HTTPS tunnel."""
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        
        ws_url = ngrok_manager_enabled.get_websocket_url()
        assert ws_url == "wss://test.ngrok.io/ws"
    
    def test_get_websocket_url_http(self, ngrok_manager_enabled):
        """Test WebSocket URL generation for HTTP tunnel."""
        ngrok_manager_enabled.public_url = "http://test.ngrok.io"
        
        ws_url = ngrok_manager_enabled.get_websocket_url()
        assert ws_url == "ws://test.ngrok.io/ws"
    
    def test_get_websocket_url_none(self, ngrok_manager_enabled):
        """Test WebSocket URL when no tunnel is active."""
        ws_url = ngrok_manager_enabled.get_websocket_url()
        assert ws_url is None


class TestNgrokManagerCORS:
    """Test CORS origin generation."""
    
    def test_get_cors_origins_no_tunnel(self, ngrok_manager_enabled):
        """Test CORS origins when no tunnel is active."""
        origins = ngrok_manager_enabled.get_cors_origins()
        assert origins == []
    
    def test_get_cors_origins_with_tunnel(self, ngrok_manager_enabled):
        """Test CORS origins when tunnel is active."""
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        
        origins = ngrok_manager_enabled.get_cors_origins()
        assert "https://test.ngrok.io" in origins


class TestNgrokManagerTunnelLifecycle:
    """Test tunnel lifecycle management."""
    
    @pytest.mark.asyncio
    async def test_start_tunnel_disabled(self, ngrok_manager_disabled):
        """Test starting tunnel when ngrok is disabled."""
        url = await ngrok_manager_disabled.start_tunnel()
        assert url is None
    
    @pytest.mark.asyncio
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', False)
    async def test_start_tunnel_not_installed(self, ngrok_manager_enabled):
        """Test starting tunnel when pyngrok is not installed."""
        # Recreate manager with mocked availability
        manager = NgrokManager()
        url = await manager.start_tunnel()
        assert url is None
    
    @pytest.mark.asyncio
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    @patch('utils.ngrok_manager.ngrok')
    @patch('utils.ngrok_manager.conf')
    async def test_start_tunnel_success(self, mock_conf, mock_ngrok, ngrok_manager_enabled):
        """Test successful tunnel startup."""
        # Mock ngrok.connect to return a tunnel object
        mock_tunnel = Mock()
        mock_tunnel.public_url = "https://abc123.ngrok.io"
        mock_ngrok.connect.return_value = mock_tunnel
        mock_ngrok.get_tunnels.return_value = [mock_tunnel]
        
        # Mock the config
        mock_default_conf = Mock()
        mock_conf.get_default.return_value = mock_default_conf
        
        url = await ngrok_manager_enabled.start_tunnel()
        
        # Should have returned the public URL
        assert url == "https://abc123.ngrok.io"
        assert ngrok_manager_enabled.public_url == "https://abc123.ngrok.io"
        assert ngrok_manager_enabled.is_healthy is True
        
        # Should have set auth token
        assert mock_default_conf.auth_token == "test_token"
        
        # Should have called ngrok.connect
        mock_ngrok.connect.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    @patch('utils.ngrok_manager.ngrok')
    async def test_stop_tunnel(self, mock_ngrok, ngrok_manager_enabled):
        """Test stopping tunnel."""
        # Set up active tunnel
        ngrok_manager_enabled.tunnel = Mock()
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        
        await ngrok_manager_enabled.stop_tunnel()
        
        # Should have disconnected
        mock_ngrok.disconnect.assert_called_once_with("https://test.ngrok.io")
        assert ngrok_manager_enabled.tunnel is None
        assert ngrok_manager_enabled.public_url is None
        assert ngrok_manager_enabled.is_healthy is False
    
    @pytest.mark.asyncio
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    @patch('utils.ngrok_manager.ngrok')
    @patch('utils.ngrok_manager.conf')
    async def test_restart_tunnel(self, mock_conf, mock_ngrok, ngrok_manager_enabled):
        """Test restarting tunnel."""
        # Set up active tunnel
        mock_tunnel = Mock()
        mock_tunnel.public_url = "https://new.ngrok.io"
        mock_ngrok.connect.return_value = mock_tunnel
        mock_ngrok.get_tunnels.return_value = [mock_tunnel]
        
        mock_default_conf = Mock()
        mock_conf.get_default.return_value = mock_default_conf
        
        ngrok_manager_enabled.tunnel = Mock()
        ngrok_manager_enabled.public_url = "https://old.ngrok.io"
        
        new_url = await ngrok_manager_enabled.restart_tunnel()
        
        # Should have stopped old tunnel and started new one
        assert new_url == "https://new.ngrok.io"
        assert ngrok_manager_enabled.public_url == "https://new.ngrok.io"


class TestNgrokManagerHealthMonitoring:
    """Test health monitoring functionality."""
    
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    @patch('utils.ngrok_manager.ngrok')
    def test_check_tunnel_health_healthy(self, mock_ngrok, ngrok_manager_enabled):
        """Test health check when tunnel is healthy."""
        mock_tunnel = Mock()
        mock_tunnel.public_url = "https://test.ngrok.io"
        
        ngrok_manager_enabled.tunnel = mock_tunnel
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        
        mock_ngrok.get_tunnels.return_value = [mock_tunnel]
        
        is_healthy = ngrok_manager_enabled._check_tunnel_health()
        assert is_healthy is True
    
    @patch('utils.ngrok_manager.NGROK_AVAILABLE', True)
    @patch('utils.ngrok_manager.ngrok')
    def test_check_tunnel_health_unhealthy(self, mock_ngrok, ngrok_manager_enabled):
        """Test health check when tunnel is unhealthy."""
        ngrok_manager_enabled.tunnel = Mock()
        ngrok_manager_enabled.public_url = "https://test.ngrok.io"
        
        # Return empty list (tunnel not found)
        mock_ngrok.get_tunnels.return_value = []
        
        is_healthy = ngrok_manager_enabled._check_tunnel_health()
        assert is_healthy is False


class TestNgrokManagerSingleton:
    """Test singleton pattern for ngrok manager."""
    
    def test_get_ngrok_manager_singleton(self):
        """Test that get_ngrok_manager returns the same instance."""
        manager1 = get_ngrok_manager()
        manager2 = get_ngrok_manager()
        
        assert manager1 is manager2


class TestNgrokManagerCustomDomain:
    """Test custom domain configuration."""
    
    @patch.dict(os.environ, {
        "NGROK_ENABLED": "true",
        "NGROK_DOMAIN": "custom.domain.com",
        "PORT": "8000"
    })
    def test_custom_domain_config(self):
        """Test that custom domain is loaded from environment."""
        manager = NgrokManager()
        assert manager.domain == "custom.domain.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
