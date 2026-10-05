# Vital Check AI – Roadmap (Explainable)

Last updated: 5 October 2026

Vital Check AI is a bilingual (Urdu/English) dermatology symptom checker agent.
It gives general guidance only and does not replace a real doctor.

**How to read this file:** every task has a short *meaning* (what it is) and a *why* (why we do it). `[x]` = done, `[~]` = in progress / written but not tested, `[ ]` = to do.

---

## 1. Project idea and team

**Idea (one line):** Many people in Pakistan search skin problems online and get confusing or unsafe answers. Vital Check AI gives safe, simple, general guidance in Urdu and English, and always sends serious cases to a doctor.

**Why dermatology:** skin problems are common, can be described in text and photos, and a public dataset (HAM10000) exists for training our own model.

| Role | Name | Responsibility |
|---|---|---|
| Founder (idea) | [fill name] | Original idea and project direction |
| Team Lead | [fill name] | Planning, task split, final decisions, deadlines |
| Member 1 | Muhammad Abdullah Nawaz (SAP 70174218) | [fill role from GitHub] |
| Member 2 | [fill name] | [fill role from GitHub] |
| Member 3 | [fill name] | [fill role from GitHub] |

> Fill the names and roles from the GitHub repo (Settings → Collaborators, or the README team section) so this table matches the repo.

**Suggested role split (use if roles are not fixed yet):**
- AI/ML: RAG, prompts, skin model training
- Backend/Agents: `agent.py`, A2A servers, safety gate, output check
- Frontend: Streamlit app, Workflow tab, PDF report
- Docs/QA: README, test set, assignments, demo video

---

## 2. Stack and architecture

**Stack (all free tier):** Groq API (Llama 3.3), LangChain, ChromaDB, sentence-transformers, Streamlit, a2a-sdk (Agent2Agent), Streamlit Community Cloud / Hugging Face Spaces.
**Optional LLM:** Google Gemini (backup LLM / vision). Needs a personal Google account (school accounts give 403).
**Own model (planned):** MobileNetV2 skin classifier trained on HAM10000 (Google Colab, TensorFlow/Keras).

```text
User (Streamlit web page: text, photo, later voice)
   |
   v
[1] Safety gate (safety_check.py)   emergency words in Urdu/English -> urgent warning, stop
   |
   v
[2] Agent (agent.py)                asks follow-up questions if symptoms are too vague
   |
   +--> [2b] Vision agent           photo -> own trained model -> top-3 "possible matches" + confidence (+ heatmap)
   |
   v
[3] Retriever (ChromaDB)            top-3 knowledge chunks (multilingual embeddings)
   |
   v
[4] LLM (Groq, Llama 3.3)           prompt + context (+ vision result) -> answer
   |
   v
[5] Output check                    rules + LLM safety judge: no diagnosis, no medicine names, disclaimer added
   |
   v
Streaming answer + sources -> PDF report

Agents talk to each other over A2A (JSON-RPC over HTTP, Agent Card at /.well-known/agent-card.json)
```

| Step | Meaning | Idea from research papers |
|---|---|---|
| 1 – Safety gate | Stops emergencies before AI runs | MALADE (validation) |
| 2 – Agent | Asks for missing details | Health-LLM (follow-up questions) |
| 2b – Vision (own CNN) | Photo → possible matches | Dermatology CNN papers (Assignment 2, papers 8–13) |
| 3 – Retriever | Finds trusted text for the AI | RAG (all three papers) |
| 4 – LLM | Writes the answer from the context | Lightweight Clinical Decision Support (small model, free tier) |
| 5 – Output check | Blocks unsafe answers | CareGuardAI (paper 18) |
| A2A | Separate agents as services | MALADE (multi-agent) |

**Algorithms used**

| Part | Algorithm |
|---|---|
| LLM | Transformer (self-attention, next-token prediction) |
| Embeddings | Transformer encoder + mean pooling |
| Retrieval | Cosine similarity with HNSW index (ChromaDB) |
| Skin classifier | CNN: MobileNetV2, transfer learning, Adam, cross-entropy, class weights |
| Explainability | Grad-CAM heatmap |
| Safety | Rule-based keyword matching + LLM judge |
| Agent communication | A2A protocol (JSON-RPC over HTTP) |
| Optional | K-Means (unsupervised) |

**Models used**

| Model | Type | Role | Trained by us? |
|---|---|---|---|
| Llama 3.3 (via Groq) | Pre-trained LLM (Transformer) | Writes the answer from retrieved context | No (used through API) |
| Multilingual sentence-transformer | Pre-trained embedding model | Turns Urdu/English text into vectors for search | No |
| MobileNetV2 (planned) | CNN, transfer learning | Skin photo → top-3 possible matches + confidence | **Yes** (HAM10000) |
| EfficientNetB0 (planned) | CNN, transfer learning | Comparison model for the report | **Yes** |
| Gemini (optional) | Pre-trained LLM / vision | Backup LLM or photo description | No |

**Learning types in this project**
- Supervised: skin image classifier (HAM10000, labeled)
- Transfer learning: MobileNetV2 starts from ImageNet weights, we fine-tune it
- Self-supervised (pre-trained, not by us): LLM and embedding model
- Unsupervised (optional): K-Means on knowledge base chunks
- Reinforcement learning: not used

**Expert system (rule-based AI)**
- Safety gate (`safety_check.py`) and output check (`output_check.py`) are a small expert system: fixed IF-THEN rules over keyword lists (IF emergency phrase THEN stop and show warning; IF medicine name or dose THEN block answer).
- No learning happens in these parts. Rules are written by humans, so they are predictable and easy to explain.
- Why both: ML models (LLM, CNN) are flexible but can be wrong; rules give hard safety limits around them.

**Overall design:** hybrid AI = rule-based expert system (safety) + retrieval (RAG) + pre-trained LLM + our own CNN, organised as a multi-agent system (A2A).

---

## 3. Workflow (for every step)

1. Learn the concept (short).
2. Build the code.
3. Test it.
4. Commit: add specific files by name (never `git add .`), scan for secrets, commit, then push.
5. **Update this roadmap** (tick the box, change the date).

Rules:
- One feature = one commit.
- The API key lives only in `.env` (local) and Streamlit Secrets (online). Never in Git.
- **Never paste a key in chat, screenshots or code.** If it happens, delete the key and create a new one.
- Before every commit run: `git diff --cached | findstr /i "AIza AQ. gsk_ sk-"` (must print nothing).
- Order is always: stage, commit, push.
- Big model files are never committed to Git (use Hugging Face Hub or Drive).
- Model names change often: keep them in `.env` (e.g. `GEMINI_MODEL`), not in code.

---

## Phase 0 – Foundation (done)

| Done | Task | Meaning | Why |
|---|---|---|---|
| [x] | Project scaffold | Folders and starter files | Clean base for the team |
| [x] | Core symptom chain | Groq + LangChain call | First working AI answer |
| [x] | Prompt with safety rules | Instructions that stop diagnosis | Safety from day one |
| [x] | Embeddings test | Turn text into vectors | Needed for search |
| [x] | Knowledge base (`data/dermatology_kb.txt`) | Our trusted skin-care text | The AI answers from this, not from memory |
| [x] | RAG with ChromaDB | Search the KB, give matches to the AI | Fewer wrong or made-up answers |
| [x] | Multilingual embeddings | Urdu query finds English KB text | Bilingual support |
| [x] | Repo cleanup | Removed nested folder | Easier for the team |
| [x] | AI Assignment 1 | Summary of 3 research papers | Research base |
| [x] | AI Assignment 2 | Literature review, 20 papers | Research base for design choices |

## Phase 1 – Core

| Done | Task | Meaning | Why |
|---|---|---|---|
| [x] | `safety_check.py` | Detects emergency words (Urdu, Roman Urdu, English) | Emergencies must never go to the AI |
| [x] | `.gitignore` covers secrets and models | Blocks `.env`, `venv/`, `chroma_db/`, `*.keras`, datasets | Keys and big files never reach Git |
| [ ] | **Get Groq key and add to `.env`** | Create key at console.groq.com (personal account) | **Blocks everything: no key, no AI answer, A2A cannot be tested** |
| [ ] | Test RAG chain end to end | Message → retrieval → LLM → answer | First full pipeline test; then commit `prompts.py`, `symptom_chain.py` |
| [ ] | Get Gemini key (optional) | Use a personal Gmail, not the school account | School account gave 403 PERMISSION_DENIED; Gemini is only a backup LLM / vision option |
| [~] | `tests/test_gemini.py` | Small script to test the Gemini key | Written, fails with 403 until a personal key is used; not committed yet |
| [ ] | Move test files into `tests/` | Keep tests in one folder | Clean repo |
| [ ] | Test set: 20 English + 20 Urdu queries | Questions with expected results | Real numbers for the report |
| [ ] | Bigger knowledge base | Add more skin conditions, note the source of each entry | Better answers and more coverage |
| [ ] | Roman Urdu support | Test retrieval and safety gate with Urdu typed in English letters | Many Pakistani users type this way |

## Phase 2 – Agent behavior

| Done | Task | Meaning | Why |
|---|---|---|---|
| [ ] | Follow-up questions (`agent.py`) | If the symptoms are vague, the agent asks (how long? itchy? spreading?) | Better answers; makes it a real agent (Health-LLM). `agent.py` is empty right now |
| [x] | Output check (rules) | Blocks medicine names, doses, definite diagnosis | Safety after the AI |
| [ ] | LLM safety judge | A second AI agent reviews the answer before it is shown | Rules miss things; one model should not check itself alone (CareGuardAI) |
| [ ] | Prompt-injection protection | Detect messages like "ignore your rules" and refuse | Public users can try to break the app |
| [ ] | Session memory (`memory.py`) | Remember earlier messages in the chat | Natural conversation |

## Phase 3 – Frontend and live link

| Done | Task | Meaning | Why |
|---|---|---|---|
| [x] | Redesign `app.py` | Clean layout, language toggle, examples, streaming, disclaimer | Good first impression |
| [x] | Workflow tab | Shows how each answer was produced | Explainability and viva demo |
| [x] | Photo upload preparation | Clean, resize, strip metadata | Privacy and model input |
| [x] | PDF health report (`report_gen.py`) | Downloadable summary | Useful for the doctor visit |
| [ ] | Show sources in the answer | Display which KB entries were used | Users can trust and check the answer |
| [ ] | Feedback buttons (👍/👎) | Users rate each answer, saved to a log | We learn what fails; feeds the analytics dashboard |
| [ ] | Build the database on first start | Create chroma_db when the app starts | chroma_db is not in Git |
| [ ] | Read the key from Streamlit Secrets | Online key storage | Key never goes to GitHub |
| [ ] | Limit input length and requests | Max characters and requests per session | Protects the Groq free quota on a public link |
| [ ] | Deploy | Streamlit Community Cloud (backup: Hugging Face Spaces) | Live link for the portfolio. Streamlit sign-in had a GitHub error, so Spaces is the likely route |
| [ ] | Live link and screenshots in README | Show the project | Portfolio |

## Phase 4 – Own trained model (supervised learning)

**Before training**

| Done | Task | Meaning | Why |
|---|---|---|---|
| [ ] | Decide scope | Model says "possible match + confidence", never a diagnosis | Safety |
| [ ] | Download HAM10000, check class counts | 7 classes, "nv" is ~67% | Imbalance changes how we train |
| [ ] | Set success targets | Example: macro recall above 60%, melanoma recall tracked separately | Honest evaluation |

**Training (Google Colab, T4 GPU)**

| Done | Task | Meaning | Why |
|---|---|---|---|
| [ ] | Run `vitalcheck_skin_train.ipynb` | MobileNetV2, 2-stage transfer learning | Our own model |
| [ ] | Split by lesion_id (80/10/10) | Same lesion never in train and test | Avoids data leakage |
| [ ] | Train EfficientNetB0 and compare | Second model as comparison | Stronger report |
| [ ] | Save report, confusion matrix, curves | Evidence of results | For README and assignment |
| [ ] | Save `skin_model.keras` + `classes.json` to Drive | Backup the model | Needed for integration |

**Honest evaluation**

| Done | Task | Meaning | Why |
|---|---|---|---|
| [ ] | Per-class recall, especially melanoma | Check how many real cases we catch | Missing melanoma is the worst error |
| [ ] | Test on 10–20 phone photos | Normal photos, not dermoscopy | Shows the real-world gap |
| [ ] | Confidence threshold | Below it: "unclear, please see a doctor" | Avoid false reassurance |
| [ ] | Grad-CAM heatmap | Shows which part of the photo the CNN looked at | Explainable AI; checks the model is not looking at the wrong thing |
| [ ] | Model card | One page: data, metrics, limits | Professional and honest |

**Integration**

| Done | Task | Meaning | Why |
|---|---|---|---|
| [ ] | Upload model to Hugging Face Hub | Host the file outside Git | Model files are too big for Git |
| [ ] | Vision agent in Streamlit | Top-3 matches + confidence (+ heatmap) | Photo feature works |
| [ ] | Pass vision result to the LLM and output check | The answer uses the photo result safely | One connected system |
| [ ] | Show vision in Workflow tab and PDF | Full trace of the answer | Explainability |
| [ ] | Results in README and Assignment report | Metrics, confusion matrix | Portfolio proof |

**Optional**
- [ ] K-Means clustering of KB chunks (small unsupervised demo)

## Phase 5 – A2A and extra features

**A2A (Agent2Agent) integration – started 5 Oct 2026**

| Done | Task | Meaning | Why |
|---|---|---|---|
| [x] | Learn A2A basics | Agent Card + Executor + JSON-RPC server + client | Standard way for agents to talk |
| [x] | Install `a2a-sdk` (v1.2.1), `uvicorn`, `starlette` | Libraries for server and client | Needed to run agents as services |
| [~] | Symptom agent server (`src/a2a_agents/symptom_server.py`) + client (`client.py`) | Wraps `check_symptoms()` as an A2A agent on port 9101 | Written, **not tested** (needs the Groq key) |
| [ ] | Wire safety gate and output check into the A2A symptom agent | Emergency stop before the LLM, rule check after | A2A agent must be as safe as the main app |
| [ ] | Vision, recommendation and report agents as A2A servers | One server per agent | Separate, replaceable services (MALADE idea) |
| [ ] | Connect the agents in the Streamlit app | App calls agents through A2A | One connected system; show calls in the Workflow tab |

**Other extras**
- [ ] Voice input – speak the symptoms (useful for low-literacy users)
- [ ] Nearby doctor suggestions – help the user take the next step

## Phase 6 – Polish (optional)

- [ ] User accounts and history (`auth.py`) – users can see past chats
- [ ] Admin analytics dashboard (`analytics.py`) – usage and 👍/👎 results
- [ ] Demo video (2 minutes) and presentation

---

## Risks (and what we do)

| Risk | What we do |
|---|---|
| **No API key yet:** the AI cannot answer and A2A cannot be tested | Create the Groq key first (Phase 1) |
| **Key leaked** (a Gemini key was pasted in a chat on 5 Oct) | Delete and recreate it; never paste keys; scan every commit |
| **School Google account blocked for Gemini** | Use a personal Gmail; Groq stays the main LLM |
| **Memory limits:** Community Cloud is small | Load the embedding model and skin model only once; fallback: Hugging Face Spaces |
| **Public link:** anyone can use our Groq quota | Input and request limits, injection protection |
| **Safety:** wrong medical advice | Never diagnose or prescribe; safety gate, output check, LLM judge, always advise a doctor |
| **A2A agent skips safety:** a new entry point bypasses the checks | Wire the safety gate and output check into every A2A agent |
| **New SDK:** `a2a-sdk` 1.x differs from older tutorials | Follow the official docs for 1.x only |
| **Model limits:** HAM10000 is dermoscopic, 7 classes (mostly moles, not eczema or acne) | Always report that phone-photo accuracy is lower |
| **Wrong reassurance:** false "benign" result | Confidence threshold and doctor advice |

## Related work

- Health-LLM: https://arxiv.org/abs/2402.00746
- Lightweight Clinical Decision Support System: https://arxiv.org/pdf/2505.03406
- MALADE: https://arxiv.org/pdf/2408.01869
- A2A protocol docs: https://a2a-protocol.org
