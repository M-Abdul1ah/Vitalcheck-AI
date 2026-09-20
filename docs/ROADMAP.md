# Vital Check AI – Roadmap

Last updated: 20 September 2026

Vital Check AI is a bilingual (Urdu/English) dermatology symptom checker agent.
It gives general guidance only and does not replace a real doctor.

**Stack (all free tier):** Groq API (Llama 3.3), LangChain, ChromaDB, sentence-transformers, Streamlit, Streamlit Community Cloud.

---

## Architecture

```text
User (Streamlit web page: text, later photo/voice)
   |
   v
[1] Safety gate (safety_check.py)   emergency words in Urdu/English -> urgent warning, stop
   |
   v
[2] Agent (agent.py)                asks follow-up questions if symptoms are too vague
   |
   v
[3] Retriever (ChromaDB)            top-3 knowledge chunks (multilingual embeddings)
   |
   v
[4] LLM (Groq, Llama 3.3)           prompt + context -> answer
   |
   v
[5] Output check                    no diagnosis, no medicine names, disclaimer added
   |
   v
Streaming answer -> (later) PDF report
```

| Step | Idea from research papers |
|---|---|
| 3 – Retriever | RAG (all three papers) |
| 2 – Agent | Follow-up questions (Health-LLM) |
| 1, 2, 5 – Separate agents + validation | MALADE |
| Small model + free tier | Lightweight Clinical Decision Support System |

---

## Workflow (for every step)

1. Learn the concept (short).
2. Build the code.
3. Test it.
4. Commit: add specific files by name (never `git add .`), commit, then push.
5. Tick the checkbox below.

Rules:
- One feature = one commit.
- The API key lives only in `.env` (local) and Streamlit Secrets (online). Never in Git.
- Order is always: stage, commit, push.

---

## Phase 0 – Foundation (done)

- [x] Project scaffold and structure
- [x] Core symptom chain (Groq + LangChain)
- [x] Prompt with safety rules
- [x] Embeddings test
- [x] Dermatology knowledge base (`data/dermatology_kb.txt`)
- [x] RAG retrieval with ChromaDB (`embed_store.py`, `retriever.py`)
- [x] Multilingual embeddings for Urdu
- [x] Repo cleanup (removed nested folder)
- [x] AI Assignment 1 (research paper summary)

## Phase 1 – Core

- [ ] `safety_check.py`: emergency word detector (Urdu + English)
- [ ] Add Groq key to `.env`
- [ ] Test RAG-connected chain (`prompts.py`, `symptom_chain.py`) and commit
- [ ] Move test files into `tests/`

## Phase 2 – Agent behavior

- [ ] Follow-up questions in `agent.py`
- [ ] Output check (no diagnosis, no medicine names)
- [ ] Session memory (`memory.py`)

## Phase 3 – Frontend and live link

- [ ] Redesign `app.py` (clean layout, language toggle, example buttons, streaming, disclaimer)
- [ ] Build the database on first start (chroma_db is not in Git)
- [ ] Read the key from Streamlit Secrets
- [ ] Limit input length and requests per session
- [ ] Push to GitHub and deploy on Streamlit Community Cloud
- [ ] Add live link and screenshots to README

## Phase 4 – Extra features

- [ ] PDF health report (`report_gen.py`)
- [ ] Skin photo analysis (vision agent, HAM10000 for testing)
- [ ] Voice input
- [ ] Nearby doctor suggestions
- [ ] A2A agent integration

## Phase 5 – Polish (optional)

- [ ] User accounts and history (`auth.py`)
- [ ] Admin analytics dashboard (`analytics.py`)
- [ ] Demo video and presentation

---

## Risks

- **Memory limits:** Community Cloud has resource limits. Load the embedding model only once. Fallback: Hugging Face Spaces.
- **Public link:** anyone can use the Groq quota. Add input and request limits.
- **Safety:** the app never diagnoses or prescribes, and always advises seeing a doctor.

## Related work

- Health-LLM: https://arxiv.org/abs/2402.00746
- Lightweight Clinical Decision Support System: https://arxiv.org/pdf/2505.03406
- MALADE: https://arxiv.org/pdf/2408.01869
