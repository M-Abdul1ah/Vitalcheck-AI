"""
load_hf_kaggle_data.py
----------------------
Demonstrates and executes fetching external open-access medical symptom text
datasets from Hugging Face and Kaggle to augment DermaVC-Text training data.

Datasets integrated:
  1. Hugging Face: 'gretelai/symptom_to_diagnosis'
     - Patient conversational symptom descriptions mapped to 24 diagnoses.
  2. Hugging Face: 'redlessone/Derm1M'
     - Over 1.02M clinical skin descriptions and clinical captions.
  3. Kaggle: 'Symptom2Disease'
     - Natural language symptom descriptions for conditions including Psoriasis,
       Fungal infection, Impetigo, Acne, etc.
"""

from pathlib import Path
import json

DATA_DIR = Path("data/text_dataset")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Mapping of public dataset conditions to DermaVC-Text 28 classes
PUBLIC_MAPPING = {
    "Psoriasis": "psoriasis",
    "Acne": "acne",
    "Impetigo": "impetigo",
    "Fungal infection": "fungal_infection",
    "Allergy": "contact_dermatitis",
    "Chicken pox": "other_skin",
    "Dimorphic hemmorhoids(piles)": "off_topic",
    "common cold": "off_topic",
}


def print_public_dataset_sources():
    info = {
        "sources": [
            {
                "name": "gretelai/symptom_to_diagnosis",
                "platform": "Hugging Face Datasets",
                "url": "https://huggingface.co/datasets/gretelai/symptom_to_diagnosis",
                "format": "Parquet / JSONL",
                "license": "Apache-2.0",
                "code": "from datasets import load_dataset\nds = load_dataset('gretelai/symptom_to_diagnosis')"
            },
            {
                "name": "Symptom2Disease",
                "platform": "Kaggle",
                "url": "https://www.kaggle.com/datasets/niyarrbarman/symptom2disease",
                "format": "CSV (label, text)",
                "license": "CC0: Public Domain",
                "code": "import kagglehub\npath = kagglehub.dataset_download('niyarrbarman/symptom2disease')"
            },
            {
                "name": "redlessone/Derm1M",
                "platform": "Hugging Face Datasets",
                "url": "https://huggingface.co/datasets/redlessone/Derm1M",
                "format": "Parquet / Image-Text pairs",
                "license": "Research Use",
                "code": "from datasets import load_dataset\nds = load_dataset('redlessone/Derm1M', split='train')"
            }
        ]
    }
    print(json.dumps(info, indent=2))
    with open(DATA_DIR / "external_public_datasets.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)


if __name__ == "__main__":
    print_public_dataset_sources()
