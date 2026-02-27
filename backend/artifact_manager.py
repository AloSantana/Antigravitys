"""
Artifact Manager

Manages storage and retrieval of generated artifacts (code, diffs, tests, screenshots, reports).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
import mimetypes
import base64

logger = logging.getLogger(__name__)


class ArtifactManager:
    """Manages artifact storage and metadata."""

    # Artifact type configuration
    ARTIFACT_TYPES = {
        "code": {"extensions": [".py", ".js", ".ts", ".go", ".java", ".cpp", ".c", ".rs"], "subdir": "code"},
        "diff": {"extensions": [".diff", ".patch"], "subdir": "diffs"},
        "test": {"extensions": [".py", ".js", ".ts", ".test.js", ".spec.ts"], "subdir": "tests"},
        "screenshot": {"extensions": [".png", ".jpg", ".jpeg", ".gif", ".svg"], "subdir": "screenshots"},
        "report": {"extensions": [".md", ".txt", ".html", ".pdf"], "subdir": "reports"},
        "other": {"extensions": [], "subdir": "other"}
    }

    # Size limits (in bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB

    def __init__(self, artifacts_dir: str = "artifacts"):
        """
        Initialize artifact manager.
        
        Args:
            artifacts_dir: Path to artifacts directory
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.metadata_file = self.artifacts_dir / "metadata.json"
        self._init_storage()
        logger.info(f"ArtifactManager initialized with directory: {artifacts_dir}")

    def _init_storage(self) -> None:
        """Initialize artifact storage structure."""
        try:
            # Create main artifacts directory
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for each artifact type
            for artifact_type, config in self.ARTIFACT_TYPES.items():
                subdir = self.artifacts_dir / config["subdir"]
                subdir.mkdir(exist_ok=True)
            
            # Initialize metadata file if it doesn't exist
            if not self.metadata_file.exists():
                self._save_metadata({})
                logger.info("Created new metadata file")
            
            logger.info("Artifact storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize artifact storage: {e}", exc_info=True)
            raise

    def _load_metadata(self) -> Dict[str, Any]:
        """Load artifact metadata."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}", exc_info=True)
            return {}

    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save artifact metadata."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}", exc_info=True)
            raise

    def _detect_artifact_type(self, filename: str) -> str:
        """
        Detect artifact type from filename.
        
        Args:
            filename: File name
            
        Returns:
            Artifact type
        """
        # Check for test files with special naming first (higher priority)
        filename_lower = filename.lower()
        if "test" in filename_lower or "spec" in filename_lower:
            return "test"
        
        extension = Path(filename).suffix.lower()
        
        for artifact_type, config in self.ARTIFACT_TYPES.items():
            if extension in config["extensions"]:
                return artifact_type
        
        return "other"

    def _get_artifact_path(self, artifact_id: str, artifact_type: str, filename: str) -> Path:
        """
        Get full path for an artifact.
        
        Args:
            artifact_id: Artifact ID
            artifact_type: Artifact type
            filename: Original filename
            
        Returns:
            Full path to artifact
        """
        subdir = self.ARTIFACT_TYPES[artifact_type]["subdir"]
        extension = Path(filename).suffix
        return self.artifacts_dir / subdir / f"{artifact_id}{extension}"

    def store_artifact(
        self,
        content: bytes,
        filename: str,
        artifact_type: Optional[str] = None,
        agent: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a new artifact.
        
        Args:
            content: Artifact content (bytes)
            filename: Original filename
            artifact_type: Type of artifact (auto-detected if None)
            agent: Agent that created the artifact
            description: Human-readable description
            metadata: Additional metadata
            
        Returns:
            Artifact information
            
        Raises:
            ValueError: If file is too large
            OSError: If storage operation fails
        """
        # Validate size
        content_size = len(content)
        if content_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {content_size} bytes "
                f"(max: {self.MAX_FILE_SIZE} bytes)"
            )
        
        # Check total storage size
        total_size = self._get_total_size()
        if total_size + content_size > self.MAX_TOTAL_SIZE:
            raise ValueError(
                f"Storage limit exceeded. Total: {total_size + content_size} bytes "
                f"(max: {self.MAX_TOTAL_SIZE} bytes)"
            )
        
        # Detect artifact type if not provided
        if not artifact_type:
            artifact_type = self._detect_artifact_type(filename)
        
        # Generate artifact ID
        artifact_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Get storage path
            artifact_path = self._get_artifact_path(artifact_id, artifact_type, filename)
            
            # Write artifact to disk
            with open(artifact_path, "wb") as f:
                f.write(content)
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            
            # Create artifact metadata
            artifact_info = {
                "id": artifact_id,
                "filename": filename,
                "artifact_type": artifact_type,
                "size": content_size,
                "mime_type": mime_type or "application/octet-stream",
                "created_at": timestamp,
                "agent": agent,
                "description": description,
                "metadata": metadata or {},
                "path": str(artifact_path.relative_to(self.artifacts_dir))
            }
            
            # Update metadata registry
            all_metadata = self._load_metadata()
            all_metadata[artifact_id] = artifact_info
            self._save_metadata(all_metadata)
            
            logger.info(
                f"Stored artifact: {artifact_id} "
                f"(type: {artifact_type}, size: {content_size} bytes)"
            )
            
            return artifact_info
            
        except Exception as e:
            logger.error(f"Failed to store artifact: {e}", exc_info=True)
            # Cleanup on failure
            if artifact_path.exists():
                artifact_path.unlink()
            raise

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get artifact metadata.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            Artifact information or None if not found
        """
        metadata = self._load_metadata()
        artifact = metadata.get(artifact_id)
        
        if not artifact:
            logger.warning(f"Artifact not found: {artifact_id}")
            return None
        
        # Verify file still exists
        artifact_path = self.artifacts_dir / artifact["path"]
        if not artifact_path.exists():
            logger.error(f"Artifact file missing: {artifact_path}")
            return None
        
        return artifact

    def read_artifact_content(self, artifact_id: str) -> Optional[bytes]:
        """
        Read artifact file content.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            Artifact content or None if not found
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return None
        
        try:
            artifact_path = self.artifacts_dir / artifact["path"]
            with open(artifact_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read artifact {artifact_id}: {e}", exc_info=True)
            return None

    def list_artifacts(
        self,
        artifact_type: Optional[str] = None,
        agent: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List artifacts with filtering and pagination.
        
        Args:
            artifact_type: Filter by artifact type
            agent: Filter by agent
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of artifact information
        """
        metadata = self._load_metadata()
        artifacts = list(metadata.values())
        
        # Apply filters
        if artifact_type:
            artifacts = [a for a in artifacts if a["artifact_type"] == artifact_type]
        
        if agent:
            artifacts = [a for a in artifacts if a.get("agent") == agent]
        
        # Sort by creation time (newest first)
        artifacts.sort(key=lambda a: a["created_at"], reverse=True)
        
        # Apply pagination
        total = len(artifacts)
        artifacts = artifacts[skip:skip + limit]
        
        logger.info(f"Listed {len(artifacts)} artifacts (total: {total})")
        return artifacts

    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            True if deleted, False if not found
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False
        
        try:
            # Delete file
            artifact_path = self.artifacts_dir / artifact["path"]
            if artifact_path.exists():
                artifact_path.unlink()
            
            # Update metadata
            metadata = self._load_metadata()
            del metadata[artifact_id]
            self._save_metadata(metadata)
            
            logger.info(f"Deleted artifact: {artifact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete artifact {artifact_id}: {e}", exc_info=True)
            raise

    def search_artifacts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search artifacts by filename or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching artifacts
        """
        metadata = self._load_metadata()
        artifacts = list(metadata.values())
        
        query_lower = query.lower()
        
        # Search in filename and description
        matches = [
            a for a in artifacts
            if query_lower in a["filename"].lower()
            or (a.get("description") and query_lower in a["description"].lower())
        ]
        
        # Sort by creation time
        matches.sort(key=lambda a: a["created_at"], reverse=True)
        
        logger.info(f"Found {len(matches)} artifacts matching '{query}'")
        return matches

    def _get_total_size(self) -> int:
        """
        Calculate total size of all artifacts.
        
        Returns:
            Total size in bytes
        """
        metadata = self._load_metadata()
        return sum(a["size"] for a in metadata.values())

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get artifact statistics.
        
        Returns:
            Dictionary with statistics
        """
        metadata = self._load_metadata()
        artifacts = list(metadata.values())
        
        # Total count and size
        total_count = len(artifacts)
        total_size = sum(a["size"] for a in artifacts)
        
        # By type
        by_type = {}
        for artifact in artifacts:
            artifact_type = artifact["artifact_type"]
            if artifact_type not in by_type:
                by_type[artifact_type] = {"count": 0, "size": 0}
            by_type[artifact_type]["count"] += 1
            by_type[artifact_type]["size"] += artifact["size"]
        
        # By agent
        by_agent = {}
        for artifact in artifacts:
            agent = artifact.get("agent", "unknown")
            if agent not in by_agent:
                by_agent[agent] = 0
            by_agent[agent] += 1
        
        return {
            "total_count": total_count,
            "total_size": total_size,
            "max_size": self.MAX_TOTAL_SIZE,
            "available_size": self.MAX_TOTAL_SIZE - total_size,
            "by_type": by_type,
            "by_agent": by_agent
        }

    def cleanup_old_artifacts(self, days: int = 30) -> int:
        """
        Delete artifacts older than specified days.
        
        Args:
            days: Number of days
            
        Returns:
            Number of artifacts deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            metadata = self._load_metadata()
            to_delete = [
                artifact_id
                for artifact_id, artifact in metadata.items()
                if artifact["created_at"] < cutoff_str
            ]
            
            deleted_count = 0
            for artifact_id in to_delete:
                if self.delete_artifact(artifact_id):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old artifacts (>{days} days)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old artifacts: {e}", exc_info=True)
            raise

    def export_artifact_preview(self, artifact_id: str, max_size: int = 1024) -> Optional[str]:
        """
        Generate a preview of the artifact content.
        
        Args:
            artifact_id: Artifact ID
            max_size: Maximum preview size in bytes
            
        Returns:
            Preview string or None if not available
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return None
        
        mime_type = artifact["mime_type"]
        
        try:
            content = self.read_artifact_content(artifact_id)
            if not content:
                return None
            
            # Text files - return first N bytes as text
            if mime_type.startswith("text/") or artifact["artifact_type"] in ("code", "diff", "test"):
                preview = content[:max_size].decode("utf-8", errors="ignore")
                if len(content) > max_size:
                    preview += "\n... (truncated)"
                return preview
            
            # Images - return base64 data URL
            elif mime_type.startswith("image/"):
                b64_content = base64.b64encode(content).decode("ascii")
                return f"data:{mime_type};base64,{b64_content}"
            
            # Binary files - just show info
            else:
                return f"[Binary file: {artifact['filename']}, {artifact['size']} bytes]"
                
        except Exception as e:
            logger.error(f"Failed to generate preview for {artifact_id}: {e}")
            return None
