from __future__ import annotations
import logging
from azime.core.orchestrator import Event, EventBus

log = logging.getLogger("azime.output.cli")

class OutputCLI:
    name = "output_cli"

    async def start(self, bus: EventBus) -> None:
        self._bus = bus

    async def stop(self) -> None:
        pass

    def subscriptions(self):
        return {"dialog.final": self.on_final}

    async def on_final(self, event: Event) -> None:
        print(event.payload.get("text", ""))