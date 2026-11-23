"""
evaluate_all_models.py
----------------------
Evaluates all three trained DermaVC-Text models on the official locked test set:
  - Model A: TF-IDF + Logistic Regression
  - Model B: Frozen Multilingual-MiniLM + Logistic Regression
  - Model C: Fine-Tuned Multilingual-MiniLM (BertForSequenceClassification)
Outputs test accuracy, macro F1, and language-specific breakdowns (en, roman, ur).
"""

import json
from pathlib import Path
import joblib
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELS_DIR = Path("models/text_models")
DATA_DIR = Path("data/text_dataset")
RESULTS_DIR = Path("training/results/text_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

test_df = pd.read_csv(DATA_DIR / "test.csv")
print(f"Loaded {len(test_df)} locked test samples from {DATA_DIR / 'test.csv'}")

results = []

# 1. Model A Evaluation
model_a_path = MODELS_DIR / "model_a_tfidf.pkl"
if model_a_path.exists():
    print("\n--- Evaluating Model A (TF-IDF + Logistic Regression) ---")
    pipe = joblib.load(model_a_path)
    preds_a = pipe.predict(test_df["text"])
    acc_a = accuracy_score(test_df["label"], preds_a)
    f1_a = f1_score(test_df["label"], preds_a, average="macro")
    
    en_acc = accuracy_score(test_df[test_df["language"] == "en"]["label"], pipe.predict(test_df[test_df["language"] == "en"]["text"]))
    roman_acc = accuracy_score(test_df[test_df["language"] == "roman"]["label"], pipe.predict(test_df[test_df["language"] == "roman"]["text"]))
    ur_acc = accuracy_score(test_df[test_df["language"] == "ur"]["label"], pipe.predict(test_df[test_df["language"] == "ur"]["text"]))
    
    print(f"Overall Accuracy: {acc_a:.4f} | Macro F1: {f1_a:.4f}")
    print(f" - English: {en_acc:.4f} | Roman Urdu: {roman_acc:.4f} | Urdu Script: {ur_acc:.4f}")
    
    results.append({
        "Model": "Model A - TF-IDF Pipeline",
        "Test_Accuracy": round(acc_a, 4),
        "Test_Macro_F1": round(f1_a, 4),
        "English_Acc": round(en_acc, 4),
        "Roman_Urdu_Acc": round(roman_acc, 4),
        "Urdu_Script_Acc": round(ur_acc, 4)
    })

# 2. Model B Evaluation
model_b_path = MODELS_DIR / "model_b_minilm_lr.pkl"
if model_b_path.exists():
    print("\n--- Evaluating Model B (Frozen MiniLM + Logistic Regression) ---")
    embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    clf = joblib.load(model_b_path)
    
    embeds = embedder.encode(test_df["text"].tolist(), show_progress_bar=False)
    preds_b = clf.predict(embeds)
    acc_b = accuracy_score(test_df["label"], preds_b)
    f1_b = f1_score(test_df["label"], preds_b, average="macro")
    
    sub_en = test_df[test_df["language"] == "en"]
    sub_ro = test_df[test_df["language"] == "roman"]
    sub_ur = test_df[test_df["language"] == "ur"]
    
    en_acc = accuracy_score(sub_en["label"], clf.predict(embedder.encode(sub_en["text"].tolist(), show_progress_bar=False)))
    roman_acc = accuracy_score(sub_ro["label"], clf.predict(embedder.encode(sub_ro["text"].tolist(), show_progress_bar=False)))
    ur_acc = accuracy_score(sub_ur["label"], clf.predict(embedder.encode(sub_ur["text"].tolist(), show_progress_bar=False)))
    
    print(f"Overall Accuracy: {acc_b:.4f} | Macro F1: {f1_b:.4f}")
    print(f" - English: {en_acc:.4f} | Roman Urdu: {roman_acc:.4f} | Urdu Script: {ur_acc:.4f}")
    
    results.append({
        "Model": "Model B - Frozen MiniLM + LR",
        "Test_Accuracy": round(acc_b, 4),
        "Test_Macro_F1": round(f1_b, 4),
        "English_Acc": round(en_acc, 4),
        "Roman_Urdu_Acc": round(roman_acc, 4),
        "Urdu_Script_Acc": round(ur_acc, 4)
    })

# 3. Model C Evaluation
model_c_path = MODELS_DIR / "model_c_reproducible_best"
if model_c_path.exists():
    print("\n--- Evaluating Model C (Fine-Tuned Multilingual-MiniLM) ---")
    tokenizer = AutoTokenizer.from_pretrained(str(model_c_path))
    model_c = AutoModelForSequenceClassification.from_pretrained(str(model_c_path))
    model_c.eval()
    
    with open(model_c_path / "label_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    inv_map = {v: k for k, v in mapping.items()}
    
    preds_c = []
    for text in test_df["text"]:
        inp = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            out = model_c(**inp)
        pred_idx = torch.argmax(out.logits, dim=-1).item()
        preds_c.append(inv_map[pred_idx])
        
    acc_c = accuracy_score(test_df["label"], preds_c)
    f1_c = f1_score(test_df["label"], preds_c, average="macro")
    
    en_idx = test_df[test_df["language"] == "en"].index
    ro_idx = test_df[test_df["language"] == "roman"].index
    ur_idx = test_df[test_df["language"] == "ur"].index
    
    en_acc = accuracy_score(test_df.loc[en_idx, "label"], [preds_c[i] for i in en_idx])
    roman_acc = accuracy_score(test_df.loc[ro_idx, "label"], [preds_c[i] for i in ro_idx])
    ur_acc = accuracy_score(test_df.loc[ur_idx, "label"], [preds_c[i] for i in ur_idx])
    
    print(f"Overall Accuracy: {acc_c:.4f} | Macro F1: {f1_c:.4f}")
    print(f" - English: {en_acc:.4f} | Roman Urdu: {roman_acc:.4f} | Urdu Script: {ur_acc:.4f}")
    
    results.append({
        "Model": "Model C - Fine-Tuned MiniLM",
        "Test_Accuracy": round(acc_c, 4),
        "Test_Macro_F1": round(f1_c, 4),
        "English_Acc": round(en_acc, 4),
        "Roman_Urdu_Acc": round(roman_acc, 4),
        "Urdu_Script_Acc": round(ur_acc, 4)
    })

# Save to disk
res_df = pd.DataFrame(results)
res_path = RESULTS_DIR / "test_benchmark_results.csv"
res_df.to_csv(res_path, index=False)
print(f"\nSaved test benchmark results to {res_path}")
