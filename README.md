# VitalCheck AI 🩺

A bilingual (Urdu/English) **dermatology guidance app** built as a semester group project with free-tier tools.
It gives general information about skin concerns and always sends serious cases to a doctor.

> ⚠️ **Disclaimer:** VitalCheck AI is an informational tool only. It does not diagnose or prescribe. Always consult a licensed doctor.

**Project idea, system architecture and workflow designed by Muhammad Abdullah Nawaz.**

---

## Status (10 November 2026)

| Built and working | In progress | Planned |
|---|---|---|
| Streamlit app (English/Urdu, RTL) | LLM explainer (Gemini, with fallback to knowledge-base text): written and unit-tested, not merged yet | **DermaVC-Text**: our own text model (28 labels, 3 languages), being built by the team |
| Emergency safety gate (English, Urdu, Roman Urdu) with pattern rules | Ollama (local, offline) as a second LLM provider | Follow-up questions and an LLM safety judge |
| Greeting and small-talk handler, input guard for vague messages | Pipeline refactor into one function (needed for tests and deployment) | Bigger, sourced knowledge base (25 to 30 conditions) |
| Knowledge-base search with a relevance cutoff (ChromaDB + multilingual embeddings) | | 40-query test set, retrieval and safety evaluation |
| **DermaVC-Net** photo analysis: top-3 possible matches, calibrated confidence, melanoma warning, Grad-CAM heatmap | | Phone-photo test and skin-tone fairness test |
| Output check (blocks medicine names, doses, definite diagnosis) | | Model hosting on Hugging Face Hub and deployment |
| Workflow tab (shows every step of each answer) | | |
| Photo upload preparation (resize, metadata removed, never stored) | | |
| PDF health report (Urdu and English) | | |
| Input length and rate limits | | |

An earlier prototype with an LLM (Groq / Gemini / LangChain) and A2A agents is kept on the branch `archive/llm-prototype`.

## How it works

```text
message -> emergency gate -> small-talk / vague check -> photo analysis (DermaVC-Net)
        -> knowledge-base search -> answer -> output check -> answer + sources + photo card -> PDF
```

1. **Emergency gate:** fixed rules and patterns. A red-flag phrase stops everything and shows the Rescue 1122 warning.
2. **Small-talk and vague check:** a greeting gets a friendly reply. A message that is too vague gets a request for details.
3. **Photo analysis:** our own EfficientNet-B0 model (DermaVC-Net) returns the top 3 possible matches with calibrated confidence. Below 50% confidence it says "unclear, please see a doctor". A melanoma probability of 25% or more triggers a warning. A Grad-CAM heatmap shows where the model looked. The photo is never written to disk.
4. **Knowledge-base search:** multilingual sentence embeddings + ChromaDB, so an Urdu message finds English text. If nothing is relevant enough, the app asks the user to describe the problem.
5. **Answer:** built from the closest knowledge-base entries. A mole-type photo result adds the ABCDE mole advice.
6. **Output check:** fixed rules block medicine names, doses and definite-diagnosis wording and add a doctor reminder.

## Our own models

| Model | Job | Status |
|---|---|---|
| **DermaVC-Net** | Skin photo to 7 lesion classes | Trained and integrated. Test accuracy 0.821 ± 0.009, macro F1 0.742 ± 0.014, AUC 0.968 (3 seeds). See `docs/MODEL_CARD.md` |
| **DermaVC-Text** | Symptom text (English, Urdu, Roman Urdu) to a condition, with confidence | In progress (team) |

## Tech stack (free)

Streamlit, ChromaDB, sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`), PyTorch + torchvision (own model), Pillow, fpdf2, pytest, GitHub Actions. Planned: Gemini and Ollama for the LLM explainer.

## Setup

```powershell
git clone https://github.com/M-Abdul1ah/Vitalcheck-AI.git
cd Vitalcheck-AI
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Python 3.10 or newer. The knowledge-base database is built automatically on the first start. No API key is needed.

**Photo analysis needs the model file.** Model files are never stored in Git. Put `C_effnet_finetune_seed7.pt` in a `models/` folder in the project, or set `SKIN_MODEL_PATH` to its location. Without the file the app still works and says that photo analysis is not available. Check your setup with:

```powershell
python scripts/check_skin_model.py
python scripts/check_skin_model.py --image "path\to\photo.jpg"
```

Run the tests:

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

## Project layout

```text
app.py                      Streamlit app
src/safety_check.py         emergency gate (rules and patterns)
src/intent.py               greeting / small-talk check
src/input_guard.py          too-vague message check
src/output_check.py         output check (rules)
src/embed_store.py          builds the ChromaDB knowledge base
src/retriever.py            knowledge-base search
src/vision_agent.py         photo preparation
src/skin_model.py           DermaVC-Net: load, predict, calibration, Grad-CAM
src/report_gen.py           PDF report
src/trace.py, workflow_ui.py   Workflow tab
src/limits.py               input length and rate limits
data/dermatology_kb.txt     knowledge base
training/                   DermaVC-Net results, splits, class files (9 runs)
docs/                       roadmap, model card, training plan, architecture review
scripts/                    model check script and learning demos
tests/                      pytest tests
```

## Team

| Member | Role |
|---|---|
| M. Abdullah Nawaz | Team lead, ML engineer: architecture, DermaVC-Net, integration, evaluation |
| M. Yousaf | DermaVC-Text: data and baseline models |
| Izhan Malik | DermaVC-Text: fine-tuned model, calibration, packaging |
| AbdulRehman | DermaVC-Text: knowledge-base sources, evaluation, model card |

## Known limits

General guidance only, not a diagnosis. DermaVC-Net is trained on dermoscopy images (HAM10000, mostly moles) and knows only 7 lesion types. It cannot recognise acne, eczema or rashes, accuracy on normal phone photos will be lower, and the data is skewed to lighter skin tones. Its melanoma recall is about 65%. The phone-photo and skin-tone tests are not done yet. The emergency word lists are a starting point, not clinically validated. See `docs/MODEL_CARD.md` and `docs/ROADMAP.md`.
