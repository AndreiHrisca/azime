from __future__ import annotations
import logging
from azime.core.orchestrator import Event, EventBus

log = logging.getLogger("azime.reasoner.llm")

class ReasonerLLM:
    name = "reasoner_llm"

    def __init__(self, provider: str = "mock") -> None:
        self._bus: EventBus | None = None
        self._provider = provider

    async def start(self, bus: EventBus) -> None:
        self._bus = bus

    async def stop(self) -> None:
        pass

    def subscriptions(self):
        return {"dialog.intent": self.on_intent}

    async def on_intent(self, event: Event) -> None:
        text = event.payload.get("text", "")
        intent = event.payload.get("intent", "UNKNOWN")
        # MOCK razonamiento: sustituye por llamada real a OpenAI/Llama cuando quieras
        reply = self._mock_reason(text=text, intent=intent)
        await self._bus.publish(Event(
            type="dialog.reply",
            payload={"text": reply, "intent": intent, "strategy": "llm"},
            source=self.name,
        ))

    def _mock_reason(self, text: str, intent: str) -> str:
        # Default creativo (tu elección 2): interpreta y aporta valor
        if intent == "HELP":
            return "Puedo ayudarte. Dame un poco más de contexto: ¿qué intentas hacer y qué error te sale?"
        return f"Mi lectura: te preocupa '{text}'. Te propongo 2 caminos rápidos: A) paso táctico ahora mismo, B) enfoque de fondo. ¿Con cuál vamos?"