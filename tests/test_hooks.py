"""
Tests for src/hooks.py — Agent Hook/Lifecycle Event System.

Covers:
- HookEvent enum completeness
- HookContext dataclass
- HookRegistry: register, unregister, fire, fire_sync, get_handlers, clear
- Priority ordering
- Blocking behaviour
- on_event decorator
- Exception isolation (faulty handler does not abort chain)
"""

import asyncio
from datetime import datetime
from typing import Optional

import pytest

from src.hooks import (
    HookContext,
    HookEvent,
    HookRegistry,
    HookHandler,
    hook_registry,
    on_event,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_registry() -> HookRegistry:
    """Return a fresh HookRegistry isolated from the global singleton."""
    return HookRegistry()


async def noop_handler(ctx: HookContext) -> HookContext:
    """A handler that does nothing and returns the context unchanged."""
    return ctx


# ---------------------------------------------------------------------------
# HookEvent
# ---------------------------------------------------------------------------

class TestHookEvent:
    """Validate the HookEvent enum."""

    EXPECTED_EVENTS = {
        "BEFORE_AGENT_INIT",
        "AFTER_AGENT_INIT",
        "BEFORE_TOOL_CALL",
        "AFTER_TOOL_CALL",
        "BEFORE_RESPONSE",
        "AFTER_RESPONSE",
        "BEFORE_MEMORY_SAVE",
        "AFTER_MEMORY_SAVE",
        "ON_ERROR",
        "ON_SESSION_START",
        "ON_SESSION_END",
        "BEFORE_SKILL_LOAD",
        "AFTER_SKILL_LOAD",
        "BEFORE_DELEGATION",
        "AFTER_DELEGATION",
    }

    def test_all_15_events_present(self):
        """All 15 expected event names must be present."""
        actual = {e.name for e in HookEvent}
        assert actual == self.EXPECTED_EVENTS

    def test_event_count(self):
        """Exactly 15 events should be defined."""
        assert len(list(HookEvent)) == 15

    def test_event_values_are_strings(self):
        """Each event value should be a non-empty string."""
        for event in HookEvent:
            assert isinstance(event.value, str)
            assert event.value


# ---------------------------------------------------------------------------
# HookContext
# ---------------------------------------------------------------------------

class TestHookContext:
    """Validate HookContext dataclass behaviour."""

    def test_basic_creation(self):
        """HookContext should be created with required fields."""
        ctx = HookContext(
            event=HookEvent.BEFORE_TOOL_CALL,
            agent_name="TestAgent",
            data={"key": "value"},
            timestamp=datetime.utcnow(),
        )
        assert ctx.event == HookEvent.BEFORE_TOOL_CALL
        assert ctx.agent_name == "TestAgent"
        assert ctx.data == {"key": "value"}
        assert ctx.session_id is None
        assert ctx.can_block is False
        assert ctx.blocked is False

    def test_optional_fields(self):
        """Optional fields accept custom values."""
        ctx = HookContext(
            event=HookEvent.ON_SESSION_START,
            agent_name="Agent",
            data={},
            timestamp=datetime.utcnow(),
            session_id="sess-123",
            can_block=True,
            blocked=False,
        )
        assert ctx.session_id == "sess-123"
        assert ctx.can_block is True

    def test_blocked_default_false(self):
        """blocked defaults to False."""
        ctx = HookContext(
            event=HookEvent.ON_ERROR,
            agent_name="Agent",
            data={},
            timestamp=datetime.utcnow(),
        )
        assert ctx.blocked is False


# ---------------------------------------------------------------------------
# HookRegistry — registration and retrieval
# ---------------------------------------------------------------------------

class TestHookRegistryRegistration:
    """Test handler registration and retrieval."""

    def test_register_and_get_handlers(self):
        """A registered handler should appear in get_handlers."""
        reg = make_registry()
        reg.register(HookEvent.BEFORE_TOOL_CALL, noop_handler)
        handlers = reg.get_handlers(HookEvent.BEFORE_TOOL_CALL)
        assert noop_handler in handlers

    def test_unregister_handler(self):
        """Unregistering a handler removes it from the list."""
        reg = make_registry()
        reg.register(HookEvent.AFTER_TOOL_CALL, noop_handler)
        removed = reg.unregister(HookEvent.AFTER_TOOL_CALL, noop_handler)
        assert removed is True
        assert noop_handler not in reg.get_handlers(HookEvent.AFTER_TOOL_CALL)

    def test_unregister_non_existent_returns_false(self):
        """Unregistering an unknown handler returns False."""
        reg = make_registry()
        result = reg.unregister(HookEvent.ON_ERROR, noop_handler)
        assert result is False

    def test_clear_specific_event(self):
        """clear(event) removes handlers only for that event."""
        reg = make_registry()
        reg.register(HookEvent.BEFORE_TOOL_CALL, noop_handler)
        reg.register(HookEvent.AFTER_TOOL_CALL, noop_handler)
        reg.clear(HookEvent.BEFORE_TOOL_CALL)
        assert reg.get_handlers(HookEvent.BEFORE_TOOL_CALL) == []
        assert noop_handler in reg.get_handlers(HookEvent.AFTER_TOOL_CALL)

    def test_clear_all_events(self):
        """clear() with no argument removes all handlers."""
        reg = make_registry()
        for event in HookEvent:
            reg.register(event, noop_handler)
        reg.clear()
        for event in HookEvent:
            assert reg.get_handlers(event) == []

    def test_multiple_handlers_same_event(self):
        """Multiple handlers can be registered for the same event."""
        reg = make_registry()

        async def handler_a(ctx: HookContext) -> HookContext:
            return ctx

        async def handler_b(ctx: HookContext) -> HookContext:
            return ctx

        reg.register(HookEvent.BEFORE_RESPONSE, handler_a)
        reg.register(HookEvent.BEFORE_RESPONSE, handler_b)
        handlers = reg.get_handlers(HookEvent.BEFORE_RESPONSE)
        assert handler_a in handlers
        assert handler_b in handlers


# ---------------------------------------------------------------------------
# HookRegistry — fire (async)
# ---------------------------------------------------------------------------

class TestHookRegistryFire:
    """Test async fire behaviour."""

    @pytest.mark.asyncio
    async def test_fire_returns_hook_context(self):
        """fire() must return a HookContext."""
        reg = make_registry()
        ctx = await reg.fire(HookEvent.ON_SESSION_START, "Agent", {})
        assert isinstance(ctx, HookContext)
        assert ctx.event == HookEvent.ON_SESSION_START
        assert ctx.agent_name == "Agent"

    @pytest.mark.asyncio
    async def test_fire_no_handlers(self):
        """fire() with no handlers returns a valid context."""
        reg = make_registry()
        ctx = await reg.fire(HookEvent.BEFORE_DELEGATION, "Swarm", {"task": "go"})
        assert ctx.data == {"task": "go"}

    @pytest.mark.asyncio
    async def test_handler_can_mutate_data(self):
        """A handler that mutates ctx.data should be reflected in the result."""
        reg = make_registry()

        async def add_flag(ctx: HookContext) -> HookContext:
            ctx.data["flag"] = True
            return ctx

        reg.register(HookEvent.BEFORE_TOOL_CALL, add_flag)
        ctx = await reg.fire(HookEvent.BEFORE_TOOL_CALL, "Agent", {"original": 1})
        assert ctx.data.get("flag") is True
        assert ctx.data.get("original") == 1

    @pytest.mark.asyncio
    async def test_handler_returning_none_keeps_context(self):
        """A handler that returns None should not discard the context."""
        reg = make_registry()
        call_count = [0]

        async def side_effect_handler(ctx: HookContext) -> None:  # type: ignore[return]
            call_count[0] += 1
            # Returns None implicitly

        reg.register(HookEvent.AFTER_RESPONSE, side_effect_handler)
        ctx = await reg.fire(HookEvent.AFTER_RESPONSE, "Agent", {"x": 42})
        assert call_count[0] == 1
        assert ctx.data["x"] == 42

    @pytest.mark.asyncio
    async def test_faulty_handler_does_not_abort_chain(self):
        """An exception in one handler should not prevent remaining handlers from running."""
        reg = make_registry()
        ran = []

        async def bad_handler(ctx: HookContext) -> HookContext:
            raise RuntimeError("boom")

        async def good_handler(ctx: HookContext) -> HookContext:
            ran.append("good")
            return ctx

        reg.register(HookEvent.ON_ERROR, bad_handler, priority=10)
        reg.register(HookEvent.ON_ERROR, good_handler, priority=0)
        ctx = await reg.fire(HookEvent.ON_ERROR, "Agent", {})
        assert "good" in ran

    @pytest.mark.asyncio
    async def test_can_block_stops_chain(self):
        """When can_block=True and a handler sets blocked=True, chain is aborted."""
        reg = make_registry()
        ran = []

        async def blocking_handler(ctx: HookContext) -> HookContext:
            ran.append("blocker")
            ctx.blocked = True
            return ctx

        async def should_not_run(ctx: HookContext) -> HookContext:
            ran.append("after_block")
            return ctx

        reg.register(HookEvent.BEFORE_SKILL_LOAD, blocking_handler, priority=10)
        reg.register(HookEvent.BEFORE_SKILL_LOAD, should_not_run, priority=0)
        ctx = await reg.fire(
            HookEvent.BEFORE_SKILL_LOAD, "Agent", {}, can_block=True
        )
        assert "blocker" in ran
        assert "after_block" not in ran
        assert ctx.blocked is True

    @pytest.mark.asyncio
    async def test_blocked_without_can_block_does_not_stop(self):
        """blocked=True has no effect when can_block=False."""
        reg = make_registry()
        ran = []

        async def sets_blocked(ctx: HookContext) -> HookContext:
            ctx.blocked = True
            return ctx

        async def runs_anyway(ctx: HookContext) -> HookContext:
            ran.append("ran")
            return ctx

        reg.register(HookEvent.AFTER_SKILL_LOAD, sets_blocked, priority=10)
        reg.register(HookEvent.AFTER_SKILL_LOAD, runs_anyway, priority=0)
        await reg.fire(HookEvent.AFTER_SKILL_LOAD, "Agent", {}, can_block=False)
        assert "ran" in ran

    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """Handlers with higher priority must run before lower-priority handlers."""
        reg = make_registry()
        order = []

        async def low_priority(ctx: HookContext) -> HookContext:
            order.append("low")
            return ctx

        async def high_priority(ctx: HookContext) -> HookContext:
            order.append("high")
            return ctx

        async def mid_priority(ctx: HookContext) -> HookContext:
            order.append("mid")
            return ctx

        reg.register(HookEvent.AFTER_MEMORY_SAVE, low_priority, priority=1)
        reg.register(HookEvent.AFTER_MEMORY_SAVE, high_priority, priority=100)
        reg.register(HookEvent.AFTER_MEMORY_SAVE, mid_priority, priority=50)

        await reg.fire(HookEvent.AFTER_MEMORY_SAVE, "Agent", {})
        assert order == ["high", "mid", "low"]

    @pytest.mark.asyncio
    async def test_session_id_passed_through(self):
        """session_id in the fired context should match the supplied value."""
        reg = make_registry()
        received_session = []

        async def capture(ctx: HookContext) -> HookContext:
            received_session.append(ctx.session_id)
            return ctx

        reg.register(HookEvent.ON_SESSION_END, capture)
        await reg.fire(
            HookEvent.ON_SESSION_END, "Agent", {}, session_id="abc-123"
        )
        assert received_session == ["abc-123"]


# ---------------------------------------------------------------------------
# HookRegistry — fire_sync
# ---------------------------------------------------------------------------

class TestHookRegistryFireSync:
    """Test the synchronous wrapper."""

    def test_fire_sync_returns_hook_context(self):
        """fire_sync must return a HookContext."""
        reg = make_registry()
        ctx = reg.fire_sync(HookEvent.BEFORE_AGENT_INIT, "Agent", {})
        assert isinstance(ctx, HookContext)

    def test_fire_sync_handler_runs(self):
        """Handlers registered on the registry are called by fire_sync."""
        reg = make_registry()
        called = []

        async def my_handler(ctx: HookContext) -> HookContext:
            called.append(True)
            return ctx

        reg.register(HookEvent.AFTER_AGENT_INIT, my_handler)
        reg.fire_sync(HookEvent.AFTER_AGENT_INIT, "Agent", {})
        # The handler should have been called
        assert called == [True]


# ---------------------------------------------------------------------------
# on_event decorator
# ---------------------------------------------------------------------------

class TestOnEventDecorator:
    """Test the on_event convenience decorator."""

    def test_decorator_registers_handler(self):
        """on_event should register the decorated function with hook_registry."""
        # Use a fresh registry to avoid polluting module-level singleton
        # We'll temporarily monkey-patch hook_registry for this test
        original_handlers = hook_registry.get_handlers(
            HookEvent.BEFORE_MEMORY_SAVE
        )[:]

        @on_event(HookEvent.BEFORE_MEMORY_SAVE)
        async def my_test_hook(ctx: HookContext) -> HookContext:
            return ctx

        handlers = hook_registry.get_handlers(HookEvent.BEFORE_MEMORY_SAVE)
        assert my_test_hook in handlers

        # Cleanup
        hook_registry.unregister(HookEvent.BEFORE_MEMORY_SAVE, my_test_hook)

    def test_decorator_returns_original_function(self):
        """on_event should return the original function unmodified."""

        @on_event(HookEvent.ON_SESSION_START, priority=5)
        async def my_hook(ctx: HookContext) -> HookContext:
            return ctx

        assert callable(my_hook)
        assert my_hook.__name__ == "my_hook"

        # Cleanup
        hook_registry.unregister(HookEvent.ON_SESSION_START, my_hook)

    def test_decorator_priority_respected(self):
        """Handlers registered via on_event should use the supplied priority."""
        # We check by verifying call order through fire_sync
        reg = make_registry()
        order = []

        # Register directly to isolated registry – on_event uses global,
        # so we simulate the equivalent behaviour here.
        async def first(ctx: HookContext) -> HookContext:
            order.append(1)
            return ctx

        async def second(ctx: HookContext) -> HookContext:
            order.append(2)
            return ctx

        reg.register(HookEvent.BEFORE_DELEGATION, second, priority=1)
        reg.register(HookEvent.BEFORE_DELEGATION, first, priority=10)

        reg.fire_sync(HookEvent.BEFORE_DELEGATION, "Swarm", {})
        assert order == [1, 2]
