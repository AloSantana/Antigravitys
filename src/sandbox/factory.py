"""
Factory for creating sandbox instances.
"""

import logging
from typing import Optional

from .base import CodeSandbox
from .local_exec import LocalSandbox
from .docker_exec import DockerSandbox
from src.config import settings

logger = logging.getLogger(__name__)


def get_sandbox(sandbox_type: Optional[str] = None) -> CodeSandbox:
    """
    Get a sandbox instance based on configuration or explicit type.
    
    Args:
        sandbox_type: Optional explicit sandbox type ("local" or "docker")
                     If not provided, uses settings.SANDBOX_TYPE
    
    Returns:
        CodeSandbox instance
        
    Raises:
        ValueError: If sandbox type is unknown or unavailable
    """
    sandbox_type = sandbox_type or settings.SANDBOX_TYPE
    sandbox_type = sandbox_type.lower()
    
    if sandbox_type == "local":
        sandbox = LocalSandbox()
        
        if not sandbox.is_available():
            raise ValueError("Local sandbox is not available")
        
        logger.info("Using local subprocess sandbox")
        return sandbox
    
    elif sandbox_type == "docker":
        sandbox = DockerSandbox()
        
        if not sandbox.is_available():
            # Fall back to local if Docker is not available
            logger.warning("Docker sandbox not available, falling back to local")
            return LocalSandbox()
        
        logger.info("Using Docker container sandbox")
        return sandbox
    
    else:
        raise ValueError(f"Unknown sandbox type: {sandbox_type}")


def get_available_sandboxes() -> list:
    """
    Get a list of available sandbox types on this system.
    
    Returns:
        List of available sandbox type names
    """
    available = []
    
    # Local is always available
    if LocalSandbox().is_available():
        available.append("local")
    
    # Check Docker availability
    if DockerSandbox().is_available():
        available.append("docker")
    
    return available
