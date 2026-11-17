# DermaVC-Text (v3.0) – End-to-End Proposal, Dataset Specification, and Model Training Plan
**Project:** Vital Check AI (Bilingual / Trilingual Dermatology Guidance Platform for Pakistan)  
**Lead & Integrator:** Muhammad Abdullah Nawaz (SAP ID: 70174218)  
**DermaVC-Text Core Team:** Yousaf (Data Lead, Models A & B), Izhan (Training Lead, Model C & Calibration), Rehman (Knowledge Base, Evaluation & Model Card)  
**Date:** 16 November 2026  
**Version:** 3.0 (Supersedes v2; incorporates concrete dataset files, public benchmark mappings, free-stack execution, and validated baseline scripts)

---

## Executive Summary & Core Objective

In **Vital Check AI**, users describe their dermatological symptoms using English, Urdu script (Nastaliq), or Roman Urdu (e.g., *"meri kohni par khujli aur dry patches hain"*). In the initial architecture, symptom routing relied on nearest-neighbor cosine retrieval against a 9-condition text knowledge base using generic sentence embeddings. This baseline suffered from high semantic confusion on clinical nuance (e.g., distinguishing *acne* from *folliculitis*, or *eczema* from *contact dermatitis*), could not capture colloquial Roman Urdu symptom descriptions reliably, and was incapable of distinguishing clinical complaints from greetings, vague statements, or off-topic queries.

Following the successful training, calibration, and integration of our vision model **DermaVC-Net** (EfficientNet-B0, 7 classes, Macro F1 $0.742 \pm 0.014$, Test Accuracy $0.821 \pm 0.009$), the team is building our second proprietary model: **DermaVC-Text**.

Unlike earlier planning drafts that lacked concrete dataset files, **the DermaVC-Text dataset has been actively built and committed directly to the project repository under `data/text_dataset/`**:
- **Dataset Name:** `PakDermaText-28` (`DermaVC-Text-Corpus-v1.0`)
- **Total Training Corpus:** 2,800 rows ($28 \text{ classes} \times 100 \text{ rows}$) across English, Roman Urdu, and Urdu script.
- **Stratified Training Split:** `data/text_dataset/train.csv` (2,240 rows, 80%)
- **Validation Split:** `data/text_dataset/val.csv` (560 rows, 20%)
- **Locked Evaluation Set:** `data/text_dataset/test.csv` (184 pure human-written evaluation rows across all 28 classes)
- **External Public Benchmark Integration:** Mapped to Kaggle `Symptom2Disease` and Hugging Face `gretelai/symptom_to_diagnosis` via `scripts/load_hf_kaggle_data.py`.

---

## 1. System Architecture & End-to-End Pipeline

```
[ User Input (Text / Speech-to-Text) ]
                 |
                 v
   +------------------------------+
   | Layer 1: Safety & Red Flags  |  --> [ Emergency Gate Triggered ]
   | (Chest pain, breathing,      |      (Immediate Red Banner & ER Guidance)
   |  anaphylaxis, severe burns)  |
   +------------------------------+
                 | PASS
                 v
   +------------------------------+
   | Layer 2: DermaVC-Text Model  |  <-- [ Trained on data/text_dataset/train.csv ]
   | (28 Classes, Calibrated)     |      (paraphrase-multilingual-MiniLM-L12-v2)
   +------------------------------+
                 |
        +--------+--------+------------------------+
        |                 |                        |
        v                 v                        v
  [ Non-Clinical ]  [ Low Confidence ]       [ High Confidence ]
  - greeting        (Top Prob < 0.55)        (Top Prob >= 0.55)
  - too_vague             |                        |
  - off_topic             v                        v
  - other_skin      [ Interactive Clarification [ Top-3 Conditions Identified ]
        |             Follow-up Question ]         |
        v                                          v
  [ Direct Conversational /                 [ Layer 3: Knowledge Base Retrieval ]
    Safety Guidance Handler ]               (ChromaDB: 24 Conditions + Sources)
                                                   |
                                                   v
                                            [ Layer 4: LLM Explainer ]
                                            (Gemini / Ollama / KB text fallback)
                                                   |
                                                   v
                                            [ Layer 5: Output Guardrail ]
                                            (Blocks prescribing, doses, diagnosis)
                                                   |
                                                   v
                                            [ Streamlit UI + Workflow Tab + PDF ]
```

---

## 2. The 28-Class Taxonomy

Every training row, test row, and model prediction adheres to these **exact 28 string labels** (lowercase, snake_case):

### Group A: Clinical Conditions (12 Classes)
| Class Label | Clinical Condition Name | Distinctive Diagnostic Features |
|---|---|---|
| `eczema` | Atopic Dermatitis | Chronic, recurrent, dry, intensely itchy patches; flexural creases (inner elbows, behind knees). |
| `psoriasis` | Plaque Psoriasis | Well-demarcated erythematous plaques with thick, silvery-white scales; extensor surfaces (elbows, knees, scalp). |
| `acne` | Acne Vulgaris | Comedones (blackheads/whiteheads), inflammatory papules, pustules, cysts on face, chest, back. |
| `ringworm` | Tinea Corporis / Cruris | Annular (ring-shaped) erythematous patch with raised, scaly active border and central clearing. |
| `contact_dermatitis` | Contact Dermatitis | Acute vesicular or erythematous eruption localized to allergen/irritant contact site (soaps, metals, cosmetics). |
| `hives` | Urticaria | Transient, pruritic, edematous wheals/welts that migrate and typically resolve within 24 hours. |
| `scabies` | Sarcoptic Scabies | Nocturnal severe pruritus, serpiginous burrows, web spaces of fingers, flexor wrists, genitalia; household spread. |
| `cellulitis` | Bacterial Cellulitis | Unilateral spreading erythema, warmth, severe edema, pain, systemic fever. *Clinical Red Flag.* |
| `melanoma_warning_signs` | Suspicious Pigmented Lesion | ABCDE criteria: Asymmetry, Border irregularity, Color variegation, Diameter >6mm, Evolving mole. |
| `dandruff` | Seborrheic Dermatitis (Scalp) | Greasy, yellowish or white flakes, mild erythema, scalp pruritus without significant hair loss. |
| `fungal_infection` | Superficial Mycoses | Maceration, scaling, erythema in moist intertriginous zones (toes/tinea pedis, groin/tinea cruris, submammary). |
| `warts` | Verruca Vulgaris | Hyperkeratotic, exophytic, rough papules with tiny punctate black dots (thrombosed capillaries); hands, feet. |

### Group B: Clinical Conditions (12 Classes)
| Class Label | Clinical Condition Name | Distinctive Diagnostic Features |
|---|---|---|
| `impetigo` | Impetigo Contagiosa | Superficial vesicles erupting into classic honey-colored (amber) crusted erosions, common around nose/mouth in children. |
| `vitiligo` | Vitiligo | Completely depigmented (chalk-white), sharply demarcated macules/patches without scale or induration. |
| `heat_rash` | Miliaria Rubra | Prickly, tiny erythematous papules and vesicles in sweat retention zones during hot/humid weather. |
| `sunburn` | Solar Erythema | Diffuse erythema, tenderness, cutaneous heat, peeling following acute ultraviolet exposure. |
| `insect_bites` | Arthropod Bite Reactions | Discrete, grouped or scattered punctate papules/urticarial lesions, central punctum, localized itching/swelling. |
| `dry_skin` | Xerosis Cutis | Generalized fine scaling, dullness, tight feeling, superficial cracking without distinct primary rash. |
| `folliculitis` | Superficial Folliculitis | Small pustules or erythematous papules pierced by a central hair shaft, common post-shaving or friction. |
| `boils` | Furuncles / Carbuncles | Deep, tender, fluctuant erythematous perifollicular nodules with central necrotic plug or purulent drainage. |
| `keratosis_pilaris` | Keratosis Pilaris | Follicular keratotic "goosebump-like" rough, small papules ("strawberry skin") on posterior upper arms and thighs. |
| `melasma` | Chloasma / Melasma | Symmetric, hyperpigmented light-to-dark brown macules on sun-exposed facial areas (cheeks, forehead, upper lip). |
| `cold_sores` | Herpes Simplex Labialis | Prodromal tingling/burning followed by grouped painful vesicles on an erythematous base at the vermilion border of lips. |
| `scalp_lice` | Pediculosis Capitis | Intense scalp pruritus, viable nits cemented firmly to hair shafts within 1 cm of scalp, visible crawling lice. |

### Group C: Non-Clinical / System Routing Classes (4 Classes)
| Class Label | Category Meaning | Representative Examples |
|---|---|---|
| `greeting` | Conversational openers, greetings, thanks | *"hello"*, *"assalam o alaikum"*, *"kia haal hai"*, *"thank you doctor"*, *"bye"* |
| `too_vague` | Underspecified complaints lacking clinical detail | *"help"*, *"mujhe skin ka masla hai"*, *"skin is bad"*, *"madad chahiye"*, *"i have a rash"* |
| `off_topic` | Questions unrelated to human skin health | *"what is the weather today"*, *"how to repair car"*, *"recipe for biryani"*, *"chest pain"* (non-skin) |
| `other_skin` | Real dermatological/cosmetic concerns outside the 24 classes | Nail fungus, severe alopecia/hair loss, keloid scars, stretch marks, wrinkles, hyperhidrosis |

---

## 3. Dataset Architecture: Concrete Files & Public Sources

### 3.1 Repository Dataset Files (Generated & Ready to Use)
The dataset files are located in `data/text_dataset/`:

| Dataset File Path | Rows | Purpose & Content | Language Distribution |
|---|---|---|---|
| `data/text_dataset/raw_corpus.csv` | **2,800** | Full pre-split corpus (100 rows per class across 28 classes) | 980 English, 980 Roman Urdu, 840 Urdu script |
| `data/text_dataset/train.csv` | **2,240** | **Stratified Training Split (80%)** for fitting Model A, B, and C | 784 English, 784 Roman Urdu, 672 Urdu script |
| `data/text_dataset/val.csv` | **560** | **Stratified Validation Split (20%)** for hyperparameter tuning & calibration | 196 English, 196 Roman Urdu, 168 Urdu script |
| `data/text_dataset/test.csv` | **184** | **Locked Test Set** (100% human-authored, 6/condition, 10/other) | 64 English, 60 Roman Urdu, 60 Urdu script |
| `data/text_dataset/dataset_summary.json` | Meta | Complete summary statistics, counts, and class balance metrics | Verified balanced across all 28 classes |

### 3.2 External Open-Source Clinical Benchmarks
To augment or scale the training pool with external clinical datasets at **$0 cost**, the helper script `scripts/load_hf_kaggle_data.py` connects to:

1. **Kaggle `Symptom2Disease`** (`niyarrbarman/symptom2disease`):
   - 1,200 real patient conversational symptom descriptions mapped to 24 diseases including Psoriasis, Fungal infection, Impetigo, Acne, and Allergy.
   - License: CC0 (Public Domain).
2. **Hugging Face `gretelai/symptom_to_diagnosis`**:
   - Natural language conversational dialogues between patients and clinicians for symptom-to-disease classification.
   - License: Apache-2.0. Accessible directly via `datasets.load_dataset('gretelai/symptom_to_diagnosis')`.
3. **Hugging Face `redlessone/Derm1M`**:
   - 1.02M clinical image-text pairs containing detailed dermatologist clinical descriptions and symptom texts across 390 conditions.

### 3.3 Dataset Quality Audit & Zero-Leakage Architecture (PakDermaText-28 v2.0 Clean)
A thorough automated integrity audit was conducted across the generated splits to ensure scientific validity:

| Audit Check | Initial Team Draft (v1.0) | Clean Production Dataset (v2.0 Clean) | Status & Fix Implemented |
|---|---|---|---|
| **Test Set Leakage in Train** | **147 / 184 rows (79.9%)** | **0 / 184 rows (0.0%)** | **FIXED:** Strict partition quarantine; test seeds strictly held out from training candidate generator. |
| **Test Set Leakage in Val** | **35 / 184 rows (19.0%)** | **0 / 184 rows (0.0%)** | **FIXED:** Complete isolation; verified zero verbatim or normalized overlap. |
| **Train & Val Split Overlap** | **0 rows** | **0 rows** | **VERIFIED:** Disjoint 80/20 stratified split. |
| **Non-Clinical Modifiers** | 118 nonsensical rows (e.g. *"hello getting worse"*, *"car puncture 3 din se"*) | **0 rows** | **FIXED:** Pure authentic 35–40 phrase candidate pools per language for `greeting`, `too_vague`, and `off_topic`. |
| **Redundant Phrasing** | Double durations (e.g. *"for three weeks for 2 weeks"*) | **0 rows** | **FIXED:** Multilingual regex duration detector (`has_duration`) prevents redundant duration concatenation. |
| **Emergency Safety Routing** | Missing from off-topic | **Included** | Acute non-derma red flags (stroke, crushing chest pain) seeded under `off_topic` for safety triage. |
   - License: Free for academic research.

---

## 4. The 100% Free Technology Stack

```
+-------------------+-------------------------------------------------------------+
| Layer             | Free Solution Selected                                      |
+-------------------+-------------------------------------------------------------+
| Active Dataset    | data/text_dataset/train.csv (Committed locally in repo)    |
| Public Benchmarks | gretelai/symptom_to_diagnosis (HF) + Symptom2Disease (Kaggle)|
| Synthetic Augment | Google AI Studio (Free Gemini 2.0/1.5 Flash API, 0 cost)     |
| Local Augment     | Ollama with Llama 3.2 3B or Mistral 7B (Offline free)       |
| Cloud Compute     | Google Colab Free T4 GPU (16GB VRAM) / Kaggle GPU P100       |
| Base Pretrained   | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Model Hosting     | Hugging Face Hub (mabdullah218/dermavc-text, Free Git-LFS)   |
| Local Inference   | Pure CPU inference via PyTorch / scikit-learn (< 50ms)      |
| Storage & Sync    | Shared Google Drive Folder for team CSVs & checkpoints      |
+-------------------+-------------------------------------------------------------+
```

---

## 5. Model Architectures & Baseline Results

We train and evaluate **three distinct models (A, B, C)** across **3 fixed random seeds (42, 7, 123)**.

### Model A: Character-Level TF-IDF + Regularized Logistic Regression
- **Verified Local Test Run:** Executed via `scripts/train_baseline_text.py` on clean `data/text_dataset/train.csv` (2,240 rows):
  - **Validation Accuracy:** $98.57\%$ | **Validation Macro F1:** $0.9856$
  - **Locked Test Set Accuracy:** **86.96%** | **Test Macro F1:** **0.8580** (Completely unseen, zero leakage)
    - **English Test Accuracy:** $90.62\%$ (64 samples)
    - **Roman Urdu Test Accuracy:** $88.33\%$ (60 samples)
    - **Urdu Script Test Accuracy:** $81.67\%$ (60 samples)
  - **Training Latency:** 3.4 seconds on CPU.
- **Pipeline:** `TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True)` + `LogisticRegression(C=1.0, class_weight='balanced')`.

### Model B: Frozen Multilingual-MiniLM Embeddings + Logistic Regression
- Uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` to extract 384-dimensional dense vectors.
- Fits regularized Logistic Regression ($C \in \{0.1, 1.0, 10.0\}$) on the vectors.

### Model C: Fine-Tuned Multilingual-MiniLM End-to-End
- Base architecture: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` with `AutoModelForSequenceClassification` (28 output logits).
- Hyperparameters: Optimizer `AdamW(lr=2e-5, weight_decay=0.01)`, Batch size 32, Max sequence length 64 tokens, Epochs up to 6, Warmup 10%, Linear decay, Early stopping on Validation Macro F1.

---

## 6. Temperature Scaling & Calibration

Logits $z_i$ are calibrated post-training on `data/text_dataset/val.csv`:

$$\hat{p}_i = \frac{\exp(z_i / T)}{\sum_{j=1}^{28} \exp(z_j / T)}$$

- The temperature parameter $T > 0$ is optimized using L-BFGS-B to minimize Cross-Entropy on `val.csv`.
- Target: Reduce Expected Calibration Error (ECE) below $0.030$.
- Confidence Threshold: Set at $t^* = 0.55$. Queries with top probability $< 0.55$ trigger an active clarification question in the app.

---

## 7. Production `predict.py` Code Contract

Abdullah integrates this standalone CPU module into `src/` and `app.py`:

```python
"""
DermaVC-Text Model Inference Module
Author: DermaVC-Text Team (Yousaf, Izhan, Rehman)
Integration: Muhammad Abdullah Nawaz
"""
import json
from pathlib import Path
from typing import Any, Dict
import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

_MODEL = None
_TOKENIZER = None
_LABEL_MAP = None
_CALIBRATION = None
_DEVICE = torch.device("cpu")


def load(model_dir: str) -> None:
    """Loads the model, tokenizer, label map, and calibration parameters once into memory."""
    global _MODEL, _TOKENIZER, _LABEL_MAP, _CALIBRATION
    path = Path(model_dir)

    with open(path / "label_map.json", "r", encoding="utf-8") as f:
        _LABEL_MAP = json.load(f)

    with open(path / "calibration.json", "r", encoding="utf-8") as f:
        _CALIBRATION = json.load(f)

    _TOKENIZER = AutoTokenizer.from_pretrained(str(path / "model"))
    _MODEL = AutoModelForSequenceClassification.from_pretrained(str(path / "model"))
    _MODEL.to(_DEVICE)
    _MODEL.eval()


def predict(text: str, top_k: int = 3) -> Dict[str, Any]:
    """Predicts calibrated top-k condition probabilities for an input message."""
    if _MODEL is None:
        raise RuntimeError("DermaVC-Text model is not loaded. Call load(model_dir) first.")

    inputs = _TOKENIZER(
        text,
        max_length=64,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    ).to(_DEVICE)

    with torch.no_grad():
        outputs = _MODEL(**inputs)
        logits = outputs.logits.squeeze(0).numpy()

    temperature = _CALIBRATION.get("temperature", 1.0)
    scaled_logits = logits / temperature

    exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
    probs = exp_logits / np.sum(exp_logits)

    top_indices = np.argsort(probs)[::-1][:top_k]
    top_predictions = [
        {"label": _LABEL_MAP[idx], "probability": round(float(probs[idx]), 3)}
        for idx in top_indices
    ]

    top_prob = top_predictions[0]["probability"]
    threshold = _CALIBRATION.get("threshold", 0.55)
    top_label = top_predictions[0]["label"]
    non_clinical = {"greeting", "too_vague", "off_topic", "other_skin"}

    return {
        "top": top_predictions,
        "confident": bool(top_prob >= threshold),
        "threshold": threshold,
        "model": _CALIBRATION.get("version", "DermaVC-Text v1.0"),
        "top_label": top_label,
        "is_clinical": bool(top_label not in non_clinical)
    }
```

---

## 8. Updated Synchronized Project Timeline

| Milestone Date | Sprint Objective | Primary Owner | Deliverables |
|---|---|---|---|
| **16 Nov 2026** | Dataset Generation & Baseline Validation | Team & Abdullah | `train.csv` (2,240 rows), `val.csv` (560), `test.csv` (184) generated; Model A verified |
| **17 – 19 Nov** | Augmentation with Public Benchmarks | Yousaf & Izhan | Kaggle `Symptom2Disease` / HF `gretelai` merged |
| **20 – 22 Nov** | Model B & C Training across Seeds 42, 7, 123 | Izhan & Yousaf | Colab T4 GPU runs, weights saved |
| **23 – 24 Nov** | Temperature Calibration & Thresholding | Izhan | Validation ECE $< 0.030$, `calibration.json` |
| **25 – 26 Nov** | Evaluation vs Baseline Search & Model Card | Rehman | Benchmarks table, confusion matrix, `MODEL_CARD.md` |
| **27 Nov 2026** | Hand-over Package Assembly | Izhan & Rehman | Delivery of `DermaVC-Text-v1.0.zip` |
| **28 – 29 Nov** | Integration into Streamlit & Workflow UI | Abdullah | Pipeline integration, test suite passing |
| **30 Nov 2026** | Research Paper Writeup & Live Spaces Release | All | Research paper submission & Hugging Face deployment |
