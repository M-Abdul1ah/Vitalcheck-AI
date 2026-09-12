# VitalCheck AI

VitalCheck AI is a symptom checker agent built using Generative AI. Users describe their symptoms, and the AI analyzes them to suggest possible conditions, guidance, and next steps — like a preliminary health assistant.

This is a group project (4-person team) built as part of a Gen AI internship, with a strong focus on learning core AI/agent concepts (LLMs, embeddings, retrieval, agents) before implementing them.

## What It Does
- Takes user symptoms as input (text, with planned voice support)
- Uses an LLM + knowledge retrieval to analyze symptoms
- Returns possible conditions with safety-conscious guidance
- Supports bilingual interaction (Urdu/English)

## Tech Stack
- **LLM**: Groq API (Llama 3.3)
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB
- **Agent Framework**: LangChain
- **UI**: Streamlit
- **Deployment**: Streamlit Community Cloud

## Planned Features
- Bilingual support (Urdu/English)
- Voice input
- User accounts with session history
- PDF health report export
- Admin analytics dashboard
- Nearby doctor/specialist suggestions
- Streaming LLM responses
- Safety guardrails

## Timeline
This project runs across the full semester (~1–2 months of active build time), following a structured "learn then build" roadmap — see `vitalcheck-ai-roadmap.md` for the step-by-step plan.