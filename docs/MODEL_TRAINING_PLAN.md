# Vital Check AI – Own Model Training Plan

Last updated: 16 November 2026

`[x]` done, `[~]` in progress, `[ ]` to do

---

## 1. Goal

Train our own skin image classifier (no external LLM/API for vision), benchmark it, integrate it into the app, and write a research paper. The model gives **possible matches + confidence**, never a diagnosis.

## 2. Model name

**DermaVC-Net** (`v1.0` = EfficientNetB0 fine-tuned, seed 7). Next versions: `v1.1`, ...

## 3. Setup (corrected)

| Item | Final |
|---|---|
| Framework | **PyTorch** (`.pt` files) |
| Platform | **Google Colab** (Kaggle dataset attach failed; not used) |
| Dataset source | HAM10000 from Harvard Dataverse, downloaded inside Colab |
| Seeds | 3 per model, report mean ± std |
| Model storage | Hugging Face Hub (`mabdullah218/dermavc-net`), never Git. The app downloads it when the local file is missing |

**Our two own models:** DermaVC-Net (photo, this document) and DermaVC-Text (symptom text, built by the team; see `ROADMAP.md`).

## 4. The 3 models

| # | Model | Idea | Status |
|---|---|---|---|
| A | Custom CNN from scratch | Baseline | [x] 3 seeds trained |
| B | MobileNetV2, frozen | Pre-trained backbone, head only | [x] 3 seeds trained |
| C | EfficientNetB0, fine-tuned | Head first, then unfreeze top layers | [x] 3 seeds trained; **seed 7 selected** |

9 runs total. Outputs: results JSONs, splits, `classes.json`, `class_weights.json`, 9 `.pt` models, `eda_overview.png`.

## 5. Data

- HAM10000 images + `HAM10000_metadata.csv` (`lesion_id`, `dx`, `age`, `sex`, `localization`)
- Split 80/10/10 **by `lesion_id`** (no leakage) [x]
- Extra common-conditions dataset (eczema, acne, psoriasis): check license first [ ]
- Phone-photo test set: 10–20 consented photos, no faces [ ]

## 6. Training recipe

Image size 224, batch 32, Adam, cross-entropy with class weights (nv ~67%), augmentation (flip, rotation, brightness, zoom), early stopping, LR scheduler, best-checkpoint saving. Temperature scaling for calibration.

## 7. Benchmark table (from the 9 result files, mean ± std over 3 seeds)

| Metric | Model A | Model B | Model C |
|---|---|---|---|
| Accuracy | 0.641 ± 0.007 | 0.563 ± 0.050 | **0.821 ± 0.009** |
| Macro F1 | 0.481 ± 0.034 | 0.416 ± 0.020 | **0.742 ± 0.014** |
| Melanoma recall (before threshold) | 0.628 ± 0.021 | 0.604 ± 0.136 | 0.652 ± 0.068 (seed 7: 0.649) |
| Melanoma recall (threshold 0.25) | not measured yet | not measured yet | not measured yet |
| AUC | 0.906 ± 0.013 | 0.898 ± 0.008 | **0.968 ± 0.001** |
| Parameters (million) | 2.36 | 2.23 | 4.02 |
| Model size (MB) | 9.5 | 9.2 | 16.4 |
| Inference time (ms/image, training environment) | 3.5 | 5.6 | 8.7 |
| Training time (min) | 19.2 | 4.0 | 12.0 |
| ECE before / after temperature scaling | n/a | n/a | 0.070 / 0.029 (seed 7) |
| Phone-photo accuracy | not measured yet | not measured yet | not measured yet |

Also save: confusion matrices, loss/accuracy curves, Grad-CAM examples. Full details are in `MODEL_CARD.md`.

## 8. Checklist (sorted)

**A. Validate**
- [ ] Confirm temperature fitted on val, seed 7 chosen by val score, not test
- [ ] Re-measure melanoma recall with the 0.25 threshold
- [x] Mean ± std table from the 9 result files
- [x] Results, splits, `classes.json`, `class_weights.json` committed to `training/`
- [ ] Notebooks 01–05 committed (still in Colab / Drive) and `requirements.txt` versions pinned
- [ ] Fill train accuracy in `fit_check.csv`, re-run Model B

**B. Real-world checks**
- [ ] Phone-photo test (domain gap)
- [x] Confidence rule (below 0.5 = unclear, please see a doctor) and melanoma warning at 0.25 in the app
- [ ] Out-of-distribution ("not skin") check
- [x] Grad-CAM heatmap in the app
- [ ] Look at 20 heatmaps: does the model look at the lesion?

**C. Integration**
- [x] `C_effnet_finetune_seed7.pt` uploaded to Hugging Face Hub (`mabdullah218/dermavc-net`)
- [x] Vision step in Streamlit (top-3 + confidence + melanoma warning + heatmap)
- [x] Workflow tab shows the photo step
- [ ] PDF report includes the photo result
- [x] Model card (`MODEL_CARD.md`)

**D. Extra research**
- [ ] Extra dataset (acne, eczema, psoriasis) and retrain as v1.1
- [ ] Fairness test by skin tone
- [ ] Ablations (class weights vs focal loss, with vs without metadata)
- [ ] ONNX/TFLite export

**E. Paper**
- [ ] Methodology and Dataset
- [ ] Results and Discussion
- [ ] Limitations and Conclusion
- [ ] References

## 9. Paper structure

1. Abstract 2. Introduction 3. Related Work (Assignment 2, 20 papers) 4. Dataset 5. Methodology (3 models) 6. Experiments and Results 7. Discussion (dermoscopy vs phone gap, fairness, safety) 8. Limitations 9. Conclusion 10. References

## 10. Team roles

| Person | Role |
|---|---|
| Abdullah | Lead + ML engineer: DermaVC-Net, app integration, evaluation, paper |
| Yousaf | DermaVC-Text: data lead, baseline models |
| Izhan | DermaVC-Text: fine-tuned model, calibration, packaging |
| Rehman | DermaVC-Text: knowledge-base sources, evaluation, model card |

Photo-model tasks that need other people: Yousaf helps collect the consented phone photos. Datasets for the fairness test are found by Yousaf.

## 11. Risks

| Risk | What we do |
|---|---|
| HAM10000 is dermoscopic, mostly moles | Extra dataset, report the phone-photo gap |
| Class imbalance | Class weights, macro F1, per-class recall |
| Data leakage | Split by `lesion_id` |
| Missing melanoma | Track melanoma recall separately, threshold |
| False reassurance | Threshold, "unclear, please see a doctor" |
| Skin-tone bias | Fairness test |
| Big model files | Hugging Face Hub, never Git |
| Colab session limits | Save checkpoints to Drive often |
