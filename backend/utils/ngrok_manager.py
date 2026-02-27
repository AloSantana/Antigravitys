"""
Ngrok Tunnel Manager for Antigravity Workspace.

Provides programmatic ngrok tunnel management:
- Auto-start tunnel on application startup
- Health monitoring and auto-reconnection
- Public URL exposure via API and WebSocket
- Integration with RemoteConfig for CORS management
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import pyngrok
try:
    from pyngrok import ngrok, conf
    from pyngrok.exception import PyngrokError
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False
    logger.warning("pyngrok not installed. Install with: pip install pyngrok")


class NgrokManager:
    """
    Manages ngrok tunnels for public URL access.
    
    Features:
    - Automatic tunnel creation and management
    - Health monitoring and reconnection
    - Public URL broadcasting
    - Integration with RemoteConfig
    """
    
    def __init__(self):
        """Initialize the ngrok manager."""
        self.enabled = os.getenv("NGROK_ENABLED", "false").lower() == "true"
        self.auth_token = os.getenv("NGROK_AUTH_TOKEN", "")
        self.region = os.getenv("NGROK_REGION", "us")
        self.domain = os.getenv("NGROK_DOMAIN", "")
        self.port = int(os.getenv("PORT", "8000"))
        
        self.tunnel = None
        self.public_url = None
        self.tunnel_created_at = None
        self.health_check_task = None
        self.is_healthy = False
        
        if not NGROK_AVAILABLE and self.enabled:
            logger.error("Ngrok is enabled but pyngrok is not installed")
            self.enabled = False
    
    async def start_tunnel(self) -> Optional[str]:
        """
        Start the ngrok tunnel.
        
        Returns:
            Public URL if successful, None otherwise
        """
        if not self.enabled:
            logger.info("Ngrok is disabled")
            return None
        
        if not NGROK_AVAILABLE:
            logger.error("Cannot start ngrok: pyngrok not installed")
            return None
        
        try:
            # Set auth token if provided
            if self.auth_token:
                conf.get_default().auth_token = self.auth_token
                logger.info("Ngrok auth token configured")
            
            # Set region
            conf.get_default().region = self.region
            logger.info(f"Ngrok region set to: {self.region}")
            
            # Kill any existing ngrok sessions to avoid ERR_NGROK_108
            try:
                existing_tunnels = ngrok.get_tunnels()
                for t in existing_tunnels:
                    ngrok.disconnect(t.public_url)
                    logger.info(f"Disconnected existing tunnel: {t.public_url}")
                if existing_tunnels:
                    ngrok.kill()
                    logger.info("Killed existing ngrok process to free session slot")
                    await asyncio.sleep(2)
            except Exception:
                # If we can't query tunnels, try killing the process directly
                try:
                    ngrok.kill()
                    await asyncio.sleep(2)
                except Exception:
                    pass
            
            # Create tunnel options
            tunnel_options = {
                "addr": self.port,
            }
            
            # Add custom domain if provided (requires paid ngrok plan)
            if self.domain:
                tunnel_options["hostname"] = self.domain
                logger.info(f"Using custom domain: {self.domain}")
            
            # Start the tunnel
            logger.info(f"Starting ngrok tunnel on port {self.port}...")
            self.tunnel = ngrok.connect(**tunnel_options)
            self.public_url = self.tunnel.public_url
            self.tunnel_created_at = datetime.now()
            self.is_healthy = True
            
            logger.info("Ngrok tunnel started successfully!")
            logger.info(f"  Public URL: {self.public_url}")
            logger.info(f"  Local Port: {self.port}")
            logger.info(f"  Region: {self.region}")
            
            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._health_monitor())
            
            return self.public_url
        
        except PyngrokError as e:
            error_msg = str(e)
            if "ERR_NGROK_108" in error_msg or "simultaneous" in error_msg:
                logger.warning("Ngrok session limit reached (free plan). Continuing without tunnel.")
            else:
                logger.error(f"Ngrok error: {e}")
            self.is_healthy = False
            return None
        except Exception as e:
            logger.error(f"Failed to start ngrok tunnel: {e}", exc_info=True)
            self.is_healthy = False
            return None
    
    async def stop_tunnel(self):
        """Stop the ngrok tunnel."""
        if not NGROK_AVAILABLE:
            return
        
        try:
            # Stop health monitoring
            if self.health_check_task:
                task = self.health_check_task
                current = asyncio.current_task()
                # Avoid a task cancelling/awaiting itself when called from _health_monitor
                if task is not current:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        # Cancellation is expected after explicit cancel() during shutdown.
                        logger.debug("Health check task cancellation acknowledged.")
                        pass
            
            # Disconnect tunnel
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
                logger.info(f"Ngrok tunnel disconnected: {self.public_url}")
                self.tunnel = None
                self.public_url = None
                self.is_healthy = False
        
        except Exception as e:
            logger.error(f"Error stopping ngrok tunnel: {e}", exc_info=True)
    
    async def restart_tunnel(self) -> Optional[str]:
        """
        Restart the ngrok tunnel.
        
        Returns:
            New public URL if successful, None otherwise
        """
        logger.info("Restarting ngrok tunnel...")
        await self.stop_tunnel()
        await asyncio.sleep(2)  # Brief pause before reconnecting
        return await self.start_tunnel()
    
    async def _health_monitor(self):
        """
        Background task to monitor tunnel health and reconnect if needed.
        Runs every 30 seconds.
        """
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check if tunnel is still active
                if not self._check_tunnel_health():
                    logger.warning("Ngrok tunnel health check failed")
                    self.is_healthy = False
                    
                    # Attempt reconnection
                    reconnect_attempts += 1
                    if reconnect_attempts <= max_reconnect_attempts:
                        logger.info(f"Attempting to reconnect ngrok tunnel (attempt {reconnect_attempts}/{max_reconnect_attempts})...")
                        new_url = await self.restart_tunnel()
                        
                        if new_url:
                            logger.info(f"Ngrok tunnel reconnected: {new_url}")
                            reconnect_attempts = 0  # Reset counter on success
                        else:
                            logger.error("Failed to reconnect ngrok tunnel")
                    else:
                        logger.error(f"Max reconnection attempts ({max_reconnect_attempts}) reached, stopping health monitor")
                        break
                else:
                    # Tunnel is healthy
                    self.is_healthy = True
                    reconnect_attempts = 0  # Reset counter
            
            except asyncio.CancelledError:
                logger.info("Ngrok health monitor cancelled")
                break
            except Exception as e:
                logger.error(f"Error in ngrok health monitor: {e}", exc_info=True)
                await asyncio.sleep(10)  # Brief pause before continuing
    
    def _check_tunnel_health(self) -> bool:
        """
        Check if the tunnel is still active.
        
        Returns:
            True if healthy, False otherwise
        """
        if not NGROK_AVAILABLE or not self.tunnel:
            return False
        
        try:
            # Get list of active tunnels
            tunnels = ngrok.get_tunnels()
            
            # Check if our tunnel is in the list
            for tunnel in tunnels:
                if tunnel.public_url == self.public_url:
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking tunnel health: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the ngrok tunnel.
        
        Returns:
            Status dictionary
        """
        status = {
            "enabled": self.enabled,
            "available": NGROK_AVAILABLE,
            "active": self.tunnel is not None,
            "healthy": self.is_healthy,
            "public_url": self.public_url,
            "port": self.port,
            "region": self.region,
        }
        
        if self.tunnel_created_at:
            status["created_at"] = self.tunnel_created_at.isoformat()
            status["uptime_seconds"] = (datetime.now() - self.tunnel_created_at).total_seconds()
        
        if self.domain:
            status["custom_domain"] = self.domain
        
        return status
    
    def get_public_url(self) -> Optional[str]:
        """
        Get the current public URL.
        
        Returns:
            Public URL if tunnel is active, None otherwise
        """
        return self.public_url if self.is_healthy else None
    
    def get_websocket_url(self) -> Optional[str]:
        """
        Get the WebSocket URL for the ngrok tunnel.
        
        Returns:
            WebSocket URL if tunnel is active, None otherwise
        """
        if not self.public_url:
            return None
        
        # Convert http(s) to ws(s)
        if self.public_url.startswith("https://"):
            return self.public_url.replace("https://", "wss://") + "/ws"
        elif self.public_url.startswith("http://"):
            return self.public_url.replace("http://", "ws://") + "/ws"
        else:
            return None
    
    def get_cors_origins(self) -> list:
        """
        Get CORS origins to add for ngrok tunnel.
        
        Returns:
            List of origin URLs to allow
        """
        if not self.public_url:
            return []
        
        return [self.public_url]


# Global instance
_ngrok_manager = None


def get_ngrok_manager() -> NgrokManager:
    """
    Get the global ngrok manager instance.
    
    Returns:
        NgrokManager instance
    """
    global _ngrok_manager
    if _ngrok_manager is None:
        _ngrok_manager = NgrokManager()
    return _ngrok_manager


async def start_ngrok() -> Optional[str]:
    """
    Convenience function to start ngrok tunnel.
    
    Returns:
        Public URL if successful, None otherwise
    """
    manager = get_ngrok_manager()
    return await manager.start_tunnel()


async def stop_ngrok():
    """Convenience function to stop ngrok tunnel."""
    manager = get_ngrok_manager()
    await manager.stop_tunnel()


def get_ngrok_status() -> Dict[str, Any]:
    """
    Convenience function to get ngrok status.
    
    Returns:
        Status dictionary
    """
    manager = get_ngrok_manager()
    return manager.get_status()
