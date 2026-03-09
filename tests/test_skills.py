"""
Tests for src/skills.py — Skill Registry.

Covers:
- Skill dataclass
- SkillRegistry: register, register_function, get, list_skills, invoke
- Tag filtering
- load_from_directory (with a temporary skill module)
- to_tool_schemas (OpenAI-compatible format)
- skill decorator
- Error cases (missing skill, disabled skill, no handler)
"""

import asyncio
import os
import sys
import textwrap
from typing import Optional

import pytest

from src.skills import Skill, SkillRegistry, skill_registry, skill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_registry() -> SkillRegistry:
    """Return a fresh, isolated SkillRegistry."""
    return SkillRegistry()


# ---------------------------------------------------------------------------
# Skill dataclass
# ---------------------------------------------------------------------------

class TestSkillDataclass:
    """Validate Skill dataclass defaults and structure."""

    def test_minimal_creation(self):
        """Skill can be created with just name and description."""
        s = Skill(name="my_skill", description="Does something")
        assert s.name == "my_skill"
        assert s.description == "Does something"
        assert s.handler is None
        assert s.tags == []
        assert s.metadata == {}
        assert s.enabled is True

    def test_full_creation(self):
        """Skill accepts all fields."""
        handler = lambda: None
        s = Skill(
            name="full",
            description="Full skill",
            handler=handler,
            tags=["a", "b"],
            metadata={"version": "1.0"},
            enabled=False,
        )
        assert s.handler is handler
        assert s.tags == ["a", "b"]
        assert s.metadata == {"version": "1.0"}
        assert s.enabled is False


# ---------------------------------------------------------------------------
# SkillRegistry — registration
# ---------------------------------------------------------------------------

class TestSkillRegistryRegistration:
    """Test skill registration methods."""

    def test_register_skill_object(self):
        """register() stores the skill under its name."""
        reg = make_registry()
        s = Skill(name="ping", description="Ping handler")
        reg.register(s)
        assert reg.get("ping") is s

    def test_register_function(self):
        """register_function() creates and stores a Skill."""
        reg = make_registry()

        def my_func(x: int) -> int:
            return x * 2

        skill_obj = reg.register_function("double", "Double a number", my_func)
        assert isinstance(skill_obj, Skill)
        assert skill_obj.name == "double"
        assert skill_obj.handler is my_func
        assert reg.get("double") is skill_obj

    def test_register_replaces_existing(self):
        """Re-registering a name overwrites the previous skill."""
        reg = make_registry()
        reg.register(Skill(name="x", description="v1"))
        reg.register(Skill(name="x", description="v2"))
        assert reg.get("x").description == "v2"

    def test_get_nonexistent_returns_none(self):
        """get() returns None for unknown skill names."""
        reg = make_registry()
        assert reg.get("no_such_skill") is None


# ---------------------------------------------------------------------------
# SkillRegistry — listing and filtering
# ---------------------------------------------------------------------------

class TestSkillRegistryListing:
    """Test list_skills and tag filtering."""

    def test_list_skills_empty(self):
        """list_skills on empty registry returns empty list."""
        reg = make_registry()
        assert reg.list_skills() == []

    def test_list_skills_excludes_disabled(self):
        """Disabled skills are excluded from list_skills."""
        reg = make_registry()
        reg.register(Skill(name="enabled", description="on"))
        reg.register(Skill(name="disabled", description="off", enabled=False))
        names = [s.name for s in reg.list_skills()]
        assert "enabled" in names
        assert "disabled" not in names

    def test_list_skills_tag_filter(self):
        """list_skills with tag_filter only returns matching skills."""
        reg = make_registry()
        reg.register(Skill(name="math_add", description="add", tags=["math"]))
        reg.register(Skill(name="text_upper", description="upper", tags=["text"]))
        reg.register(Skill(name="math_sub", description="sub", tags=["math"]))

        math_skills = reg.list_skills(tag_filter="math")
        names = [s.name for s in math_skills]
        assert "math_add" in names
        assert "math_sub" in names
        assert "text_upper" not in names

    def test_list_skills_tag_filter_case_insensitive(self):
        """Tag filtering is case-insensitive."""
        reg = make_registry()
        reg.register(Skill(name="s1", description="d", tags=["UTILITY"]))
        results = reg.list_skills(tag_filter="utility")
        assert len(results) == 1

    def test_list_skills_no_filter_returns_all_enabled(self):
        """list_skills() without filter returns all enabled skills."""
        reg = make_registry()
        for i in range(5):
            reg.register(Skill(name=f"skill_{i}", description=f"s{i}"))
        assert len(reg.list_skills()) == 5


# ---------------------------------------------------------------------------
# SkillRegistry — invocation
# ---------------------------------------------------------------------------

class TestSkillRegistryInvocation:
    """Test async invocation."""

    @pytest.mark.asyncio
    async def test_invoke_sync_handler(self):
        """invoke() wraps sync handlers and returns their result."""
        reg = make_registry()
        reg.register_function("add", "Add two ints", lambda a, b: a + b)
        result = await reg.invoke("add", 3, 4)
        assert result == 7

    @pytest.mark.asyncio
    async def test_invoke_async_handler(self):
        """invoke() awaits async handlers correctly."""
        reg = make_registry()

        async def async_double(x: int) -> int:
            return x * 2

        reg.register_function("async_double", "Double", async_double)
        result = await reg.invoke("async_double", x=5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_invoke_unknown_skill_raises_key_error(self):
        """invoke() raises KeyError for unregistered skill names."""
        reg = make_registry()
        with pytest.raises(KeyError, match="not registered"):
            await reg.invoke("ghost")

    @pytest.mark.asyncio
    async def test_invoke_disabled_skill_raises_value_error(self):
        """invoke() raises ValueError when the skill is disabled."""
        reg = make_registry()
        reg.register(
            Skill(
                name="disabled_skill",
                description="d",
                handler=lambda: None,
                enabled=False,
            )
        )
        with pytest.raises(ValueError, match="disabled"):
            await reg.invoke("disabled_skill")

    @pytest.mark.asyncio
    async def test_invoke_skill_without_handler_raises_runtime_error(self):
        """invoke() raises RuntimeError when no handler is set."""
        reg = make_registry()
        reg.register(Skill(name="no_handler", description="d"))
        with pytest.raises(RuntimeError, match="no handler"):
            await reg.invoke("no_handler")

    @pytest.mark.asyncio
    async def test_invoke_with_kwargs(self):
        """invoke() forwards keyword arguments to the handler."""
        reg = make_registry()

        def greet(person: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {person}!"

        reg.register_function("greet", "Greet", greet)
        result = await reg.invoke("greet", person="World", greeting="Hi")
        assert result == "Hi, World!"


# ---------------------------------------------------------------------------
# SkillRegistry — load_from_directory
# ---------------------------------------------------------------------------

class TestSkillRegistryLoadFromDirectory:
    """Test auto-discovery from a directory of Python files."""

    def test_load_from_nonexistent_directory(self):
        """load_from_directory on a missing path loads 0 skills."""
        reg = make_registry()
        loaded = reg.load_from_directory("/no/such/path/here")
        assert loaded == 0

    def test_load_valid_skill_module(self, tmp_path):
        """A module with SKILL_METADATA is discovered and registered."""
        skill_file = tmp_path / "my_skill.py"
        skill_file.write_text(
            textwrap.dedent("""\
                SKILL_METADATA = {
                    "name": "my_skill",
                    "description": "A test skill",
                    "tags": ["test"],
                }

                def run(x):
                    return x + 1
            """)
        )

        reg = make_registry()
        loaded = reg.load_from_directory(str(tmp_path))
        assert loaded == 1
        s = reg.get("my_skill")
        assert s is not None
        assert s.description == "A test skill"
        assert s.tags == ["test"]

    def test_load_module_without_skill_metadata(self, tmp_path):
        """Modules without SKILL_METADATA are silently skipped."""
        skill_file = tmp_path / "plain.py"
        skill_file.write_text("x = 42\n")

        reg = make_registry()
        loaded = reg.load_from_directory(str(tmp_path))
        assert loaded == 0

    def test_load_module_missing_name_key(self, tmp_path):
        """Modules whose SKILL_METADATA lacks 'name' are skipped."""
        skill_file = tmp_path / "bad.py"
        skill_file.write_text(
            "SKILL_METADATA = {'description': 'no name here'}\n"
        )

        reg = make_registry()
        loaded = reg.load_from_directory(str(tmp_path))
        assert loaded == 0

    def test_load_ignores_private_modules(self, tmp_path):
        """Files starting with underscore are not loaded."""
        (tmp_path / "_private.py").write_text(
            "SKILL_METADATA = {'name': 'private', 'description': 'd'}\n"
        )
        reg = make_registry()
        loaded = reg.load_from_directory(str(tmp_path))
        assert loaded == 0


# ---------------------------------------------------------------------------
# SkillRegistry — to_tool_schemas
# ---------------------------------------------------------------------------

class TestToToolSchemas:
    """Test OpenAI-compatible schema generation."""

    def test_returns_list(self):
        """to_tool_schemas returns a list."""
        reg = make_registry()
        assert isinstance(reg.to_tool_schemas(), list)

    def test_empty_registry_returns_empty_list(self):
        """No skills → empty schema list."""
        reg = make_registry()
        assert reg.to_tool_schemas() == []

    def test_schema_structure(self):
        """Each schema has the required OpenAI tool structure."""
        reg = make_registry()
        reg.register_function("ping", "Ping", lambda: "pong")
        schemas = reg.to_tool_schemas()
        assert len(schemas) == 1
        s = schemas[0]
        assert s["type"] == "function"
        assert "function" in s
        fn = s["function"]
        assert fn["name"] == "ping"
        assert fn["description"] == "Ping"
        assert "parameters" in fn

    def test_schema_includes_typed_params(self):
        """Parameters with type annotations are reflected in the schema."""
        reg = make_registry()

        def calculate(value: int, factor: float) -> float:
            return value * factor

        reg.register_function("calculate", "Calc", calculate)
        schemas = reg.to_tool_schemas()
        params = schemas[0]["function"]["parameters"]["properties"]
        assert params["value"]["type"] == "integer"
        assert params["factor"]["type"] == "number"

    def test_disabled_skills_excluded_from_schemas(self):
        """Disabled skills do not appear in to_tool_schemas()."""
        reg = make_registry()
        reg.register(
            Skill(name="visible", description="v", handler=lambda: None)
        )
        reg.register(
            Skill(name="hidden", description="h", handler=lambda: None, enabled=False)
        )
        names = [s["function"]["name"] for s in reg.to_tool_schemas()]
        assert "visible" in names
        assert "hidden" not in names

    def test_required_params_listed(self):
        """Parameters with no default appear in the 'required' list."""
        reg = make_registry()

        def fn(required_arg: str, optional_arg: str = "default") -> str:
            return required_arg + optional_arg

        reg.register_function("fn", "fn", fn)
        schema = reg.to_tool_schemas()[0]["function"]
        assert "required" in schema["parameters"]
        assert "required_arg" in schema["parameters"]["required"]
        assert "optional_arg" not in schema["parameters"].get("required", [])


# ---------------------------------------------------------------------------
# skill decorator
# ---------------------------------------------------------------------------

class TestSkillDecorator:
    """Test the @skill convenience decorator."""

    def test_decorator_registers_skill(self):
        """@skill registers the function with skill_registry."""
        @skill("decorator_test_skill", "A decorated skill", tags=["decorator"])
        def my_skill_fn(x: int) -> int:
            return x + 100

        s = skill_registry.get("decorator_test_skill")
        assert s is not None
        assert s.handler is my_skill_fn
        assert "decorator" in s.tags

        # Cleanup
        del skill_registry._skills["decorator_test_skill"]

    def test_decorator_returns_original_function(self):
        """@skill should return the original callable unchanged."""
        @skill("identity_skill", "Returns its input")
        def identity(x):
            return x

        assert callable(identity)
        assert identity(42) == 42

        # Cleanup
        del skill_registry._skills["identity_skill"]

    @pytest.mark.asyncio
    async def test_decorated_skill_is_invokable(self):
        """A skill registered via @skill can be invoked through skill_registry."""
        @skill("async_decorated", "Async decorated skill")
        async def async_fn(msg: str) -> str:
            return f"echo: {msg}"

        result = await skill_registry.invoke("async_decorated", msg="hello")
        assert result == "echo: hello"

        # Cleanup
        del skill_registry._skills["async_decorated"]
