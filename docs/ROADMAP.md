# Vital Check AI – Roadmap

Last updated: 10 November 2026

`[x]` done, `[~]` in progress, `[ ]` to do. Work top to bottom. One feature = one commit, on a branch, merged by pull request.

---

## 1. Project in one line

Bilingual (Urdu/English) dermatology guidance app. Our own models read a skin photo (DermaVC-Net) and a symptom message (DermaVC-Text) and give **possible matches + confidence, never a diagnosis**. An LLM explains the result in the user's language. Serious cases always go to a doctor.

**Team:** Abdullah (lead: architecture, integration, evaluation). Yousaf, Izhan, Rehman (build and train DermaVC-Text, see `DermaVC-Text` proposal).

## 2. Decisions (as of 10 Nov)

| # | Decision | Note |
|---|---|---|
| 1 | Vision = our own model, trained in **PyTorch on Google Colab** | Not Keras, not Kaggle |
| 2 | **Own models: DermaVC-Net (photo) and DermaVC-Text (text)** | The course project needs at least 2 trained models |
| 3 | **LLM returns as a writer, not the brain** (changed on 4 Nov) | Roles: explain, one follow-up question, safety judge. Providers: Gemini (cloud) + Ollama (local). Our models decide, the LLM explains |
| 4 | Answer text comes from the knowledge base, shown with sources | Every model class maps to a knowledge-base entry |
| 5 | A2A, voice, accounts, analytics dashboard = **cut** | Mention as "explored, deferred" in the paper |
| 6 | Models and data files never go in Git | `.pt` to Hugging Face Hub |
| 7 | Deployment: Hugging Face Spaces for now. **Vercel is parked** | Vercel cannot run Streamlit or torch. Would need a frontend + API split |

## 3. Architecture

```text
User (Streamlit: text, photo)
  |
[1] Input guard + emergency gate (rules)   red flags EN / Urdu / Roman Urdu -> warning, stop
  |
[2] Small-talk / vague check (rules)       friendly reply or "tell me more"
  |
[3] DermaVC-Net (photo)                    top-3 matches + calibrated confidence + Grad-CAM
  |   DermaVC-Text (message)               condition + confidence (planned)
  |
[4] Confidence rules                       low confidence -> "unclear, please see a doctor"
  |
[5] Retriever (ChromaDB)                   knowledge-base entries + relevance cutoff
  |
[6] LLM explainer (Gemini -> Ollama -> KB text)   answers only from retrieved text (planned)
  |
[7] Output check (rules) + LLM safety judge       no medicine, no dose, no diagnosis
  |
Answer + sources + photo card -> Workflow tab -> PDF report
```

## 4. Status snapshot

**Done and on `main`:** research (Assignments 1 and 2), Streamlit UI, Workflow tab, photo prep, PDF report, safety gate with pattern rules, greeting handler, vague-message guard, relevance cutoff, output check, RAG with multilingual embeddings, rate limits, CI, 9 DermaVC-Net training runs with results, tests and docs.

**Built, waiting for merge:** DermaVC-Net photo analysis in the app (branch `feature/photo-analysis`), model card.

**Written, not merged:** LLM explainer (Gemini, with internet check and fallback), tested with mocked calls only.

**Next:** merge photo analysis, merge the LLM explainer, hand-over of DermaVC-Text from the team, pipeline refactor, evaluation.

---

## 5. Action list

### Step 1 – Repo and results (finish first)

| | Task |
|---|---|
| [x] | `.gitignore`: `.vscode/`, `*.pt`, `*.onnx`, `models/` |
| [x] | `training/`: results, splits, `classes.json`, `class_weights.json`, `eda_overview.png` committed |
| [x] | LLM cleanup of `main`, A2A removed, README honest (Built / In progress / Planned) |
| [ ] | Commit notebooks 01–05 and pin `requirements.txt` versions (notebooks are still in Colab/Drive) |
| [ ] | Run the secret scan before every commit: `git diff --cached \| findstr /i "AIza AQ. gsk_ sk-"` |

### Step 2 – Make the results valid

| | Task | Why |
|---|---|---|
| [ ] | Confirm in the notebook: temperature fitted on **val**, seed 7 chosen by **val** score | No test leakage |
| [ ] | Re-measure melanoma recall with the 0.25 rule (0.652 is plain top-1) | Honest safety number |
| [x] | Mean ± std benchmark table from the 9 runs (`training/results/benchmark_mean_std.csv`) | Core of the paper |
| [ ] | Add train accuracy to `fit_check.csv`, re-run Model B | "GOOD FIT" must be backed by data |
| [ ] | Upload `C_effnet_finetune_seed7.pt` to Hugging Face Hub and add a download fallback in the app | The model is on one laptop only today |
| [x] | Model card (`docs/MODEL_CARD.md`) | Honest data, metrics and limits |

### Step 3 – Real-world test of the model

| | Task | Owner |
|---|---|---|
| [ ] | Phone-photo test (10–20 consented photos, no faces) = domain-gap result | Abdullah (photos: Yousaf) |
| [ ] | Not-skin / out-of-distribution check on top of the confidence rule | Abdullah |
| [x] | Grad-CAM heatmap in the app | Abdullah |
| [ ] | Look at 20 heatmaps: does the model look at the lesion? | Abdullah |
| [ ] | Skin-tone fairness test (Fitzpatrick17k / DDI, check license) | Abdullah, datasets found by Yousaf |

### Step 4 – App integration

| | Task |
|---|---|
| [x] | Photo analysis in Streamlit: top-3 + confidence + melanoma warning + heatmap (needs PR merge) |
| [x] | Workflow tab shows the photo step |
| [ ] | PDF report includes the photo result |
| [ ] | Show knowledge-base **sources** for every answer |
| [ ] | Merge the LLM explainer (Gemini) with the internet check and fallback |
| [ ] | Add Ollama as the second provider (`LLM_ORDER=gemini,ollama`) |
| [ ] | Structured output, one follow-up question, LLM safety judge (see `LLM_DESIGN.md`) |
| [ ] | Extract the pipeline into `src/pipeline.py` (one function, plain data out) |

### Step 5 – DermaVC-Text (team)

| | Task | Owner |
|---|---|---|
| [~] | Proposal document v2 written and handed to the team | Abdullah |
| [ ] | Freeze the 28-label list | Abdullah |
| [ ] | Training rows (about 100 per label, 3 languages) and human test rows (about 184) | Yousaf, Izhan, Rehman |
| [ ] | Knowledge-base entries with sources for the 15 new conditions | Rehman |
| [ ] | Models A (TF-IDF), B (frozen MiniLM), C (fine-tuned MiniLM), 3 seeds, calibration, threshold | Yousaf, Izhan |
| [ ] | Evaluation vs the old nearest-text search, model card, hand-over package | Rehman, Izhan |
| [ ] | Integrate `predict()` into the app and combine with DermaVC-Net | Abdullah |

### Step 6 – Tests and numbers (parallel)

| | Task | Owner |
|---|---|---|
| [x] | Gate probes for chest pain, face swelling, black skin, fever + rash, Roman Urdu; pattern rule for wording variants | Abdullah |
| [x] | pytest suite (100+ tests) and CI | Abdullah |
| [ ] | 40-query test set (20 English + 20 Urdu) | Rehman |
| [ ] | Evaluation script `scripts/run_eval.py`: retrieval Recall@3 and MRR, gate recall, output-check red team | Abdullah |
| [ ] | Baseline test: old "first sentence" answers vs LLM explainer on the same 40 queries | Abdullah |
| [ ] | Knowledge base: 25–30 conditions, source for every entry, doctor or student review | Rehman |

### Step 7 – Deploy and show

| | Task |
|---|---|
| [ ] | Deploy on Hugging Face Spaces (model files from Hugging Face Hub, Gemini key in secrets) |
| [ ] | Live link and screenshots in README |
| [ ] | Demo video (2 min) |
| [ ] | Later, only if time: Vercel frontend + API backend |

### Step 8 – Extra research (only after Steps 1–6)

| | Task |
|---|---|
| [ ] | Extra common-conditions image dataset (acne, eczema, psoriasis), retrain as DermaVC-Net v1.1 |
| [ ] | Ablations: class weights vs focal loss, image vs image + metadata |
| [ ] | ONNX/TFLite export and latency |

### Step 9 – Paper and assignments

Abstract, Introduction, Related Work (Assignment 2), Dataset, Methodology (both models), Results (benchmark, calibration, domain gap, DermaVC-Text vs old search), Discussion (dermoscopy vs phone, fairness, safety), Limitations, Conclusion, References.

| | Task |
|---|---|
| [ ] | AI Assignment 3: fine-tuning DermaVC-Net (EfficientNet-B0) |
| [ ] | Paper draft |

---

## 6. Later (only if time) / Cut

**Later:** session memory, Roman Urdu retrieval tests, Vercel frontend.
**Cut:** A2A servers, voice input, user accounts, analytics dashboard, nearby doctors.

## 7. Risks

| Risk | What we do |
|---|---|
| HAM10000 is dermoscopic and mostly moles | Extra dataset, always report the phone-photo gap |
| Class imbalance (nv 67%) | Class weights, macro F1, per-class recall |
| Missing melanoma (recall about 65%) | Track separately, 0.25 warning rule, top-3 shown, always advise a doctor |
| False reassurance | Confidence threshold, "unclear, please see a doctor" |
| Photo of a rash or acne gets a mole answer | Low-confidence rule now, out-of-distribution check next, note shown every time |
| Skin-tone bias | Fairness test, report it |
| Model file only on one laptop | Upload to Hugging Face Hub, download fallback |
| LLM hallucination | Answer only from retrieved text, output check, LLM judge, sources shown |
| Free-tier limits (Gemini) | Input and rate limits, fallback to Ollama and then knowledge-base text |
| Synthetic training data for DermaVC-Text | Human-written test set, different authors for train and test, report the limit |
| Gate misses wording variants | Pattern rules, red-flag test file, recall must be 100% |
| Vercel cannot host the current app | Hugging Face Spaces first; Vercel only with a frontend + API split |
