# \# Vital Check AI – Roadmap

# 

# Last updated: 24 September 2026

# 

# Vital Check AI is a bilingual (Urdu/English) dermatology symptom checker agent.

# It gives general guidance only and does not replace a real doctor.

# 

# \*\*Stack (all free tier):\*\* Groq API (Llama 3.3), LangChain, ChromaDB, sentence-transformers, Streamlit, Streamlit Community Cloud (backup: Hugging Face Spaces).

# 

# \---

# 

# \## Architecture

# 

# ```text

# User (Streamlit: text + optional photo)

# &#x20;  |

# &#x20;  v

# \[1] Safety gate (safety\_check.py)     emergency words in Urdu/English -> urgent warning, stop

# &#x20;  |

# &#x20;  v

# \[2] Photo prep (vision\_agent.py)      resize, strip metadata

# &#x20;  |

# &#x20;  v

# \[3] Retriever (ChromaDB)              top-3 knowledge chunks (multilingual embeddings)

# &#x20;  |

# &#x20;  v

# \[4] Agents (A2A)                      symptom agent + vision agent + recommendation agent

# &#x20;  |                                  each does one task and passes its result on

# &#x20;  v

# \[5] Output check (output\_check.py)    no diagnosis, no medicine names, doctor advice added

# &#x20;  |

# &#x20;  v

# \[6] Resolution agent (A2A)            combines all results into one final outcome

# &#x20;  |

# &#x20;  v

# Streaming answer + Workflow tab -> PDF report

# ```

# 

# \*\*Resolution outcomes:\*\* ANSWERED\_FROM\_KB, ESCALATED\_EMERGENCY, KB\_ONLY\_FALLBACK, KB\_UNAVAILABLE, AI\_ERROR.

# 

# \### Agents

# 

# | Agent | Job | Model |

# |---|---|---|

# | Symptom agent | Possible causes from text + retrieved context | Llama 3.3 (Groq) |

# | Vision agent | Describe the skin photo in plain language | (vision model – fill in) |

# | Recommendation agent | Self-care tip + when to see a doctor | (model – fill in) |

# | Resolution agent | Merge agent outputs, apply safety result, pick final outcome | rules + A2A messages |

# 

# | Step | Idea from research papers |

# |---|---|

# | 3 – Retriever | RAG (all three papers) |

# | 4 – Agents | Follow-up questions (Health-LLM), task split (MALADE) |

# | 1, 5, 6 – Checks + resolution | MALADE, CareGuardAI |

# | Small model + free tier | Lightweight Clinical Decision Support System |

# 

# \---

# 

# \## Workflow (for every step)

# 

# 1\. Learn the concept (short).

# 2\. Build the code.

# 3\. Test it.

# 4\. Commit: add specific files by name (never `git add .`), commit, then `git pull --rebase --autostash`, then push.

# 5\. Tick the checkbox below.

# 

# Rules:

# \- One feature = one commit.

# \- The API key lives only in `.env` (local) and Streamlit Secrets (online). Never in Git.

# \- Order is always: stage, commit, pull, push.

# 

# \---

# 

# \## Phase 0 – Foundation (done)

# 

# \- \[x] Project scaffold and structure

# \- \[x] Core symptom chain (Groq + LangChain)

# \- \[x] Prompt with safety rules

# \- \[x] Embeddings test

# \- \[x] Dermatology knowledge base (`data/dermatology\_kb.txt`)

# \- \[x] RAG retrieval with ChromaDB (`embed\_store.py`, `retriever.py`)

# \- \[x] Multilingual embeddings for Urdu

# \- \[x] Repo cleanup

# \- \[x] AI Assignment 1 (research paper summary)

# \- \[x] AI Assignment 2 (literature review, 20 papers)

# 

# \## Phase 1 – Core

# 

# \- \[x] `safety\_check.py`: emergency word detector (Urdu + English)

# \- \[x] Move test files into `tests/`

# \- \[ ] Add Groq key to `.env`

# \- \[ ] Test RAG-connected chain (`prompts.py`, `symptom\_chain.py`) and commit

# 

# \## Phase 2 – Agent behavior

# 

# \- \[x] Output check (no diagnosis, no medicine names)

# \- \[x] Workflow tab (live trace of every agent and the final resolution)

# \- \[ ] Multi-agent flow with A2A messages between agents

# \- \[ ] Resolution agent (final outcome from all agent results)

# \- \[ ] Follow-up questions in `agent.py`

# \- \[ ] Session memory (`memory.py`)

# 

# \## Phase 3 – Frontend and live link

# 

# \- \[x] Redesign `app.py` (layout, language toggle, example buttons, streaming, disclaimer)

# \- \[x] Build the database on first start

# \- \[x] Limit input length and requests per session (`limits.py`)

# \- \[ ] Read the key from Streamlit Secrets

# \- \[ ] Deploy (Streamlit Community Cloud, backup Hugging Face Spaces)

# \- \[ ] Add live link and screenshots to README

# 

# \## Phase 4 – Extra features

# 

# \- \[x] PDF health report (`report\_gen.py`)

# \- \[x] Photo upload and preparation

# \- \[ ] Skin photo analysis (vision agent connected, HAM10000 for testing)

# \- \[ ] Voice input

# \- \[ ] Nearby doctor suggestions

# \- \[ ] A2A agent integration (agent cards + message passing)

# \- \[ ] Offline mode (Ollama local model, parked)

# 

# \## Phase 5 – Polish (optional)

# 

# \- \[ ] User accounts and history (`auth.py`)

# \- \[ ] Admin analytics dashboard (`analytics.py`)

# \- \[ ] Demo video and presentation

# 

# \---

# 

# \## Risks

# 

# \- \*\*Memory limits:\*\* Community Cloud has resource limits. Load the embedding model only once. Fallback: Hugging Face Spaces.

# \- \*\*Public link:\*\* anyone can use the Groq quota. Input and request limits are in place; the limit is per browser session.

# \- \*\*Safety:\*\* the app never diagnoses or prescribes, and always advises seeing a doctor.

# \- \*\*Multi-agent latency:\*\* more agents means slower answers and more API calls. Keep each agent small and time every step.

# \- \*\*Agent disagreement:\*\* if agents give conflicting results, the resolution agent must fall back to the safer outcome.

# \- \*\*Urdu quality:\*\* in-house keyword lists and knowledge base are not clinically validated.

# 

# \## Related work

# 

# \- Health-LLM: https://arxiv.org/abs/2402.00746

# \- Lightweight Clinical Decision Support System: https://arxiv.org/pdf/2505.03406

# \- MALADE: https://arxiv.org/pdf/2408.01869

