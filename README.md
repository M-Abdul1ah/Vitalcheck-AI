# VitalCheck AI 🩺

A bilingual (Urdu/English) **dermatology-focused symptom checker agent**, built entirely on free-tier tools as a semester-long group project.

> ⚠️ **Disclaimer:** VitalCheck AI is an informational tool only. It does not diagnose or prescribe treatment. Always consult a licensed doctor for medical concerns.

---

## What it does

Users describe a skin concern — by **text, voice, or photo** — and get:
- Possible general causes (phrased as possibilities, never a diagnosis)
- Basic self-care guidance for mild cases
- A clear recommendation to see a dermatologist, with urgency flagged for severe cases

**Why dermatology?** It's the one symptom category where a photo is genuinely diagnostic-relevant — most other symptoms (fever, fatigue, headache) can't be meaningfully assessed from an image. This keeps text, voice, and image input working together as one coherent flow instead of three disconnected features.

---

## Features

- 🗣️ Multi-modal input: text, voice (speech-to-text), and image (skin photo analysis)
- 🌐 Bilingual — replies in Urdu or English, matching the user's input
- 🔗 Multi-agent architecture using the **A2A (Agent2Agent)** protocol
- ⚡ Streaming responses
- 🛡️ Built-in safety guardrails (no diagnosis, no prescriptions, always routes to a real doctor)
- 📄 PDF health report export
- 👤 User accounts with history
- 📊 Admin analytics dashboard
- 📍 Nearby dermatologist suggestions

---

## Tech stack — 100% free tier

| Layer | Tool | Why |
|---|---|---|
| LLM (text) | Groq API — Llama 3.3 | Free, extremely fast inference |
| LLM (vision) | Groq API — Llama 3.2 Vision | Same provider, one API key |
| Speech-to-text | Groq-hosted Whisper | Free, no separate service needed |
| Agent framework | LangChain | Chains + prompt management |
| Agent-to-agent comms | A2A protocol | Open standard, no vendor lock-in |
| Embeddings | sentence-transformers | Free, runs locally |
| Vector DB | ChromaDB | Free, local/embedded |
| UI | Streamlit | Free to build and host |
| Deployment | Streamlit Community Cloud | Free hosting |
| Reference dataset | HAM10000 (skin lesion images) | Free, public, used for demo/testing |

No paid API keys or subscriptions required anywhere in the stack.

---

## Architecture

Instead of one monolithic chain, VitalCheck AI splits work across independent agents that communicate over **A2A**:

1. **Symptom Analysis Agent** — core text/voice intake + LLM reasoning
2. **Vision Agent** — analyzes uploaded skin photos (Dermatology focus)
3. **Recommendation Agent** — suggests nearby dermatologists / urgency level
4. **Report Agent** — generates the PDF health report

Each agent exposes an Agent Card describing its capabilities, so team members can build and test their agent independently before wiring them together.

---

## Team (4 members, roles self-assigned)
## Team members names:
    M. Abdullah Nawaz
    M.Yousaf
    AbdulRehman
    Izhan Malik
| Role | Owns |
|---|---|
| Core LLM & Prompts | Symptom Analysis Agent, safety guardrails |
| Voice Pipeline | Speech-to-text integration |
| Vision Pipeline | Skin photo analysis, HAM10000 testing |
| Orchestration & UI | A2A wiring, Streamlit front-end |

---

## Timeline

Full semester (~1–2 months of active build time), tracked day-by-day in `vitalcheck-ai-roadmap.md` (learn-then-build format with checkbox progress).

---

## Setup

```bash
git clone https://github.com/M-Abdul1ah/Vitalcheck-AI.git
cd Vitalcheck-AI
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # add your free Groq API key
streamlit run app.py
```

---

## Status

🚧 In active development — core text chain built and tested; voice, vision, and A2A layers in progress.
