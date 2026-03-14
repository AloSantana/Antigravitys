"""
Agent Hook/Lifecycle Event System.

Provides a priority-based hook registry for firing lifecycle events
across agent initialization, tool calls, memory operations, and
delegation workflows.  Inspired by the Moltis local-first AI gateway
architecture (Rust) – ported to async-first Python.

Example::

    from src.hooks import hook_registry, HookEvent, on_event

    @on_event(HookEvent.BEFORE_TOOL_CALL, priority=10)
    async def log_tool(ctx):
        print(f"About to call a tool: {ctx.data}")
        return ctx

    await hook_registry.fire(
        HookEvent.BEFORE_TOOL_CALL,
        agent_name="MyAgent",
        data={"tool": "search"},
    )
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Event catalogue
# ---------------------------------------------------------------------------

class HookEvent(Enum):
    """All recognised lifecycle event types.

    Values are string-keyed so they serialise cleanly to JSON/logs.
    """

    BEFORE_AGENT_INIT = "before_agent_init"
    AFTER_AGENT_INIT = "after_agent_init"
    BEFORE_TOOL_CALL = "before_tool_call"
    AFTER_TOOL_CALL = "after_tool_call"
    BEFORE_RESPONSE = "before_response"
    AFTER_RESPONSE = "after_response"
    BEFORE_MEMORY_SAVE = "before_memory_save"
    AFTER_MEMORY_SAVE = "after_memory_save"
    ON_ERROR = "on_error"
    ON_SESSION_START = "on_session_start"
    ON_SESSION_END = "on_session_end"
    BEFORE_SKILL_LOAD = "before_skill_load"
    AFTER_SKILL_LOAD = "after_skill_load"
    BEFORE_DELEGATION = "before_delegation"
    AFTER_DELEGATION = "after_delegation"


# ---------------------------------------------------------------------------
# Context object passed through every handler chain
# ---------------------------------------------------------------------------

@dataclass
class HookContext:
    """Mutable context object threaded through every handler in a chain.

    Attributes:
        event: The lifecycle event that was fired.
        agent_name: Name of the agent that fired the event.
        data: Arbitrary payload; handlers may mutate this freely.
        timestamp: UTC timestamp at which the event was created.
        session_id: Optional session identifier for the firing agent.
        can_block: When ``True`` a handler may set ``blocked=True`` to
            short-circuit remaining handlers in the chain.
        blocked: Set to ``True`` by a handler that wants to abort the
            remaining chain (only honoured when ``can_block`` is ``True``).
    """

    event: HookEvent
    agent_name: str
    data: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[str] = None
    can_block: bool = False
    blocked: bool = False


# ---------------------------------------------------------------------------
# Handler type
# ---------------------------------------------------------------------------

# A handler is an async callable that receives a HookContext and optionally
# returns a (possibly modified) HookContext.  Returning ``None`` is fine –
# the original context is used in that case.
HookHandler = Callable[[HookContext], Awaitable[Optional[HookContext]]]


# ---------------------------------------------------------------------------
# Internal priority-wrapped record
# ---------------------------------------------------------------------------

@dataclass(order=True)
class _HandlerRecord:
    """Pairs a priority score with a handler callable.

    Records are sorted in *descending* priority order (highest first) via
    a negated priority key so that Python's ascending sort works correctly.
    """

    sort_key: int = field(init=False, repr=False)
    priority: int = field(compare=False)
    handler: HookHandler = field(compare=False)

    def __post_init__(self) -> None:
        # Negate so that higher priority sorts first (ascending sort)
        self.sort_key = -self.priority


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class HookRegistry:
    """Central registry for lifecycle event handlers.

    Handlers registered for the same event are called in descending
    priority order.  Handlers with equal priority are called in
    registration order.

    Example::

        registry = HookRegistry()

        async def my_handler(ctx: HookContext) -> HookContext:
            ctx.data["logged"] = True
            return ctx

        registry.register(HookEvent.BEFORE_TOOL_CALL, my_handler, priority=5)
        ctx = await registry.fire(HookEvent.BEFORE_TOOL_CALL, "agent", {})
    """

    def __init__(self) -> None:
        self._handlers: Dict[HookEvent, List[_HandlerRecord]] = {
            event: [] for event in HookEvent
        }

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        event: HookEvent,
        handler: HookHandler,
        priority: int = 0,
    ) -> None:
        """Register *handler* for *event* with optional *priority*.

        Args:
            event: The lifecycle event to listen for.
            handler: Async callable that accepts a :class:`HookContext`.
            priority: Higher values run first.  Defaults to ``0``.
        """
        record = _HandlerRecord(priority=priority, handler=handler)
        self._handlers[event].append(record)
        # Keep sorted descending by priority (sort_key = -priority)
        self._handlers[event].sort()
        logger.debug(
            "Registered hook handler %r for event %s (priority=%d)",
            getattr(handler, "__name__", handler),
            event.value,
            priority,
        )

    def unregister(self, event: HookEvent, handler: HookHandler) -> bool:
        """Remove *handler* from *event*.

        Args:
            event: The lifecycle event.
            handler: The handler to remove.

        Returns:
            ``True`` if the handler was found and removed, ``False`` otherwise.
        """
        before = len(self._handlers[event])
        self._handlers[event] = [
            r for r in self._handlers[event] if r.handler is not handler
        ]
        removed = len(self._handlers[event]) < before
        if removed:
            logger.debug(
                "Unregistered hook handler %r from event %s",
                getattr(handler, "__name__", handler),
                event.value,
            )
        return removed

    # ------------------------------------------------------------------
    # Firing
    # ------------------------------------------------------------------

    async def fire(
        self,
        event: HookEvent,
        agent_name: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        can_block: bool = False,
    ) -> HookContext:
        """Fire *event* and run all registered handlers in priority order.

        Args:
            event: The lifecycle event to fire.
            agent_name: Identifier of the agent firing the event.
            data: Arbitrary payload forwarded to every handler.
            session_id: Optional session identifier.
            can_block: When ``True``, a handler may set
                ``ctx.blocked = True`` to abort the remaining chain.

        Returns:
            The final :class:`HookContext` after all handlers have run
            (or after an early-block if ``can_block`` is ``True``).
        """
        ctx = HookContext(
            event=event,
            agent_name=agent_name,
            data=data,
            timestamp=datetime.now(timezone.utc),
            session_id=session_id,
            can_block=can_block,
        )

        for record in self._handlers[event]:
            try:
                result = await record.handler(ctx)
                if result is not None:
                    ctx = result
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Hook handler %r raised an exception for event %s: %s",
                    getattr(record.handler, "__name__", record.handler),
                    event.value,
                    exc,
                    exc_info=True,
                )

            if ctx.can_block and ctx.blocked:
                logger.debug(
                    "Hook chain blocked after handler %r for event %s",
                    getattr(record.handler, "__name__", record.handler),
                    event.value,
                )
                break

        return ctx

    def fire_sync(
        self,
        event: HookEvent,
        agent_name: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        can_block: bool = False,
    ) -> HookContext:
        """Synchronous wrapper around :meth:`fire`.

        Uses the running event loop when one exists (e.g. inside an async
        context) or creates a new one via :func:`asyncio.run` otherwise.

        Args:
            event: The lifecycle event to fire.
            agent_name: Identifier of the agent firing the event.
            data: Arbitrary payload forwarded to every handler.
            session_id: Optional session identifier.
            can_block: When ``True``, a handler may block the chain.

        Returns:
            The final :class:`HookContext`.
        """
        coro = self.fire(
            event=event,
            agent_name=agent_name,
            data=data,
            session_id=session_id,
            can_block=can_block,
        )

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We are inside an already-running loop; schedule as a task
                # and return a bare context (handlers run in the background).
                # This is a best-effort fallback for sync callers inside async
                # code – prefer `await fire(...)` in that scenario.
                import concurrent.futures

                future: concurrent.futures.Future = concurrent.futures.Future()

                async def _run() -> None:
                    try:
                        result = await coro
                        future.set_result(result)
                    except asyncio.CancelledError:
                        future.cancel()
                        raise
                    except Exception as exc:  # noqa: BLE001
                        future.set_exception(exc)

                loop.create_task(_run())
                # Return a placeholder context immediately
                return HookContext(
                    event=event,
                    agent_name=agent_name,
                    data=data,
                    timestamp=datetime.now(timezone.utc),
                    session_id=session_id,
                    can_block=can_block,
                )
            return loop.run_until_complete(coro)
        except RuntimeError:
            # No current event loop – use asyncio.run (Python 3.7+)
            return asyncio.run(coro)

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def get_handlers(self, event: HookEvent) -> List[HookHandler]:
        """Return the ordered list of handlers registered for *event*.

        Args:
            event: The lifecycle event to query.

        Returns:
            Handlers in priority-descending order.
        """
        return [r.handler for r in self._handlers[event]]

    def clear(self, event: Optional[HookEvent] = None) -> None:
        """Remove all handlers, optionally scoped to a single event.

        Args:
            event: When provided, only handlers for this event are removed.
                When ``None`` (default), *all* handlers for every event are
                cleared.
        """
        if event is None:
            for ev in HookEvent:
                self._handlers[ev].clear()
        else:
            self._handlers[event].clear()


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Global default registry – import and use directly throughout the project.
hook_registry: HookRegistry = HookRegistry()


# ---------------------------------------------------------------------------
# Decorator helper
# ---------------------------------------------------------------------------

def on_event(
    event: HookEvent,
    priority: int = 0,
) -> Callable[[HookHandler], HookHandler]:
    """Decorator that auto-registers an async function as a hook handler.

    Args:
        event: The lifecycle event to listen for.
        priority: Handler priority (higher runs first).  Defaults to ``0``.

    Returns:
        A decorator that registers the wrapped function with
        :data:`hook_registry` and returns it unchanged.

    Example::

        @on_event(HookEvent.BEFORE_TOOL_CALL, priority=10)
        async def audit_tool_call(ctx: HookContext) -> HookContext:
            print(f"Tool call: {ctx.data}")
            return ctx
    """

    def decorator(fn: HookHandler) -> HookHandler:
        hook_registry.register(event, fn, priority=priority)
        return fn

    return decorator
