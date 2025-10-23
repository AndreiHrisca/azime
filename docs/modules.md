# 🧩 Azime Modules Overview

> Overview of all current Azime modules and their primary communication links.  
> This document defines the **system topology** — how perception, processing, and control layers interact.

---

## 🔷 Perception Layer

| Module | Description | Communicates With |
|:--|:--|:--|
| `azime.audio` | Handles raw audio input, wake word detection, and voice activity detection (VAD). | `azime.voice`, `azime.core`, `azime.context` |
| `azime.voice` | Performs ASR (speech-to-text) and TTS (text-to-speech). | `azime.audio`, `azime.core`, `azime.persona` |
| `azime.vision` | Processes camera frames for facial, object, and environmental perception. | `azime.context`, `azime.core` |
| `azime.bio` | Interfaces with biometric sensors (heart rate, stress, body temperature, etc.). | `azime.context`, `azime.selfstate` |
| `azime.context` | Gathers environmental and situational context (location, time, device state). | `azime.core`, `azime.reasoner`, `azime.memory` |

---

## 🔶 Processing Layer

| Module | Description | Communicates With |
|:--|:--|:--|
| `azime.core` | Central orchestration unit. Routes data between perception, reasoning, and memory modules. | All modules (main hub) |
| `azime.memory` | Manages long-term and short-term memory (semantic retrieval, embeddings, knowledge). | `azime.core`, `azime.reasoner`, `azime.context` |
| `azime.reasoner` | Handles reasoning, action planning, and cognitive decision-making. | `azime.core`, `azime.memory`, `azime.persona`, `azime.context` |
| `azime.persona` | Defines personality traits, tone, behavior, and moral constraints. | `azime.core`, `azime.reasoner`, `azime.voice` |

---

## 🧠 Cognitive / Awareness Layer

| Module | Description | Communicates With |
|:--|:--|:--|
| `azime.selfstate` | Tracks internal states (emotions, confidence, focus, fatigue). | `azime.core`, `azime.bio`, `azime.awareness` |
| `azime.reflector` | Performs self-reflection based on recent decisions, improving reasoning quality. | `azime.core`, `azime.reasoner`, `azime.memory` |
| `azime.awareness` | Monitors the system’s perception of itself and its environment — early metacognition. | `azime.core`, `azime.selfstate`, `azime.context`, `azime.reflector` |

---

## 🔗 Interaction / Integration Layer

| Module | Description | Communicates With |
|:--|:--|:--|
| `azime.connect` | Handles API integrations and external network connections. | `azime.core`, `azime.actions`, `azime.guard` |
| `azime.iot` | Interfaces with IoT devices (sensors, actuators, environmental data). | `azime.context`, `azime.core` |
| `azime.haptics` | Provides haptic or tactile feedback (vibrations, responses to emotional state). | `azime.selfstate`, `azime.core` |
| `azime.actions` | Executes real-world or digital actions derived from reasoning results. | `azime.core`, `azime.reasoner`, `azime.connect` |

---

## 🛡️ Control / Safety Layer

| Module | Description | Communicates With |
|:--|:--|:--|
| `azime.guard` | Filters outputs for ethical, privacy, and safety compliance. | `azime.core`, `azime.persona`, `azime.privacy` |
| `azime.privacy` | Handles user data protection, anonymization, and access control. | `azime.guard`, `azime.context`, `azime.bio` |
| `azime.control` | Oversees system-level decisions, resource allocation, and process supervision. | All modules (monitoring and overrides) |

---