from __future__ import annotations
import asyncio
import logging
from typing import Optional
from azime.core.orchestrator import Event, EventBus

log = logging.getLogger("azime.audio.stt_dummy")

class STTDummy:
    name = "stt_dummy"

    def __init__(self, prompt: str = "> ") -> None:
        self._bus: Optional[EventBus] = None
        self._task: Optional[asyncio.Task] = None
        self._prompt = prompt

    async def start(self, bus: EventBus) -> None:
        self._bus = bus
        async def loop() -> None:
            log.info("STT dummy listo. Escribe texto y pulsa Enter (Ctrl+C para salir).")
            while True:
                # input() es blocking, así que lo pasamos a hilo
                txt = await asyncio.to_thread(input, self._prompt)
                if not txt.strip():
                    continue
                await self._bus.publish(Event(
                    type="audio.transcript",
                    payload={"text": txt.strip(), "lang": "es"},
                    source=self.name,
                ))
        self._task = asyncio.create_task(loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(Exception):
                await self._task

    def subscriptions(self):
        # no consume eventos, solo publica
        return {}