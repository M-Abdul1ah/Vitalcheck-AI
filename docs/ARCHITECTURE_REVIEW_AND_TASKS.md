# Vital Check AI – Architecture Review and Team Tasks

Muhammad Abdullah Nawaz | SAP ID: 70174218 | 3 November 2026

`[x]` done, `[~]` in progress, `[ ]` to do

---

## 1. Review summary

**Verdict:** good design for a student project. Strong points: layered rule-based safety, multilingual RAG, Workflow tab, honest risk list, good Git habits.
**Main risks:** README promises more than the repo has, few measured results, vision model vs knowledge base mismatch.

## 2. Problems and fixes

| # | Problem | Fix | Status |
|---|---|---|---|
| 1 | README lists voice, accounts, analytics, A2A, nearby doctors that are not on `main` | Rewrite as Built / In progress / Planned | [x] |
| 2 | LLM code still on `main` (`config.py` crashes without a key, `symptom_chain.py`, `prompts.py`, `tests/test_chain.py`) | Remove; it stays on `archive/llm-prototype` | [x] |
| 3 | HAM10000 is mostly moles, KB covers eczema, psoriasis, acne | Extra dataset + class-to-KB mapping | [ ] |
| 4 | Few measured results | 40-query test set, benchmark table, gate recall | [ ] |
| 5 | KB is small (9 conditions) and unsourced | 25–30 entries, source for each, doctor review | [ ] |
| 6 | Emergency gate misses Roman Urdu and some red flags | Red-flag test file, recall = 100% | [x] |
| 7 | Skin-tone bias | Fairness test | [ ] |
| 8 | Docs out of date (Keras, Kaggle, hybrid-with-LLM) | Replaced by the 3 new docs | [x] |
| 9 | Streaming shows an answer before the output check can block it | Only matters if an LLM layer returns. Then: buffer first, check, then show | Later |
| 10 | LLM provider default (gemini) differs from docs (Groq) | Only matters if an LLM layer returns | Later |

## 3. Architecture decision (replaces "hybrid")

**No LLM for now.** DermaVC-Net gives top-3 matches + calibrated confidence. A threshold/OOD check decides if the result is shown. The retriever then shows the matching KB entry with its source. The output check runs on the final text.

An LLM explanation layer is optional later (structured output, safety judge). The LLM would never decide the vision result.

## 4. Scope

| Do now | Later | Cut |
|---|---|---|
| Repo fixes, validate results, HF upload, phone-photo test, OOD, Grad-CAM, vision agent, test sets, CI, KB sources, deploy | LLM layer, follow-up-question agent, session memory, Roman Urdu retrieval tests | A2A servers, voice, accounts, analytics, nearby doctors |

## 5. The 10 additions (status)

| # | Addition | Status |
|---|---|---|
| 1 | Calibration (reliability curve, ECE, temperature scaling) | [~] temperature fitted; confirm on val, report ECE |
| 2 | Out-of-distribution check | [ ] |
| 3 | Fairness test by skin tone | [ ] |
| 4 | Domain-gap experiment (HAM10000 vs phone photos) | [ ] |
| 5 | Two evaluation suites (retrieval Recall@3/MRR, safety gate recall) | [ ] |
| 6 | Structured LLM output (Pydantic) | Later, only with LLM |
| 7 | GitHub Actions CI (pytest + gitleaks) | [ ] |
| 8 | ONNX/TFLite export | [ ] |
| 9 | Ablations | [ ] |
| 10 | Experiment tracking + pinned requirements | [ ] |

## 6. Team and tasks

Abdullah does all technical work. The other three do **R&D only**.

### Abdullah (Lead)
- [ ] Repo fixes: `.gitignore`, `training/` outputs, notebooks, requirements, LLM cleanup, README
- [ ] Validate results (val-fitted temperature, melanoma recall at 0.25, mean ± std)
- [ ] Hugging Face upload, vision agent, Workflow tab, PDF
- [ ] Phone-photo test, threshold/OOD, Grad-CAM
- [ ] Retrieval + safety evaluation, pytest, CI
- [ ] Extra dataset training, fairness, ablations, ONNX
- [ ] Model card, demo video, paper

### Yousaf (R&D – datasets)
- [ ] 2–3 extra common-conditions datasets: name, link, size, classes, license
- [ ] 2 skin-tone-labelled datasets (Fitzpatrick17k, DDI), same table
- [ ] 10–20 consented phone photos (no faces or identifying details)
- [ ] Draft class-to-KB table (each class matches a KB entry or "missing")

### Izhan (R&D – methods)
- [ ] 1-page notes: calibration, OOD detection, skin-tone fairness
- [ ] 1-page note: ablation ideas
- [ ] Summarize papers 8–13 of Assignment 2 (model, dataset, result, limitation)

### Rehman (R&D – knowledge and queries)
- [ ] 40-query test set (20 English + 20 Urdu) with expected KB entry
- [ ] Red-flag phrase list (English, Urdu, Roman Urdu) for the gate test
- [ ] Source for every KB entry, `sources.md`, doctor/student review
- [ ] Related Work draft from Assignment 2

## 7. Team rules

- Work comes as `.md` in `docs/research/` (or a Google Doc link) to Abdullah. He reviews and commits.
- One issue per task, one branch per feature.
- Never share keys, datasets or model files in chat.
- Weekly 15-minute standup: done, doing, blocked.
- Roadmap updated after every finished task.

## 8. Timeline (4 weeks)

| Week | Work |
|---|---|
| 1 | Repo fixes, validate results, HF upload, 40-query set, KB sources started |
| 2 | Phone-photo test, threshold/OOD, Grad-CAM, red-flag tests, CI |
| 3 | Vision agent in app, retrieval evaluation, extra dataset, fairness |
| 4 | README, deploy, model card, paper, demo video |
