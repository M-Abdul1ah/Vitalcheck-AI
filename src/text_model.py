"""
src/text_model.py
-----------------
DermaVC-Text in the app: multilingual text symptom classifier for VitalCheck AI.
Supports English, Roman Urdu, and Urdu script across 28 classes (24 clinical + 4 non-clinical).

Models supported:
- Model A (Default): Fast Character/Word TF-IDF + Logistic Regression (models/text_models/model_a_tfidf.pkl)
- Model C (Transformer): Fine-Tuned Multilingual-MiniLM (models/text_models/model_c_reproducible_best)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.getenv("TEXT_MODELS_DIR", str(ROOT / "models" / "text_models")))
LABEL_MAP_PATH = ROOT / "src" / "label_mapping.json"

MODEL_A_PATH = MODELS_DIR / "model_a_tfidf.pkl"
MODEL_C_PATH = MODELS_DIR / "model_c_reproducible_best"

DEFAULT_CONFIDENCE_THRESHOLD = 0.55

NON_CLINICAL_CLASSES = {"greeting", "too_vague", "off_topic", "other_skin"}

# English display name, Urdu display name
LABELS = {
    "eczema": ("Eczema (Atopic Dermatitis)", "ایگزیما (خارش اور سوزش زدہ جلد)"),
    "psoriasis": ("Psoriasis (Scaly Plaques)", "سورائسس (چنبل، چاندی جیسے چھلکے)"),
    "acne": ("Acne Vulgaris (Pimples/Blackheads)", "کیل مہاسے (چہرے اور جسم کے دانے)"),
    "ringworm": ("Ringworm (Tinea Corporis)", "داد / چنبل نما گول دائرہ"),
    "contact_dermatitis": ("Contact Dermatitis", "کانٹیکٹ الرجی (کسی چیز کے چھونے سے سوزش)"),
    "hives": ("Hives (Urticaria)", "پتی / چھپاکی (جلد پر ابھرے سرخ نشانات)"),
    "scabies": ("Scabies (Mite Infestation)", "سکیبیز / رات کی شدید خارش"),
    "cellulitis": ("Cellulitis (Bacterial Skin Infection)", "سیلولائٹس (شدید بیکٹیریل انفیکشن)"),
    "melanoma_warning_signs": ("Melanoma Warning Signs (Suspicious Mole)", "میلانوما کے انتباہی علامات (مشکوک تل)"),
    "dandruff": ("Dandruff (Seborrheic Dermatitis)", "خشکی / سکری (سر کی جلد کی سوزش)"),
    "fungal_infection": ("Fungal Skin Infection", "فنگل انفیکشن (پھپھوندی کا انفیکشن)"),
    "warts": ("Warts (Verruca)", "مسے (جلد کے سخت ابھار)"),
    "impetigo": ("Impetigo (Crusted Sores)", "امپیٹیگو (زرد چھلکوں والے دانے)"),
    "vitiligo": ("Vitiligo (White Patches)", "برص / پھلبہری (سفید داغ)"),
    "heat_rash": ("Heat Rash (Prickly Heat)", "گرمی دانے (پسینے کے دانے)"),
    "sunburn": ("Sunburn", "دھوپ سے جھلسنا"),
    "insect_bites": ("Insect Bites", "کیڑے کے کاٹنے کے نشانات"),
    "dry_skin": ("Dry Skin (Xerosis)", "خشک جلد"),
    "folliculitis": ("Folliculitis (Hair Follicle Infection)", "بالوں کی جڑوں کی سوزش"),
    "boils": ("Boils (Furuncles)", "پھوڑے پھنسیاں"),
    "keratosis_pilaris": ("Keratosis Pilaris", "کھردری جلد (اسٹرابیری اسکن)"),
    "melasma": ("Melasma (Dark Skin Patches)", "جھائیاں (چہرے پر گہرے دھبے)"),
    "cold_sores": ("Cold Sores (Herpes Simplex)", "ہونٹوں کے چھالے"),
    "scalp_lice": ("Scalp Lice (Head Lice)", "سر کی جوئیں"),
    "greeting": ("Greeting / Small Talk", "سلام اور عمومی گفتگو"),
    "too_vague": ("Too Vague / Needs Details", "غیر واضح سوال"),
    "off_topic": ("Off-Topic Query", "غیر متعلقہ سوال"),
    "other_skin": ("Other Skin / Hair / Nail Condition", "جلد یا ناخن کا دیگر مسئلہ")
}

# Maps clinical class to knowledge base entry prefix in data/dermatology_kb.txt
KB_CLASS_MAP = {
    "eczema": "Eczema (atopic dermatitis)",
    "psoriasis": "Psoriasis",
    "acne": "Acne",
    "ringworm": "Ringworm (tinea)",
    "contact_dermatitis": "Contact dermatitis",
    "hives": "Hives (urticaria)",
    "scabies": "Scabies",
    "cellulitis": "Cellulitis (skin infection)",
    "melanoma_warning_signs": "Melanoma warning signs (ABCDE)",
    "dandruff": "Dandruff (seborrheic dermatitis of the scalp)",
    "fungal_infection": "Fungal skin infection (athlete's foot, groin and body fungus)",
    "warts": "Warts",
    "impetigo": "Impetigo",
    "vitiligo": "Vitiligo",
    "heat_rash": "Heat rash (prickly heat)",
    "sunburn": "Sunburn",
    "insect_bites": "Insect bites",
    "dry_skin": "Dry skin (xerosis)",
    "folliculitis": "Folliculitis",
    "boils": "Boils",
    "keratosis_pilaris": "Keratosis pilaris",
    "melasma": "Melasma",
    "cold_sores": "Cold sores",
    "scalp_lice": "Scalp lice (head lice)",
}


class TextModelError(Exception):
    """Raised when the text model fails to load or infer."""


def is_available() -> bool:
    """Returns True if at least one trained text model checkpoint is present."""
    return MODEL_A_PATH.exists() or (MODEL_C_PATH / "model.safetensors").exists()


def why_unavailable() -> str:
    """Explains why the text model cannot run."""
    if is_available():
        return ""
    return (
        f"Text model checkpoints not found. Expected {MODEL_A_PATH} or {MODEL_C_PATH}."
    )


class TextModel:
    """Inference engine for DermaVC-Text."""

    def __init__(self, model_type: Optional[str] = None):
        self.model_type = model_type or os.getenv("TEXT_MODEL_TYPE", "auto").lower()
        self.model_name = ""
        self.pipeline = None
        self.tokenizer = None
        self.transformer = None
        self.inv_mapping = {}

        self._load()

    def _load(self):
        # Auto-detect or use requested type
        use_c = (self.model_type == "transformer") or (
            self.model_type == "auto" and (MODEL_C_PATH / "model.safetensors").exists() and not MODEL_A_PATH.exists()
        )

        if not use_c and MODEL_A_PATH.exists():
            import joblib
            try:
                self.pipeline = joblib.load(MODEL_A_PATH)
                self.model_name = "DermaVC-Text Model A (TF-IDF + Logistic Regression)"
                self.model_type = "tfidf"
                return
            except Exception as e:
                # If loading Model A fails, try Model C
                pass

        if (MODEL_C_PATH / "model.safetensors").exists():
            try:
                import torch
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                self.tokenizer = AutoTokenizer.from_pretrained(str(MODEL_C_PATH))
                self.transformer = AutoModelForSequenceClassification.from_pretrained(str(MODEL_C_PATH))
                self.transformer.eval()

                mapping_file = MODEL_C_PATH / "label_mapping.json"
                if not mapping_file.exists():
                    mapping_file = LABEL_MAP_PATH
                with open(mapping_file, "r", encoding="utf-8") as f:
                    mapping = json.load(f)
                self.inv_mapping = {int(v): k for k, v in mapping.items()}

                self.model_name = "DermaVC-Text Model C (Fine-Tuned Multilingual-MiniLM)"
                self.model_type = "transformer"
                return
            except Exception as e:
                raise TextModelError(f"Failed to load transformer Model C: {e}")

        raise TextModelError(why_unavailable())

    def predict(self, text: str, top_k: int = 3, temperature: float = 1.0) -> Dict[str, Any]:
        """
        Predicts the top-k skin conditions for the input text query.
        Returns probabilities, human-readable labels, and clinical routing status.
        """
        text = (text or "").strip()
        if not text:
            raise TextModelError("Input text cannot be empty.")

        if self.model_type == "tfidf":
            probs = self.pipeline.predict_proba([text])[0]
            classes = list(self.pipeline.classes_)
            class_prob_pairs = list(zip(classes, probs))
        else:
            import numpy as np
            import torch

            inp = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                out = self.transformer(**inp)
                logits = out.logits.squeeze(0).cpu().numpy()

            scaled = logits / max(temperature, 0.01)
            exp_logits = np.exp(scaled - np.max(scaled))
            probs = exp_logits / np.sum(exp_logits)

            classes = [self.inv_mapping.get(i, f"class_{i}") for i in range(len(probs))]
            class_prob_pairs = list(zip(classes, probs))

        # Sort descending by probability
        class_prob_pairs.sort(key=lambda x: x[1], reverse=True)

        top_predictions = []
        for label, prob in class_prob_pairs[:top_k]:
            en_name, ur_name = LABELS.get(label, (label.replace("_", " ").title(), label))
            top_predictions.append({
                "label": label,
                "name": en_name,
                "name_ur": ur_name,
                "probability": round(float(prob), 4),
                "percentage": f"{round(float(prob) * 100, 1)}%",
                "kb_title": KB_CLASS_MAP.get(label)
            })

        top_match = top_predictions[0]
        top_prob = top_match["probability"]
        is_clinical = top_match["label"] not in NON_CLINICAL_CLASSES

        return {
            "top": top_predictions,
            "top_label": top_match["label"],
            "top_name": top_match["name"],
            "top_name_ur": top_match["name_ur"],
            "probability": top_prob,
            "confident": bool(top_prob >= DEFAULT_CONFIDENCE_THRESHOLD),
            "threshold": DEFAULT_CONFIDENCE_THRESHOLD,
            "model": self.model_name,
            "is_clinical": is_clinical,
            "kb_title": top_match["kb_title"]
        }
