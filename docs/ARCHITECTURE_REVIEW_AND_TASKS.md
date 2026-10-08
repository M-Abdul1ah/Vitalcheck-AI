# Vital Check AI – Architecture Review and Team Tasks

Muhammad Abdullah Nawaz | SAP ID: 70174218 | 8 October 2026

`[x]` = done, `[~]` = in progress, `[ ]` = to do

---

## 1. Review summary

**Verdict:** Good design for a student project. Main risks: too much scope, almost no measured results, and one architecture mismatch (vision vs knowledge base).

**Strong points**
- Layered safety: emergency gate before the LLM, rule check after
- RAG with multilingual embeddings (Urdu query finds English knowledge-base text)
- Explainability: Workflow tab, planned Grad-CAM and model card
- Honest risk list (dermoscopy vs phone-photo gap, melanoma recall)
- Good habits: one feature per commit, secret scanning, keys out of Git

## 2. Problems found

| # | Problem | Fix |
|---|---|---|
| 1 | Uncommitted files: `symptom_chain.py`, `prompts.py`, `embed_store.py`, `report_gen.py`, `tests/test_gemini.py` | Commit them first |
| 2 | Vision and text mismatch: HAM10000 is mostly moles, our knowledge base covers eczema, psoriasis, acne | Add a common-conditions dataset and map every model class to a knowledge-base entry |
| 3 | LLM or no LLM is undecided | **Decision: hybrid.** Our own CNN does the vision. The LLM only explains the result in Urdu/English |
| 4 | Too much scope | Cut A2A, voice, accounts, analytics. Move LLM judge, session memory, Roman Urdu to "later" |
| 5 | No measured results | 40-query test set, benchmark table, safety tests |
| 6 | Knowledge base is unvalidated | Note the source of every entry, get a doctor or medical student to review |
| 7 | Skin-tone bias (HAM10000 is mostly lighter skin) | Fairness test and report it |

## 3. Architecture decision

**Hybrid:** DermaVC-Net (our model) → top-3 possible matches + confidence → retriever → LLM explains in Urdu/English → output check.

The LLM never decides the vision result. Update `ROADMAP.md` and `MODEL_TRAINING_PLAN.md` to say this.

## 4. Scope change

| Do now | Later | Cut |
|---|---|---|
| Commit, test RAG in the app, 40-query test set, speed fixes (Phase 1.5), model training, deploy | LLM judge, session memory, Roman Urdu | A2A servers, voice, user accounts, analytics dashboard |

## 5. New additions (all 10)

| # | Addition | Meaning | Why |
|---|---|---|---|
| 1 | **Calibration** | Reliability curve, ECE, temperature scaling | Confidence only means something if it is calibrated. Strong paper section |
| 2 | **Out-of-distribution check** | If the photo is not skin or confidence is low, say "unclear, please see a doctor" | Avoids false reassurance |
| 3 | **Fairness test by skin tone** | Evaluate on a dataset with skin-tone labels (e.g. Fitzpatrick17k or DDI; check licenses) | Our users are in Pakistan, HAM10000 is mostly lighter skin |
| 4 | **Domain-gap experiment** | HAM10000 vs our phone photos | Main research question of the paper |
| 5 | **Two evaluation suites** | Retrieval: Recall@3 and MRR on the 40 queries. Safety: red-team prompts and gate recall on emergency phrases | Real numbers for the report |
| 6 | **Structured LLM output** | Pydantic schema: causes, self-care, when to see a doctor | Makes the output check much easier |
| 7 | **GitHub Actions CI** | Run pytest and a secret scan (gitleaks) on every push | What real teams do |
| 8 | **Export to ONNX / TFLite** | Convert the best model, report latency | Stronger benchmark table |
| 9 | **Ablations** | Class weights vs focal loss. With vs without CSV metadata (age, sex, location) | Shows we understand why the model works |
| 10 | **Experiment tracking + pinned requirements** | Weights & Biases (free tier), pinned `requirements.txt` | Reproducible results |

## 6. Team and ownership

Abdullah does all technical work. Yousaf, Izhan and Rehman do **R&D tasks only** (research, reading, collecting, writing). They do not touch the main code.

| Person | Role | Owns |
|---|---|---|
| Muhammad Abdullah Nawaz | Team Lead + ML Engineer | All code, data pipeline, training, evaluation, integration, CI, tests, README, model card, final decisions |
| Yousaf | R&D – datasets | Dataset search and license table, phone-photo collection, class-to-knowledge-base draft |
| Izhan | R&D – methods | Research notes (calibration, OOD, fairness, ablation methods), paper summaries |
| Rehman | R&D – knowledge and queries | 40-query test set, knowledge-base sources and doctor review, Related Work draft |

## 7. Task assignment

### Muhammad Abdullah Nawaz (Lead – all technical work)
- [ ] Commit the uncommitted files (one feature per commit)
- [ ] Phase 1.5 speed fixes: cache models, thinking level, Stop button
- [ ] Update `ROADMAP.md` and `MODEL_TRAINING_PLAN.md` with the hybrid decision and scope change
- [ ] `01_eda` notebook and split 80/10/10 by `lesion_id`
- [ ] Add extra dataset and class-to-knowledge-base mapping (using Yousaf's research)
- [ ] Train Model A, B, C (3 seeds each)
- [ ] Ablations (#9) and experiment tracking (#10)
- [ ] Calibration (#1), out-of-distribution check (#2), fairness test (#3), domain-gap experiment (#4)
- [ ] Retrieval and safety evaluation (#5) using Rehman's test set
- [ ] Structured LLM output (#6)
- [ ] GitHub Actions CI (#7) and pytest tests for the safety gate and output check
- [ ] ONNX/TFLite export (#8)
- [ ] Grad-CAM, integration into Streamlit (vision agent, Workflow tab, PDF)
- [ ] README, model card, demo video, paper

### Yousaf (R&D – datasets)
- [ ] Find 2–3 extra common-conditions datasets (eczema, acne, psoriasis) and fill a table: name, link, size, classes, license
- [ ] Find 2 skin-tone-labelled datasets for the fairness test (e.g. Fitzpatrick17k, DDI) and fill the same table
- [ ] Collect 10–20 phone photos of skin (get consent, no faces or identifying details) for the domain-gap test
- [ ] Draft the class-to-knowledge-base table: for each dataset class, which knowledge-base entry matches it, or "missing"

### Izhan (R&D – methods)
- [ ] 1-page notes each on: calibration (ECE, temperature scaling), out-of-distribution detection, skin-tone fairness in dermatology AI
- [ ] 1-page note on ablation ideas: class weights vs focal loss, image-only vs image + metadata
- [ ] Summarize 5 papers from Assignment 2 (papers 8–13) in 5 lines each: model, dataset, result, limitation

### Rehman (R&D – knowledge and queries)
- [ ] Write the 40-query test set (20 English + 20 Urdu), each with the expected knowledge-base entry
- [ ] Find and write a source (link or book) for every knowledge-base entry
- [ ] Ask a doctor or medical student to review the knowledge base and note their comments
- [ ] Write a draft of the Related Work section from Assignment 2

## 8. Team rules

- Everyone sends work as a markdown file in `docs/research/` (or a Google Doc link) to Abdullah
- Abdullah reviews, fixes and commits it
- Never share keys, datasets or model files in the group chat
- Weekly 15-minute standup: done, doing, blocked
- Abdullah updates the roadmap after every finished task

## 9. Timeline

| Week | Work |
|---|---|
| 1 | Commit pending files, speed fixes, EDA + split, 40-query test set, issues board |
| 2 | Model A, B, C training, extra dataset, retrieval evaluation, CI |
| 3 | Evaluation, calibration, OOD, fairness, domain-gap test, ablations, Grad-CAM |
| 4 | Integration, ONNX export, model card, paper, demo video |
