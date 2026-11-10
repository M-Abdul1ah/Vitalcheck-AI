# DermaVC-Net v1.0 – Model Card

Last updated: 10 November 2026

---

## 1. Summary

DermaVC-Net is our own skin-photo model for Vital Check AI. It reads one photo of a skin lesion and returns the **top 3 possible matches with calibrated probabilities**. It never gives a diagnosis. It knows 7 lesion types, mostly moles, because it was trained on HAM10000 (dermoscopy images).

## 2. Model details

| Item | Value |
|---|---|
| Name and version | DermaVC-Net v1.0 (deployed file: `C_effnet_finetune_seed7.pt`) |
| Architecture | EfficientNet-B0 (torchvision), ImageNet pre-trained, fine-tuned in 2 stages, 7-class output |
| Framework | PyTorch, trained on Google Colab |
| Parameters / file size | 4.02 million / 16.4 MB |
| Input | One RGB photo, resized to 224 x 224, ImageNet mean and standard deviation (confirm against the training notebook; `scripts/check_skin_model.py` checks it on HAM10000 test images) |
| Output | 7 probabilities after temperature scaling (T = 1.756) |
| Classes | `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv`, `vasc` |
| Code in the app | `src/skin_model.py` |
| File location | `models/` on each machine. Never in Git. Planned: Hugging Face Hub |

## 3. Intended use

- **For:** showing a user possible matches and a calibrated confidence for a lesion photo, inside a guidance app that also gives general advice (ABCDE mole signs) and always advises a doctor when unsure.
- **Not for:** diagnosis, screening, or replacing a doctor. Not for rashes, eczema, acne, hives or infections, because those classes are not in the training data. Not for faces or ID documents.

## 4. Data

| Item | Value |
|---|---|
| Dataset | HAM10000: 10,015 dermoscopy images, 7 classes, with `HAM10000_metadata.csv` |
| Split | 80 / 10 / 10 **by `lesion_id`**, so the same lesion is never in two sets |
| Train / validation / test | 7,995 / 1,028 / 992 images (5,975 / 748 / 747 lesions) |
| Imbalance | `nv` (common mole) is 67% of the training images |

| Class | Meaning | Train | Val | Test |
|---|---|---|---|---|
| `nv` | Common mole | 5,369 | 685 | 651 |
| `bkl` | Benign keratosis-like lesion | 885 | 113 | 101 |
| `mel` | Melanoma | 884 | 118 | 111 |
| `bcc` | Basal cell carcinoma | 395 | 53 | 66 |
| `akiec` | Actinic keratosis | 247 | 42 | 38 |
| `vasc` | Vascular lesion | 115 | 12 | 15 |
| `df` | Dermatofibroma | 100 | 5 | 10 |

## 5. Training

Three models were compared, each with 3 seeds (42, 7, 123): **A** a CNN from scratch, **B** MobileNetV2 with a frozen backbone, **C** EfficientNet-B0 fine-tuned in two stages. Image size 224, Adam, cross-entropy with class weights (for example `nv` 0.21, `df` 11.4, `vasc` 9.9), data augmentation, early stopping on validation. The deployed model is **C, seed 7**.

## 6. Results (test set, mean ± std over 3 seeds)

| Model | Accuracy | Macro F1 | Melanoma recall | AUC | Params (M) | Size (MB) | Latency (ms) | Train time (min) |
|---|---|---|---|---|---|---|---|---|
| A: scratch CNN | 0.641 ± 0.007 | 0.481 ± 0.034 | 0.628 ± 0.021 | 0.906 ± 0.013 | 2.36 | 9.5 | 3.5 | 19.2 |
| B: MobileNetV2 frozen | 0.563 ± 0.050 | 0.416 ± 0.020 | 0.604 ± 0.136 | 0.898 ± 0.008 | 2.23 | 9.2 | 5.6 | 4.0 |
| **C: EfficientNet-B0 fine-tuned** | **0.821 ± 0.009** | **0.742 ± 0.014** | 0.652 ± 0.068 | **0.968 ± 0.001** | 4.02 | 16.4 | 8.7 | 12.0 |

Latency was measured per image in the training environment. In the app on a laptop CPU, one test photo took about 1 second including the heatmap.

**Per-class recall of Model C (mean of 3 seeds) and test size:**

| Class | Recall | Test images |
|---|---|---|
| `df` | 0.933 ± 0.115 | 10 |
| `nv` | 0.887 ± 0.020 | 651 |
| `vasc` | 0.822 ± 0.038 | 15 |
| `bkl` | 0.716 ± 0.087 | 101 |
| `bcc` | 0.677 ± 0.137 | 66 |
| `akiec` | 0.667 ± 0.015 | 38 |
| `mel` | 0.652 ± 0.068 | 111 |

**Deployed model (seed 7):** accuracy 0.826, macro F1 0.758, melanoma recall 0.649, AUC 0.967.

## 7. Calibration and decision policy

- **Temperature scaling** (fitted on the validation set, T = 1.756) lowered the expected calibration error from 0.070 to 0.029.
- **Minimum confidence 0.5:** if the top probability is below 0.5, the app says the photo is unclear and advises seeing a doctor.
- **Melanoma warning at 0.25:** if the melanoma probability reaches 0.25, a warning is shown even when another class is on top.
- **Not yet measured:** melanoma recall with the 0.25 rule applied. The 0.652 above is the plain top-1 recall.

## 8. Limits and risks (read before trusting any number)

- **Dermoscopy vs phone photos.** The training images are close-up, calibrated dermoscopy images. Ordinary phone photos are different, so accuracy there will be lower. The phone-photo test (10 to 20 consented photos) is not done yet.
- **Only 7 classes, mostly moles.** The model cannot recognise acne, eczema, psoriasis, rashes or infections. It will still output one of its 7 classes, so low confidence is the only protection. There is no separate "not skin" detector yet.
- **Melanoma recall is weak.** About 65% of melanomas in the test set were ranked first. This is why the app shows the top 3, a separate warning rule, and always advises a doctor.
- **Skin tone.** HAM10000 is mostly lighter skin. The fairness test on a tone-labelled dataset is not done yet. Our users are in Pakistan, so this matters.
- **Small classes.** `df` has 10 and `vasc` has 15 test images, so their recall numbers are very uncertain. The validation set has only 5 `df` and 12 `vasc` images, which makes the temperature fit weaker for those classes.
- **Model B is unstable** (best epoch ranged from 1 to 11 across seeds).
- **Checks still open:** `fit_check.csv` has empty train-accuracy columns, so the "GOOD FIT" verdicts are not backed by that data. Confirm that temperature was fitted on validation and that seed 7 was chosen by validation score, not test score.

## 9. Ethics and safety

- The app shows possible matches, never a diagnosis, and always advises a doctor for serious or unclear cases.
- Photos are cleaned (metadata removed, resized), used in memory only, and never stored.
- A rule-based emergency gate runs before everything, and a rule-based output check runs after.
- Users should avoid faces and ID documents in photos.

## 10. Planned improvements

1. Phone-photo test and domain-gap number.
2. Extra common-conditions dataset (acne, eczema, psoriasis) and retraining as v1.1.
3. Fairness test on a skin-tone-labelled dataset.
4. Re-measure melanoma recall with the 0.25 rule.
5. Upload the model to Hugging Face Hub and load it from there.
