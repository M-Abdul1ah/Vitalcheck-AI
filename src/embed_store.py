"""
Builds the vector database (run once, or whenever data/ changes).
Text files in data/ -> chunks -> embeddings -> ChromaDB (saved in chroma_db/).
"""
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_DIR = ROOT / "chroma_db"
COLLECTION = "dermatology"

# Same model as test_embeddings.py, so meaning -> vector works the same way
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(name=COLLECTION, embedding_function=embed_fn)


def load_chunks():
    """One chunk = one paragraph (blank-line separated) in each .txt file."""
    chunks, ids, metas = [], [], []
    for file in DATA_DIR.glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        for i, block in enumerate(text.split("\n\n")):
            block = block.strip()
            if block:
                chunks.append(block)
                ids.append(f"{file.stem}-{i}")
                metas.append({"source": file.name})
    return chunks, ids, metas


def build():
    collection = get_collection()
    chunks, ids, metas = load_chunks()
    collection.upsert(documents=chunks, ids=ids, metadatas=metas)
    print(f"Stored {len(chunks)} chunks in ChromaDB.")


if __name__ == "__main__":
    build()