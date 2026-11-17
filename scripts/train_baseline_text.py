"""
train_baseline_text.py
----------------------
Trains and evaluates Model A (TF-IDF + Logistic Regression)
on the freshly generated PakDermaText-28 dataset splits.
"""

from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.pipeline import Pipeline

DATA_DIR = Path("data/text_dataset")

train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "val.csv")
test_df = pd.read_csv(DATA_DIR / "test.csv")

print(f"Loaded train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")

# Model A Pipeline: Character n-grams (2 to 5) + Balanced Logistic Regression
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        sublinear_tf=True,
        min_df=2
    )),
    ("clf", LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    ))
])

print("Training Model A...")
pipeline.fit(train_df["text"], train_df["label"])

# Validation eval
val_preds = pipeline.predict(val_df["text"])
val_acc = accuracy_score(val_df["label"], val_preds)
val_f1 = f1_score(val_df["label"], val_preds, average="macro")
print(f"Validation Accuracy: {val_acc:.4f}, Macro F1: {val_f1:.4f}")

# Test eval
test_preds = pipeline.predict(test_df["text"])
test_acc = accuracy_score(test_df["label"], test_preds)
test_f1 = f1_score(test_df["label"], test_preds, average="macro")
print(f"Test Set Accuracy:   {test_acc:.4f}, Macro F1: {test_f1:.4f}")

# Language breakdown on test set
for lang in ["en", "roman", "ur"]:
    sub = test_df[test_df["language"] == lang]
    sub_preds = pipeline.predict(sub["text"])
    acc = accuracy_score(sub["label"], sub_preds)
    print(f" - Test Accuracy ({lang}): {acc:.4f} ({len(sub)} samples)")
