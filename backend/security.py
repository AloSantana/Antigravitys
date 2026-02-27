"""
Security utilities for the Antigravity Workspace Backend.
Provides input validation, rate limiting, and authentication helpers.
"""

import os
import re
from pathlib import Path
from typing import Optional, List
from fastapi import HTTPException, UploadFile
import logging

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 10000))  # 10000 chars default
ALLOWED_EXTENSIONS = {'.py', '.js', '.md', '.txt', '.json', '.yaml', '.yml', '.sh', '.html', '.css'}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename (basename only, no path components)
        
    Raises:
        HTTPException: If filename is invalid
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty")
    
    # Check for path traversal attempts
    if '..' in filename or filename.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid filename: path traversal detected")
    
    # Get just the filename without any directory components
    safe_filename = os.path.basename(filename)
    
    # Additional check - filename must be reasonable
    if not safe_filename or safe_filename == '.' or safe_filename == '..':
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check for null bytes (can cause issues)
    if '\x00' in safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename: contains null bytes")
    
    return safe_filename


def validate_file_extension(filename: str, allowed_extensions: set = ALLOWED_EXTENSIONS) -> None:
    """
    Validate that a file has an allowed extension.
    
    Args:
        filename: The filename to check
        allowed_extensions: Set of allowed extensions (with leading dot)
        
    Raises:
        HTTPException: If extension is not allowed
    """
    ext = Path(filename).suffix.lower()
    
    if not ext:
        raise HTTPException(
            status_code=400, 
            detail="File must have an extension"
        )
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(allowed_extensions))}"
        )


async def validate_upload_file(file: UploadFile) -> tuple[str, int]:
    """
    Validate an uploaded file for security.
    
    Args:
        file: The uploaded file
        
    Returns:
        Tuple of (sanitized_filename, file_size)
        
    Raises:
        HTTPException: If validation fails
    """
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Validate extension
    validate_file_extension(safe_filename)
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    if size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    return safe_filename, size


def validate_message_length(message: str, max_length: int = MAX_MESSAGE_LENGTH) -> None:
    """
    Validate message length to prevent abuse.
    
    Args:
        message: The message to validate
        max_length: Maximum allowed length
        
    Raises:
        HTTPException: If message is too long or empty
    """
    if not message or len(message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if len(message) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Maximum length: {max_length} characters"
        )


def get_allowed_origins() -> List[str]:
    """
    Get allowed CORS origins from environment variable.
    Supports remote access, ngrok, and wildcard for development.
    
    Returns:
        List of allowed origin URLs or ["*"] for wildcard
    """
    origins_str = os.getenv("ALLOWED_ORIGINS", "")
    
    # Check for wildcard (development/testing only)
    if origins_str.strip() == "*":
        logger.warning("CORS configured for wildcard (*) - DO NOT use in production!")
        return ["*"]
    
    # Check if remote access is enabled
    remote_access = os.getenv("REMOTE_ACCESS", "false").lower() == "true"
    external_host = os.getenv("EXTERNAL_HOST", "")
    frontend_port = os.getenv("FRONTEND_PORT", "3000")
    backend_port = os.getenv("BACKEND_PORT", "8000")
    
    # Start with default localhost origins
    default_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Add remote origins if enabled
    remote_origins = []
    if remote_access and external_host:
        remote_origins.extend([
            f"http://{external_host}:{frontend_port}",
            f"http://{external_host}:{backend_port}",
            f"https://{external_host}:{frontend_port}",
            f"https://{external_host}:{backend_port}",
            f"http://{external_host}",
            f"https://{external_host}"
        ])
        logger.info(f"Remote access enabled for host: {external_host}")
        
    # Add ngrok origin if enabled and active
    ngrok_origins = []
    try:
        from utils.ngrok_manager import get_ngrok_manager
        ngrok_manager = get_ngrok_manager()
        if ngrok_manager.enabled and ngrok_manager.get_public_url():
            ngrok_url = ngrok_manager.get_public_url()
            if ngrok_url:
                ngrok_origins.append(ngrok_url)
                logger.info(f"Ngrok CORS origin added: {ngrok_url}")
    except ImportError:
        logger.debug("Could not import ngrok_manager, skipping ngrok origin check.")
    except Exception as e:
        logger.warning(f"Error getting ngrok URL for CORS: {e}")

    # Parse custom origins from environment
    custom_origins = []
    if origins_str:
        origins = [origin.strip() for origin in origins_str.split(',')]
        for origin in origins:
            if origin and (origin.startswith('http://') or origin.startswith('https://')):
                custom_origins.append(origin)
            elif origin:
                logger.warning(f"Invalid origin format ignored: {origin}")
    
    # Combine all origins and deduplicate
    all_origins = list(set(default_origins + remote_origins + custom_origins + ngrok_origins))
    
    if not all_origins:
        logger.warning("No valid CORS origins configured, using default localhost only")
        return default_origins
    
    return all_origins


def validate_required_env_vars() -> None:
    """
    Validate that all required environment variables are set.
    
    Raises:
        RuntimeError: If required variables are missing
    """
    # Optional but recommended variables
    optional_vars = {
        "GEMINI_API_KEY": "Gemini AI functionality will be unavailable",
        "ALLOWED_ORIGINS": "Using default localhost origins for CORS",
    }
    
    # Check optional vars and warn
    for var, warning in optional_vars.items():
        if not os.getenv(var):
            logger.warning(f"{var} not set. {warning}")
    
    # Could add required vars here in the future
    # For now, the app can run without Gemini API key (uses local only)
