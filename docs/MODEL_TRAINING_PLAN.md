# Vital Check AI – Own Model Training Plan

Muhammad Abdullah Nawaz | SAP ID: 70174218 | 8 October 2026

`[x]` = done, `[~]` = in progress, `[ ]` = to do

---

## 1. Goal

Train our own skin image classifier (no external LLM/API for the vision part), benchmark it, integrate it into the Vital Check AI app, and write a research paper from the results.

The model gives "possible matches + confidence", never a diagnosis.

## 2. Model name

**DermaVC-Net** (alternatives: SkinSight-PK, VitalDerm)

Versioning: `DermaVC-Net v1.0`, `v1.1`, ...

## 3. The 3 models

| # | Model | Idea | Epochs (with early stopping) |
|---|---|---|---|
| A | Custom CNN from scratch | Baseline, no pre-training | 40–50 |
| B | MobileNetV2, frozen (feature extraction) | Pre-trained backbone, train only the head | 10–15 |
| C | EfficientNetB0, fine-tuned | Stage 1: head only. Stage 2: unfreeze top layers, low learning rate | 10 + 15 |

## 4. Data

- **HAM10000** images + `HAM10000_metadata.csv` (`lesion_id`, `dx`, `age`, `sex`, `localization`)
- CSV is used for: class counts and EDA, split by `lesion_id` (no leakage), optional multimodal model (image + age/sex/location)
- **Extra dataset** from Kaggle with common conditions (eczema, acne, psoriasis). Check the license first.
- **Phone-photo test set:** 10–20 normal photos (not dermoscopy) to show the real-world gap

## 5. Kaggle setup

1. New notebook, GPU (T4 x2 / P100), attach the dataset.
2. One notebook per experiment:
   - `01_eda`
   - `02_scratch`
   - `03_mobilenet_frozen`
   - `04_efficientnet_finetune`
   - `05_evaluation`
3. Save outputs to `/kaggle/working/`: `.keras` model, `classes.json`, metrics JSON, plots.
4. Upload the final model to Hugging Face Hub (never to Git).
5. Fixed seed. Run each model with 3 seeds, report mean ± std.

## 6. Training recipe

- Image size 224, batch size 32, Adam, cross-entropy with class weights (nv is ~67%)
- Augmentation: flip, rotation, brightness, zoom
- Callbacks: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
- Split: 80/10/10 by `lesion_id`

## 7. Benchmark (core of the paper)

| Metric | Model A | Model B | Model C |
|---|---|---|---|
| Accuracy | | | |
| Macro F1 | | | |
| Melanoma recall | | | |
| AUC | | | |
| Parameters | | | |
| Model size (MB) | | | |
| Inference time (ms/image) | | | |
| Training time | | | |
| Best epoch | | | |
| Phone-photo accuracy | | | |

Also save: confusion matrix, loss/accuracy curves, Grad-CAM examples.

## 8. Team roles

| Person | Role | Work |
|---|---|---|
| Muhammad Abdullah Nawaz | Team Lead + ML Engineer | Training pipeline, all experiments, app integration, final decisions |
| Member 2 | Data | EDA, cleaning, split, augmentation, extra dataset, phone-photo set |
| Member 3 | R&D | Literature, comparison baselines, ablations, Grad-CAM analysis |
| Member 4 | Docs + QA | Paper writing, README, model card, demo video, testing |

Real-world habits:
- One GitHub issue per task, one branch per feature
- Experiment log (CSV or Weights & Biases free tier)
- Weekly 15-minute standup
- Model card for the final model

## 9. Timeline (about 4 weeks)

| Week | Work |
|---|---|
| 1 | EDA, split by `lesion_id`, scratch baseline |
| 2 | MobileNetV2 frozen and EfficientNetB0 fine-tune |
| 3 | Evaluation, Grad-CAM, phone-photo test, choose best model |
| 4 | Integrate into Streamlit, finish paper |

## 10. Task checklist

**Data**
- [ ] Download HAM10000 + metadata CSV on Kaggle
- [ ] EDA: class counts, age/sex/location plots
- [ ] Split 80/10/10 by `lesion_id`
- [ ] Add extra common-conditions dataset
- [ ] Collect 10–20 phone photos

**Training**
- [ ] Model A: CNN from scratch
- [ ] Model B: MobileNetV2 frozen
- [ ] Model C: EfficientNetB0 fine-tune
- [ ] 3 seeds per model
- [ ] Save model + `classes.json`

**Evaluation**
- [ ] Benchmark table filled
- [ ] Confusion matrices and curves
- [ ] Melanoma recall checked
- [ ] Confidence threshold chosen
- [ ] Grad-CAM heatmaps
- [ ] Model card

**Integration**
- [ ] Upload best model to Hugging Face Hub
- [ ] Vision agent in Streamlit (top-3 + confidence + heatmap)
- [ ] Pass vision result to the LLM and output check
- [ ] Show vision step in Workflow tab and PDF

**Paper**
- [ ] Related Work (reuse Assignment 2)
- [ ] Methodology and Dataset
- [ ] Results and Discussion
- [ ] Limitations and Conclusion
- [ ] References

## 11. Research paper structure

1. Abstract
2. Introduction
3. Related Work (from Assignment 2, 20 papers)
4. Dataset
5. Methodology (3 models)
6. Experiments and Results (benchmark table)
7. Discussion (dermoscopy vs phone-photo gap, safety)
8. Limitations
9. Conclusion
10. References

## 12. Risks

| Risk | What we do |
|---|---|
| HAM10000 is dermoscopic, mostly moles | Add extra dataset, always report the phone-photo gap |
| Class imbalance (nv ~67%) | Class weights, report macro F1 and per-class recall |
| Data leakage | Split by `lesion_id` |
| Missing melanoma | Track melanoma recall separately |
| False reassurance | Confidence threshold, "unclear, please see a doctor" |
| Big model files | Hugging Face Hub, never Git |
| Kaggle session limits | Save checkpoints often, one notebook per experiment |
