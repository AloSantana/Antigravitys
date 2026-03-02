"""
Ecosystem Manager for Antigravity Workspace.

Provides logic to list, install, and manage OpenCode plugins through the
oh-my-opencode harness, acting as a proxy to the underlying plugin
marketplace (opencode.cafe / openhav).
"""

import os
import json
import logging
import subprocess
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Well-known OpenCode plugin marketplace endpoints
MARKETPLACE_CATALOG_URL = "https://opencode.cafe/api/plugins"

# Paths used for plugin state
_PROJECT_ROOT = Path(__file__).parent.parent
_OPENCODE_JSON = _PROJECT_ROOT / "opencode.json"
_OH_MY_OPENCODE_JSON = _PROJECT_ROOT / ".opencode" / "oh-my-opencode.json"
_ECOSYSTEM_DIR = _PROJECT_ROOT / "ecosystem"


class EcosystemManager:
    """
    Manages ecosystem integration: OpenCode plugin listing, installation, and
    status reporting for the oh-my-opencode harness.
    """

    def __init__(
        self,
        opencode_json_path: Optional[Path] = None,
        oh_my_opencode_json_path: Optional[Path] = None,
    ) -> None:
        self.opencode_json = opencode_json_path or _OPENCODE_JSON
        self.oh_my_opencode_json = oh_my_opencode_json_path or _OH_MY_OPENCODE_JSON

    # ── Plugin catalog ────────────────────────────────────────────────────────

    def list_installed_plugins(self) -> List[Dict[str, Any]]:
        """
        Return a list of currently installed OpenCode plugins from opencode.json.

        Returns:
            List of plugin descriptor dicts with at least ``name`` and ``enabled``.
        """
        if not self.opencode_json.exists():
            logger.warning("opencode.json not found at %s", self.opencode_json)
            return []

        try:
            with open(self.opencode_json, "r", encoding="utf-8") as fh:
                config = json.load(fh)

            # opencode.json may use "plugin" (singular) or "plugins" (plural)
            raw = config.get("plugins", config.get("plugin", []))

            plugins: List[Dict[str, Any]] = []
            for entry in raw:
                if isinstance(entry, str):
                    plugins.append({"name": entry, "enabled": True})
                elif isinstance(entry, dict):
                    plugins.append(
                        {
                            "name": entry.get("name", "unknown"),
                            "enabled": entry.get("enabled", True),
                            **{k: v for k, v in entry.items() if k not in ("name", "enabled")},
                        }
                    )
            return plugins
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read opencode.json: %s", exc)
            return []

    def install_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """
        Install a plugin by adding it to opencode.json and running the
        oh-my-opencode harness install command if available.

        Args:
            plugin_name: The npm package name of the plugin
                         (e.g. ``opencode-plugin-github``).

        Returns:
            Result dict with ``success`` bool and optional ``message``/``error``.
        """
        # Validate name
        if not plugin_name or not isinstance(plugin_name, str):
            return {"success": False, "error": "plugin_name must be a non-empty string"}

        # Persist into opencode.json using whichever key already exists
        try:
            config = self._read_opencode_json()
            # Prefer the existing key; default to "plugin" (opencode.json convention)
            plugin_key = "plugins" if "plugins" in config else "plugin"
            plugins = config.setdefault(plugin_key, [])

            # Avoid duplicates
            existing_names = [
                (p if isinstance(p, str) else p.get("name", "")) for p in plugins
            ]
            if plugin_name in existing_names:
                return {"success": True, "message": f"Plugin '{plugin_name}' is already installed"}

            plugins.append(plugin_name)
            self._write_opencode_json(config)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to update opencode.json: %s", exc)
            return {"success": False, "error": f"Failed to update opencode.json: {exc}"}

        # Try to invoke the harness CLI if npm / oh-my-opencode is available
        harness_result = self._run_harness_command("install", plugin_name)

        return {
            "success": True,
            "message": f"Plugin '{plugin_name}' installed",
            "harness": harness_result,
        }

    def uninstall_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """
        Remove a plugin from opencode.json.

        Args:
            plugin_name: The plugin name to remove.

        Returns:
            Result dict with ``success`` bool.
        """
        try:
            config = self._read_opencode_json()
            plugin_key = "plugins" if "plugins" in config else "plugin"
            plugins = config.get(plugin_key, [])

            new_plugins = [
                p for p in plugins
                if (p if isinstance(p, str) else p.get("name", "")) != plugin_name
            ]

            if len(new_plugins) == len(plugins):
                return {"success": False, "error": f"Plugin '{plugin_name}' not found"}

            config[plugin_key] = new_plugins
            self._write_opencode_json(config)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to update opencode.json: %s", exc)
            return {"success": False, "error": str(exc)}

        return {"success": True, "message": f"Plugin '{plugin_name}' uninstalled"}

    # ── Ecosystem component status ────────────────────────────────────────────

    def get_ecosystem_status(self) -> Dict[str, Any]:
        """
        Return the current status of all ecosystem components.

        Returns:
            Dict mapping component names to their status dicts.
        """
        components = {
            "oh-my-opencode": self._probe_component(
                "oh-my-opencode",
                pid_file=".oh-my-opencode.pid",
                log_file="logs/oh-my-opencode.log",
            ),
            "opencode-hub": self._probe_component(
                "opencode-hub",
                pid_file=".opencode-hub.pid",
                log_file="logs/opencode-hub.log",
            ),
            "openclaw-gateway": self._probe_component(
                "openclaw-gateway",
                pid_file=".openclaw.pid",
                log_file="logs/openclaw.log",
            ),
            "swarm-tools": self._probe_component(
                "swarm-tools",
                pid_file=".swarm-tools.pid",
                log_file="logs/swarm-tools.log",
            ),
        }
        installed_plugins = self.list_installed_plugins()
        return {
            "components": components,
            "installed_plugins": installed_plugins,
            "ecosystem_dir": str(_ECOSYSTEM_DIR),
            "ecosystem_ready": _ECOSYSTEM_DIR.exists(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _probe_component(
        self, name: str, pid_file: str, log_file: str
    ) -> Dict[str, Any]:
        """Check whether an ecosystem component process is running."""
        pid_path = _PROJECT_ROOT / pid_file
        repo_path = _ECOSYSTEM_DIR / name

        running = False
        pid: Optional[int] = None

        if pid_path.exists():
            try:
                pid = int(pid_path.read_text().strip())
                # Send signal 0 to check existence without killing
                os.kill(pid, 0)
                running = True
            except (ProcessLookupError, PermissionError, ValueError):
                running = False
                pid = None

        return {
            "name": name,
            "running": running,
            "pid": pid,
            "installed": repo_path.exists(),
            "log_file": str(_PROJECT_ROOT / log_file),
        }

    def _read_opencode_json(self) -> Dict[str, Any]:
        """Read opencode.json, returning an empty dict if missing."""
        if not self.opencode_json.exists():
            return {}
        with open(self.opencode_json, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write_opencode_json(self, config: Dict[str, Any]) -> None:
        """Write config back to opencode.json with 2-space indentation."""
        with open(self.opencode_json, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
            fh.write("\n")

    def _run_harness_command(
        self, command: str, plugin_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to run ``npx oh-my-opencode <command> <plugin>`` if available.

        Returns a result dict on success/failure, or None if the harness CLI
        is not found.
        """
        if not shutil.which("npx"):
            return None

        harness_dir = _ECOSYSTEM_DIR / "oh-my-opencode"
        cwd = str(harness_dir) if harness_dir.exists() else str(_PROJECT_ROOT)

        try:
            result = subprocess.run(
                ["npx", "--yes", "oh-my-opencode", command, plugin_name],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stderr": "harness command timed out"}
        except FileNotFoundError:
            return None
        except Exception as exc:  # pragma: no cover
            logger.error("Harness command failed: %s", exc)
            return {"returncode": -1, "stderr": str(exc)}
