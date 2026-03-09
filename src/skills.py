"""
Skill Registry for the Antigravitys agent system.

Provides a lightweight registry that maps named skills to callable
handlers, supports tagging and filtering, generates OpenAI-compatible
tool schemas, and can auto-discover skills from Python modules on disk.

Example::

    from src.skills import skill_registry, skill

    @skill("greet", "Say hello to someone", tags=["utility"])
    async def greet(name: str) -> str:
        return f"Hello, {name}!"

    result = await skill_registry.invoke("greet", name="World")
"""

import asyncio
import importlib.util
import inspect
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    """A registered skill with metadata and a callable handler.

    Attributes:
        name: Unique skill identifier.
        description: Human-readable description of what the skill does.
        handler: Optional async or sync callable that implements the skill.
        tags: List of category/tag strings for filtering.
        metadata: Arbitrary key/value pairs (e.g. version, author).
        enabled: When ``False`` the skill is excluded from listings and
            invocations.
    """

    name: str
    description: str
    handler: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class SkillRegistry:
    """Central registry for agent skills.

    Skills are callable units of capability that can be discovered, listed,
    invoked, and exposed as OpenAI tool schemas.

    Example::

        registry = SkillRegistry()
        registry.register_function(
            name="add",
            description="Add two integers",
            handler=lambda a, b: a + b,
            tags=["math"],
        )
        result = await registry.invoke("add", a=1, b=2)
    """

    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, skill: Skill) -> None:
        """Register a :class:`Skill` instance.

        Args:
            skill: The skill to register.  Replaces any previously
                registered skill with the same name.
        """
        self._skills[skill.name] = skill
        logger.debug("Registered skill: %s", skill.name)

    def register_function(
        self,
        name: str,
        description: str,
        handler: Callable,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Skill:
        """Create and register a skill from a plain callable.

        Args:
            name: Unique skill identifier.
            description: Human-readable description.
            handler: Async or sync callable that implements the skill.
            tags: Optional category tags.
            metadata: Optional arbitrary metadata dictionary.

        Returns:
            The newly created and registered :class:`Skill`.
        """
        skill = Skill(
            name=name,
            description=description,
            handler=handler,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.register(skill)
        return skill

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[Skill]:
        """Retrieve a skill by name.

        Args:
            name: Skill identifier.

        Returns:
            The :class:`Skill` if registered, otherwise ``None``.
        """
        return self._skills.get(name)

    def list_skills(
        self,
        tag_filter: Optional[str] = None,
    ) -> List[Skill]:
        """Return all *enabled* skills, optionally filtered by tag.

        Args:
            tag_filter: When provided, only skills containing this tag
                (case-insensitive substring match) are returned.

        Returns:
            List of matching enabled skills.
        """
        skills = [s for s in self._skills.values() if s.enabled]
        if tag_filter is not None:
            tag_lower = tag_filter.lower()
            skills = [
                s for s in skills
                if any(tag_lower in t.lower() for t in s.tags)
            ]
        return skills

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------

    async def invoke(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a registered skill by name.

        Args:
            name: Skill identifier.
            *args: Positional arguments forwarded to the handler.
            **kwargs: Keyword arguments forwarded to the handler.

        Returns:
            The result returned by the skill handler.

        Raises:
            KeyError: If no skill with *name* is registered.
            ValueError: If the skill is disabled.
            RuntimeError: If the skill has no handler.
        """
        skill = self._skills.get(name)
        if skill is None:
            raise KeyError(f"Skill '{name}' is not registered")
        if not skill.enabled:
            raise ValueError(f"Skill '{name}' is disabled")
        if skill.handler is None:
            raise RuntimeError(f"Skill '{name}' has no handler")

        if inspect.iscoroutinefunction(skill.handler):
            return await skill.handler(*args, **kwargs)
        # Run sync handlers in the default executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: skill.handler(*args, **kwargs)
        )

    # ------------------------------------------------------------------
    # Directory-based discovery
    # ------------------------------------------------------------------

    def load_from_directory(self, path: str) -> int:
        """Scan *path* for Python modules that expose ``SKILL_METADATA``.

        Each discovered module must define a module-level dictionary named
        ``SKILL_METADATA`` with at least the keys ``"name"`` and
        ``"description"``.  An optional ``"handler"`` key points to the
        callable to use (defaults to a function named ``"run"`` if
        present).

        Args:
            path: Filesystem path to scan.

        Returns:
            Number of skills successfully loaded.
        """
        loaded = 0
        if not os.path.isdir(path):
            logger.warning("Skill directory not found: %s", path)
            return loaded

        for filename in os.listdir(path):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            filepath = os.path.join(path, filename)
            module_name = f"_skill_{filename[:-3]}"

            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, filepath
                )
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)  # type: ignore[union-attr]

                meta: Optional[Dict[str, Any]] = getattr(
                    module, "SKILL_METADATA", None
                )
                if not isinstance(meta, dict):
                    continue

                name = meta.get("name")
                description = meta.get("description", "")
                if not name:
                    logger.warning(
                        "SKILL_METADATA in %s missing 'name' key – skipped",
                        filename,
                    )
                    continue

                handler = meta.get("handler") or getattr(module, "run", None)
                tags = meta.get("tags", [])
                metadata = {
                    k: v
                    for k, v in meta.items()
                    if k not in {"name", "description", "handler", "tags"}
                }

                self.register_function(
                    name=name,
                    description=description,
                    handler=handler,
                    tags=tags,
                    metadata=metadata,
                )
                loaded += 1
                logger.debug("Auto-loaded skill '%s' from %s", name, filename)

            except (ImportError, AttributeError, SyntaxError, TypeError, ValueError) as exc:
                logger.error(
                    "Failed to load skill from %s: %s", filename, exc,
                    exc_info=True,
                )

        return loaded

    # ------------------------------------------------------------------
    # Schema generation
    # ------------------------------------------------------------------

    def to_tool_schemas(self) -> List[Dict[str, Any]]:
        """Generate OpenAI-compatible tool schemas for all enabled skills.

        Each schema follows the ``tools`` array format accepted by the
        OpenAI Chat Completions API (``type: function``).

        Returns:
            List of tool schema dictionaries.
        """
        schemas: List[Dict[str, Any]] = []
        for skill in self.list_skills():
            parameters: Dict[str, Any] = {"type": "object", "properties": {}}
            required: List[str] = []

            if skill.handler is not None:
                try:
                    sig = inspect.signature(skill.handler)
                    for param_name, param in sig.parameters.items():
                        if param_name in ("self", "cls"):
                            continue
                        prop: Dict[str, Any] = {"type": "string"}
                        if param.annotation is not inspect.Parameter.empty:
                            py_type = param.annotation
                            if py_type is int:
                                prop["type"] = "integer"
                            elif py_type is float:
                                prop["type"] = "number"
                            elif py_type is bool:
                                prop["type"] = "boolean"
                            elif py_type is list or (
                                hasattr(py_type, "__origin__")
                                and py_type.__origin__ is list
                            ):
                                prop["type"] = "array"
                                prop["items"] = {}
                        parameters["properties"][param_name] = prop
                        if param.default is inspect.Parameter.empty:
                            required.append(param_name)
                except (ValueError, TypeError):
                    pass

            if required:
                parameters["required"] = required

            schema: Dict[str, Any] = {
                "type": "function",
                "function": {
                    "name": skill.name,
                    "description": skill.description,
                    "parameters": parameters,
                },
            }
            if skill.tags:
                schema["function"]["tags"] = skill.tags  # type: ignore[index]
            schemas.append(schema)

        return schemas


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Global default skill registry.
skill_registry: SkillRegistry = SkillRegistry()


# ---------------------------------------------------------------------------
# Decorator helper
# ---------------------------------------------------------------------------

def skill(
    name: str,
    description: str,
    tags: Optional[List[str]] = None,
) -> Callable[[Callable], Callable]:
    """Decorator that registers a function as a skill in :data:`skill_registry`.

    Args:
        name: Unique skill identifier.
        description: Human-readable description.
        tags: Optional category tags.

    Returns:
        A decorator that registers the wrapped function and returns it
        unchanged.

    Example::

        @skill("reverse", "Reverse a string", tags=["text"])
        def reverse_string(text: str) -> str:
            return text[::-1]
    """

    def decorator(fn: Callable) -> Callable:
        skill_registry.register_function(
            name=name,
            description=description,
            handler=fn,
            tags=tags or [],
        )
        return fn

    return decorator
