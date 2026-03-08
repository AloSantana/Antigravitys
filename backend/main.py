from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field
import uvicorn
import os
import logging
import signal
import asyncio
import sqlite3
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from agent.orchestrator import Orchestrator
from agent.manager import AgentManager
from watcher import Watcher
from utils.performance import add_performance_endpoints
from utils.remote_config import get_remote_config
from utils.ngrok_manager import get_ngrok_manager
from utils.platform_detect import get_platform_info
from security import (
    get_allowed_origins, 
    validate_required_env_vars,
    validate_upload_file,
    validate_message_length
)
from settings_manager import SettingsManager
from conversation_manager import ConversationManager
from artifact_manager import ArtifactManager
from user_manager import UserManager, VALID_ROLES as _USER_VALID_ROLES

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate environment on startup
validate_required_env_vars()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Check if running under pytest and disable limiter
import sys
if "pytest" in sys.modules:
    limiter.enabled = False
    logger.info("Rate limiter disabled for testing execution")

# Global instances (initialized in lifespan)
orchestrator = None
watcher = None
settings_manager = None
conversation_manager = None
artifact_manager = None
agent_manager_instance = None
user_manager = None

# Project root (parent of backend/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Shutdown management
shutdown_event = asyncio.Event()
shutdown_timeout = 30  # seconds

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(signum).name
    logger.info(f"Received signal {signal_name}, initiating graceful shutdown...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Antigravity Workspace Backend...")
    
    # Detect platform
    platform_info = get_platform_info()
    logger.info(f"Platform: {platform_info['platform']} ({platform_info['system']} {platform_info['release']})")
    
    # Initialize global components
    global orchestrator, watcher, settings_manager, conversation_manager, artifact_manager, agent_manager_instance, user_manager
    
    # Initialize basic managers first
    try:
        settings_manager = SettingsManager()
        # Ensure data directory exists for SQLite databases
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        conversation_manager = ConversationManager(db_path=os.path.join(data_dir, "conversations.db"))
        artifact_manager = ArtifactManager(artifacts_dir=os.path.join(project_root, "artifacts"))
        user_manager = UserManager(db_path=os.path.join(data_dir, "users.db"))
        agent_manager_instance = AgentManager(agents_dir=os.path.join(project_root, ".github", "agents"))
        logger.info("Basic managers initialized")
    except Exception as e:
        logger.critical(f"Failed to initialize basic managers: {e}", exc_info=True)
        # Critical failure, likely permissions or disk issue
    
    # Initialize Orchestrator (may connect to external services)
    try:
        logger.info("Initializing Orchestrator...")
        orchestrator = Orchestrator()
        logger.info("Orchestrator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Orchestrator: {e}", exc_info=True)
        # TODO: Initialize a fallback/mock orchestrator here if needed
        
    # Initialize Watcher
    try:
        watcher_path = os.path.join(project_root, "drop_zone")
        if not os.path.exists(watcher_path):
            os.makedirs(watcher_path, exist_ok=True)
        watcher = Watcher(watch_dir=watcher_path)
        watcher.start()
        logger.info("Watcher started successfully")
    except Exception as e:
        logger.error(f"Failed to start watcher: {e}", exc_info=True)
        # Continue anyway - watcher failure shouldn't prevent app startup
    
    # Start ngrok tunnel if enabled
    ngrok_manager = get_ngrok_manager()
    if ngrok_manager.enabled:
        public_url = await ngrok_manager.start_tunnel()
        if public_url:
            logger.info(f"✓ Ngrok tunnel active: {public_url}")
            # Note: WebSocket client broadcasting would require a connection manager
            # This is a placeholder for when that's implemented
    
    yield
    
    # Shutdown
    logger.info("Shutting down Antigravity Workspace Backend...")
    
    try:
        # Create shutdown task with timeout
        shutdown_task = asyncio.create_task(graceful_shutdown())
        
        # Wait for shutdown with timeout
        try:
            await asyncio.wait_for(shutdown_task, timeout=shutdown_timeout)
            logger.info("Graceful shutdown completed")
        except asyncio.TimeoutError:
            logger.warning(f"Shutdown exceeded {shutdown_timeout}s timeout, forcing shutdown")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

async def graceful_shutdown():
    """Perform graceful shutdown of all components."""
    shutdown_tasks = []
    
    # Stop ngrok tunnel
    ngrok_manager = get_ngrok_manager()
    if ngrok_manager.enabled:
        try:
            logger.info("Stopping ngrok tunnel...")
            await ngrok_manager.stop_tunnel()
            logger.info("Ngrok tunnel stopped")
        except Exception as e:
            logger.error(f"Error stopping ngrok tunnel: {e}")
    
    # Stop watcher
    try:
        logger.info("Stopping file watcher...")
        watcher.stop()
        logger.info("File watcher stopped")
    except Exception as e:
        logger.error(f"Error stopping watcher: {e}")
    
    # Close orchestrator clients
    if orchestrator:
        try:
            logger.info("Closing orchestrator clients...")
            await orchestrator.local.close()
            logger.info("Orchestrator clients closed")
        except Exception as e:
            logger.warning(f"Failed to close orchestrator client: {e}")
    
    # Clear caches
    if orchestrator:
        try:
            logger.info("Clearing caches...")
            orchestrator.clear_cache()
            logger.info("Caches cleared")
        except Exception as e:
            logger.warning(f"Error clearing caches: {e}")
    
    # Give time for pending operations
    logger.info("Waiting for pending operations...")
    await asyncio.sleep(0.5)

app = FastAPI(
    title="Antigravity Workspace Backend",
    description="AI-powered development workspace with performance optimization",
    version="2.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with environment-based allowed origins
allowed_origins = get_allowed_origins()
logger.info(f"Configured CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://.*\.ngrok-free\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from utils.file_utils import get_file_structure

# Mount frontend static files for cloud deployment
frontend_dir = os.path.join(project_root, "frontend")
if os.path.exists(frontend_dir) and os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    # Mount frontend/css
    css_dir = os.path.join(frontend_dir, "css")
    if os.path.exists(css_dir) and os.path.isdir(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    
    # Mount frontend/js
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir) and os.path.isdir(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
        
    logger.info(f"Frontend static files mounted from: {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}, static file serving disabled")

@app.get("/")
async def root(request: Request):
    """
    Root endpoint with content negotiation:
    - Browser requests (Accept: text/html) → Serve frontend/index.html
    - API/programmatic requests → Return JSON status
    """
    # Check if request accepts HTML (browser request)
    accept_header = request.headers.get("accept", "")
    
    if "text/html" in accept_header:
        # Serve frontend for browser requests
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            # Fallback to JSON if frontend not available
            logger.warning("Frontend index.html not found, returning JSON response")
            return JSONResponse({
                "message": "Antigravity Workspace Backend is Running",
                "version": "2.0.0",
                "status": "operational",
                "note": "Frontend not available - index.html not found"
            })
    
    # Return JSON for API/programmatic requests
    return {
        "message": "Antigravity Workspace Backend is Running",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
@limiter.limit("120/minute")
async def health_check(request: Request):
    """Basic health check endpoint - lightweight for load balancers."""
    return {
        "status": "healthy",
        "watcher": "running" if (watcher is not None and watcher.is_running()) else "stopped",
        "cache_hit_rate": f"{orchestrator.get_cache_hit_rate():.1%}" if orchestrator is not None else "N/A"
    }

@app.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe - checks if app is alive.
    Returns 200 if app is running, should restart if this fails.
    """
    return {"status": "alive", "service": "antigravity-workspace"}

@app.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe - checks if app is ready to serve traffic.
    Returns detailed component health status.
    """
    from health_check import build_readiness_report

    health_status, all_healthy = build_readiness_report(watcher, orchestrator)

    # Return 503 if not ready
    if not all_healthy:
        from fastapi import Response
        return Response(
            content=str(health_status),
            status_code=503,
            media_type="application/json"
        )

    return health_status

@app.get("/config")
@limiter.limit("60/minute")
async def get_config(request: Request):
    """
    Returns the current remote configuration and URLs.
    Useful for frontend to detect backend location.
    """
    config = get_remote_config()
    return config.get_config_summary()

@app.get("/files")
@limiter.limit("60/minute")
async def get_files(request: Request):
    """
    Returns the file structure of the drop_zone.
    """
    return get_file_structure(watcher.watch_dir)

from fastapi import UploadFile, File, Request
import shutil

@app.post("/upload")
@limiter.limit("20/minute")  # Stricter rate limit for uploads
async def upload_files(request: Request, files: list[UploadFile] = File(...)):
    """
    Handles file uploads from the browser drag-and-drop.
    Includes security validations:
    - File size limits
    - Extension whitelist
    - Filename sanitization
    - Path traversal prevention
    """
    uploaded_files = []
    
    for file in files:
        try:
            # Validate file with security checks
            safe_filename, file_size = await validate_upload_file(file)
            
            # Create safe file location
            file_location = os.path.join(watcher.watch_dir, safe_filename)
            
            # Ensure we're writing within the watch directory
            file_location = os.path.abspath(file_location)
            watch_dir_abs = os.path.abspath(watcher.watch_dir)
            if not file_location.startswith(watch_dir_abs):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file path: directory traversal detected"
                )
            
            # Write file
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(file.file, file_object)
            
            uploaded_files.append({
                "filename": safe_filename,
                "size": file_size
            })
            logger.info(f"Uploaded file: {safe_filename} ({file_size} bytes)")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files
    }


@app.get("/api/files/read")
@limiter.limit("60/minute")
async def read_file_content(request: Request, path: str = Query(..., min_length=1)):
    """
    Read the content of a file inside the drop_zone.

    Args:
        path: Relative path to the file within the drop_zone directory

    Returns:
        File name and UTF-8 decoded content
    """
    try:
        watch_dir_abs = os.path.abspath(watcher.watch_dir if watcher else os.path.join(project_root, "drop_zone"))
        # Resolve to absolute, preventing path traversal
        requested = os.path.abspath(os.path.join(watch_dir_abs, path))
        if not requested.startswith(watch_dir_abs + os.sep) and requested != watch_dir_abs:
            raise HTTPException(status_code=400, detail="Invalid path: directory traversal detected")
        if not os.path.isfile(requested):
            raise HTTPException(status_code=404, detail="File not found")

        file_size = os.path.getsize(requested)
        max_read = 1 * 1024 * 1024  # 1 MB cap for preview
        with open(requested, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_read)
        truncated = file_size > max_read

        return {
            "name": os.path.basename(requested),
            "path": path,
            "size": file_size,
            "content": content,
            "truncated": truncated,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to read file '{path}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


class RepoIndexRequest(BaseModel):
    """Request body for repo indexing."""
    directories: List[str] = Field(
        default=[".", "src", "backend", "docs", ".github/agents", "tests", "scripts", "tools", "examples", ".antigravity", ".specs"],
        description="Project-relative directories to index (relative to project root). Use '.' to include root-level files."
    )
    extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".md", ".txt", ".json", ".yaml", ".yml", ".html", ".css"],
        description="File extensions to include"
    )
    overwrite: bool = Field(default=False, description="Overwrite existing files in drop_zone")


@app.post("/api/repo/index")
@limiter.limit("5/minute")
async def index_repo_files(request: Request, body: RepoIndexRequest = RepoIndexRequest()):
    """
    Copy project source files into the drop_zone so they are automatically
    ingested into the RAG knowledge base.

    Only files within the project root are accessible. Files are copied with
    a flattened name (path separators replaced with '__') to avoid collisions.

    Returns:
        Summary of files copied / skipped / failed
    """
    try:
        watch_dir_abs = os.path.abspath(watcher.watch_dir if watcher else os.path.join(project_root, "drop_zone"))
        allowed_ext = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in body.extensions}

        # Validate requested directories — must stay inside project root
        safe_dirs: List[str] = []
        root_files_only: bool = False  # flag to handle "." (root-level files without recursion)
        for rel_dir in body.directories:
            if rel_dir == ".":
                root_files_only = True
                safe_dirs.append(project_root)
                continue
            candidate = os.path.abspath(os.path.join(project_root, rel_dir))
            if not candidate.startswith(project_root):
                logger.warning(f"Skipping directory outside project root: {rel_dir}")
                continue
            if os.path.isdir(candidate):
                safe_dirs.append(candidate)

        copied: List[str] = []
        skipped: List[str] = []
        failed: List[str] = []

        for source_dir in safe_dirs:
            for root, _dirs, files in os.walk(source_dir):
                # When source_dir is the project root, only process root-level files (no recursion)
                if root_files_only and os.path.abspath(root) == os.path.abspath(project_root):
                    _dirs.clear()  # prevent recursion into subdirectories for root-level scan
                # Skip hidden dirs and common noise
                _dirs[:] = [d for d in _dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", ".venv", "venv")]
                for filename in files:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in allowed_ext:
                        continue

                    src_path = os.path.join(root, filename)

                    # Build a unique flat name: relative path with / → __
                    rel = os.path.relpath(src_path, project_root)
                    flat_name = rel.replace(os.sep, "__")

                    dest_path = os.path.join(watch_dir_abs, flat_name)

                    try:
                        if os.path.exists(dest_path) and not body.overwrite:
                            skipped.append(rel)
                            continue
                        # Only copy text-readable files up to 2 MB
                        if os.path.getsize(src_path) > 2 * 1024 * 1024:
                            skipped.append(f"{rel} (too large)")
                            continue
                        import shutil as _shutil
                        _shutil.copy2(src_path, dest_path)
                        copied.append(rel)
                    except Exception as copy_err:
                        logger.warning(f"Failed to copy {rel}: {copy_err}")
                        failed.append(rel)

        logger.info(f"Repo index: {len(copied)} copied, {len(skipped)} skipped, {len(failed)} failed")
        return {
            "message": f"Indexed {len(copied)} file(s) into drop_zone for RAG analysis",
            "copied": copied,
            "skipped": skipped,
            "failed": failed,
            "total_copied": len(copied),
            "total_skipped": len(skipped),
            "total_failed": len(failed),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to index repo files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to index repo files: {str(e)}")


@app.post("/agent/ask")
@limiter.limit("30/minute")
async def ask_agent(request: Request, query: str):
    """
    Process a request through the AI orchestrator.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized. Check server logs.")
        
    response = await orchestrator.process_request(query)
    return response

@app.post("/agent/clear-cache")
@limiter.limit("30/minute")
async def clear_cache(request: Request):
    """Clear the orchestrator's response cache and return statistics."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    stats = orchestrator.clear_cache()
    vector_cleared = orchestrator.store.clear_cache()
    stats['vector_cache_cleared'] = vector_cleared
    return {
        "message": "Cache cleared successfully",
        "stats": stats
    }

@app.get("/agent/stats")
async def get_agent_stats(request: Request):
    """Get comprehensive orchestrator statistics including cache performance and AI provider status."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    cache_stats = orchestrator.get_cache_stats()
    
    try:
        vector_stats = orchestrator.store.get_stats()
    except Exception:
        vector_stats = {"total_queries": 0, "cache_hits": 0, "cache_hit_rate": 0.0, "cache_hit_rate_percentage": "0.00%", "error": "ChromaDB not available"}
    
    try:
        vertex_stats = orchestrator.vertex.get_stats()
    except Exception:
        vertex_stats = {"available": False, "error": "Vertex AI not configured"}
    
    return {
        "orchestrator": cache_stats,
        "vector_store": vector_stats,
        "vertex_ai": vertex_stats,
        "ai_providers": {
            "vertex_ai_available": orchestrator.vertex.is_available(),
            "gemini_available": orchestrator.gemini.client is not None,
            "local_available": True  # Local is always available
        },
        "combined_hit_rate": (cache_stats.get('hit_rate', 0) + vector_stats.get('cache_hit_rate', 0)) / 2
    }

@app.post("/agent/warm-cache")
@limiter.limit("10/minute")
async def warm_cache(request: Request, queries: List[str] = None):
    """Warm the cache with common queries for better initial performance."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    result = await orchestrator.warm_cache(queries)
    return {
        "message": "Cache warming completed",
        "stats": result
    }

# ═══════════════════════════════════════════════════════════════
# Settings & Configuration API Endpoints
# ═══════════════════════════════════════════════════════════════

# Pydantic models for request/response validation
class SettingsUpdate(BaseModel):
    """Model for settings update requests."""
    server: Optional[Dict[str, Any]] = None
    cors: Optional[Dict[str, List[str]]] = None
    features: Optional[Dict[str, bool]] = None
    active_model: Optional[str] = None

class APIKeyUpdate(BaseModel):
    """Model for API key update requests."""
    key_var: str = Field(..., description="Environment variable name")
    value: str = Field(..., min_length=10, description="API key value")

class APIKeyValidation(BaseModel):
    """Model for API key validation requests."""
    service: str = Field(..., description="Service name (gemini, vertex, github)")
    api_key: str = Field(..., min_length=10, description="API key to validate")

class MCPServerToggle(BaseModel):
    """Model for MCP server toggle requests."""
    enabled: bool = Field(..., description="Enable or disable server")

class EnvVarUpdate(BaseModel):
    """Model for environment variable update."""
    key: str = Field(..., description="Variable name")
    value: str = Field(..., description="Variable value")

@app.get("/settings")
@limiter.limit("60/minute")
async def get_settings(request: Request, include_sensitive: bool = False):
    """
    Get current application settings.
    
    Args:
        include_sensitive: Include redacted sensitive values
        
    Returns:
        Current configuration settings
    """
    try:
        settings = settings_manager.get_settings(include_sensitive=include_sensitive)
        return {
            "success": True,
            "settings": settings
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get settings: {str(e)}"
        )

@app.post("/settings")
@limiter.limit("30/minute")
async def update_settings(request: Request, settings: SettingsUpdate):
    """
    Update application settings.
    
    Args:
        settings: Settings to update
        
    Returns:
        Update results
    """
    try:
        result = settings_manager.update_settings(settings.dict(exclude_none=True))
        
        if result['success']:
            return {
                "success": True,
                "message": "Settings updated successfully",
                "updated": result['updated']
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update settings: {', '.join(result['errors'])}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update settings: {str(e)}"
        )

@app.get("/settings/mcp")
@limiter.limit("30/minute")
async def get_mcp_servers(request: Request):
    """
    Get status of all MCP servers.
    
    Returns:
        List of MCP servers with their status
    """
    try:
        servers = settings_manager.get_mcp_servers_status()
        return {
            "success": True,
            "servers": servers,
            "total": len(servers)
        }
    except Exception as e:
        logger.error(f"Error getting MCP servers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get MCP servers: {str(e)}"
        )

@app.post("/settings/mcp/{server_name}")
@limiter.limit("30/minute")
async def toggle_mcp_server(request: Request, server_name: str, toggle: MCPServerToggle):
    """
    Enable or disable an MCP server.
    
    Args:
        server_name: Name of the MCP server
        toggle: Toggle configuration
        
    Returns:
        Toggle result
    """
    try:
        result = settings_manager.toggle_mcp_server(server_name, toggle.enabled)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling MCP server: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to toggle MCP server: {str(e)}"
        )

@app.get("/ngrok/status")
@limiter.limit("30/minute")
async def get_ngrok_status(request: Request):
    """Get ngrok tunnel status."""
    from utils.ngrok_manager import get_ngrok_manager
    
    ngrok_manager = get_ngrok_manager()
    return ngrok_manager.get_status()

@app.get("/settings/models")
@limiter.limit("30/minute")
async def get_available_models(request: Request):
    """
    Get list of available AI models.
    
    Returns:
        List of AI models with configuration status
    """
    try:
        models = settings_manager.get_available_models()
        active_model = os.getenv('ACTIVE_MODEL', 'gemini')
        
        return {
            "success": True,
            "models": models,
            "active_model": active_model
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models: {str(e)}"
        )

@app.post("/settings/models")
@limiter.limit("30/minute")
async def set_active_model(request: Request, model_id: str):
    """
    Set the active AI model.
    
    Args:
        model_id: Model identifier (gemini, vertex, ollama)
        
    Returns:
        Update result
    """
    try:
        result = settings_manager.set_active_model(model_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting active model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set active model: {str(e)}"
        )

@app.post("/settings/validate")
@limiter.limit("20/minute")
async def validate_settings(request: Request, validation: APIKeyValidation):
    """
    Validate API key and connection.
    
    Args:
        validation: Validation request
        
    Returns:
        Validation result
    """
    try:
        # First validate the key format
        key_validation = settings_manager.validate_api_key(
            validation.service, 
            validation.api_key
        )
        
        if not key_validation['valid']:
            return {
                "success": False,
                "error": key_validation['error']
            }
        
        # Then test the connection
        connection_test = settings_manager.test_connection(validation.service)
        
        return {
            "success": connection_test['success'],
            "validation": key_validation,
            "connection": connection_test
        }
    except Exception as e:
        logger.error(f"Error validating settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate settings: {str(e)}"
        )

@app.post("/settings/api-keys")
@limiter.limit("10/minute")
async def update_api_key(request: Request, update: APIKeyUpdate):
    """
    Update an API key securely.
    
    Args:
        update: API key update request
        
    Returns:
        Update result
    """
    try:
        result = settings_manager.update_api_key(update.key_var, update.value)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update API key: {str(e)}"
        )

@app.get("/settings/env")
@limiter.limit("30/minute")
async def get_environment_variables(request: Request, include_sensitive: bool = False):
    """
    Get environment variables (non-sensitive by default).
    
    Args:
        include_sensitive: Include redacted sensitive values
        
    Returns:
        Environment variables
    """
    try:
        env_vars = settings_manager.get_environment_variables(include_sensitive=include_sensitive)
        
        return {
            "success": True,
            "variables": env_vars,
            "count": len(env_vars)
        }
    except Exception as e:
        logger.error(f"Error getting environment variables: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get environment variables: {str(e)}"
        )

@app.post("/settings/env")
@limiter.limit("20/minute")
async def update_environment_variable(request: Request, update: EnvVarUpdate):
    """
    Update a single environment variable.
    
    Args:
        update: Environment variable update
        
    Returns:
        Update result
    """
    try:
        result = settings_manager.update_environment_variable(update.key, update.value)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating environment variable: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update environment variable: {str(e)}"
        )

@app.get("/settings/export")
@limiter.limit("10/minute")
async def export_configuration(request: Request):
    """
    Export current configuration (sanitized).
    
    Returns:
        Configuration export
    """
    try:
        config = settings_manager.export_config()
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        logger.error(f"Error exporting configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export configuration: {str(e)}"
        )

@app.post("/settings/reload-env")
@limiter.limit("10/minute")
async def reload_environment(request: Request):
    """Reload environment variables and reinitialize orchestrator."""
    try:
        # Reload environment
        reload_result = settings_manager.reload_environment()
        
        # Reinitialize orchestrator with new settings
        orchestrator.reinitialize()
        
        return {
            "success": True,
            "environment_reload": reload_result,
            "orchestrator_reinitialized": True,
            "message": "Environment reloaded and orchestrator reinitialized successfully"
        }
    except Exception as e:
        logger.error(f"Error reloading environment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings/test-connection/{service}")
@limiter.limit("20/minute")
async def test_service_connection(request: Request, service: str):
    """
    Test connection to a service.
    
    Args:
        service: Service name (gemini, vertex, ollama)
        
    Returns:
        Connection test result
    """
    try:
        result = settings_manager.test_connection(service)
        return result
    except Exception as e:
        logger.error(f"Error testing connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test connection: {str(e)}"
        )

# ═══════════════════════════════════════════════════════════════
# End Settings API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Conversation History API
# ═══════════════════════════════════════════════════════════════

class ConversationCreate(BaseModel):
    """Model for creating a new conversation."""
    title: str = Field(..., min_length=1, max_length=200)
    agent_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    """Model for adding a message to a conversation."""
    role: str = Field(..., pattern="^(user|agent)$")
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None

class ConversationUpdate(BaseModel):
    """Model for updating a conversation."""
    title: str = Field(..., min_length=1, max_length=200)

@app.get("/api/conversations")
@limiter.limit("60/minute")
async def list_conversations(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    agent_type: Optional[str] = None
):
    """
    List all conversations with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        agent_type: Filter by agent type
        
    Returns:
        List of conversations with pagination info
    """
    try:
        # Validate pagination parameters
        if limit > 100:
            limit = 100
        if skip < 0:
            skip = 0
        
        conversations, total = conversation_manager.list_conversations(
            skip=skip,
            limit=limit,
            agent_type=agent_type
        )
        
        return {
            "conversations": conversations,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + len(conversations) < total
        }
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversations"
        )

@app.post("/api/conversations", status_code=201)
@limiter.limit("30/minute")
async def create_conversation(request: Request, data: ConversationCreate):
    """
    Create a new conversation.
    
    Args:
        data: Conversation creation data
        
    Returns:
        Created conversation information
    """
    try:
        conversation = conversation_manager.create_conversation(
            title=data.title,
            agent_type=data.agent_type,
            metadata=data.metadata
        )
        return conversation
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create conversation"
        )

@app.get("/api/conversations/{conversation_id}")
@limiter.limit("60/minute")
async def get_conversation(request: Request, conversation_id: str, include_messages: bool = True):
    """
    Get a conversation by ID.
    
    Args:
        conversation_id: Conversation ID
        include_messages: Whether to include messages
        
    Returns:
        Conversation data with messages
    """
    try:
        conversation = conversation_manager.get_conversation(
            conversation_id=conversation_id,
            include_messages=include_messages
        )
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation"
        )

@app.patch("/api/conversations/{conversation_id}")
@limiter.limit("30/minute")
async def update_conversation(request: Request, conversation_id: str, data: ConversationUpdate):
    """
    Update a conversation.
    
    Args:
        conversation_id: Conversation ID
        data: Update data
        
    Returns:
        Success message
    """
    try:
        updated = conversation_manager.update_conversation_title(
            conversation_id=conversation_id,
            title=data.title
        )
        
        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update conversation"
        )

@app.delete("/api/conversations/{conversation_id}")
@limiter.limit("30/minute")
async def delete_conversation(request: Request, conversation_id: str):
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Success message
    """
    try:
        deleted = conversation_manager.delete_conversation(conversation_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete conversation"
        )

@app.post("/api/conversations/{conversation_id}/messages", status_code=201)
@limiter.limit("60/minute")
async def add_message(request: Request, conversation_id: str, data: MessageCreate):
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: Conversation ID
        data: Message data
        
    Returns:
        Created message information
    """
    try:
        message = conversation_manager.add_message(
            conversation_id=conversation_id,
            role=data.role,
            content=data.content,
            metadata=data.metadata
        )
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to add message"
        )

@app.get("/api/conversations/{conversation_id}/export")
@limiter.limit("20/minute")
async def export_conversation(request: Request, conversation_id: str):
    """
    Export a conversation as Markdown.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Markdown formatted conversation
    """
    from fastapi.responses import PlainTextResponse
    
    try:
        markdown = conversation_manager.export_conversation_markdown(conversation_id)
        return PlainTextResponse(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.md"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to export conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to export conversation"
        )

@app.get("/api/conversations/search")
@limiter.limit("30/minute")
async def search_conversations(request: Request, q: str, skip: int = 0, limit: int = 20):
    """
    Search conversations.
    
    Args:
        q: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Matching conversations
    """
    try:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search query must be at least 2 characters"
            )
        
        conversations, total = conversation_manager.search_conversations(
            query=q,
            skip=skip,
            limit=min(limit, 100)
        )
        
        return {
            "conversations": conversations,
            "total": total,
            "query": q
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search conversations"
        )

@app.get("/api/conversations/stats")
@limiter.limit("10/minute")
async def get_conversation_stats(request: Request):
    """
    Get conversation statistics.
    
    Returns:
        Statistics about conversations
    """
    try:
        stats = conversation_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get conversation stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )

# ═══════════════════════════════════════════════════════════════
# End Conversation History API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Artifacts API
# ═══════════════════════════════════════════════════════════════

class ArtifactCreate(BaseModel):
    """Model for creating an artifact."""
    content: str = Field(..., description="Base64 encoded content")
    filename: str = Field(..., min_length=1)
    artifact_type: Optional[str] = None
    agent: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.get("/api/artifacts")
@limiter.limit("60/minute")
async def list_artifacts(
    request: Request,
    artifact_type: Optional[str] = None,
    agent: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    List all artifacts with filtering and pagination.
    
    Args:
        artifact_type: Filter by artifact type
        agent: Filter by agent
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of artifacts
    """
    try:
        artifacts = artifact_manager.list_artifacts(
            artifact_type=artifact_type,
            agent=agent,
            skip=skip,
            limit=min(limit, 100)
        )
        return {"artifacts": artifacts}
    except Exception as e:
        logger.error(f"Failed to list artifacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve artifacts"
        )

@app.post("/api/artifacts", status_code=201)
@limiter.limit("30/minute")
async def create_artifact(request: Request, data: ArtifactCreate):
    """
    Store a new artifact.
    
    Args:
        data: Artifact data
        
    Returns:
        Created artifact information
    """
    try:
        # Decode base64 content
        import base64
        try:
            content = base64.b64decode(data.content)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid base64 content"
            )
        
        artifact = artifact_manager.store_artifact(
            content=content,
            filename=data.filename,
            artifact_type=data.artifact_type,
            agent=data.agent,
            description=data.description,
            metadata=data.metadata
        )
        return artifact
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create artifact: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to store artifact"
        )

@app.get("/api/artifacts/search")
@limiter.limit("30/minute")
async def search_artifacts(request: Request, q: str):
    """
    Search artifacts.
    
    Args:
        q: Search query
        
    Returns:
        Matching artifacts
    """
    try:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search query must be at least 2 characters"
            )
        
        artifacts = artifact_manager.search_artifacts(q)
        return {"artifacts": artifacts}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search artifacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search artifacts"
        )

@app.get("/api/artifacts/stats")
@limiter.limit("10/minute")
async def get_artifact_stats(request: Request):
    """
    Get artifact statistics.
    
    Returns:
        Statistics about artifacts
    """
    try:
        stats = artifact_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get artifact stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )

@app.get("/api/artifacts/{artifact_id}")
@limiter.limit("60/minute")
async def get_artifact(request: Request, artifact_id: str):
    """
    Get artifact metadata.
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        Artifact information
    """
    try:
        artifact = artifact_manager.get_artifact(artifact_id)
        
        if not artifact:
            raise HTTPException(
                status_code=404,
                detail="Artifact not found"
            )
        
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get artifact: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve artifact"
        )

@app.get("/api/artifacts/{artifact_id}/download")
@limiter.limit("30/minute")
async def download_artifact(request: Request, artifact_id: str):
    """
    Download artifact file.
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        Artifact file
    """
    from fastapi.responses import Response
    
    try:
        artifact = artifact_manager.get_artifact(artifact_id)
        
        if not artifact:
            raise HTTPException(
                status_code=404,
                detail="Artifact not found"
            )
        
        content = artifact_manager.read_artifact_content(artifact_id)
        
        if content is None:
            raise HTTPException(
                status_code=404,
                detail="Artifact content not found"
            )
        
        return Response(
            content=content,
            media_type=artifact["mime_type"],
            headers={
                "Content-Disposition": f"attachment; filename={artifact['filename']}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download artifact: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to download artifact"
        )

@app.get("/api/artifacts/{artifact_id}/preview")
@limiter.limit("60/minute")
async def preview_artifact(request: Request, artifact_id: str):
    """
    Get artifact preview.
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        Artifact preview
    """
    try:
        preview = artifact_manager.export_artifact_preview(artifact_id)
        
        if preview is None:
            raise HTTPException(
                status_code=404,
                detail="Artifact not found or preview not available"
            )
        
        return {"preview": preview}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get artifact preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate preview"
        )

@app.delete("/api/artifacts/{artifact_id}")
@limiter.limit("30/minute")
async def delete_artifact(request: Request, artifact_id: str):
    """
    Delete an artifact.
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        Success message
    """
    try:
        deleted = artifact_manager.delete_artifact(artifact_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Artifact not found"
            )
        
        return {"message": "Artifact deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete artifact: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete artifact"
        )

@app.post("/api/artifacts/cleanup")
@limiter.limit("5/minute")
async def cleanup_artifacts(request: Request, days: int = 30):
    """
    Cleanup old artifacts.
    
    Args:
        days: Delete artifacts older than this many days
        
    Returns:
        Number of artifacts deleted
    """
    try:
        if days < 1:
            raise HTTPException(
                status_code=400,
                detail="Days must be at least 1"
            )
        
        deleted_count = artifact_manager.cleanup_old_artifacts(days)
        return {
            "message": f"Cleaned up {deleted_count} artifacts",
            "deleted_count": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup artifacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to cleanup artifacts"
        )

# ═══════════════════════════════════════════════════════════════
# End Artifacts API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Agent Coordination API (Jules & Dual-Agent Mode)
# ═══════════════════════════════════════════════════════════════

class AgentSessionRequest(BaseModel):
    agent_name: str
    context: Optional[Dict[str, Any]] = None
    is_primary: bool = True

class AgentHandoffRequest(BaseModel):
    from_agent: str
    to_agent: str
    context: Dict[str, Any]
    reason: str

class CollaborativeRequest(BaseModel):
    request: str
    agents: List[str]
    mode: str = "sequential"  # or "parallel"

class AgentSuggestRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    limit: int = 3

@app.post("/api/agents/session", status_code=201)
@limiter.limit("30/minute")
async def create_agent_session(request: Request, session_request: AgentSessionRequest):
    """
    Create a new agent session for dual-agent mode.

    Args:
        session_request: Agent session details

    Returns:
        Created session information
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())

        session = orchestrator.create_agent_session(
            agent_name=session_request.agent_name,
            session_id=session_id,
            context=session_request.context,
            is_primary=session_request.is_primary
        )

        return {
            "session_id": session_id,
            "agent_name": session.agent_name,
            "created_at": session.created_at,
            "is_primary": session.is_primary,
            "message": f"Created agent session for {session.agent_name}"
        }
    except Exception as e:
        logger.error(f"Failed to create agent session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create agent session"
        )

@app.get("/api/agents/sessions")
@limiter.limit("30/minute")
async def list_agent_sessions(request: Request):
    """
    List all active agent sessions.

    Returns:
        List of active sessions
    """
    try:
        sessions = orchestrator.list_active_sessions()
        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "agent_name": s.agent_name,
                    "created_at": s.created_at,
                    "is_primary": s.is_primary
                }
                for s in sessions
            ],
            "total": len(sessions)
        }
    except Exception as e:
        logger.error(f"Failed to list agent sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to list agent sessions"
        )

@app.delete("/api/agents/session/{session_id}")
@limiter.limit("30/minute")
async def end_agent_session(request: Request, session_id: str):
    """
    End an active agent session.

    Args:
        session_id: Session ID to end

    Returns:
        Success message
    """
    try:
        success = orchestrator.end_agent_session(session_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return {
            "message": f"Session {session_id} ended successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end agent session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to end agent session"
        )

@app.post("/api/agents/handoff")
@limiter.limit("30/minute")
async def handoff_agent(request: Request, handoff_request: AgentHandoffRequest):
    """
    Execute a handoff from one agent to another.

    Args:
        handoff_request: Handoff details

    Returns:
        Handoff information
    """
    try:
        handoff = orchestrator.handoff_agent(
            from_agent=handoff_request.from_agent,
            to_agent=handoff_request.to_agent,
            context=handoff_request.context,
            reason=handoff_request.reason
        )

        return {
            "from_agent": handoff.from_agent,
            "to_agent": handoff.to_agent,
            "timestamp": handoff.timestamp,
            "reason": handoff.handoff_reason,
            "message": f"Handoff from {handoff.from_agent} to {handoff.to_agent} completed"
        }
    except Exception as e:
        logger.error(f"Failed to execute handoff: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to execute agent handoff"
        )

@app.get("/api/agents/handoffs")
@limiter.limit("30/minute")
async def get_handoff_history(request: Request, agent_name: Optional[str] = None, limit: int = 10):
    """
    Get agent handoff history.

    Args:
        agent_name: Optional agent name to filter by
        limit: Maximum number of results

    Returns:
        List of handoffs
    """
    try:
        handoffs = orchestrator.get_handoff_history(
            agent_name=agent_name,
            limit=min(limit, 100)
        )

        return {
            "handoffs": [
                {
                    "from_agent": h.from_agent,
                    "to_agent": h.to_agent,
                    "timestamp": h.timestamp,
                    "reason": h.handoff_reason
                }
                for h in handoffs
            ],
            "total": len(handoffs)
        }
    except Exception as e:
        logger.error(f"Failed to get handoff history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve handoff history"
        )

@app.post("/api/agents/collaborate")
@limiter.limit("10/minute")
async def collaborative_process(request: Request, collab_request: CollaborativeRequest):
    """
    Process a request collaboratively with multiple agents.

    Args:
        collab_request: Collaborative request details

    Returns:
        Combined results from all agents
    """
    try:
        if not collab_request.agents:
            raise HTTPException(
                status_code=400,
                detail="At least one agent must be specified"
            )

        if collab_request.mode not in ["sequential", "parallel"]:
            raise HTTPException(
                status_code=400,
                detail="Mode must be 'sequential' or 'parallel'"
            )

        result = await orchestrator.collaborative_process(
            request=collab_request.request,
            agents=collab_request.agents,
            mode=collab_request.mode
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process collaborative request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process collaborative request"
        )

@app.get("/api/agents/route")
@limiter.limit("30/minute")
async def route_request(request: Request, query: str = Query(..., alias="request"), exclude: Optional[str] = None):
    """
    Get the best agent to route a request to.

    Args:
        request: The request to route
        exclude: Comma-separated list of agents to exclude

    Returns:
        Recommended agent name
    """
    try:
        if not request or len(request) < 3:
            raise HTTPException(
                status_code=400,
                detail="Request must be at least 3 characters"
            )

        exclude_agents = exclude.split(",") if exclude else None

        best_agent = orchestrator.route_to_best_agent(
            request=request,
            exclude_agents=exclude_agents
        )

        return {
            "recommended_agent": best_agent,
            "request": request[:100]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to route request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to route request"
        )

@app.post("/api/agents/suggest")
@limiter.limit("60/minute")
async def suggest_agents(request: Request, suggest_request: AgentSuggestRequest):
    """
    Get AI-powered agent suggestions for a task with confidence scores.

    Args:
        suggest_request: Contains message, optional conversation_id, and limit

    Returns:
        Ranked list of suggested agents with confidence and auto_select flag
    """
    try:
        if not suggest_request.message or len(suggest_request.message.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Message must be at least 3 characters"
            )

        mgr = agent_manager_instance
        if mgr is None:
            # Fallback: create a temporary instance
            mgr = AgentManager(agents_dir=os.path.join(project_root, ".github", "agents"))

        suggestions = mgr.suggest_agents(
            task_description=suggest_request.message,
            limit=min(suggest_request.limit, 5)
        )

        # Determine if we should auto-select
        auto_select = (
            len(suggestions) > 0
            and suggestions[0].get('auto_select', False)
        )

        return {
            "suggestions": suggestions,
            "auto_select": auto_select,
            "query": suggest_request.message[:100]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to suggest agents: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to suggest agents"
        )

@app.get("/api/agents/stats")
@limiter.limit("30/minute")
async def get_agent_stats(request: Request):
    """
    Get agent coordination statistics.

    Returns:
        Agent usage and coordination stats
    """
    try:
        stats = orchestrator.get_agent_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get agent stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve agent statistics"
        )

@app.post("/api/agents/context")
@limiter.limit("30/minute")
async def update_shared_context(request: Request, key: str, value: Any):
    """
    Update shared context accessible by all agents.

    Args:
        key: Context key
        value: Context value

    Returns:
        Success message
    """
    try:
        orchestrator.update_shared_context(key, value)
        return {
            "message": f"Updated shared context: {key}",
            "key": key
        }
    except Exception as e:
        logger.error(f"Failed to update shared context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update shared context"
        )

@app.get("/api/agents/context")
@limiter.limit("30/minute")
async def get_shared_context(request: Request, key: Optional[str] = None):
    """
    Get shared context value(s).

    Args:
        key: Optional specific key to retrieve

    Returns:
        Context value or entire context
    """
    try:
        context = orchestrator.get_shared_context(key)

        if key and context is None:
            raise HTTPException(
                status_code=404,
                detail=f"Context key '{key}' not found"
            )

        return {
            "context": context,
            "key": key
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get shared context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve shared context"
        )

# ═══════════════════════════════════════════════════════════════
# End Agent Coordination API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Context Fusion API
# ═══════════════════════════════════════════════════════════════

_context_fusion_engine = None

def _get_context_fusion():
    """Lazy-initialize the Context Fusion Engine."""
    global _context_fusion_engine
    if _context_fusion_engine is None:
        from context_fusion import ContextFusionEngine
        _context_fusion_engine = ContextFusionEngine(
            conversation_manager=conversation_manager,
            vector_store=getattr(orchestrator, 'store', None) if orchestrator else None,
            embedding_fn=None,  # Will be set when async embeddings are needed
        )
    return _context_fusion_engine

@app.get("/api/context/relevant")
@limiter.limit("30/minute")
async def get_relevant_context(
    request: Request,
    query: str = Query(..., min_length=3),
    limit: int = 5,
    exclude_conversation: Optional[str] = None,
):
    """
    Retrieve relevant past context for a query using Context Fusion.

    Args:
        query: The search query
        limit: Max results (default 5)
        exclude_conversation: Optional conversation ID to exclude

    Returns:
        List of relevant context items with scores
    """
    try:
        engine = _get_context_fusion()
        results = engine.get_relevant_context(
            query=query,
            limit=min(limit, 20),
            exclude_conversation_id=exclude_conversation,
        )

        return {
            "results": results,
            "query": query[:100],
            "total": len(results),
        }
    except Exception as e:
        logger.error(f"Failed to get relevant context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve relevant context",
        )

@app.post("/api/context/index")
@limiter.limit("10/minute")
async def index_conversation_context(
    request: Request,
    conversation_id: str = Query(..., min_length=1),
):
    """
    Index a conversation into the knowledge base for future Context Fusion retrieval.

    Args:
        conversation_id: ID of the conversation to index

    Returns:
        Success status
    """
    try:
        engine = _get_context_fusion()
        success = engine.index_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or could not be indexed",
            )

        return {
            "message": f"Conversation {conversation_id} indexed successfully",
            "conversation_id": conversation_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to index conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to index conversation",
        )

# ═══════════════════════════════════════════════════════════════
# End Context Fusion API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Auto-Pilot API
# ═══════════════════════════════════════════════════════════════

_autopilot_pipeline = None

def _get_autopilot():
    """Lazy-initialize the Auto-Pilot Pipeline."""
    global _autopilot_pipeline
    if _autopilot_pipeline is None:
        from autopilot import AutoPilotPipeline
        _autopilot_pipeline = AutoPilotPipeline(
            orchestrator=orchestrator,
            agent_manager=agent_manager_instance,
        )
    return _autopilot_pipeline

class AutoPilotStartRequest(BaseModel):
    goal: str = Field(..., min_length=10, max_length=10000)

@app.post("/api/autopilot/start", status_code=201)
@limiter.limit("5/minute")
async def start_autopilot(request: Request, start_request: AutoPilotStartRequest):
    """
    Start an Auto-Pilot pipeline for a goal.

    Args:
        start_request: Contains the goal description

    Returns:
        Pipeline ID and initial status
    """
    try:
        ap = _get_autopilot()
        pipeline_id = ap.start(goal=start_request.goal)
        status = ap.get_status(pipeline_id)

        return {
            "pipeline_id": pipeline_id,
            "status": status,
            "message": f"Auto-Pilot pipeline started for: {start_request.goal[:100]}",
        }
    except Exception as e:
        logger.error(f"Failed to start autopilot: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start Auto-Pilot pipeline",
        )

@app.get("/api/autopilot/status/{pipeline_id}")
@limiter.limit("60/minute")
async def get_autopilot_status(request: Request, pipeline_id: str):
    """
    Get the status of an Auto-Pilot pipeline.

    Args:
        pipeline_id: Pipeline ID

    Returns:
        Pipeline status with stage details
    """
    try:
        ap = _get_autopilot()
        status = ap.get_status(pipeline_id)

        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline {pipeline_id} not found",
            )

        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get autopilot status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get pipeline status",
        )

@app.post("/api/autopilot/cancel/{pipeline_id}")
@limiter.limit("10/minute")
async def cancel_autopilot(request: Request, pipeline_id: str):
    """
    Cancel a running Auto-Pilot pipeline.

    Args:
        pipeline_id: Pipeline ID to cancel

    Returns:
        Success message
    """
    try:
        ap = _get_autopilot()
        success = ap.cancel(pipeline_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline {pipeline_id} not found or not running",
            )

        return {
            "message": f"Pipeline {pipeline_id} cancelled",
            "pipeline_id": pipeline_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel autopilot: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel pipeline",
        )

@app.get("/api/autopilot/history")
@limiter.limit("30/minute")
async def get_autopilot_history(request: Request, limit: int = 20):
    """
    List past Auto-Pilot pipelines.

    Returns:
        List of pipelines (most recent first)
    """
    try:
        ap = _get_autopilot()
        pipelines = ap.list_pipelines(limit=min(limit, 50))

        return {
            "pipelines": pipelines,
            "total": len(pipelines),
        }
    except Exception as e:
        logger.error(f"Failed to get autopilot history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pipeline history",
        )

# ═══════════════════════════════════════════════════════════════
# End Auto-Pilot API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Debug Logging API
# ═══════════════════════════════════════════════════════════════

@app.get("/debug/logs")
@limiter.limit("20/minute")
async def get_debug_logs(
    request: Request,
    page: int = 1,
    per_page: int = 50,
    severity: Optional[str] = None,
    model: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get paginated debug logs with optional filters."""
    from utils.debug_logger import get_debug_logger, LogLevel
    
    debug_logger = get_debug_logger()
    
    # Convert severity string to LogLevel enum
    severity_filter = None
    if severity:
        try:
            severity_filter = LogLevel(severity.upper())
        except ValueError:
            pass
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    logs = debug_logger.get_logs(
        severity=severity_filter,
        model=model,
        start_date=start_date,
        end_date=end_date,
        limit=per_page,
        offset=offset
    )
    
    return {
        "logs": logs,
        "page": page,
        "per_page": per_page,
        "total": len(logs)
    }

@app.get("/debug/export")
@limiter.limit("5/minute")
async def export_debug_logs(
    request: Request,
    format: str = "json",
    severity: Optional[str] = None,
    model: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export debug logs in JSON or CSV format."""
    from fastapi.responses import PlainTextResponse
    from utils.debug_logger import get_debug_logger, LogLevel
    
    debug_logger = get_debug_logger()
    
    # Convert severity string to LogLevel enum
    severity_filter = None
    if severity:
        try:
            severity_filter = LogLevel(severity.upper())
        except ValueError:
            pass
    
    # Export logs
    exported_data = debug_logger.export_logs(
        format=format,
        severity=severity_filter,
        model=model,
        start_date=start_date,
        end_date=end_date
    )
    
    # Return appropriate content type
    if format == "csv":
        return PlainTextResponse(
            content=exported_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=debug_logs.csv"}
        )
    else:
        return PlainTextResponse(
            content=exported_data,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=debug_logs.json"}
        )

@app.get("/debug/failed")
@limiter.limit("20/minute")
async def get_failed_requests(request: Request):
    """Get all failed requests from debug logs."""
    from utils.debug_logger import get_debug_logger
    
    debug_logger = get_debug_logger()
    failed = debug_logger.get_failed_requests()
    
    return {
        "failed_requests": failed,
        "count": len(failed)
    }

@app.get("/debug/missing-data")
@limiter.limit("20/minute")
async def get_missing_data_requests(request: Request):
    """Get requests where RAG context was missing or embeddings failed."""
    from utils.debug_logger import get_debug_logger
    
    debug_logger = get_debug_logger()
    missing = debug_logger.get_missing_data_requests()
    
    return {
        "missing_data_requests": missing,
        "count": len(missing)
    }

@app.post("/debug/clear")
@limiter.limit("2/minute")
async def clear_debug_logs(request: Request):
    """Clear all debug logs (with backup)."""
    from utils.debug_logger import get_debug_logger
    
    debug_logger = get_debug_logger()
    
    try:
        debug_logger.clear_logs()
        return {"success": True, "message": "Debug logs cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# End Debug Logging API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Swarm System API
# ═══════════════════════════════════════════════════════════════

class SwarmExecutionRequest(BaseModel):
    """Model for swarm execution request."""
    task: str = Field(..., min_length=3, max_length=10000)
    verbose: bool = True
    priority: str = Field(default="NORMAL", pattern="^(LOW|NORMAL|HIGH|CRITICAL)$")

@app.post("/api/swarm/execute")
@limiter.limit("10/minute")
async def execute_swarm_task(request: Request, swarm_request: SwarmExecutionRequest):
    """
    Execute a task using the multi-agent swarm system.
    
    Args:
        swarm_request: Task, execution options, and priority level
        
    Returns:
        Swarm execution results including delegation plan, worker results,
        confidence scores, wall time, and cache status
    """
    try:
        # Import swarm system
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from swarm import SwarmOrchestrator, TaskPriority
        
        # Map string priority to enum
        priority_map = {
            "LOW": TaskPriority.LOW,
            "NORMAL": TaskPriority.NORMAL,
            "HIGH": TaskPriority.HIGH,
            "CRITICAL": TaskPriority.CRITICAL,
        }
        priority = priority_map.get(swarm_request.priority.upper(), TaskPriority.NORMAL)
        
        # Create orchestrator
        swarm = SwarmOrchestrator()
        
        # Execute task
        result = await swarm.execute(
            swarm_request.task,
            verbose=swarm_request.verbose,
            priority=priority,
        )

        # Extract per-agent result summaries (output text + timing)
        agent_results = {}
        for agent_name, agent_result in result.get("worker_results", {}).items():
            agent_results[agent_name] = {
                "success": agent_result.get("success", True),
                "output": agent_result.get("output", ""),
                "execution_time_ms": agent_result.get("execution_time_ms", 0),
            }

        return {
            "success": result["success"],
            "task": result["task"],
            "delegation_plan": result["delegation_plan"],
            "workers_used": result["workers_used"],
            "synthesis": result["synthesis"],
            "message_count": result["message_count"],
            # New enriched fields
            "agent_results": agent_results,
            "confidence_scores": result.get("confidence_scores", {}),
            "wall_time_ms": result.get("wall_time_ms", 0),
            "from_cache": result.get("from_cache", False),
            "priority": result.get("priority", swarm_request.priority),
        }
    except ImportError as e:
        logger.error(f"Failed to import swarm system: {e}")
        raise HTTPException(
            status_code=500,
            detail="Swarm system not available"
        )
    except Exception as e:
        logger.error(f"Failed to execute swarm task: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute swarm task: {str(e)}"
        )

@app.get("/api/swarm/capabilities")
@limiter.limit("30/minute")
async def get_swarm_capabilities(request: Request):
    """
    Get capabilities of all agents in the swarm.
    
    Returns:
        Dictionary of agent capabilities
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from swarm import SwarmOrchestrator
        
        swarm = SwarmOrchestrator()
        capabilities = swarm.get_agent_capabilities()
        
        return {
            "capabilities": capabilities,
            "agent_count": len(capabilities)
        }
    except ImportError as e:
        logger.error(f"Failed to import swarm system: {e}")
        raise HTTPException(
            status_code=500,
            detail="Swarm system not available"
        )
    except Exception as e:
        logger.error(f"Failed to get swarm capabilities: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve capabilities: {str(e)}"
        )

@app.get("/api/swarm/metrics")
@limiter.limit("30/minute")
async def get_swarm_metrics(request: Request):
    """
    Get swarm performance metrics.

    Returns:
        Swarm-level counters, cache statistics, and per-agent metrics.
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from swarm import SwarmOrchestrator

        swarm = SwarmOrchestrator()
        return swarm.get_swarm_metrics()
    except ImportError as e:
        logger.error(f"Failed to import swarm system: {e}")
        raise HTTPException(status_code=500, detail="Swarm system not available")
    except Exception as e:
        logger.error(f"Failed to get swarm metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")

class SwarmReportRequest(BaseModel):
    """Request body for generating a formatted swarm execution report."""
    task: str = Field(default="", description="The original task prompt")
    priority: str = Field(default="NORMAL", description="Execution priority")
    wall_time_ms: Optional[float] = Field(default=None, description="Wall-clock execution time in ms")
    from_cache: bool = Field(default=False, description="Whether result was served from cache")
    message_count: int = Field(default=0, description="Number of messages exchanged")
    delegation_plan: Optional[dict] = Field(default=None, description="Agent delegation plan")
    confidence_scores: Optional[dict] = Field(default=None, description="Routing confidence scores per agent")
    agent_results: Optional[dict] = Field(default=None, description="Per-agent execution results")
    synthesis: Optional[str] = Field(default=None, description="Synthesised final output")
    format: str = Field(default="html", description="Output format: 'html' or 'pdf'")


@app.post("/api/swarm/report")
@limiter.limit("20/minute")
async def generate_swarm_report(request: Request, body: SwarmReportRequest):
    """
    Generate a formatted HTML or print-ready PDF report from swarm execution results.

    Accepts the full swarm result payload and returns a self-contained HTML document
    with professional styling. When format='pdf', the HTML includes a print trigger
    so the browser renders it as a PDF via the system print dialog.

    Returns:
        HTML document (text/html) suitable for download or printing.
    """
    try:
        from fastapi.responses import HTMLResponse
        import html as html_lib
        from datetime import datetime as _dt

        now = _dt.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        task_escaped = html_lib.escape(body.task or "")
        priority = html_lib.escape(body.priority or "NORMAL")
        wall_time = f"{body.wall_time_ms:.0f} ms" if body.wall_time_ms is not None else "—"
        cache_badge = (
            '<span style="background:#f59e0b;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.75rem;">⚡ Cache Hit</span>'
            if body.from_cache else
            '<span style="background:#6b7280;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.75rem;">Fresh</span>'
        )
        priority_colors = {"LOW": "#6b7280", "NORMAL": "#3b82f6", "HIGH": "#f59e0b", "CRITICAL": "#ef4444"}
        priority_color = priority_colors.get(priority.upper(), "#3b82f6")

        # --- Build delegation plan section ---
        delegation_html = ""
        if body.delegation_plan:
            rows = ""
            for agent_name, sub_task in body.delegation_plan.items():
                conf = (body.confidence_scores or {}).get(agent_name)
                conf_html = (
                    f'<span style="background:{priority_color}22;color:{priority_color};padding:1px 6px;border-radius:10px;font-size:0.75rem;margin-left:6px;">'
                    f'{round(conf * 100)}%</span>'
                ) if conf is not None else ""
                rows += (
                    f'<tr><td style="padding:8px 12px;font-weight:600;white-space:nowrap;width:140px;">'
                    f'{html_lib.escape(str(agent_name))}{conf_html}</td>'
                    f'<td style="padding:8px 12px;color:#374151;">{html_lib.escape(str(sub_task))}</td></tr>'
                )
            delegation_html = f"""
            <section class="section">
                <h2>Delegation Plan</h2>
                <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                    <thead><tr style="background:#f3f4f6;">
                        <th style="padding:8px 12px;text-align:left;font-size:0.8rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Agent</th>
                        <th style="padding:8px 12px;text-align:left;font-size:0.8rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Assigned Task</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </section>"""

        # --- Build agent results section ---
        results_html = ""
        if body.agent_results:
            cards = ""
            for agent_name, result in body.agent_results.items():
                success = result.get("success", True) is not False
                status_color = "#10b981" if success else "#ef4444"
                status_label = "✓ Success" if success else "✗ Error"
                timing = f' — {result["execution_time_ms"]:.0f} ms' if result.get("execution_time_ms") is not None else ""
                output = html_lib.escape(str(result.get("output", "")))
                cards += f"""
                <div style="border:1px solid #e5e7eb;border-radius:8px;margin-bottom:16px;overflow:hidden;">
                    <div style="background:#f9fafb;padding:10px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #e5e7eb;">
                        <span style="font-weight:700;">{html_lib.escape(str(agent_name))}</span>
                        <span style="color:{status_color};font-size:0.85rem;">{status_label}{html_lib.escape(timing)}</span>
                    </div>
                    <pre style="margin:0;padding:16px;background:#1e1e2e;color:#cdd6f4;font-size:0.8rem;overflow-x:auto;white-space:pre-wrap;word-break:break-word;">{output}</pre>
                </div>"""
            results_html = f"""
            <section class="section">
                <h2>Agent Results</h2>
                {cards}
            </section>"""

        # --- Synthesis section ---
        synthesis_html = ""
        if body.synthesis:
            synthesis_html = f"""
            <section class="section" style="border-left:4px solid {priority_color};padding-left:20px;">
                <h2>Final Synthesis</h2>
                <div style="color:#374151;line-height:1.7;white-space:pre-wrap;">{html_lib.escape(body.synthesis)}</div>
            </section>"""

        print_script = '<script>window.onload=function(){{window.print();}}</script>' if body.format == "pdf" else ""

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Antigravity Swarm Report — {now}</title>
{print_script}
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8fafc;color:#111827;padding:32px}}
  .page{{max-width:900px;margin:0 auto;background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.08);overflow:hidden}}
  .header{{background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);color:#fff;padding:32px 40px}}
  .header h1{{font-size:1.6rem;font-weight:700;margin-bottom:4px}}
  .header .meta{{font-size:0.85rem;opacity:.75;margin-top:8px;display:flex;flex-wrap:wrap;gap:16px}}
  .body{{padding:32px 40px}}
  .section{{margin-bottom:32px}}
  .section h2{{font-size:1.1rem;font-weight:700;margin-bottom:16px;color:#1e1b4b;border-bottom:2px solid #e5e7eb;padding-bottom:8px}}
  .task-box{{background:#f3f4f6;border-radius:8px;padding:16px 20px;font-size:0.95rem;line-height:1.6;color:#374151;white-space:pre-wrap;word-break:break-word}}
  .stats{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:0}}
  .stat-chip{{background:#f3f4f6;border-radius:8px;padding:8px 16px;font-size:0.85rem}}
  .stat-chip b{{color:#111827}}
  footer{{text-align:center;font-size:0.75rem;color:#9ca3af;padding:16px 40px;border-top:1px solid #f3f4f6}}
  @media print{{body{{background:#fff;padding:0}}  .page{{box-shadow:none;border-radius:0}}}}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>🐝 Antigravity Multi-Agent Swarm Report</h1>
    <div class="meta">
      <span>Generated: {now}</span>
      <span>Priority: <b style="color:#fbbf24;">{priority}</b></span>
      <span>Wall Time: <b>{wall_time}</b></span>
      <span>Messages: <b>{body.message_count}</b></span>
      <span>{cache_badge}</span>
    </div>
  </div>
  <div class="body">
    <section class="section">
      <h2>Task</h2>
      <div class="task-box">{task_escaped}</div>
    </section>
    {delegation_html}
    {results_html}
    {synthesis_html}
  </div>
  <footer>Antigravity Multi-Agent Swarm &bull; {now}</footer>
</div>
</body>
</html>"""

        media_type = "text/html"
        filename = f"swarm-report-{_dt.now().strftime('%Y%m%d-%H%M%S')}.{'pdf' if body.format == 'pdf' else 'html'}"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return HTMLResponse(content=html_doc, headers=headers, media_type=media_type)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate swarm report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# End Swarm System API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Sandbox Execution API
# ═══════════════════════════════════════════════════════════════

class SandboxExecutionRequest(BaseModel):
    """Model for sandbox execution request."""
    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="python", pattern="^(python|javascript|bash)$")
    timeout: Optional[int] = Field(default=None, ge=1, le=300)

@app.post("/api/sandbox/run")
@limiter.limit("10/minute")
async def run_sandbox_code(request: Request, exec_request: SandboxExecutionRequest):
    """
    Execute code in a sandbox environment.
    
    Args:
        exec_request: Code execution request
        
    Returns:
        Execution results
    """
    try:
        # Import sandbox system
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from sandbox import get_sandbox
        
        # Get sandbox
        sandbox = get_sandbox()
        
        # Execute code
        result = await sandbox.execute(
            code=exec_request.code,
            language=exec_request.language,
            timeout=exec_request.timeout
        )
        
        return result.to_dict()
    except ImportError as e:
        logger.error(f"Failed to import sandbox system: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sandbox system not available"
        )
    except Exception as e:
        logger.error(f"Failed to execute code in sandbox: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute code: {str(e)}"
        )

@app.get("/api/sandbox/status")
@limiter.limit("30/minute")
async def get_sandbox_status(request: Request):
    """
    Get sandbox system status.
    
    Returns:
        Sandbox availability and configuration
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from sandbox import get_available_sandboxes
        from config import settings as src_settings
        
        available_sandboxes = get_available_sandboxes()
        
        return {
            "available_sandboxes": available_sandboxes,
            "active_sandbox": src_settings.SANDBOX_TYPE,
            "timeout_sec": src_settings.SANDBOX_TIMEOUT_SEC,
            "max_output_kb": src_settings.SANDBOX_MAX_OUTPUT_KB
        }
    except ImportError as e:
        logger.error(f"Failed to import sandbox system: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sandbox system not available"
        )
    except Exception as e:
        logger.error(f"Failed to get sandbox status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sandbox status: {str(e)}"
        )

# ═══════════════════════════════════════════════════════════════
# End Sandbox Execution API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Model Rotator API
# ═══════════════════════════════════════════════════════════════

class ModelRotatorKeyAdd(BaseModel):
    """Model for adding a new API key to the rotator."""
    service: str = Field(..., pattern="^(gemini|openai|vertex)$")
    key: str = Field(..., min_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    tags: Optional[List[str]] = None

class ModelRotatorKeyAction(BaseModel):
    """Model for key actions (enable/disable/remove)."""
    service: str = Field(..., pattern="^(gemini|openai|vertex)$")
    name: str = Field(..., min_length=1)

@app.post("/api/rotator/keys")
@limiter.limit("10/minute")
async def add_rotator_key(request: Request, key_data: ModelRotatorKeyAdd):
    """
    Add a new API key to the rotator.
    
    Args:
        key_data: Key configuration
        
    Returns:
        Success status
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        success = rotator.add_key(
            service=key_data.service,
            key=key_data.key,
            name=key_data.name,
            tags=key_data.tags
        )
        
        if success:
            return {
                "success": True,
                "message": f"Key {key_data.name} added to {key_data.service}"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Key already exists or could not be added"
            )
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add key: {str(e)}"
        )

@app.delete("/api/rotator/keys")
@limiter.limit("10/minute")
async def remove_rotator_key(request: Request, key_action: ModelRotatorKeyAction):
    """
    Remove an API key from the rotator.
    
    Args:
        key_action: Key identification
        
    Returns:
        Success status
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        success = rotator.remove_key(key_action.service, key_action.name)
        
        if success:
            return {
                "success": True,
                "message": f"Key {key_action.name} removed from {key_action.service}"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Key not found"
            )
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove key: {str(e)}"
        )

@app.post("/api/rotator/keys/disable")
@limiter.limit("20/minute")
async def disable_rotator_key(request: Request, key_action: ModelRotatorKeyAction):
    """
    Disable an API key temporarily.
    
    Args:
        key_action: Key identification
        
    Returns:
        Success status
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        success = rotator.disable_key(key_action.service, key_action.name)
        
        if success:
            return {
                "success": True,
                "message": f"Key {key_action.name} disabled"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Key not found"
            )
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disable key: {str(e)}"
        )

@app.post("/api/rotator/keys/enable")
@limiter.limit("20/minute")
async def enable_rotator_key(request: Request, key_action: ModelRotatorKeyAction):
    """
    Enable a previously disabled API key.
    
    Args:
        key_action: Key identification
        
    Returns:
        Success status
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        success = rotator.enable_key(key_action.service, key_action.name)
        
        if success:
            return {
                "success": True,
                "message": f"Key {key_action.name} enabled"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Key not found or already enabled"
            )
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable key: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable key: {str(e)}"
        )

@app.get("/api/rotator/stats")
@limiter.limit("30/minute")
async def get_rotator_stats(request: Request, service: Optional[str] = None):
    """
    Get usage statistics for the model rotator.
    
    Args:
        service: Optional service filter (gemini, openai, vertex)
        
    Returns:
        Usage statistics
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        
        if service:
            stats = rotator.get_service_stats(service)
            return {
                "service": service,
                "stats": stats
            }
        else:
            stats = rotator.get_all_stats()
            return {
                "all_services": stats
            }
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@app.post("/api/rotator/stats/reset")
@limiter.limit("5/minute")
async def reset_rotator_stats(request: Request, service: Optional[str] = None):
    """
    Reset usage statistics.
    
    Args:
        service: Optional service to reset (resets all if not specified)
        
    Returns:
        Success status
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(project_root, "src"))
        from model_rotator import get_rotator
        
        rotator = get_rotator()
        rotator.reset_stats(service)
        
        return {
            "success": True,
            "message": f"Stats reset for {service if service else 'all services'}"
        }
    except ImportError as e:
        logger.error(f"Failed to import model rotator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Model rotator not available"
        )
    except Exception as e:
        logger.error(f"Failed to reset stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset statistics: {str(e)}"
        )

# ═══════════════════════════════════════════════════════════════
# End Model Rotator API
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# User Management API
# ═══════════════════════════════════════════════════════════════

_role_pattern = "^(" + "|".join(sorted(_USER_VALID_ROLES)) + ")$"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=128)
    role: str = Field("user", pattern=_role_pattern)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, min_length=5, max_length=254)
    full_name: Optional[str] = Field(None, max_length=128)
    role: Optional[str] = Field(None, pattern=_role_pattern)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)


@app.post("/api/users", status_code=201)
async def create_user(user: UserCreate):
    """Create a new user account."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        created = user_manager.create_user(
            username=user.username,
            email=user.email,
            password=user.password,
            full_name=user.full_name,
            role=user.role,
            metadata=user.metadata,
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username or email already exists")
    except Exception as e:
        logger.error(f"Failed to create user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/api/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List users with optional filtering and pagination."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        users, total = user_manager.list_users(
            skip=skip, limit=limit, role=role, is_active=is_active
        )
        return {"users": users, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        logger.error(f"Failed to list users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list users")


@app.get("/api/users/search")
async def search_users(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Search users by username, email, or full name."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        users, total = user_manager.search_users(query=q, skip=skip, limit=limit)
        return {"users": users, "total": total, "query": q}
    except Exception as e:
        logger.error(f"Failed to search users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search users")


@app.get("/api/users/stats")
async def get_user_stats():
    """Return aggregate user statistics."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        return user_manager.get_statistics()
    except Exception as e:
        logger.error(f"Failed to get user statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user statistics")


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Retrieve a user by ID."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@app.patch("/api/users/{user_id}")
async def update_user(user_id: str, updates: UserUpdate):
    """Update an existing user's fields."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        updated = user_manager.update_user(
            user_id=user_id,
            email=updates.email,
            full_name=updates.full_name,
            role=updates.role,
            is_active=updates.is_active,
            metadata=updates.metadata,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user")


@app.post("/api/users/{user_id}/password")
async def update_user_password(user_id: str, body: PasswordUpdate):
    """Update a user's password."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        updated = user_manager.update_password(user_id=user_id, new_password=body.new_password)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update password for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update password")


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user account."""
    if user_manager is None:
        raise HTTPException(status_code=503, detail="User manager not available")
    try:
        deleted = user_manager.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": f"User {user_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete user")

# ═══════════════════════════════════════════════════════════════
# End User Management API
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication.
    Includes input validation and proper error handling.
    """
    # Generate unique connection ID
    import uuid
    connection_id = str(uuid.uuid4())
    
    # Track connection
    from utils.performance import get_stats_tracker
    stats_tracker = get_stats_tracker()
    stats_tracker.track_websocket_connect(connection_id)
    
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            
            # Track received message
            stats_tracker.track_websocket_message(connection_id, 'received')
            
            # Validate message length
            try:
                validate_message_length(data)
            except HTTPException as e:
                await websocket.send_json({"error": e.detail})
                stats_tracker.track_websocket_message(connection_id, 'sent')
                continue
            
            # Process request
            try:
                response = await orchestrator.process_request(data)
                await websocket.send_json(response)
                stats_tracker.track_websocket_message(connection_id, 'sent')
            except Exception as e:
                logger.error(f"Error processing WebSocket request: {e}")
                await websocket.send_json({
                    "error": "Failed to process request",
                    "details": str(e)
                })
                stats_tracker.track_websocket_message(connection_id, 'sent')
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {connection_id} disconnected")
        stats_tracker.track_websocket_disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"error": "Internal server error"})
            stats_tracker.track_websocket_message(connection_id, 'sent')
        except (RuntimeError, ConnectionError) as e:
            # WebSocket already closed, cannot send error message
            logger.debug(f"Could not send error message, connection already closed: {e}")
        finally:
            stats_tracker.track_websocket_disconnect(connection_id)

# Add performance monitoring endpoints
add_performance_endpoints(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", "8000")), 
        reload=True
    )
