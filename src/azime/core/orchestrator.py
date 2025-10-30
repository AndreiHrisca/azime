"""
Azime Core Orchestrator (v1)

Self‑contained MVP of the event‑driven core. No external deps.
- Async event bus
- BaseModule interface
- Orchestrator with lifecycle (start/stop) and routing
- Minimal demo module (EchoModule)

Run (dev):
    python orchestrator.py

Integrate later into your tree as: src/azime/core/orchestrator.py
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

# -------------------------
# Logging setup
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("azime.core")

# -------------------------
# Event model & bus
# -------------------------

@dataclass(slots=True)
class Event:
    type: str
    payload: Dict[str, Any]
    source: str
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:  # compact logs
        return f"Event(type={self.type!r}, source={self.source!r}, ts={self.ts.isoformat()}, keys={list(self.payload.keys())})"


# Handler signature for subscribers
EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """Minimal async pub/sub. In‑proc only.

    - Handlers subscribe by event type. Use '*' to receive all events.
    - Publish is fan‑out to all matching handlers.
    - Backpressure: handlers are awaited sequentially to keep it simple.
    """

    def __init__(self) -> None:
        self._subs: Dict[str, List[EventHandler]] = {}
        self._lock = asyncio.Lock()
        self._closed = False

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        async with self._lock:
            self._subs.setdefault(event_type, []).append(handler)

    async def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        async with self._lock:
            if event_type in self._subs:
                with contextlib.suppress(ValueError):
                    self._subs[event_type].remove(handler)

    async def publish(self, event: Event) -> None:
        if self._closed:
            log.debug("drop event %s: bus closed", event)
            return
        # snapshot subscribers without holding lock while invoking
        async with self._lock:
            targets = list(self._subs.get(event.type, [])) + list(self._subs.get("*", []))
        if not targets:
            log.debug("no subscribers for %s", event)
            return
        for h in targets:
            try:
                await h(event)
            except Exception:
                log.exception("handler error for %s", event)

    async def close(self) -> None:
        self._closed = True
        # nothing else to drain — kept simple for v1


# -------------------------
# Module interface
# -------------------------

class BaseModule(Protocol):
    name: str

    async def start(self, bus: EventBus) -> None: ...
    async def stop(self) -> None: ...

    # Optional: module can expose which events it wants to handle
    def subscriptions(self) -> Dict[str, EventHandler]: ...


# -------------------------
# Orchestrator
# -------------------------

class Orchestrator:
    def __init__(self) -> None:
        self.bus = EventBus()
        self.modules: List[BaseModule] = []
        self._running = False
        self._bg_tasks: List[asyncio.Task] = []

    def register(self, module: BaseModule) -> None:
        if self._running:
            raise RuntimeError("register modules before start()")
        self.modules.append(module)

    async def start(self) -> None:
        if self._running:
            return
        log.info("starting orchestrator with %d module(s)", len(self.modules))
        # start modules
        for m in self.modules:
            await m.start(self.bus)
            for evt_type, handler in m.subscriptions().items():
                await self.bus.subscribe(evt_type, handler)
                log.debug("%s subscribed to '%s'", m.name, evt_type)
        self._running = True
        # fire system event
        await self.bus.publish(Event(type="system.started", payload={}, source="core"))

    async def stop(self) -> None:
        if not self._running:
            return
        log.info("stopping orchestrator")
        # fire system stopping
        await self.bus.publish(Event(type="system.stopping", payload={}, source="core"))
        # cancel bg tasks
        for t in self._bg_tasks:
            t.cancel()
        await asyncio.gather(*self._bg_tasks, return_exceptions=True)
        # stop modules
        for m in reversed(self.modules):
            with contextlib.suppress(Exception):
                await m.stop()
        await self.bus.close()
        self._running = False

    def schedule(self, coro: Awaitable[Any]) -> None:
        self._bg_tasks.append(asyncio.create_task(coro))


# -------------------------
# Demo: Echo module
# -------------------------

class EchoModule:
    name = "echo"

    def __init__(self, prefix: str = "AZIME") -> None:
        self._bus: Optional[EventBus] = None
        self._prefix = prefix

    async def start(self, bus: EventBus) -> None:
        self._bus = bus
        log.info("module %s started", self.name)
        # announce presence
        await self._bus.publish(Event(
            type="module.started",
            payload={"module": self.name},
            source=self.name,
        ))

    async def stop(self) -> None:
        log.info("module %s stopped", self.name)

    def subscriptions(self) -> Dict[str, EventHandler]:
        return {
            "audio.transcript": self.on_transcript,
            "*": self.on_any,
        }

    async def on_transcript(self, event: Event) -> None:
        text = event.payload.get("text", "")
        reply = f"{self._prefix}: {text}"
        # emit a response event
        assert self._bus is not None
        await self._bus.publish(Event(
            type="dialog.reply",
            payload={"text": reply, "original": text},
            source=self.name,
        ))

    async def on_any(self, event: Event) -> None:
        if event.type.startswith("system."):
            log.debug("%s saw %s", self.name, event)


# -------------------------
# Demo runner
# -------------------------

async def _demo_run() -> None:
    orch = Orchestrator()
    orch.register(EchoModule(prefix="Azime"))

    # a tiny sink that prints replies
    async def printer(e: Event) -> None:
        if e.type == "dialog.reply":
            log.info("REPLY → %s", e.payload["text"])  # visible output

    await orch.bus.subscribe("dialog.reply", printer)

    await orch.start()

    # simulate a speech‑to‑text output
    await orch.bus.publish(Event(
        type="audio.transcript",
        payload={"text": "hola, soy Andrei, ¿qué tal?"},
        source="stt.whisper",
    ))

    await asyncio.sleep(0.1)
    await orch.stop()


if __name__ == "__main__":
    try:
        asyncio.run(_demo_run())
    except KeyboardInterrupt:
        pass
