# Vital Check AI – Architecture Review and Team Tasks

Last updated: 16 November 2026

`[x]` done, `[~]` in progress, `[ ]` to do

---

## 1. Review summary

**Verdict:** good design for a student project. Strong points: layered rule-based safety, multilingual RAG, Workflow tab, honest risk list, good Git habits.
**Main risks:** README promises more than the repo has, few measured results, vision model vs knowledge base mismatch.

## 2. Problems and fixes

| # | Problem | Fix | Status |
|---|---|---|---|
| 1 | README listed voice, accounts, analytics, A2A, nearby doctors that are not on `main` | Rewrite as Built / In progress / Planned | [x] |
| 2 | LLM code on `main` (`config.py` crashed without a key) | Removed; kept on `archive/llm-prototype`. The LLM comes back as a separate, optional layer | [x] |
| 3 | HAM10000 is mostly moles, KB covers eczema, psoriasis, acne | Second own model for text (DermaVC-Text) + class-to-KB mapping + extra image dataset later | [~] |
| 4 | Few measured results | Safety suite with numbers [x]. 40-query test set and retrieval evaluation [ ] | [~] |
| 5 | KB is small (9 conditions) and unsourced | 25–30 entries, source for each, doctor review (Rehman) | [ ] |
| 6 | Emergency gate missed Roman Urdu and natural wording (recall was 10% on 39 natural messages) | Pattern rules per emergency type. Now 39 of 39, 0 false alarms on 58 normal messages. This is a dev set: an independent set written by a teammate is still needed | [x] |
| 7 | Skin-tone bias | Fairness test | [ ] |
| 8 | Docs out of date | README, roadmap, model card, this file and the training plan updated | [x] |
| 9 | An LLM answer must not be shown before the output check | Design rule: buffer the answer, check it, then show it | Design |
| 10 | Photo model failed silently when torch or the file was missing | Clear message in the app, download from Hugging Face Hub, `check_skin_model.py` | [x] |
| 11 | Output check missed Pakistani brand names and "you have eczema" wording (57% of unsafe test answers blocked) | Brand-name list, prescribing and diagnosis patterns. Now 30 of 30 | [x] |

## 3. Architecture decision (updated 4 Nov, replaces "no LLM for now")

**Hybrid.** Our own models decide; an LLM only explains.
- **DermaVC-Net** (photo) gives top-3 matches with calibrated confidence. A confidence rule and a melanoma warning decide what is shown.
- **DermaVC-Text** (symptom text, in progress) gives the likely condition with confidence and asks a follow-up question when it is unsure.
- The retriever shows the matching knowledge-base entries with their source.
- An **LLM explainer** (Gemini first, Ollama as local backup, knowledge-base text as the last fallback) writes the answer from the retrieved text only, asks one follow-up question, and a second model acts as a safety judge. Details in `LLM_DESIGN.md`.
- Rule-based emergency gate before everything and rule-based output check after everything. The LLM never decides the vision result or the emergency gate.

## 4. Scope

| Do now | Later | Cut |
|---|---|---|
| Hand-over of DermaVC-Text, LLM explainer, pipeline refactor, evaluation script, phone-photo test, KB sources, 40-query test set, deployment | Follow-up agent and safety judge (after the explainer), session memory, Roman Urdu retrieval tests, Vercel frontend | A2A servers, voice, accounts, analytics, nearby doctors |

## 5. The 10 additions (status)

| # | Addition | Status |
|---|---|---|
| 1 | Calibration (reliability curve, ECE, temperature scaling) | [~] temperature fitted, ECE 0.070 to 0.029; confirm it was fitted on val |
| 2 | Out-of-distribution check | [ ] |
| 3 | Fairness test by skin tone | [ ] |
| 4 | Domain-gap experiment (HAM10000 vs phone photos) | [ ] |
| 5 | Two evaluation suites (retrieval Recall@3/MRR, safety) | [~] safety suite done; retrieval needs the 40 queries |
| 6 | Structured LLM output (Pydantic) | [ ] with the LLM explainer |
| 7 | GitHub Actions CI | [~] runs pytest on every push; secret scan (gitleaks) still to add |
| 8 | ONNX/TFLite export | [ ] |
| 9 | Ablations | [ ] |
| 10 | Experiment tracking + pinned requirements | [ ] |

## 6. Team and tasks

Abdullah does the integration and evaluation. Yousaf, Izhan and Rehman build and train DermaVC-Text and hand over a finished model (see the DermaVC-Text proposal).

### Abdullah (Lead)
- [x] Repo fixes, photo analysis in the app, model hosting on Hugging Face Hub, safety suite, model card
- [ ] Merge the LLM explainer, add Ollama, follow-up question, safety judge
- [ ] Pipeline refactor (`src/pipeline.py`) and evaluation script
- [ ] Phone-photo test, out-of-distribution check, 20 heatmap checks, fairness test
- [ ] Validate results (val-fitted temperature, melanoma recall at 0.25)
- [ ] Integrate DermaVC-Text, deploy, paper, demo video

### Yousaf (DermaVC-Text: data and models A and B)
- [ ] Training rows for 12 conditions, test rows for the other 12, clean splits
- [ ] Notebooks for the TF-IDF baseline and frozen embeddings, 3 seeds
- [ ] Consented phone photos for the domain-gap test, skin-tone datasets with licenses

### Izhan (DermaVC-Text: model C)
- [ ] Training rows for 12 conditions and the 4 other labels, test rows for 12 conditions
- [ ] Fine-tuned model, calibration, confidence threshold, `predict()` package
- [ ] One-page notes on calibration, out-of-distribution detection, fairness

### Rehman (DermaVC-Text: knowledge and evaluation)
- [ ] Knowledge-base entries with sources for the 15 new conditions
- [ ] Human test rows for the 4 other labels, review of 10% of training rows
- [ ] Evaluation notebook, model card, 40-query test set, a fresh independent list of 30 red-flag messages for the safety gate

## 7. Team rules

- Share files in one Google Drive folder (or a Google Doc link). Abdullah reviews and commits.
- One issue per task, one branch per feature, pull request into `main`.
- Never share keys, datasets or model files in chat.
- Check-in twice a week: done, doing, blocked.
- Roadmap updated after every finished task.

## 8. Timeline

| Week | Work |
|---|---|
| 1 | Data writing for DermaVC-Text, knowledge-base sources, LLM explainer merged |
| 2 | Team trains DermaVC-Text. Abdullah: pipeline refactor, evaluation script, phone-photo test |
| 3 | Hand-over and integration, evaluation numbers, paper, demo video, deployment |
