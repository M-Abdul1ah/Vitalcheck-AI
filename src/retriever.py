"""
Finds the knowledge chunks closest in meaning to the user's symptoms.
"""
from src.embed_store import get_collection


def retrieve(query: str, k: int = 3) -> list[str]:
    results = get_collection().query(query_texts=[query], n_results=k)
    return results["documents"][0]


if __name__ == "__main__":
    for doc in retrieve("itchy red patches on my elbows with dry scaly skin"):
        print("-", doc[:120], "\n")