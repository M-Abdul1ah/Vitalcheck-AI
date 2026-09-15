from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the local embedding model (downloads once, then cached)
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    "I have a headache",
    "My head is hurting",
    "What's the weather today"
]

# Convert each sentence into a vector (list of numbers)
embeddings = model.encode(sentences)

# Compare how similar each pair of sentences is
print("Similarity scores (closer to 1.0 = more similar meaning):\n")
for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        score = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
        print(f'"{sentences[i]}"  vs  "{sentences[j]}"  ->  {score:.4f}')
