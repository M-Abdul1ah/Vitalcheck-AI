# Vital Check AI – Own Model Training Plan

Muhammad Abdullah Nawaz | SAP ID: 70174218 | 3 November 2026

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
| Model storage | Hugging Face Hub, never Git |

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

## 7. Benchmark table (fill from the 9 JSONs)

| Metric | Model A | Model B | Model C |
|---|---|---|---|
| Accuracy (mean ± std) | | | |
| Macro F1 | | | |
| Melanoma recall (before threshold) | | | 0.652 (seed 7) |
| Melanoma recall (threshold 0.25) | | | |
| AUC | | | |
| Parameters | | | |
| Model size (MB) | | | |
| Inference time (ms/image) | | | |
| Training time | | | |
| Best epoch | | | |
| ECE before / after temperature scaling | | | |
| Phone-photo accuracy | | | |

Also save: confusion matrices, loss/accuracy curves, Grad-CAM examples.

## 8. Checklist (sorted)

**A. Validate (now)**
- [ ] Confirm temperature fitted on val, seed 7 chosen by val score, not test
- [ ] Re-measure melanoma recall with the 0.25 threshold
- [ ] Mean ± std table from 9 JSONs
- [ ] Commit results to `training/`, notebooks 01–05, `requirements.txt`

**B. Real-world checks**
- [ ] Phone-photo test (domain gap)
- [ ] Confidence threshold + OOD check
- [ ] Grad-CAM heatmaps

**C. Integration**
- [ ] Upload `C_effnet_finetune_seed7.pt` + `classes.json` to Hugging Face Hub
- [ ] Vision agent in Streamlit (top-3 + confidence + heatmap)
- [ ] Workflow tab and PDF show the vision step
- [ ] Model card

**D. Extra research**
- [ ] Extra dataset and retrain
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

## 10. Team roles (R&D-only version)

| Person | Role |
|---|---|
| Abdullah | Lead + ML Engineer: all code, training, evaluation, integration |
| Yousaf | R&D datasets: dataset/license table, phone photos, class-to-KB draft |
| Izhan | R&D methods: notes on calibration, OOD, fairness, ablations; paper summaries |
| Rehman | R&D knowledge: 40-query test set, KB sources and review, Related Work draft |

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
