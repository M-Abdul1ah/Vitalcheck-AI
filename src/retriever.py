"""
Finds the knowledge chunks closest in meaning to the user's symptoms.
"""
import numpy as np

from src.embed_store import embed_fn, get_collection


def retrieve(query: str, k: int = 3) -> list[str]:
    results = get_collection().query(query_texts=[query], n_results=k)
    return results["documents"][0]


def retrieve_with_scores(query: str, k: int = 3) -> list[tuple[str, float]]:
    """Same search, but also returns a 0-1 cosine similarity for each chunk (used by the Workflow tab)."""
    q = np.array(embed_fn([query])[0], dtype=float)
    res = get_collection().query(
        query_embeddings=[q.tolist()], n_results=k, include=["documents", "embeddings", "distances"]
    )
    docs = res["documents"][0]
    out = []
    for i, doc in enumerate(docs):
        try:
            d = np.array(res["embeddings"][0][i], dtype=float)
            score = float(np.dot(q, d) / (np.linalg.norm(q) * np.linalg.norm(d)))
        except Exception:                      # fall back to a distance-based score
            score = 1.0 / (1.0 + float(res["distances"][0][i]))
        out.append((doc, round(max(0.0, min(1.0, score)), 2)))
    return out


if __name__ == "__main__":
    for doc, score in retrieve_with_scores("itchy red patches on my elbows with dry scaly skin"):
        print(f"{score:.2f}", "-", doc[:100], "\n")
