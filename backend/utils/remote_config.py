"""
Remote configuration utilities for Antigravity Workspace.
Handles remote VPS deployment configuration and validation.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from project root .env
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)


class RemoteConfig:
    """Manages remote access configuration."""
    
    def __init__(self, ngrok_url: Optional[str] = None):
        self.remote_access = os.getenv("REMOTE_ACCESS", "false").lower() == "true"
        self.external_host = os.getenv("EXTERNAL_HOST", "")
        self.frontend_port = int(os.getenv("FRONTEND_PORT", "3000"))
        self.backend_port = int(os.getenv("BACKEND_PORT", "8000"))
        self.host = os.getenv("HOST", "0.0.0.0")
        self.ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
        self.ssl_cert_path = os.getenv("SSL_CERT_PATH", "")
        self.ssl_key_path = os.getenv("SSL_KEY_PATH", "")
        
        # Ngrok configuration
        self.ngrok_enabled = os.getenv("NGROK_ENABLED", "false").lower() == "true"
        self.ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN", "")
        # Check for ngrok URL from parameter, env var, or manager
        self.ngrok_url = ngrok_url or os.getenv("NGROK_URL", "")
        if not self.ngrok_url and self.ngrok_enabled:
            # Try to get from ngrok manager if available
            try:
                from utils.ngrok_manager import get_ngrok_manager
                manager = get_ngrok_manager()
                self.ngrok_url = manager.get_public_url() or ""
            except Exception:
                pass
    
    def is_remote_mode(self) -> bool:
        """Check if running in remote access mode."""
        return (self.remote_access and bool(self.external_host)) or self.is_ngrok_mode()
    
    def is_ngrok_mode(self) -> bool:
        """Check if running in ngrok tunnel mode."""
        return self.ngrok_enabled and bool(self.ngrok_url)
    
    def get_frontend_url(self) -> str:
        """Get the frontend URL based on configuration."""
        # Ngrok takes precedence
        if self.is_ngrok_mode():
            return self.ngrok_url
        
        if self.is_remote_mode():
            protocol = "https" if self.ssl_enabled else "http"
            port_suffix = "" if (
                (protocol == "https" and self.frontend_port == 443) or
                (protocol == "http" and self.frontend_port == 80)
            ) else f":{self.frontend_port}"
            return f"{protocol}://{self.external_host}{port_suffix}"
        return f"http://localhost:{self.frontend_port}"
    
    def get_backend_url(self) -> str:
        """Get the backend URL based on configuration."""
        # Ngrok takes precedence
        if self.is_ngrok_mode():
            return self.ngrok_url
        
        if self.is_remote_mode():
            protocol = "https" if self.ssl_enabled else "http"
            port_suffix = "" if (
                (protocol == "https" and self.backend_port == 443) or
                (protocol == "http" and self.backend_port == 80)
            ) else f":{self.backend_port}"
            return f"{protocol}://{self.external_host}{port_suffix}"
        return f"http://localhost:{self.backend_port}"
    
    def get_websocket_url(self) -> str:
        """Get the WebSocket URL based on configuration."""
        # Ngrok takes precedence
        if self.is_ngrok_mode():
            # Convert http(s) to ws(s) for ngrok URL
            if self.ngrok_url.startswith("https://"):
                return self.ngrok_url.replace("https://", "wss://") + "/ws"
            elif self.ngrok_url.startswith("http://"):
                return self.ngrok_url.replace("http://", "ws://") + "/ws"
        
        if self.is_remote_mode():
            protocol = "wss" if self.ssl_enabled else "ws"
            port_suffix = "" if (
                (protocol == "wss" and self.backend_port == 443) or
                (protocol == "ws" and self.backend_port == 80)
            ) else f":{self.backend_port}"
            return f"{protocol}://{self.external_host}{port_suffix}/ws"
        return f"ws://localhost:{self.backend_port}/ws"
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate remote configuration.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check ngrok configuration
        if self.ngrok_enabled:
            if not self.ngrok_url:
                warnings.append("NGROK_ENABLED is true but tunnel is not active")
        
        # Check remote access configuration
        if self.remote_access:
            if not self.external_host and not self.is_ngrok_mode():
                issues.append("REMOTE_ACCESS is enabled but EXTERNAL_HOST is not set and ngrok is not active")
            
            # Check SSL configuration
            if self.ssl_enabled:
                if not self.ssl_cert_path or not os.path.exists(self.ssl_cert_path):
                    issues.append(f"SSL enabled but cert file not found: {self.ssl_cert_path}")
                if not self.ssl_key_path or not os.path.exists(self.ssl_key_path):
                    issues.append(f"SSL enabled but key file not found: {self.ssl_key_path}")
            else:
                warnings.append("Remote access enabled without SSL - connections will not be encrypted")
        
        # Check port configuration
        if self.frontend_port == self.backend_port:
            warnings.append(f"Frontend and backend using same port: {self.frontend_port}")
        
        # Check host binding
        if self.remote_access and self.host == "127.0.0.1":
            issues.append("Remote access enabled but HOST is set to 127.0.0.1 (should be 0.0.0.0)")
        
        mode = "local"
        if self.is_ngrok_mode():
            mode = "ngrok"
        elif self.is_remote_mode():
            mode = "remote"
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "mode": mode,
            "ngrok_enabled": self.ngrok_enabled,
            "ngrok_active": self.is_ngrok_mode(),
            "frontend_url": self.get_frontend_url(),
            "backend_url": self.get_backend_url(),
            "websocket_url": self.get_websocket_url()
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        mode = "local"
        if self.is_ngrok_mode():
            mode = "ngrok"
        elif self.is_remote_mode():
            mode = "remote"
        
        return {
            "remote_access": self.remote_access,
            "external_host": self.external_host or "not configured",
            "frontend_port": self.frontend_port,
            "backend_port": self.backend_port,
            "host": self.host,
            "ssl_enabled": self.ssl_enabled,
            "ngrok_enabled": self.ngrok_enabled,
            "ngrok_active": self.is_ngrok_mode(),
            "ngrok_url": self.ngrok_url or "not active",
            "mode": mode,
            "urls": {
                "frontend": self.get_frontend_url(),
                "backend": self.get_backend_url(),
                "websocket": self.get_websocket_url()
            }
        }


def get_remote_config() -> RemoteConfig:
    """Get the current remote configuration."""
    return RemoteConfig()


def validate_remote_config() -> None:
    """
    Validate remote configuration and log results.
    
    Raises:
        RuntimeError: If configuration has critical issues
    """
    config = get_remote_config()
    validation = config.validate()
    
    # Log configuration summary
    logger.info(f"Running in {validation['mode']} mode")
    logger.info(f"Frontend URL: {validation['frontend_url']}")
    logger.info(f"Backend URL: {validation['backend_url']}")
    logger.info(f"WebSocket URL: {validation['websocket_url']}")
    
    # Log warnings
    for warning in validation['warnings']:
        logger.warning(warning)
    
    # Log and raise critical issues
    if validation['issues']:
        for issue in validation['issues']:
            logger.error(issue)
        raise RuntimeError(
            f"Remote configuration validation failed: {', '.join(validation['issues'])}"
        )
    
    logger.info("Remote configuration validation passed")
