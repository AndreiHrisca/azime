from __future__ import annotations
import logging
from azime.core.orchestrator import Event, EventBus

log = logging.getLogger("azime.persona")

class Persona:
    name = "persona"

    async def start(self, bus: EventBus) -> None:
        self._bus = bus

    async def stop(self) -> None:
        pass

    def subscriptions(self):
        return {"dialog.reply": self.on_reply}

    async def on_reply(self, event: Event) -> None:
        text = event.payload.get("text", "")
        intent = event.payload.get("intent", "UNKNOWN")
        styled = self._style(text, intent)
        await self._bus.publish(Event(
            type="dialog.final",
            payload={"text": styled, "intent": intent},
            source=self.name,
        ))

    def _style(self, text: str, intent: str) -> str:
        # Estilo D (adaptativo)
        if intent in {"GREETING"}:
            return f"😎 {text}"
        if intent in {"FAREWELL"}:
            return f"👋 {text}"
        if intent in {"HELP"}:
            return f"💼 {text}"  # tono corporativo breve
        if intent in {"UNKNOWN"}:
            return f"🤝 {text}"  # empático por defecto
        return text