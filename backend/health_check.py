"""Health check utility functions for Antigravity Workspace backend.

Provides reusable component-level health checks used by the /health/ready
endpoint in main.py.
"""

import logging
import shutil
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def check_watcher(watcher: Any) -> Tuple[Dict[str, Any], bool]:
    """Check the file-watcher component health.

    Args:
        watcher: The Watcher instance to inspect.

    Returns:
        A tuple of (component_status_dict, is_healthy).
    """
    try:
        healthy = watcher.is_healthy()
        return (
            {"status": "healthy" if healthy else "unhealthy", "running": watcher.is_running()},
            healthy,
        )
    except Exception as exc:
        logger.error(f"Error checking watcher health: {exc}")
        return {"status": "error", "error": str(exc)}, False


def check_chromadb() -> Tuple[Dict[str, Any], bool]:
    """Check the ChromaDB / VectorStore component health.

    Returns:
        A tuple of (component_status_dict, is_healthy).
    """
    try:
        from rag.store import VectorStore

        store = VectorStore()
        if store.collection:
            result = store.query([[0.1] * 384], n_results=1)
            healthy = result is not None
            return (
                {
                    "status": "healthy" if healthy else "unhealthy",
                    "collection": "initialized",
                },
                healthy,
            )
        return {"status": "unhealthy", "collection": "not initialized"}, False
    except Exception as exc:
        logger.error(f"Error checking ChromaDB health: {exc}")
        return {"status": "error", "error": str(exc)}, False


def check_cache(orchestrator: Any) -> Tuple[Dict[str, Any], bool]:
    """Check the response-cache component health.

    Args:
        orchestrator: The Orchestrator instance whose cache is inspected.

    Returns:
        A tuple of (component_status_dict, is_healthy).
    """
    try:
        if orchestrator:
            cache_size = len(orchestrator._response_cache)
            hit_rate = orchestrator.get_cache_hit_rate()
            return (
                {"status": "healthy", "size": cache_size, "hit_rate": f"{hit_rate:.1%}"},
                True,
            )
        return {"status": "unhealthy", "error": "Orchestrator not initialized"}, False
    except Exception as exc:
        logger.error(f"Error checking cache health: {exc}")
        return {"status": "error", "error": str(exc)}, True  # cache error is non-critical


def check_disk(watch_dir: str) -> Tuple[Dict[str, Any], bool]:
    """Check available disk space.

    Args:
        watch_dir: Path to the directory to check (e.g. drop_zone).

    Returns:
        A tuple of (component_status_dict, is_healthy).
    """
    try:
        usage = shutil.disk_usage(watch_dir)
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100
        healthy = used_pct < 95
        if not healthy:
            logger.warning(f"Disk usage high: {used_pct:.1f}%")
        return (
            {
                "status": "healthy" if healthy else "warning",
                "free_gb": f"{free_gb:.2f}",
                "total_gb": f"{total_gb:.2f}",
                "used_percent": f"{used_pct:.1f}%",
            },
            True,  # disk warning is non-critical for readiness
        )
    except Exception as exc:
        logger.error(f"Error checking disk space: {exc}")
        return {"status": "error", "error": str(exc)}, True  # disk error is non-critical


def check_local_llm() -> Dict[str, Any]:
    """Check whether the local LLM client can be instantiated.

    Returns:
        A component status dict. LLM availability is never critical for readiness.
    """
    try:
        from agent.local_client import LocalClient  # noqa: F401

        _ = LocalClient()  # only test instantiation, not an actual inference call
        return {"status": "available", "note": "Not tested (expensive operation)"}
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


def build_readiness_report(watcher: Any, orchestrator: Optional[Any]) -> Tuple[Dict[str, Any], bool]:
    """Assemble a full readiness report for all components.

    Args:
        watcher: The Watcher instance.
        orchestrator: The Orchestrator instance (may be None).

    Returns:
        A tuple of (health_status_dict, all_healthy).
    """
    components: Dict[str, Any] = {}
    all_healthy = True

    watcher_status, watcher_ok = check_watcher(watcher)
    components["watcher"] = watcher_status
    if not watcher_ok:
        all_healthy = False

    chromadb_status, chromadb_ok = check_chromadb()
    components["chromadb"] = chromadb_status
    if not chromadb_ok:
        all_healthy = False

    cache_status, cache_ok = check_cache(orchestrator)
    components["cache"] = cache_status
    if not cache_ok:
        all_healthy = False

    if watcher is not None:
        disk_status, _ = check_disk(watcher.watch_dir)
        components["disk"] = disk_status

    components["local_llm"] = check_local_llm()

    status = "ready" if all_healthy else "degraded"
    return {"status": status, "components": components}, all_healthy
