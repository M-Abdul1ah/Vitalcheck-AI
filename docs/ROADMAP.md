# Vital Check AI – Roadmap

Muhammad Abdullah Nawaz | SAP ID: 70174218 | 3 November 2026

`[x]` done, `[~]` in progress, `[ ]` to do. Work top to bottom. One feature = one commit.

---

## 1. Project in one line

Bilingual (Urdu/English) dermatology guidance app. Our own model (DermaVC-Net) reads a skin photo and gives **possible matches + confidence, never a diagnosis**. Serious cases always go to a doctor.

**Team:** Abdullah (lead, all technical work). Yousaf, Izhan, Rehman (R&D only: research, collecting, writing).

## 2. Decisions (final, as of 3 Nov)

| # | Decision | Note |
|---|---|---|
| 1 | Vision = our own model, trained in **PyTorch on Google Colab** | Not Keras, not Kaggle |
| 2 | **No LLM for now** (no Groq/Gemini keys) | Old LLM work is on branch `archive/llm-prototype`. Optional layer later |
| 3 | Answer text comes from the **knowledge base (KB)**, shown with sources | Each model class must map to a KB entry |
| 4 | A2A, voice, accounts, analytics dashboard = **cut** | Mention as "explored, deferred" in the paper |
| 5 | Models and data files never go in Git | `.pt` to Hugging Face Hub |

## 3. Architecture

```text
User (Streamlit: text, photo)
  |
[1] Safety gate (rules)        emergency words EN / Urdu / Roman Urdu -> warning, stop
  |
[2] DermaVC-Net (photo)        top-3 possible matches + calibrated confidence
  |
[3] Confidence / OOD check     low confidence or not skin -> "unclear, please see a doctor"
  |
[4] Retriever (ChromaDB)       KB entry for each match (multilingual embeddings)
  |
[5] Output check (rules)       no medicine names, no doses, no definite diagnosis
  |
Answer + sources + Grad-CAM -> Workflow tab -> PDF report
```

## 4. Status snapshot

**Done:** research (Assignments 1 and 2), Streamlit UI, Workflow tab, photo prep, PDF report, safety gate, output check, RAG with multilingual embeddings, rate limits, planning docs, 9 training runs (3 models x 3 seeds).

**Pending now:** repo hygiene, validate results, HF upload, then phone-photo test and integration.

---

## 5. Action list (sorted)

### Step 1 – Fix the repo (do first, 1 day)

| | Task | Why |
|---|---|---|
| [x] | `.gitignore`: add `.vscode/`, `*.pt`, `*.onnx`, `models/` | Models are PyTorch, not `*.keras` |
| [ ] | Copy `results/`, `splits/`, `classes.json`, `class_weights.json`, `eda_overview.png` into `training/` and commit | Evidence for the paper |
| [ ] | Commit notebooks 01–05 and `requirements.txt` (pin versions) | Reproducible |
| [ ] | Replace the three docs with the new versions (this file, training plan, architecture) and commit | Docs match reality |
| [x] | Finish LLM cleanup: `config.py` crashes without `GROQ_API_KEY`; remove `symptom_chain.py`, `prompts.py`, `tests/test_chain.py` and the call near `app.py` line 255 (they stay on the archive branch) | App must run with no key |
| [x] | Remove `a2a-sdk`, `uvicorn`, `starlette` from `requirements.txt` | Smaller install |
| [ ] | Run the secret scan before every commit: `git diff --cached \| findstr /i "AIza AQ. gsk_ sk-"` | Keys never reach Git |

### Step 2 – Make the results valid (2–3 days)

| | Task | Why |
|---|---|---|
| [ ] | Confirm in the notebook: temperature fitted on **val**, seed 7 picked by **val** score (not test) | No test leakage |
| [ ] | Re-measure melanoma recall with the 0.25 threshold (0.652 is before the threshold) | Honest safety number |
| [ ] | Build the mean ± std table from the 9 result JSONs | Core of the paper |
| [ ] | Upload `C_effnet_finetune_seed7.pt` + `classes.json` to Hugging Face Hub | Needed by the app |

### Step 3 – Real-world test and safety of the model (1 week)

| | Task | Owner |
|---|---|---|
| [ ] | Phone-photo test (10–20 consented photos, no faces) = domain-gap result | Abdullah (photos: Yousaf) |
| [ ] | Confidence threshold + OOD ("not skin / unclear") | Abdullah |
| [ ] | Grad-CAM heatmaps, check the model looks at the lesion | Abdullah |
| [ ] | Class-to-KB mapping table (every class has a KB entry or "missing") | Yousaf drafts, Abdullah checks |

### Step 4 – App integration (1 week)

| | Task |
|---|---|
| [ ] | Vision agent in Streamlit: top-3 + confidence + heatmap |
| [ ] | Show the KB text and **sources** for each match |
| [ ] | Safety gate and output check applied to the new flow |
| [ ] | Workflow tab and PDF show the vision step |
| [ ] | Show "photo analysis" only when the model is loaded (load it once, cache it) |

### Step 5 – Tests and numbers (parallel with Step 4)

| | Task | Owner |
|---|---|---|
| [ ] | 40-query test set (20 English + 20 Urdu) with expected KB entry | Rehman |
| [ ] | Retrieval evaluation: Recall@3, MRR | Abdullah |
| [ ] | Red-flag phrase file (EN / Urdu / Roman Urdu); assert gate recall = 100% | Rehman writes, Abdullah tests |
| [x] | Add missing red flags: stiff neck with rash, skin turning black, blistering all over, Roman Urdu breathing/bleeding phrases | Abdullah |
| [x] | pytest for safety gate and output check; GitHub Actions CI (pytest + gitleaks) in `.github/workflows/ci.yml` (confirm it runs green on GitHub) | Abdullah |
| [ ] | KB: 25–30 conditions, source for every entry, `sources.md`, doctor/student review | Rehman |

### Step 6 – Deploy and show (week 4)

| | Task |
|---|---|
| [x] | Fix README: Built / In progress / Planned (remove features that do not exist), Windows setup lines, Python 3.10+ |
| [ ] | Deploy (Hugging Face Spaces; Streamlit Cloud had a sign-in error) |
| [ ] | Live link + screenshots in README |
| [ ] | Model card, demo video (2 min) |

### Step 7 – Extra research (only after Steps 1–5)

| | Task | Owner |
|---|---|---|
| [ ] | Extra common-conditions dataset (eczema, acne, psoriasis); check license | Yousaf finds, Abdullah trains |
| [ ] | Fairness test on skin tone (Fitzpatrick17k / DDI) | Yousaf finds, Abdullah runs |
| [ ] | Ablations: class weights vs focal loss, image vs image + metadata | Izhan notes, Abdullah runs |
| [ ] | ONNX/TFLite export + latency | Abdullah |
| [ ] | Weights & Biases tracking | Abdullah |

### Step 8 – Paper

Abstract, Introduction, Related Work (from Assignment 2), Dataset, Methodology (3 models), Results (benchmark + calibration + domain gap), Discussion (dermoscopy vs phone, fairness, safety), Limitations, Conclusion, References.

| | Task | Owner |
|---|---|---|
| [ ] | Related Work draft | Rehman |
| [ ] | Notes: calibration, OOD, fairness, ablations | Izhan |
| [ ] | Rest of the paper | Abdullah |

---

## 6. Later (only if time) / Cut

**Later:** LLM explanation layer (structured output, safety judge), one follow-up-question agent, session memory, Roman Urdu retrieval tests, Hugging Face / Cloud polish.
**Cut:** A2A servers, voice input, user accounts, analytics dashboard, nearby doctors.

## 7. Risks

| Risk | What we do |
|---|---|
| HAM10000 is dermoscopic and mostly moles | Extra dataset, always report the phone-photo gap |
| Class imbalance (nv ~67%) | Class weights, macro F1, per-class recall |
| Missing melanoma | Track melanoma recall separately, threshold |
| False reassurance | Confidence threshold, "unclear, please see a doctor" |
| Skin-tone bias | Fairness test, report it |
| KB unvalidated | Sources + doctor review |
| Gate misses Roman Urdu | Test file, recall = 100% |
| Docs promise features that do not exist | README rewrite (Step 6) |
| Big files in Git | `.gitignore`, Hugging Face Hub |

## 8. Team rules

- One GitHub issue per task, one branch per feature (`feature/<name>`).
- R&D members send work as `.md` in `docs/research/` (or a Google Doc link) to Abdullah. Abdullah reviews and commits.
- Never share keys, datasets or model files in chat.
- Weekly 15-minute standup: done, doing, blocked.
- Update this roadmap after every finished task.

## 9. Related work

- Health-LLM: https://arxiv.org/abs/2402.00746
- Lightweight Clinical Decision Support System: https://arxiv.org/pdf/2505.03406
- MALADE: https://arxiv.org/pdf/2408.01869
