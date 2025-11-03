from sentence_transformers import SentenceTransformer
import numpy as np

def embed_chunks(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    return embeddings

if __name__ == "__main__":
    with open("chunks.txt", "r", encoding="utf-8") as f:
        chunks = f.read().split("\n\n---\n\n")
    embeddings = embed_chunks(chunks)
    np.save("embeddings.npy", embeddings)

