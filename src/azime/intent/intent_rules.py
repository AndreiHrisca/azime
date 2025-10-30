from __future__ import annotations
import re
import logging
from typing import Dict, Callable
from azime.core.orchestrator import Event, EventBus

log = logging.getLogger("azime.intent.rules")

# Reglas simples → intent + optional direct reply
RuleFn = Callable[[str], Dict]


def rule_greeting(text: str) -> Dict:
    if re.search(r"\b(hola|buenas|hey|que\s+tal|hello)\b", text, re.I):
        return {"intent": "GREETING", "confidence": 0.95, "reply": "¡Buenas, Andrei!"}
    return {}


def rule_farewell(text: str) -> Dict:
    if re.search(r"\b(adios|hasta\s+luego|chao|me\s+voy)\b", text, re.I):
        return {"intent": "FAREWELL", "confidence": 0.95, "reply": "¡Cuídate!"}
    return {}


def rule_help(text: str) -> Dict:
    if re.search(r"\b(ayuda|help|no\s+se|como\s+hago)\b", text, re.I):
        return {"intent": "HELP", "confidence": 0.8}
    return {}


RULES: list[RuleFn] = [rule_greeting, rule_farewell, rule_help]


class IntentRules:
    name = "intent_rules"

    def __init__(self, min_confidence: float = 0.6) -> None:
        self._bus: EventBus | None = None
        self._min = min_confidence

    async def start(self, bus: EventBus) -> None:
        self._bus = bus

    async def stop(self) -> None:
        pass

    def subscriptions(self):
        return {"audio.transcript": self.on_transcript}

    async def on_transcript(self, event: Event) -> None:
        text = event.payload.get("text", "")
        intent_data: Dict = {}
        for rule in RULES:
            intent_data = rule(text)
            if intent_data:
                break
        if not intent_data:
            # sin match → mandamos a razonador
            await self._bus.publish(Event(
                type="dialog.intent",
                payload={"text": text, "intent": "UNKNOWN", "confidence": 0.0},
                source=self.name,
            ))
            return
        # Si hay reply directa, la emitimos; si no, publicamos intent
        if "reply" in intent_data and intent_data["confidence"] >= self._min:
            await self._bus.publish(Event(
                type="dialog.reply",
                payload={"text": intent_data["reply"], "intent": intent_data["intent"], "strategy": "rule"},
                source=self.name,
            ))
        else:
            await self._bus.publish(Event(
                type="dialog.intent",
                payload={"text": text, **intent_data},
                source=self.name,
            ))