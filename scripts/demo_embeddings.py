"""
Learning demo (not a test): how embeddings turn meaning into numbers.
Run:  python scripts/demo_embeddings.py
Uses the same multilingual model as the app, so an Urdu sentence and an English sentence can be compared.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

sentences = [
    "I have itchy red patches on my elbows",
    "میری کہنیوں پر خارش اور سرخ دھبے ہیں",
    "What's the weather today",
]
vectors = model.encode(sentences)


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


print("Similarity (closer to 1.0 = more similar meaning):\n")
for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        print(f"{sentences[i]!r} vs {sentences[j]!r} -> {cosine(vectors[i], vectors[j]):.3f}")
