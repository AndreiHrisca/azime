from __future__ import annotations
import asyncio
import logging
from azime.core.orchestrator import Orchestrator
from azime.audio.stt_dummy import STTDummy
from azime.intent.intent_rules import IntentRules
from azime.reasoner.reasoner_llm import ReasonerLLM
from azime.persona.persona import Persona
from azime.output.output_cli import OutputCLI

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

async def main():
    orch = Orchestrator()
    orch.register(STTDummy(prompt=">> "))
    orch.register(IntentRules())
    orch.register(ReasonerLLM(provider="mock"))
    orch.register(Persona())
    orch.register(OutputCLI())

    await orch.start()
    try:
        # corre hasta Ctrl+C
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        await orch.stop()

if __name__ == "__main__":
    asyncio.run(main())