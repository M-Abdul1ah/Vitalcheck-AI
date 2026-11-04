# VitalCheck AI 🩺

A bilingual (Urdu/English) **dermatology guidance app** built as a semester group project with free-tier tools.
It gives general information about skin concerns and always sends serious cases to a doctor.

> ⚠️ **Disclaimer:** VitalCheck AI is an informational tool only. It does not diagnose or prescribe. Always consult a licensed doctor.

**Project idea, system architecture and workflow designed by Muhammad Abdullah Nawaz.**

---

## Status (3 November 2026)

| Built and working | In progress | Planned |
|---|---|---|
| Streamlit app (English/Urdu, RTL) | Own skin-photo model **DermaVC-Net** (PyTorch, trained on Colab; validating results) | Photo analysis in the app (top-3 matches + confidence + Grad-CAM) |
| Emergency safety gate (English, Urdu, Roman Urdu) | | Confidence threshold and out-of-distribution check |
| Knowledge-base search (ChromaDB + multilingual embeddings) | | Bigger, sourced knowledge base |
| Answer built from the knowledge base (no AI model, no API key) | | 40-query test set, retrieval and safety evaluation |
| Output check (blocks medicine names, doses, definite diagnosis) | | Deployment (Hugging Face Spaces) |
| Workflow tab (shows every step of each answer) | | Fairness test and phone-photo test |
| Photo upload preparation (resize, metadata removed, never stored) | | |
| PDF health report (Urdu and English) | | |
| Input length and rate limits | | |

An earlier prototype with an LLM (Groq / Gemini / LangChain) and A2A agents is kept on the branch `archive/llm-prototype`. It was removed from `main` so the app needs no API key. An LLM explanation layer may return later.

## How it works

```text
message -> emergency gate -> (photo prep) -> knowledge-base search -> answer from matches -> output check -> answer + sources -> PDF
```

1. **Emergency gate:** fixed rules. A red-flag phrase stops everything and shows the Rescue 1122 warning.
2. **Photo prep:** checks the file, removes metadata, resizes. The photo is never written to disk. (Analysis by DermaVC-Net is not connected yet.)
3. **Knowledge-base search:** multilingual sentence embeddings + ChromaDB, so an Urdu message finds English knowledge-base text.
4. **Answer:** built from the closest knowledge-base entries.
5. **Output check:** fixed rules block medicine names, doses and definite-diagnosis wording and add a doctor reminder.

## Tech stack (free)

Streamlit, ChromaDB, sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`), Pillow, fpdf2, PyTorch (own model), pytest, GitHub Actions.

## Setup

```powershell
git clone https://github.com/M-Abdul1ah/Vitalcheck-AI.git
cd Vitalcheck-AI
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Python 3.10 or newer. No API key is needed. The knowledge-base database is built automatically on the first start.

Run the tests:

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

## Project layout

```text
app.py                  Streamlit app
src/safety_check.py     emergency gate (rules)
src/output_check.py     output check (rules)
src/embed_store.py      builds the ChromaDB knowledge base
src/retriever.py        knowledge-base search
src/vision_agent.py     photo preparation
src/report_gen.py       PDF report
src/trace.py, workflow_ui.py   Workflow tab
src/limits.py           input length and rate limits
data/dermatology_kb.txt knowledge base
docs/                   roadmap, training plan, architecture review
tests/                  pytest tests
scripts/                learning demos
```

## Team

| Member | Role |
|---|---|
| M. Abdullah Nawaz | Team lead, ML engineer: all code, training, evaluation, integration |
| M. Yousaf | R&D: datasets, licenses, phone-photo collection |
| Izhan Malik | R&D: methods (calibration, OOD, fairness, ablations) |
| AbdulRehman | R&D: knowledge-base sources, test queries, related work |

## Known limits

General guidance only, not a diagnosis. The skin model is trained on dermoscopic images (HAM10000, mostly moles), so accuracy on normal phone photos will be lower, and the data is skewed to lighter skin tones. The emergency word lists are a starting point, not clinically validated. See `docs/ROADMAP.md` for the plan.
